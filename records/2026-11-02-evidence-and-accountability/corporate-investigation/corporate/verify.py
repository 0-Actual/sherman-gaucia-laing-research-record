#!/usr/bin/env python3
"""Rerun the calculator and verify its fixture plus independent rational checks.

Run: python verify.py
The fixed fractions and totals were computed independently of calculate.py.
This verifies arithmetic and policy invariants, not source truth, empirical
accuracy, causal influence, or the completeness of public disclosures.
"""

from decimal import Decimal, ROUND_HALF_UP, localcontext
from fractions import Fraction
import json
from pathlib import Path
import subprocess
import sys


BASE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def at(data, dotted):
    for key in dotted.split("."):
        data = data[key]
    return data


def main():
    command = [sys.executable, str(BASE / "calculate.py"), "--inputs", str(BASE / "inputs.json")]
    run = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
    repeated = subprocess.run(command, check=True, capture_output=True, text=True, encoding="utf-8")
    require(run.stdout == repeated.stdout, "Repeated runs differ")
    expected_text = (BASE / "expected_outputs.json").read_text(encoding="utf-8")
    require(run.stdout == expected_text, "Calculator output differs from expected_outputs.json")
    actual = json.loads(run.stdout)
    require(actual == json.loads(expected_text), "Parsed expected-output comparison failed")

    # Independently reduced fractions, not copied calculator decimal strings.
    rational_constants = {
        "alphabet.Page_class_B_vote_fraction": (1296837200, 4727151841),
        "alphabet.Brin_specified_vote_fraction": (1196479083, 4727151841),
        "alphabet.combined_specified_founder_vote_fraction": (2493316283, 4727151841),
        "microsoft_financial.funded_fraction_of_reported_commitment": (12, 13),
        "microsoft_financial.commercial_to_total_revenue_comparison": (10000, 92279),
        "mobvoi.sold_fraction_of_pre_sale_holding": (13328750, 35831711),
        "mobvoi.sold_fraction_of_stated_issued_shares": (53315000, 1537700537),
        "mobvoi.retained_fraction_of_stated_issued_shares": (90011844, 1537700537),
        "mobvoi.box_19_fraction_of_stated_issued_shares": (90011944, 1537700537),
        "mobvoi.pre_sale_fraction_of_stated_issued_shares": (143326844, 1537700537),
        "vnet.supplied_fraction": (27101008, 71207115),
        "lobbying.entities.Microsoft.within_entity_comparisons.2025_vs_base_year_change_fraction": (-7, 4687),
        "lobbying.entities.Google.within_entity_comparisons.2025_vs_base_year_change_fraction": (557, 753),
        "lobbying.entities.OpenAI.within_entity_comparisons.2025_vs_base_year_change_fraction": (123, 176),
        "lobbying.entities.Microsoft.within_entity_comparisons.2026_Jan_Sep_vs_2025_Jan_Sep_change_fraction": (29, 347),
        "lobbying.entities.Google.within_entity_comparisons.2026_Jan_Sep_vs_2025_Jan_Sep_change_fraction": (-3, 325),
        "lobbying.entities.OpenAI.within_entity_comparisons.2026_Jan_Sep_vs_2025_Jan_Sep_change_fraction": (11, 14),
        "google_corporate_disclosures.2025_to_2020_amount_ratio": (364083, 21512),
        "google_corporate_disclosures.2025_vs_2020_amount_growth": (342571, 21512),
        "google_corporate_disclosures.selected_rows_fraction_of_2025_total": (80000, 121361),
        "fec.committees.Microsoft.line_23_fraction_of_total_disbursements": (65325000, 73842443),
        "fec.committees.Google.line_23_fraction_of_total_disbursements": (166538432, 180583407),
        "bilderberg.pairs.Altman__Nadella.jaccard": (1, 3),
        "bilderberg.pairs.Altman__Smith.jaccard": (0, 1),
        "bilderberg.pairs.Nadella__Smith.jaccard": (0, 1),
    }
    checks = 0
    for path, (numerator, denominator) in rational_constants.items():
        record = at(actual, path)
        require((record["numerator"], record["denominator"]) == (numerator, denominator), f"Wrong reduced fraction: {path}")
        require(Fraction(numerator, denominator).numerator == numerator, f"Expected fraction not reduced: {path}")
        with localcontext() as context:
            context.prec = 80
            value = Decimal(numerator) * 100 / Decimal(denominator)
            for places in (1, 6):
                independently_rounded = str(value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP))
                require(record[f"percentage_{places}dp"] == independently_rounded, f"Rounding mismatch: {path}")
                checks += 1
        checks += 2

    exact_constants = {
        "alphabet.total_class_A_B_votes": 14181455523,
        "alphabet.Page_class_B_votes": 3890511600,
        "alphabet.Brin_specified_votes": 3589437249,
        "alphabet.combined_specified_founder_votes": 7479948849,
        "microsoft_financial.reported_commitment_less_funded_billions": "1.0",
        "mobvoi.calculated_retained_shares": 90011844,
        "mobvoi.box_19_minus_calculated_retained_shares": 100,
        "mobvoi.box_20_minus_calculated_retained_shares": 0,
        "lobbying.entities.Microsoft.periods.2020.sum_reported_estimates_usd": 9374000,
        "lobbying.entities.Microsoft.periods.2025.sum_reported_estimates_usd": 9360000,
        "lobbying.entities.Microsoft.periods.2026_Jan_Sep.sum_reported_estimates_usd": 7520000,
        "lobbying.entities.Google.periods.2020.sum_reported_estimates_usd": 7530000,
        "lobbying.entities.Google.periods.2025.sum_reported_estimates_usd": 13100000,
        "lobbying.entities.Google.periods.2026_Jan_Sep.sum_reported_estimates_usd": 9660000,
        "lobbying.entities.OpenAI.periods.2024.sum_reported_estimates_usd": 1760000,
        "lobbying.entities.OpenAI.periods.2025.sum_reported_estimates_usd": 2990000,
        "lobbying.entities.OpenAI.periods.2026_Jan_Sep.sum_reported_estimates_usd": 3750000,
        "lobbying.entities.Microsoft.within_entity_comparisons.2025_Jan_Sep_sum_reported_estimates_usd": 6940000,
        "lobbying.entities.Google.within_entity_comparisons.2025_Jan_Sep_sum_reported_estimates_usd": 9750000,
        "lobbying.entities.OpenAI.within_entity_comparisons.2025_Jan_Sep_sum_reported_estimates_usd": 2100000,
        "google_corporate_disclosures.sums_reported_usd.2020": 537800,
        "google_corporate_disclosures.sums_reported_usd.2025": 9102075,
        "google_corporate_disclosures.row_counts.2020": 74,
        "google_corporate_disclosures.row_counts.2025": 264,
        "google_corporate_disclosures.2025_less_2020_reported_usd": 8564275,
        "google_corporate_disclosures.2025_less_2020_rows": 190,
        "google_corporate_disclosures.selected_rows_combined_reported_usd": 6000000,
        "google_corporate_disclosures.other_rows_reported_usd": 3102075,
        "fec.committees.Microsoft.total_less_line_23_usd": "170348.86",
        "fec.committees.Google.total_less_line_23_usd": "140449.75",
        "bilderberg.listed_year_counts.Altman": 2,
        "bilderberg.listed_year_counts.Nadella": 2,
        "bilderberg.listed_year_counts.Smith": 1,
        "bilderberg.person_year_entries": 5,
        "bilderberg.all_three_co_list_count": 0,
        "bilderberg.pairs.Altman__Nadella.co_list_count": 1,
        "bilderberg.pairs.Altman__Nadella.union_count": 3,
        "bilderberg.pairs.Altman__Smith.co_list_count": 0,
        "bilderberg.pairs.Altman__Smith.union_count": 3,
        "bilderberg.pairs.Nadella__Smith.co_list_count": 0,
        "bilderberg.pairs.Nadella__Smith.union_count": 3,
    }
    for path, value in exact_constants.items():
        require(at(actual, path) == value, f"Wrong independent constant: {path}")
        checks += 1
    # Undefined inferential metrics must not silently become numeric zeros.
    for name in ("intent_probability", "precision", "recall", "empirical_accuracy"):
        require(actual["unsupported_inferential_metrics"][name] is None, f"Unsupported {name} must be null")
        checks += 1
    require(actual["lobbying"]["cross_company_spending_ranking"] is None, "Cross-method spending ranking must remain null")
    require(actual["lobbying"]["entities"]["Microsoft"]["method"] == "C", "Microsoft method changed")
    require(actual["lobbying"]["entities"]["Google"]["method"] == "A", "Google method changed")
    require(actual["lobbying"]["entities"]["OpenAI"]["method"] == "A", "OpenAI source-verified method changed")
    checks += 4
    print("PASS: calculator was rerun and matched expected_outputs.json byte for byte")
    print("PASS: repeated calculator runs were identical")
    print(f"PASS: {checks} independent rational, decimal, count, and policy checks")
    print("Scope: arithmetic verification only; source truth and causal influence are not measured")


if __name__ == "__main__":
    main()
