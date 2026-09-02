"""Neither ingestion path may invent a retail price.

Both Phase 2 staging candidates reached founder review carrying a gross_selling_price
that no research produced: `scout_bot` defaulted to 29.99/69.90 when a dossier had no
parseable price, and `dsa_ad_ingestion` defaulted to 69.99 when an ad creative had
none. A fabricated retail reconciles perfectly against its own derived costs, so
nothing downstream could catch it — see reports/2026-09-02-founder-decision-matrix.md
sec. 3.1. These tests hold both paths to refusing instead of guessing.
"""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from agency.bots.scout_bot import ScoutBot
from agency.core.store import Store
from agency.ingestion.dsa_ad_ingestion import DSAAdIngestionPipeline

DOSSIER_WITH_PRICE = """# Product Validation — Test Widget

- Name: Test Widget
| Retail price | USD 34.99 |
| Product cost | USD 8.00 |
| Shipping cost | USD 3.00 |
"""

DOSSIER_WITHOUT_PRICE = """# Product Validation — Priceless Widget

- Name: Priceless Widget
| Product cost | USD 8.00 |
| Shipping cost | USD 3.00 |
"""


class ScoutBotRefusesToInventRetail(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.bot = ScoutBot(Store(db_path=self.tmp / "t.db", data_dir=self.tmp))

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _dossier(self, name: str, body: str) -> Path:
        path = self.tmp / name
        path.write_text(body, encoding="utf-8")
        return path

    def test_dossier_with_a_price_is_ingested_at_that_price(self):
        cand = self.bot.discover_from_markdown(
            self._dossier("us-test-widget.md", DOSSIER_WITH_PRICE)
        )
        self.assertIsNotNone(cand)
        self.assertEqual(cand["unit_economics"]["gross_selling_price"], 34.99)

    def test_dossier_without_a_price_is_skipped_not_defaulted(self):
        cand = self.bot.discover_from_markdown(
            self._dossier("us-priceless-widget.md", DOSSIER_WITHOUT_PRICE)
        )
        self.assertIsNone(cand)

    def test_the_skip_is_recorded_with_a_reason(self):
        self.bot.discover_from_markdown(
            self._dossier("us-priceless-widget.md", DOSSIER_WITHOUT_PRICE)
        )
        self.assertEqual(len(self.bot.skipped), 1)
        name, reason = self.bot.skipped[0]
        self.assertEqual(name, "us-priceless-widget.md")
        self.assertIn("refusing to invent", reason)

    def test_no_record_ever_carries_the_old_default_prices(self):
        cand = self.bot.discover_from_markdown(
            self._dossier("eu-priceless-widget.md", DOSSIER_WITHOUT_PRICE)
        )
        self.assertIsNone(cand, "a priceless dossier must not yield 69.90")


def _ad(ad_id: str, text: str) -> dict:
    return {
        "id": ad_id,
        "page_name": f"Advertiser {ad_id}",
        "ad_creative_bodies": [text],
        "ad_delivery_start_time": "2026-01-01",
        "eu_total_reach": 10000,
    }


class DSAIngestionDropsUnpricedAds(unittest.TestCase):
    def test_an_ad_with_no_price_produces_no_price_evidence(self):
        res = DSAAdIngestionPipeline.normalize_dsa_ads(
            raw_ads=[_ad("a", "Buy now for €49.90"), _ad("b", "Best organizer ever")],
            candidate_id="cand-test",
            query="organizer",
        )
        self.assertEqual(len(res["competitor_evidence"]), 1)
        self.assertEqual(res["competitor_evidence"][0]["observed_price"], 49.90)
        self.assertEqual(res["ads_without_parseable_price"], 1)

    def test_no_priced_ad_yields_no_median_rather_than_a_placeholder(self):
        res = DSAAdIngestionPipeline.normalize_dsa_ads(
            raw_ads=[_ad("a", "Great product"), _ad("b", "Buy today")],
            candidate_id="cand-test",
            query="organizer",
        )
        self.assertIsNone(res["median_competitor_price"])
        self.assertEqual(res["ads_without_parseable_price"], 2)
        self.assertEqual(res["competitor_evidence"], [])

    def test_priced_ads_still_produce_a_median(self):
        res = DSAAdIngestionPipeline.normalize_dsa_ads(
            raw_ads=[_ad("a", "Only €40.00"), _ad("b", "Just €60.00")],
            candidate_id="cand-test",
            query="organizer",
        )
        self.assertIsNotNone(res["median_competitor_price"])
        self.assertEqual(res["ads_without_parseable_price"], 0)


if __name__ == "__main__":
    unittest.main()
