#!/usr/bin/env python3
"""
Hermes-Ecom infrastructure + documentation validator.

Static checks only — it validates the *definitions* in infra/ and the agreement
between AGENTS.md, HERMES-PROMPT.md and README.md. It does not contact Docker or
deploy anything.

PyYAML is used when present; without it the YAML-dependent checks downgrade to
NOTE rather than failing, so this stays runnable on a bare host.

Run:  python3 scripts/validate_infra.py [workspace_root]
Exit 0 = clean, 1 = at least one ERROR.
"""
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

errors, warnings, notes = [], [], []
err = errors.append
warn = warnings.append
note = notes.append


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


REQUIRED_INFRA = ["docker-compose.yml", ".env.example", "Makefile", "README.md",
                  "cloudflared/config.example.yml"]


def check_files(root):
    inf = os.path.join(root, "infra")
    if not os.path.isdir(inf):
        err("infra/ missing")
        return False
    for f in REQUIRED_INFRA:
        if not os.path.isfile(os.path.join(inf, f)):
            err(f"infra/{f} missing")
    if os.path.isfile(os.path.join(inf, ".env")):
        err("infra/.env exists in the source-of-record folder — real secrets must "
            "live only on the deploy host, never here")
    return True


def check_env_coverage(root):
    """Every ${VAR} used by compose must be declared in .env.example."""
    comp = os.path.join(root, "infra", "docker-compose.yml")
    envf = os.path.join(root, "infra", ".env.example")
    if not (os.path.isfile(comp) and os.path.isfile(envf)):
        return
    used = set(re.findall(r"\$\{(\w+)\}", read(comp)))
    declared = set(re.findall(r"^([A-Z][A-Z0-9_]*)=", read(envf), re.MULTILINE))
    for v in sorted(used - declared):
        err(f"docker-compose.yml uses ${{{v}}} but .env.example never declares it — "
            f"the stack will start with it empty")
    for v in sorted(declared - used):
        if v not in {"FIRECRAWL_API_URL", "MEDUSA_BACKEND_URL",
                     "NEXT_PUBLIC_MEDUSA_BACKEND_URL", "NEXT_PUBLIC_BASE_URL"}:
            note(f".env.example declares {v} which compose does not consume")


def check_compose(root):
    p = os.path.join(root, "infra", "docker-compose.yml")
    if not os.path.isfile(p):
        return
    text = read(p)
    if not HAVE_YAML:
        note("PyYAML absent — compose structural checks skipped (pip install pyyaml)")
        for s in ("medusa-server", "medusa-worker"):
            if s not in text:
                err(f"docker-compose.yml has no '{s}' service")
        return
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError as e:
        err(f"docker-compose.yml is not valid YAML: {str(e).splitlines()[0]}")
        return

    svcs = (doc or {}).get("services") or {}
    if not svcs:
        err("docker-compose.yml declares no services")
        return

    # Medusa v2 requires two processes; server-only silently drops background work.
    modes = {}
    for name, s in svcs.items():
        envd = (s or {}).get("environment") or {}
        if isinstance(envd, list):
            envd = dict(e.split("=", 1) for e in envd if "=" in e)
        if "MEDUSA_WORKER_MODE" in envd:
            modes[name] = str(envd["MEDUSA_WORKER_MODE"])
    if "server" not in modes.values():
        err("no service sets MEDUSA_WORKER_MODE=server")
    if "worker" not in modes.values():
        err("no service sets MEDUSA_WORKER_MODE=worker — Medusa v2 needs a separate "
            "worker or scheduled jobs and subscribers never run")

    # Nothing may be published to all interfaces; Cloudflare Tunnel is the ingress.
    for name, s in svcs.items():
        for port in ((s or {}).get("ports") or []):
            if not str(port).startswith("127.0.0.1:"):
                err(f"service '{name}' publishes {port} on all interfaces — bind "
                    f"127.0.0.1 and let Cloudflare Tunnel provide ingress")

    # Stateful deps must be health-gated, or Medusa races them on boot.
    for dep in ("postgres", "valkey"):
        if dep not in svcs:
            err(f"docker-compose.yml has no '{dep}' service")
            continue
        if not (svcs[dep] or {}).get("healthcheck"):
            err(f"service '{dep}' has no healthcheck")
    for name in [n for n, m in modes.items()]:
        d = (svcs.get(name) or {}).get("depends_on") or {}
        if isinstance(d, dict):
            for dep, cond in d.items():
                if isinstance(cond, dict) and cond.get("condition") != "service_healthy":
                    warn(f"'{name}' depends on '{dep}' without service_healthy")
        elif d:
            warn(f"'{name}' uses short-form depends_on — it will not wait for health")

    for dep in ("postgres", "valkey"):
        if dep in svcs and not (svcs[dep] or {}).get("volumes"):
            err(f"service '{dep}' has no volume — data is lost on recreate")


def check_tunnel(root):
    p = os.path.join(root, "infra", "cloudflared", "config.example.yml")
    if not os.path.isfile(p):
        return
    text = read(p)
    if HAVE_YAML:
        try:
            doc = yaml.safe_load(text) or {}
        except yaml.YAMLError as e:
            err(f"cloudflared config is not valid YAML: {str(e).splitlines()[0]}")
            return
        ing = doc.get("ingress") or []
        if not ing:
            err("cloudflared config has no ingress rules")
            return
        if "service" not in (ing[-1] or {}) or "http_status" not in str(ing[-1].get("service")):
            err("cloudflared ingress does not end with a catch-all "
                "(service: http_status:404) — cloudflared refuses to start")
        for rule in ing[:-1]:
            if not (rule or {}).get("hostname"):
                err("cloudflared has a non-final ingress rule with no hostname")
    if ":3002" in text and "http_status" not in text.split(":3002")[0][-80:]:
        err("cloudflared config routes Firecrawl (:3002) publicly — it must stay "
            "on the tailnet, never through the tunnel")


def check_make_docs(root):
    mk = os.path.join(root, "infra", "Makefile")
    rd = os.path.join(root, "infra", "README.md")
    if not (os.path.isfile(mk) and os.path.isfile(rd)):
        return
    targets = set(re.findall(r"^([a-zA-Z][\w-]*):", read(mk), re.MULTILINE))
    for t in sorted(set(re.findall(r"\bmake ([a-z][\w-]*)", read(rd)))):
        if t not in targets:
            err(f"infra/README.md tells the operator to run 'make {t}' but the "
                f"Makefile has no such target")


PROTOCOLS = ["PROTOCOL-01", "PROTOCOL-02", "PROTOCOL-03"]
SHARED_RULES = [
    ("Vercel", "the Vercel Hobby prohibition"),
    ("Ad Library", "the ad-library scraping prohibition"),
]


def check_docs(root):
    a = os.path.join(root, "AGENTS.md")
    h = os.path.join(root, "HERMES-PROMPT.md")
    r = os.path.join(root, "README.md")
    if not (os.path.isfile(a) and os.path.isfile(h)):
        err("AGENTS.md or HERMES-PROMPT.md missing — cannot check prompt parity")
        return
    at, ht = read(a), read(h)

    for p in PROTOCOLS:
        if p not in at:
            err(f"AGENTS.md does not define {p}")
        if p not in ht:
            err(f"HERMES-PROMPT.md is out of sync — {p} is in AGENTS.md but not the "
                f"portable prompt")
    for token, label in SHARED_RULES:
        if token in at and token not in ht:
            err(f"HERMES-PROMPT.md is missing {label} that AGENTS.md carries")

    for marker in ("## COPY FROM HERE", "## COPY TO HERE"):
        if marker not in ht:
            err(f"HERMES-PROMPT.md has no '{marker}' marker — the copy block is unusable")

    if os.path.isfile(r):
        rt = read(r)
        for d in sorted(x for x in os.listdir(root)
                        if os.path.isdir(os.path.join(root, x)) and not x.startswith(".")):
            if f"`{d}/`" not in rt:
                warn(f"README.md does not document the {d}/ directory")


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))
    print(f"Hermes-Ecom infra + docs validation — {root}\n")

    if check_files(root) is not False:
        check_env_coverage(root)
        check_compose(root)
        check_tunnel(root)
        check_make_docs(root)
    check_docs(root)

    for label, items in (("ERROR", errors), ("WARN", warnings), ("NOTE", notes)):
        for m in items:
            print(f"  [{label}] {m}")
    if not (errors or warnings or notes):
        print("  (nothing to report)")

    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s), {len(notes)} note(s)")
    print("RESULT: " + ("FAIL" if errors else "PASS"))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
