"""True Margin Matrix arithmetic and the Buying Constraint solver (PROTOCOL-01)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import margin_solver as ms  # noqa: E402


class CalcMargin(unittest.TestCase):
    def test_agents_md_worked_example_fails_the_3x_gate(self):
        # AGENTS.md worked example: retail 49.90, cost 8.20, ship 3.10, DE VAT.
        r = ms.calc_margin(49.90, 8.20, 3.10, duty=0.0, vat=0.19)
        self.assertAlmostEqual(r["cogs"], 11.30, places=2)
        self.assertAlmostEqual(r["ex_vat_rev"], 41.93, places=2)
        self.assertAlmostEqual(r["fee"], 1.50, places=2)
        self.assertAlmostEqual(r["net_margin"], 29.13, places=2)
        self.assertFalse(r["gate_3x"])          # needs >= 33.90
        self.assertTrue(r["gate_15"])
        self.assertEqual(r["verdict"], "FAIL")

    def test_passing_case_clears_every_gate(self):
        r = ms.calc_margin(59.90, 7.50, 2.50, duty=0.0, vat=0.19)
        self.assertAlmostEqual(r["net_margin"], 38.54, places=2)
        self.assertTrue(r["gate_3x"] and r["gate_15"] and r["gate_retail"])
        self.assertEqual(r["verdict"], "PASS")

    def test_duty_lands_in_cogs_and_can_flip_the_verdict(self):
        without = ms.calc_margin(59.90, 7.50, 2.50, duty=0.0, vat=0.19)
        with_duty = ms.calc_margin(59.90, 7.50, 2.50, duty=3.00, vat=0.19)
        self.assertAlmostEqual(with_duty["cogs"] - without["cogs"], 3.00, places=2)
        self.assertAlmostEqual(without["net_margin"] - with_duty["net_margin"], 3.00, places=2)

    def test_vat_and_fee_accept_percent_or_fraction(self):
        frac = ms.calc_margin(34.90, 6.00, 1.00, vat=0.19, fee_rate=0.03)
        pct = ms.calc_margin(34.90, 6.00, 1.00, vat=19, fee_rate=3)
        self.assertEqual(frac["net_margin"], pct["net_margin"])
        self.assertEqual(pct["vat"], 0.19)

    def test_zero_vat_raises_net_margin(self):
        # Non-EU sale: no VAT is remitted, so the whole retail price is revenue.
        de = ms.calc_margin(34.90, 6.00, 1.00, vat=0.19)
        no_vat = ms.calc_margin(34.90, 6.00, 1.00, vat=0.0)
        self.assertGreater(no_vat["net_margin"], de["net_margin"])
        self.assertAlmostEqual(no_vat["ex_vat_rev"], 34.90, places=2)

    def test_retail_floor_is_an_independent_gate(self):
        # A cheap item can clear 3x-COGS and the EUR 15 floor and still be
        # rejected: under EUR 20 there is no room for acquisition cost at all.
        r = ms.calc_margin(19.90, 0.10, 0.10, vat=0.0)
        self.assertTrue(r["gate_3x"])
        self.assertTrue(r["gate_15"])
        self.assertFalse(r["gate_retail"])
        self.assertEqual(r["verdict"], "FAIL")

    def test_negative_margin_is_reported_not_clamped(self):
        r = ms.calc_margin(24.90, 30.00, 5.00, vat=0.19)
        self.assertLess(r["net_margin"], 0)
        self.assertEqual(r["verdict"], "FAIL")


class MaxLandedCost(unittest.TestCase):
    def test_reference_value_for_the_34_90_tier(self):
        cogs, net = ms.max_landed_cost(34.90, vat=0.19)
        self.assertAlmostEqual(cogs, 7.07, places=2)
        self.assertAlmostEqual(net, 21.21, places=2)

    def test_the_binding_bound_is_3x_cogs_at_normal_tiers(self):
        # Net margin at the ceiling equals exactly 3x the ceiling cost.
        cogs, net = ms.max_landed_cost(44.90, vat=0.19)
        # Both sides are rounded to cents independently, so allow one cent of drift.
        self.assertAlmostEqual(net, 3 * cogs, delta=0.02)

    def test_retail_too_low_to_ever_clear_the_15_floor(self):
        # At EUR 15 gross there is no landed cost, not even zero, that yields
        # net > 15, so the solver reports the tier as impossible rather than
        # returning a misleading small ceiling.
        self.assertEqual(ms.max_landed_cost(15.00, vat=0.19), (0.0, 0.0))

    def test_ceiling_is_actually_binding(self):
        # Buying at the ceiling passes; buying 50 cents above it must not.
        for retail, _, _ in ms.generate_buying_table(vat=0.19):
            cogs, _ = ms.max_landed_cost(retail, vat=0.19)
            over = ms.calc_margin(retail, cogs + 0.50, 0.0, vat=0.19)
            self.assertEqual(over["verdict"], "FAIL",
                             f"EUR {retail}: paying 0.50 over the ceiling should fail")

    def test_ceiling_scales_with_vat(self):
        # Higher VAT leaves less ex-VAT revenue, so the buying ceiling falls.
        low, _ = ms.max_landed_cost(34.90, vat=0.07)
        high, _ = ms.max_landed_cost(34.90, vat=0.25)
        self.assertGreater(low, high)


class BuyingTable(unittest.TestCase):
    def test_six_tiers_with_monotonic_ceilings(self):
        rows = ms.generate_buying_table(vat=0.19)
        self.assertEqual(len(rows), 6)
        retails = [r for r, _, _ in rows]
        self.assertEqual(retails, sorted(retails))
        ceilings = [c for _, c, _ in rows]
        self.assertEqual(ceilings, sorted(ceilings))


class Markdown(unittest.TestCase):
    def test_output_carries_the_verdict_and_the_table(self):
        res = ms.calc_margin(59.90, 7.50, 2.50, vat=0.19)
        out = ms.format_markdown(res, ms.generate_buying_table(vat=0.19))
        self.assertIn("## True Margin Matrix", out)
        self.assertIn("Margin Matrix Verdict: **PASS**", out)
        self.assertIn("Maximum Landed Cost Reference", out)

    def test_markdown_reports_the_same_numbers_as_the_calculation(self):
        res = ms.calc_margin(34.90, 6.00, 1.00, vat=0.19)
        out = ms.format_markdown(res)
        self.assertIn(f"Net Margin: {res['net_margin']:.2f}", out)


class BundledSelftest(unittest.TestCase):
    def test_module_selftest_still_passes(self):
        self.assertEqual(ms.selftest(), 0)


if __name__ == "__main__":
    unittest.main()
