"""Tests for Dropship Agency System.

Redirects the agency's data and config directories into a scratch directory for
the duration of the run. Without this, importing and exercising the agency writes
into the working tree — `data/audit/audit_log.jsonl`, `data/medusa_catalog/`, and
`config/autonomous_windows.json` all picked up test writes, leaving three tracked
files modified after a clean run. The audit log is a governance record; tests must
not append to it.

`config/` is not redirected wholesale — it also holds committed configuration the
code reads (`markets/`, `feature_flags.json`). Only the mutable windows file is
pointed elsewhere.

This must run before any `agency.*` import, because the paths are bound once at
module import. Being in the package `__init__` guarantees that under
`unittest discover`.

Tests that deliberately assert against the real repository data (for example the
live-record guards in `test_candidate_economics.py`) read it through explicit
paths rather than these settings, so they are unaffected.
"""
from __future__ import annotations

import atexit
import os
import shutil
import tempfile

_SCRATCH = tempfile.mkdtemp(prefix="dropship-tests-")

os.environ.setdefault("DROPSHIP_DATA_DIR", os.path.join(_SCRATCH, "data"))
os.environ.setdefault("DROPSHIP_WINDOWS_FILE",
                      os.path.join(_SCRATCH, "config", "autonomous_windows.json"))

os.makedirs(os.environ["DROPSHIP_DATA_DIR"], exist_ok=True)
os.makedirs(os.path.dirname(os.environ["DROPSHIP_WINDOWS_FILE"]), exist_ok=True)

atexit.register(shutil.rmtree, _SCRATCH, True)
