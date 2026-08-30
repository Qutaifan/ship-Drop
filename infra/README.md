# Infrastructure — Hermes-Ecom

Self-hosted, free/OSS stack per `AGENTS.md` §7. Marginal infra cost: **€0**.

## Where this runs

| Component | Host | Why |
|---|---|---|
| Medusa + Postgres + Valkey + Umami + Uptime Kuma | `ahmad-thinkbook` (Ubuntu) | Already on 24/7 for Hindsight |
| Firecrawl | `hq-2` (Windows dev box) | Multi-container + headless browsers; do not stack it beside the storefront |
| Public ingress | Cloudflare Tunnel | Free, commercial use permitted, TLS included |

These files live in the Dropshiping folder on `hq`. Copy `infra/` to the target host to deploy — this folder is the source of record, not the running deployment.

## Bootstrap order

1. **Create the Medusa app** (this scaffold builds from it, it is not vendored here):
   ```
   npx create-medusa-app@latest medusa
   ```
   Place it beside `infra/` so `build: ../medusa` resolves.

2. **Configure secrets**:
   ```
   cp .env.example .env
   openssl rand -base64 32   # once for JWT_SECRET, once for COOKIE_SECRET
   ```
   Set real hostnames in the CORS vars. `.env` is never committed.

3. **Start**: `make up` → `make migrate` → `make admin EMAIL=... PASSWORD=...`

4. **Backups & Media Storage (Cloudflare R2)**:
   - Configure R2 S3-compatible credentials in environment (`R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`).
   - Run automated database dumps and offsite sync with `make backup` (`infra/backup_r2.sh`).
   - Programmatically upload staged product media with `scripts/r2_storage.py --upload <image.webp> --remote products/<slug>/hero.webp`.
   - Compatible with `awslabs/s3` MCP server when pointing `AWS_ENDPOINT_URL` to Cloudflare R2.

5. **Publish**: create a tunnel from `cloudflared/config.example.yml`. Use a **separate** tunnel from the existing Ollama one so the two cannot take each other down.

6. **Verify**: `make validate` must exit 0 before any commit. `make selftest` proves the validators still fail correctly on broken input — run it after changing any validator.

## Firecrawl (separate host)

Clone upstream and use its own compose — do not hand-roll one:

```
git clone https://github.com/firecrawl/firecrawl
cd firecrawl && cp apps/api/.env.example .env
docker compose up -d
```

Then point the MCP server at it, with no cloud key:

```
env FIRECRAWL_API_URL=http://<hq-2>:3002 npx -y firecrawl-mcp
```

Keep it on the tailnet. It is not published through the tunnel.

**Do not aim it at Meta Ad Library or TikTok Creative Center** — that breaches their terms and risks the same account that runs the ad spend. Official Meta Ad Library API for the PROTOCOL-01 gates.

## Open items

- Domain not purchased (~€10/yr — the only fixed cost).
- Payment provider not chosen; ~2.9% + fixed either way, already modelled as the 3% fee in the True Margin Matrix.
- Supplier tooling unverified (`AGENTS.md` §7C).
