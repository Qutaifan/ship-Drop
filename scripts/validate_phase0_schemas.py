#!/usr/bin/env python3
"""Validate Phase 0 schemas and fixture files.

This script intentionally validates only local files. It performs JSON Schema
validation plus the deterministic semantic checks needed for Phase 0 governance.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

CHECKS = [
    (ROOT / "schemas" / "market-config.schema.json", ROOT / "config" / "markets" / "us-pilot.json"),
    (ROOT / "schemas" / "evidence.schema.json", ROOT / "fixtures" / "evidence.sample.json"),
    (ROOT / "schemas" / "candidate.schema.json", ROOT / "fixtures" / "candidate.sample.json"),
    (ROOT / "schemas" / "supplier.schema.json", ROOT / "fixtures" / "supplier.sample.json"),
    (ROOT / "schemas" / "trade_signal.schema.json", ROOT / "fixtures" / "trade_signal.sample.json"),
    (ROOT / "schemas" / "approval.schema.json", ROOT / "fixtures" / "approval.sample.json"),
    (ROOT / "schemas" / "supplier_verification.schema.json", ROOT / "fixtures" / "supplier_verification.sample.json"),
    (ROOT / "schemas" / "sourcing_ranker.schema.json", ROOT / "fixtures" / "sourcing_ranker.sample.json"),
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_schema(schema_path: Path, data_path: Path) -> list[str]:
    schema = load_json(schema_path)
    data = load_json(data_path)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda err: list(err.path))
    return [f"{data_path.relative_to(ROOT)}: {'/'.join(map(str, err.path)) or '<root>'}: {err.message}" for err in errors]


def validate_market_semantics(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    days = data["target_delivery_days"]
    if days["max"] < days["min"]:
        errors.append("config/markets/us-pilot.json: target_delivery_days.max must be >= min")
    limits = data["live_risk_limits"]
    if any(limits.values()):
        errors.append("config/markets/us-pilot.json: Phase 0 live_risk_limits must all be false")
    if data["market_type"] == "US" and data["currency"] != "USD":
        errors.append("config/markets/us-pilot.json: US market must use USD")
    return errors


def validate_candidate_semantics(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    econ = data["unit_economics"]
    net_revenue = econ["gross_selling_price"] - econ["sales_tax_liability"] - econ["discounts"] - econ["refund_allowance"]
    contribution = (
        net_revenue
        - econ["product_cost"]
        - econ["shipping_cost"]
        - econ["duty"]
        - econ["payment_fees"]
        - econ["packaging_cost"]
        - econ["variable_support_cost"]
        - econ["return_allowance"]
    )
    target_cpa = contribution * econ["safety_factor"]
    expected_profit = contribution - target_cpa
    checks = {
        "net_revenue": net_revenue,
        "contribution_before_ads": contribution,
        "break_even_cpa": contribution,
        "target_cpa": target_cpa,
        "expected_profit_per_order": expected_profit,
    }
    for field, expected in checks.items():
        if abs(econ[field] - expected) > 0.02:
            errors.append(
                f"fixtures/candidate.sample.json: unit_economics.{field} "
                f"expected {expected:.2f}, got {econ[field]:.2f}"
            )
    if data["recommendation"] == "founder_review" and data["status"] != "FOUNDER_REVIEW":
        errors.append("fixtures/candidate.sample.json: founder_review recommendation must use FOUNDER_REVIEW status")
    return errors


def main() -> int:
    errors: list[str] = []
    for schema_path, data_path in CHECKS:
        errors.extend(validate_schema(schema_path, data_path))

    errors.extend(validate_market_semantics(load_json(ROOT / "config" / "markets" / "us-pilot.json")))
    errors.extend(validate_candidate_semantics(load_json(ROOT / "fixtures" / "candidate.sample.json")))

    if errors:
        print("Phase 0 schema validation FAILED")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Phase 0 schema validation PASSED")
    for _, data_path in CHECKS:
        print(f"- validated {data_path.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
