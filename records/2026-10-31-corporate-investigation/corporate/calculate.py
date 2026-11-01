#!/usr/bin/env python3
"""Deterministic arithmetic over disclosed inputs; no causal inference or simulation.

Usage: python calculate.py [--inputs INPUTS.json] [--output OUTPUT.json]
All dependencies are Python standard library modules. Money is never parsed as
binary float. Exact arithmetic on rounded disclosures does not make the
underlying monetary amounts exact.
"""

import argparse
from decimal import Decimal, ROUND_HALF_UP, localcontext
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path


BASE = Path(__file__).resolve().parent


def ratio(numerator, denominator):
    """Return an exact supplied-input fraction and reproducible display strings."""
    n, d = Fraction(numerator), Fraction(denominator)
    if d <= 0:
        raise ValueError("A ratio denominator must be positive")
    f = n / d
    with localcontext() as ctx:
        ctx.prec = 70
        percent = Decimal(f.numerator) * 100 / Decimal(f.denominator)
        result = {
            "numerator": f.numerator,
            "denominator": f.denominator,
            "percentage_6dp": str(percent.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)),
            "percentage_1dp": str(percent.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)),
        }
    return result


def amount(value):
    """Read decimal money text without a float conversion."""
    if not isinstance(value, str):
        raise TypeError("Monetary decimal inputs must be strings")
    return Decimal(value)


def money_text(value):
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def validate(data):
    a = data["alphabet"]
    for key, value in a.items():
        if key != "record_date" and (type(value) is not int or value < 0):
            raise ValueError("Alphabet counts and vote multipliers must be nonnegative integers")
    if a["votes_per_A"] <= 0 or a["votes_per_B"] <= 0:
        raise ValueError("Vote multipliers must be positive")
    for section in ("mobvoi", "vnet"):
        if any(type(v) is not int or v < 0 for v in data[section].values()):
            raise ValueError("Share inputs must be nonnegative integers")
    if data["mobvoi"]["sale_shares"] > data["mobvoi"]["pre_sale_shares"]:
        raise ValueError("Sale exceeds pre-sale holding")
    for entity in data["lobbying"].values():
        for period, quarters in entity["quarters_reported_estimate_usd"].items():
            expected_length = 3 if period == "2026_Jan_Sep" else 4
            if len(quarters) != expected_length:
                raise ValueError("Incorrect quarter count")
            if any(type(v) is not int or v < 0 for v in quarters):
                raise ValueError("Reported lobbying estimates must be nonnegative integers")
    b = data["bilderberg"]
    if len(set(b["years"])) != len(b["years"]):
        raise ValueError("Duplicate matrix years")
    for row in b["list_presence"].values():
        if len(row) != len(b["years"]) or any(type(v) is not int or v not in (0, 1) for v in row):
            raise ValueError("Participant-list matrix must be a binary matrix with one column per year")


def calculate(data):
    validate(data)
    a = data["alphabet"]
    votes = a["class_A_shares"] * a["votes_per_A"] + a["class_B_shares"] * a["votes_per_B"]
    page = a["Page_class_B"] * a["votes_per_B"]
    brin = a["Brin_class_B"] * a["votes_per_B"] + a["Brin_class_A"] * a["votes_per_A"]
    out = {
        "schema_version": 1,
        "cutoff_date": data["cutoff_date"],
        "arithmetic_policy": {
            "integer_counts": "Exact arithmetic on supplied reported integers.",
            "money": "Exact arithmetic on reported numbers, retaining source rounding and estimate status; not exact underlying dollars.",
            "rounding": "ROUND_HALF_UP; six decimal places for audit percentages and one for concise display.",
            "source_validation": "Provenance and source-date checks are separate from arithmetic verification.",
        },
        "alphabet": {
            "record_date": a["record_date"],
            "total_class_A_B_votes": votes,
            "Page_class_B_votes": page,
            "Brin_specified_votes": brin,
            "combined_specified_founder_votes": page + brin,
            "Page_class_B_vote_fraction": ratio(page, votes),
            "Brin_specified_vote_fraction": ratio(brin, votes),
            "combined_specified_founder_vote_fraction": ratio(page + brin, votes),
            "scope": "Voting fractions of the specified holdings and Class A/B voting denominator; not an economic-ownership percentage.",
        },
    }
    f = data["microsoft_financial"]
    committed = amount(f["funding_commitment_billions"])
    funded = amount(f["funding_funded_billions"])
    commercial = amount(f["commercial_revenue_billions"]) * 1000
    total_revenue = amount(f["total_quarter_revenue_millions"])
    out["microsoft_financial"] = {
        "reported_commitment_less_funded_billions": str(committed - funded),
        "funded_fraction_of_reported_commitment": ratio(funded, committed),
        "commercial_to_total_revenue_comparison": ratio(commercial, total_revenue),
        "precision_note": f["precision_note"],
        "interpretation": "The revenue ratio compares reported revenue recognized from commercial arrangements with OpenAI with reported total Microsoft quarter revenue. It is not a counterfactual causal incrementality estimate, profit share, governance or control measure, or policy-bias measure. The funding difference is not a determination of legally payable debt.",
    }
    m = data["mobvoi"]
    retained = m["pre_sale_shares"] - m["sale_shares"]
    out["mobvoi"] = {
        "calculated_retained_shares": retained,
        "box_19_minus_calculated_retained_shares": m["reported_box_19"] - retained,
        "box_20_minus_calculated_retained_shares": m["reported_box_20"] - retained,
        "sold_fraction_of_pre_sale_holding": ratio(m["sale_shares"], m["pre_sale_shares"]),
        "sold_fraction_of_stated_issued_shares": ratio(m["sale_shares"], m["issued_shares"]),
        "retained_fraction_of_stated_issued_shares": ratio(retained, m["issued_shares"]),
        "box_19_fraction_of_stated_issued_shares": ratio(m["reported_box_19"], m["issued_shares"]),
        "pre_sale_fraction_of_stated_issued_shares": ratio(m["pre_sale_shares"], m["issued_shares"]),
        "interpretation": "Arithmetic agrees with Box 20 and differs from Box 19 by 100 shares. It does not determine authoritative legal disclosure or establish that the issued-share denominator applied at the pre-sale date.",
    }
    out["vnet"] = {
        "supplied_fraction": ratio(data["vnet"]["numerator"], data["vnet"]["denominator"]),
        "interpretation": "The source index defines the share classes, date, and rights represented by this numerator and denominator; the fraction alone does not establish voting power.",
    }
    lobbying = {}
    for name, entity in sorted(data["lobbying"].items()):
        periods = {}
        for period, quarters in sorted(entity["quarters_reported_estimate_usd"].items()):
            periods[period] = {
                "quarter_count": len(quarters),
                "sum_reported_estimates_usd": sum(quarters),
            }
        lobbying[name] = {"method": entity["method"], "periods": periods}
        raw_periods = entity["quarters_reported_estimate_usd"]
        base_year = "2020" if "2020" in raw_periods else "2024"
        base = sum(raw_periods[base_year])
        annual_2025 = sum(raw_periods["2025"])
        comparable_2025 = sum(raw_periods["2025"][:3])
        ytd_2026 = sum(raw_periods["2026_Jan_Sep"])
        lobbying[name]["within_entity_comparisons"] = {
            "annual_base_year": base_year,
            "2025_less_base_year_reported_estimates_usd": annual_2025 - base,
            "2025_vs_base_year_change_fraction": ratio(annual_2025 - base, base),
            "2025_Jan_Sep_sum_reported_estimates_usd": comparable_2025,
            "2026_Jan_Sep_less_2025_Jan_Sep_reported_estimates_usd": ytd_2026 - comparable_2025,
            "2026_Jan_Sep_vs_2025_Jan_Sep_change_fraction": ratio(ytd_2026 - comparable_2025, comparable_2025),
        }
        if "method_status" in entity:
            lobbying[name]["method_status"] = entity["method_status"]
    out["lobbying"] = {
        "entities": lobbying,
        "cross_company_spending_ranking": None,
        "interpretation": "Sums retain the filings' reported-estimate status. Microsoft Method C differs from Google and OpenAI Method A. No cross-company spending ranking or annualization of January-September figures is produced.",
    }
    c = data["google_corporate_disclosures"]
    sums = {year: sum(quarters) for year, quarters in sorted(c["quarterly_reported_usd"].items())}
    selected = sum(c["selected_rows_already_in_2025_total"].values())
    if selected > sums["2025"]:
        raise ValueError("Selected included rows exceed their stated total")
    out["google_corporate_disclosures"] = {
        "sums_reported_usd": sums,
        "row_counts": c["row_counts"],
        "2025_less_2020_reported_usd": sums["2025"] - sums["2020"],
        "2025_to_2020_amount_ratio": ratio(sums["2025"], sums["2020"]),
        "2025_vs_2020_amount_growth": ratio(sums["2025"] - sums["2020"], sums["2020"]),
        "2025_less_2020_rows": c["row_counts"]["2025"] - c["row_counts"]["2020"],
        "selected_rows_already_in_2025_total": c["selected_rows_already_in_2025_total"],
        "selected_rows_combined_reported_usd": selected,
        "selected_rows_fraction_of_2025_total": ratio(selected, sums["2025"]),
        "other_rows_reported_usd": sums["2025"] - selected,
        "interpretation": "Selected rows are a subset of the reported total and are not added a second time. Reported sums preserve the disclosures' scope; no recipient-intent or influence conclusion follows.",
        "period_note": c["period_note"],
    }
    fec = {}
    for name, entity in sorted(data["fec"].items()):
        total = amount(entity["total_disbursements_usd"])
        line23 = amount(entity["line_23_usd"])
        fec[name] = {
            "period_description": entity["period_description"],
            "reported_total_disbursements_usd": money_text(total),
            "reported_line_23_usd": money_text(line23),
            "total_less_line_23_usd": money_text(total - line23),
            "line_23_fraction_of_total_disbursements": ratio(line23, total),
        }
    out["fec"] = {
        "committees": fec,
        "interpretation": "Calculations describe the named committee filings, not corporate treasury contributions. Total disbursements and Line 23 are distinct reporting fields.",
    }
    b = data["bilderberg"]
    sets = {name: {year for year, present in zip(b["years"], row) if present} for name, row in sorted(b["list_presence"].items())}
    pairs = {}
    for left, right in combinations(sorted(sets), 2):
        intersection, union = sets[left] & sets[right], sets[left] | sets[right]
        pairs[f"{left}__{right}"] = {
            "co_listed_years": sorted(intersection),
            "co_list_count": len(intersection),
            "union_years": sorted(union),
            "union_count": len(union),
            "jaccard": ratio(len(intersection), len(union)) if union else None,
        }
    all_sets = list(sets.values())
    out["bilderberg"] = {
        "years": b["years"],
        "listed_years": {name: sorted(years) for name, years in sets.items()},
        "listed_year_counts": {name: len(years) for name, years in sets.items()},
        "person_year_entries": sum(map(len, sets.values())),
        "all_three_co_listed_years": sorted(set.intersection(*all_sets)),
        "all_three_co_list_count": len(set.intersection(*all_sets)),
        "pairs": pairs,
        "interpretation": "List presence and Jaccard describe overlap in published lists. They do not establish attendance, a meeting, agreement, intent, or influence.",
    }
    out["unsupported_inferential_metrics"] = {
        "intent_probability": None,
        "precision": None,
        "recall": None,
        "empirical_accuracy": None,
        "reason": "No independently labeled validation denominator or identified model for intent is supplied. Undefined quantities remain null and are not set to zero.",
    }
    return out


def serialized(result):
    return json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", type=Path, default=BASE / "inputs.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with args.inputs.open(encoding="utf-8") as handle:
        result = calculate(json.load(handle))
    text = serialized(result)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
