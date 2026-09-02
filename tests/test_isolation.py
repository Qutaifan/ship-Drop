"""Guard: the suite must run against a scratch data directory, not the repo.

`tests/__init__.py` redirects the agency's data directory and mutable windows file
into a temp directory. That only happens when the suite is run so that `tests` is
imported as a package:

    python3 -m unittest discover -s tests -t .        # correct
    python3 -m unittest discover -s tests             # package __init__ skipped

Under the second form unittest imports the modules as top-level names, the package
`__init__` never executes, and the run writes into `data/` and `config/` — which is
how three tracked files ended up modified by a clean test run.

These tests make that failure loud. A red test here means the invocation is wrong,
not the code.
"""
from __future__ import annotations

import os
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


class Isolation(unittest.TestCase):
    def test_data_dir_is_redirected(self):
        value = os.environ.get("DROPSHIP_DATA_DIR")
        self.assertTrue(
            value,
            "DROPSHIP_DATA_DIR is unset — run the suite with "
            "`python3 -m unittest discover -s tests -t .` so tests/__init__.py loads",
        )

    def test_data_dir_is_outside_the_repository(self):
        value = os.environ.get("DROPSHIP_DATA_DIR")
        self.assertTrue(value, "DROPSHIP_DATA_DIR is unset")
        self.assertFalse(
            Path(value).resolve().is_relative_to(REPO),
            f"tests would write inside the repository ({value})",
        )

    def test_windows_file_is_outside_the_repository(self):
        value = os.environ.get("DROPSHIP_WINDOWS_FILE")
        self.assertTrue(value, "DROPSHIP_WINDOWS_FILE is unset")
        self.assertFalse(
            Path(value).resolve().is_relative_to(REPO),
            f"tests would write config/autonomous_windows.json in place ({value})",
        )

    def test_store_resolves_to_the_scratch_directory(self):
        from agency.config.settings import DATA_DIR

        self.assertFalse(
            DATA_DIR.resolve().is_relative_to(REPO),
            f"agency settings still point at the repository ({DATA_DIR})",
        )


if __name__ == "__main__":
    unittest.main()
