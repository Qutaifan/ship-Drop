"""Tests for the candidate unit-economics reconciler.

A validator that reports "clean" is only worth trusting if it is known to fail on
bad input — the principle `scripts/selftest.py` already applies to the workspace
validators. These tests establish that for the economics reconciler, and guard the
live records against new arithmetic drift.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location(
    "validate_candidate_economics", ROOT / "scripts" / "validate_candidate_economics.py"
)
vce = importlib.util.module_from_spec(_spec)
sys.modules["validate_candidate_economics"] = vce
_spec.loader.exec_module(vce)


def econ(**overrides):
    """A record whose stated figures reconcile exactly with its components."""
    base = {
        "gross_selling_price": 29.99,
        "sales_tax_liability": 0.0,
        "discounts": 0.0,
        "refund_allowance": 1.0,
        "product_cost": 6.0,
        "shipping_cost": 2.5,
        "duty": 0.0,
        "payment_fees": 1.17,
        "packaging_cost": 1.0,
        "variable_support_cost": 0.8,
        "return_allowance": 1.2,
        "safety_factor": 0.7,
    }
    base.update(overrides)
    derived = vce.recompute(base)
    base.update(derived)
    return base


def write_record(directory, candidate_id, economics):
    path = Path(directory) / f"{candidate_id}.json"
    path.write_text(
        json.dumps({"candidate_id": candidate_id, "unit_economics": economics}),
        encoding="utf-8",
    )
    return path


class Recompute(unittest.TestCase):
    def test_refund_allowance_reduces_net_revenue(self):
        r = vce.recompute(econ(gross_selling_price=100.0, refund_allowance=5.0,
                               sales_tax_liability=0.0, discounts=0.0))
        self.assertAlmostEqual(r["net_revenue"], 95.0, places=2)

    def test_every_cost_line_reduces_contribution(self):
        clean = vce.recompute(econ())
        for line in ("product_cost", "shipping_cost", "duty", "payment_fees",
                     "packaging_cost", "variable_support_cost", "return_allowance"):
            bumped = vce.recompute(econ(**{line: econ()[line] + 1.0}))
            self.assertAlmostEqual(
                clean["contribution_before_ads"] - bumped["contribution_before_ads"],
                1.0, places=2, msg=f"{line} must reduce contribution one-for-one")

    def test_break_even_cpa_equals_contribution(self):
        r = vce.recompute(econ())
        self.assertAlmostEqual(r["break_even_cpa"], r["contribution_before_ads"], places=2)

    def test_target_cpa_applies_the_safety_factor(self):
        r = vce.recompute(econ(safety_factor=0.7))
        self.assertAlmostEqual(r["target_cpa"], r["contribution_before_ads"] * 0.7, places=2)

    def test_expected_profit_is_net_of_target_cpa(self):
        # The defect found in the two staged US candidates: expected profit stated
        # as the whole contribution, with target_cpa never subtracted.
        r = vce.recompute(econ())
        self.assertAlmostEqual(
            r["expected_profit_per_order"],
            r["contribution_before_ads"] - r["target_cpa"], places=2)
        self.assertLess(r["expected_profit_per_order"], r["contribution_before_ads"])


class CheckRecord(unittest.TestCase):
    def test_a_reconciling_record_reports_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            p = write_record(d, "clean-one", econ())
            self.assertEqual(vce.check_record(p), [])

    def test_overstated_contribution_is_caught_and_labelled(self):
        with tempfile.TemporaryDirectory() as d:
            e = econ()
            e["contribution_before_ads"] += 1.00
            p = write_record(d, "overstated", e)
            problems = vce.check_record(p)
            self.assertTrue(problems)
            self.assertTrue(any("contribution_before_ads" in x and "overstated" in x
                                for x in problems), problems)

    def test_understated_figure_is_labelled_the_other_way(self):
        with tempfile.TemporaryDirectory() as d:
            e = econ()
            e["net_revenue"] -= 2.00
            p = write_record(d, "understated", e)
            self.assertTrue(any("understated" in x for x in vce.check_record(p)))

    def test_placeholder_retail_price_is_caught(self):
        # The exact shape of the live defect: gross_selling_price left at a
        # placeholder while the derived figures were computed from it.
        with tempfile.TemporaryDirectory() as d:
            e = econ(gross_selling_price=29.99)
            e["net_revenue"] = 69.99          # never reduced by refund_allowance
            p = write_record(d, "placeholder", e)
            self.assertTrue(any("net_revenue" in x for x in vce.check_record(p)))

    def test_drift_inside_tolerance_is_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            e = econ()
            e["contribution_before_ads"] += 0.01     # under the 0.02 rounding tolerance
            p = write_record(d, "rounding", e)
            self.assertEqual(vce.check_record(p), [])

    def test_missing_unit_economics_is_reported_not_raised(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "empty.json"
            p.write_text(json.dumps({"candidate_id": "empty"}), encoding="utf-8")
            self.assertEqual(vce.check_record(p), ["no unit_economics block"])

    def test_missing_cost_line_is_reported_not_raised(self):
        with tempfile.TemporaryDirectory() as d:
            e = econ()
            del e["packaging_cost"]
            p = write_record(d, "incomplete", e)
            problems = vce.check_record(p)
            self.assertTrue(any("missing field" in x for x in problems), problems)


class LiveRecords(unittest.TestCase):
    """Guards on the real data/candidates/ store."""

    def setUp(self):
        self.records = sorted((ROOT / "data" / "candidates").glob("*.json"))

    def test_there_are_records_to_check(self):
        self.assertTrue(self.records, "data/candidates/ is empty")

    def test_no_new_reconciliation_failures(self):
        # Anything failing must be listed in KNOWN_DEBT with a stated cause.
        undeclared = []
        for path in self.records:
            data = json.loads(path.read_text(encoding="utf-8"))
            cid = data.get("candidate_id", path.stem)
            if vce.check_record(path) and cid not in vce.KNOWN_DEBT:
                undeclared.append(cid)
        self.assertEqual(undeclared, [], f"unreconciled and undeclared: {undeclared}")

    def test_known_debt_entries_all_still_exist_and_still_fail(self):
        # Keeps the quarantine list shrinking rather than rotting: an entry for a
        # record that no longer exists, or that now reconciles, is stale.
        present = {}
        for path in self.records:
            data = json.loads(path.read_text(encoding="utf-8"))
            present[data.get("candidate_id", path.stem)] = path
        for cid in vce.KNOWN_DEBT:
            self.assertIn(cid, present, f"KNOWN_DEBT names {cid}, which no longer exists")
            self.assertTrue(vce.check_record(present[cid]),
                            f"KNOWN_DEBT names {cid}, but it reconciles now — remove it")

    def test_every_debt_entry_states_a_cause(self):
        for cid, reason in vce.KNOWN_DEBT.items():
            self.assertTrue(reason.strip(), f"{cid} is quarantined with no stated cause")

    def test_validator_exits_clean_on_the_current_tree(self):
        self.assertEqual(vce.main(), 0)


if __name__ == "__main__":
    unittest.main()
