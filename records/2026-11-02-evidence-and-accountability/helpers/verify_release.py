"""Verifier for the NEW research edition; retained historical verifiers are not replaced."""
from pathlib import Path, PurePosixPath
from datetime import date
from decimal import Decimal
from urllib.parse import urlsplit
import argparse
import hashlib
import importlib.util
import json
import math
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
SCHEMA = "qel.research-edition-verification.v1"


class VerificationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "json.duplicate_key: " + key)
        result[key] = value
    return result


def load_json(path):
    def invalid(value):
        raise VerificationError("json.nonfinite: " + value)
    return json.loads(Path(path).read_text(encoding="utf-8-sig"),
                      object_pairs_hook=unique_object, parse_constant=invalid)


def sha_file(path):
    digest = hashlib.sha256()
    size = 0
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            size += len(block)
            digest.update(block)
    return {"bytes": size, "sha256": digest.hexdigest()}


def identity_matches(path, expected):
    observed = sha_file(path)
    require(observed["bytes"] == expected.get("bytes") and
            observed["sha256"] == expected.get("sha256"), "identity: " + str(path))
    return observed


def safe_path(root, relative):
    require(isinstance(relative, str) and relative and relative == relative.strip(),
            "reference.path_whitespace_or_missing")
    require("\\" not in relative and ":" not in relative and
            not any(ord(char) < 32 for char in relative), "reference.unsafe_path")
    parts = PurePosixPath(relative).parts
    require(not relative.startswith("/") and all(p not in ("", ".", "..") for p in relative.split("/")),
            "reference.path_escape")
    target = root.joinpath(*parts)
    current = root
    for part in parts:
        current = current / part
        require(not current.is_symlink(), "reference.symlink")
    require(target.is_file(), "reference.missing_file: " + relative)
    require(target.resolve().is_relative_to(root), "reference.resolved_escape")
    return target


def ids_exact(rows, expected, label, field="id"):
    require(isinstance(rows, list), label + ".not_array")
    ids = [row.get(field) if isinstance(row, dict) else None for row in rows]
    require(all(isinstance(value, str) for value in ids), label + ".missing_id")
    require(len(ids) == len(expected) and len(set(ids)) == len(ids) and set(ids) == set(expected),
            label + ".ids: expected " + str(len(expected)) + " distinct pinned identifiers")
    return {row[field]: row for row in rows}


def number(value):
    require(isinstance(value, (int, float)) and not isinstance(value, bool) and
            math.isfinite(value), "arithmetic.nonfinite_or_nonnumeric")
    return Decimal(str(value))


def evaluate(operation, values):
    a = [number(value) for value in values]
    if operation == "sum":
        require(len(a) >= 1, "arithmetic.empty_sum")
        return sum(a)
    require(operation in {"subtract", "ratio_percent", "percent", "spread",
                          "multiply", "divide", "growth_percent"}, "arithmetic.unknown_operation")
    require(len(a) == (3 if operation == "spread" else 2), "arithmetic.arity")
    if operation == "subtract":
        return a[0] - a[1]
    if operation == "multiply":
        return a[0] * a[1]
    if operation == "spread":
        return (a[0] - a[1]) / 100 * a[2]
    require(a[1] != 0, "arithmetic.zero_denominator")
    if operation in {"ratio_percent", "percent"}:
        return a[0] / a[1] * 100
    if operation == "growth_percent":
        return (a[0] - a[1]) / a[1] * 100
    return a[0] / a[1]


def verify_arithmetic(data, contract):
    counts = {}
    for family in ("financial", "slavery"):
        expected = contract["arithmetic"][family]
        actual = ids_exact(data.get(family), [r["id"] for r in expected], "arithmetic." + family)
        for pin in expected:
            row = actual[pin["id"]]
            require(row.get("operation") == pin["operation"] and row.get("inputs") == pin["inputs"] and
                    row.get("result") == pin["result"], "arithmetic.pinned_inputs_result: " + pin["id"])
            computed = evaluate(row["operation"], row["inputs"])
            stated = number(row["result"])
            tolerance = max(Decimal("0.000001") if family == "financial" else Decimal("0.000000000001"),
                            abs(stated) * Decimal("0.000000000001"))
            require(abs(computed - stated) <= tolerance, "arithmetic.result: " + pin["id"])
        counts[family + "_calculations"] = len(actual)
    pin = contract["arithmetic"]["procurement"]
    row = data.get("procurement_face_value", {})
    require(row.get("formula") == pin["formula"] and row.get("source_case") == pin["source_case"],
            "arithmetic.procurement_binding")
    computed = evaluate("multiply", pin["inputs"])
    require(number(row.get("result")) == computed == number(pin["result"]), "arithmetic.procurement")
    counts["procurement_calculations"] = 1
    counts["arithmetic_results"] = sum(counts.values())
    return counts


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)


def full_urls(value):
    return {item for item in strings(value) if re.fullmatch(r"https?://\S+", item)}


def leaves(value, pointer):
    if isinstance(value, dict) and value:
        for key, child in value.items():
            escaped = key.replace("~", "~0").replace("/", "~1")
            yield from leaves(child, pointer + "/" + escaped)
    elif isinstance(value, list) and value:
        for index, child in enumerate(value):
            yield from leaves(child, pointer + "/" + str(index))
    else:
        yield pointer, value


def typed_equal(a, b):
    return type(a) is type(b) and a == b


def verify_coverage(root, comparisons):
    coverage = load_json(safe_path(root, "comparison-coverage.json"))
    require(coverage.get("schema") == "qel.comparisons.markdown-coverage.v1", "coverage.schema")
    require(coverage.get("source", {}).get("retainedPath") == "prior-work/corrected-comparisons.json",
            "coverage.source_binding")
    require(coverage.get("report", {}).get("path") == "PROJECT-COMPARISONS.md", "coverage.report_binding")
    identity_matches(safe_path(root, coverage["source"]["retainedPath"]), coverage["source"])
    report_path = safe_path(root, coverage["report"]["path"])
    identity_matches(report_path, coverage["report"])
    text = report_path.read_bytes().decode("utf-8")
    require("\r" not in text, "coverage.report_requires_LF")
    lines = text.split("\n")
    expected = {}
    for index, row in enumerate(comparisons):
        require("latest_corrected_conclusions" in row, "coverage.missing_conclusions")
        for pointer, value in leaves(row["latest_corrected_conclusions"],
                                     "/comparisons/" + str(index) + "/latest_corrected_conclusions"):
            expected[pointer] = (row["id"], value)
    sections = ids_exact(coverage.get("sections"), [row["id"] for row in comparisons],
                         "coverage.sections", "comparisonId")
    last_section_end = 0
    for row in comparisons:
        section = sections[row["id"]]
        start, end = section.get("startLine"), section.get("endLine")
        require(type(start) is int and type(end) is int and
                1 <= start <= end <= len(lines) and start > last_section_end, "coverage.section_bounds")
        require(lines[start - 1] == section.get("reportSection") and row["id"] in lines[start - 1],
                "coverage.section_heading")
        anchor = section.get("reportAnchor")
        require(isinstance(anchor, str) and
                '<a id="' + anchor + '"></a>' in text, "coverage.section_anchor")
        last_section_end = end
    actual = coverage.get("conclusions")
    require(isinstance(actual, list), "coverage.conclusions_not_array")
    require(len(actual) == len(expected), "coverage.leaf_count")
    seen, intervals = set(), []
    for entry in actual:
        pointer = entry.get("pointer")
        require(pointer in expected and pointer not in seen, "coverage.pointer_missing_duplicate_or_extra")
        seen.add(pointer)
        comparison_id, value = expected[pointer]
        require(entry.get("comparisonId") == comparison_id and typed_equal(entry.get("value"), value),
                "coverage.source_value")
        section = sections[comparison_id]
        require(entry.get("encoding") == "json" and
                entry.get("reportSection") == section["reportSection"] and
                entry.get("reportAnchor") == section["reportAnchor"], "coverage.section_binding")
        start, end = entry.get("startLine"), entry.get("endLine")
        require(type(start) is int and type(end) is int and
                section["startLine"] < start <= end < section["endLine"], "coverage.leaf_bounds")
        require(start >= 2 and end < len(lines), "coverage.fence_bounds")
        opening, closing = lines[start - 2], lines[end]
        require(opening.endswith("json") and len(opening[:-4]) >= 3 and
                len(set(opening[:-4])) == 1 and opening[0] in (chr(96), "~") and
                closing == opening[:-4], "coverage.json_fence")
        decoded = json.loads("\n".join(lines[start - 1:end]), object_pairs_hook=unique_object)
        require(typed_equal(decoded, value), "coverage.report_payload_differs")
        intervals.append((start, end))
    require(seen == set(expected), "coverage.incomplete_pointer_set")
    ordered = sorted(intervals)
    require(all(a[1] < b[0] for a, b in zip(ordered, ordered[1:])), "coverage.overlapping_payloads")
    require(coverage.get("comparisonCount") == len(comparisons) and
            coverage.get("conclusionLeafCount") == len(expected), "coverage.declared_counts")
    return len(expected)


def verify_source_index(root, paths, contract):
    data = load_json(safe_path(root, "source-index.json"))
    entries = data.get("sources")
    require(isinstance(entries, list), "sources.not_array")
    by_url = {}
    json_cache = {}
    occurrences = 0
    for entry in entries:
        url = entry.get("url")
        require(isinstance(url, str) and url == url.strip() and
                re.fullmatch(r"https?://\S+", url) is not None, "sources.invalid_url")
        parsed = urlsplit(url)
        require(parsed.scheme in ("http", "https") and bool(parsed.netloc), "sources.invalid_url_host")
        require(url not in by_url, "sources.duplicate_url")
        refs = entry.get("occurs_in")
        require(isinstance(refs, list) and refs and len(set(refs)) == len(refs), "sources.invalid_occurs_in")
        for relative in refs:
            p = safe_path(root, relative)
            if p.suffix.lower() == ".json":
                if relative not in json_cache:
                    json_cache[relative] = load_json(p)
                present = url in set(strings(json_cache[relative]))
            else:
                present = url in p.read_text(encoding="utf-8-sig")
            require(present, "sources.url_absent_in_reference: " + relative)
            occurrences += 1
        by_url[url] = set(refs)
    require(set(contract["baselineSourceUrls"]) <= set(by_url), "sources.baseline_url_omitted")
    excluded_names = {"source-index.json", "publication-manifest.json",
                      "expected-records.json", "comparison-coverage.json"}
    scanned = 0
    for relative in sorted(paths):
        p = root / relative
        if p.suffix.lower() != ".json" or p.name in excluded_names:
            continue
        scanned += 1
        if relative not in json_cache:
            json_cache[relative] = load_json(p)
        for url in full_urls(json_cache[relative]):
            require(url in by_url and relative in by_url[url],
                    "sources.unindexed_url_occurrence: " + relative)
    return {"source_urls": len(by_url), "source_occurrences": occurrences, "source_json_files": scanned}


def verify_relocation(root, contract):
    data = load_json(safe_path(root, "relocation-map.json"))
    require(data.get("schema") == "qel.edition-relocations.v1" and isinstance(data.get("entries"), list),
            "relocation.schema")
    pin = contract["relocation"]
    matches = [row for row in data["entries"]
               if row.get("sourceFile") == pin["sourceFile"] and row.get("jsonPointer") == pin["jsonPointer"]]
    require(len(matches) == 1, "relocation.required_mapping")
    row = matches[0]
    require(all(row.get(key) == value for key, value in pin.items()), "relocation.pinned_target")
    source = load_json(safe_path(root, pin["sourceFile"]))
    require(source.get("license_path") == pin["originalValue"], "relocation.original_value_changed")
    safe_path(root, pin["targetPath"])
    require(isinstance(row.get("reason"), str) and row["reason"].strip(), "relocation.missing_reason")
    return len(matches)


def verify_release(root):
    root = Path(root).resolve()
    require(root.is_dir() and not root.is_symlink(), "edition.root_missing_or_link")
    contract = load_json(HERE / "expected-records.json")
    require(contract.get("schema") == "qel.research-verifier.expected-records.v1", "contract.schema")
    manifest = load_json(safe_path(root, "publication-manifest.json"))
    entries = manifest.get("files")
    require(isinstance(entries, list), "manifest.files_not_array")
    paths = set()
    for entry in entries:
        relative = entry.get("path")
        require(relative not in paths and relative != "publication-manifest.json", "manifest.duplicate_or_self")
        file_path = safe_path(root, relative)
        identity_matches(file_path, entry)
        paths.add(relative)
    actual = set()
    for directory, directories, files in os.walk(root, followlinks=False):
        require(not any((Path(directory) / name).is_symlink() for name in directories), "manifest.link_directory")
        for name in files:
            p = Path(directory) / name
            require(not p.is_symlink(), "manifest.link_file")
            actual.add(p.relative_to(root).as_posix())
    require(actual == paths | {"publication-manifest.json"}, "manifest.unlisted_or_missing_file")
    required = set(contract["requiredMoneyPaths"] + contract["requiredCorporatePaths"] +
                   contract["requiredNewPaths"])
    require(required <= paths, "manifest.required_original_or_new_file_omitted")
    for expected in contract["preservedIdentities"]:
        identity_matches(safe_path(root, expected["path"]), expected)
    group_counts, groups = {}, {}
    for specification in contract["recordGroups"]:
        document = load_json(safe_path(root, specification["path"]))
        if "schema" in specification:
            require(document.get("schema") == specification["schema"], "records.schema")
        rows = document.get(specification["field"])
        group = ids_exact(rows, specification["ids"], "records." + specification["path"],
                          specification.get("idField", "id"))
        groups[specification["path"]] = group
        group_counts[specification["path"]] = len(group)
    comparisons = load_json(root / "prior-work/corrected-comparisons.json")["comparisons"]
    purchases = groups["purchases.json"]
    matrix = load_json(safe_path(root, "correlation-matrix.json"))
    joined = ids_exact(matrix.get("rows"), list(purchases), "correlations", "transaction_id")
    expected_joins = ids_exact(contract.get("correlationBindings"), list(purchases),
                               "contract.correlations", "transaction_id")
    unmapped = matrix.get("unmapped_prior_comparison_ids")
    require(isinstance(unmapped, list) and len(set(unmapped)) == len(unmapped) and
            set(unmapped) == set(contract["unmappedComparisonIds"]), "correlations.unmapped_membership")
    comparison_ids = set(groups["prior-work/corrected-comparisons.json"])
    date_gaps = 0
    for identifier, row in joined.items():
        expected_join = expected_joins[identifier]
        references = row.get("comparison_ids")
        require(isinstance(references, list) and len(set(references)) == len(references) and
                set(references) <= comparison_ids, "correlations.comparison_reference")
        require(set(references) == set(expected_join["comparison_ids"]),
                "correlations.required_membership")
        require(row.get("buyer") == purchases[identifier]["buyer"] and
                row.get("target") == purchases[identifier]["target"], "correlations.purchase_identity")
        stages = row.get("owner_stages")
        require(isinstance(stages, list), "correlations.owner_stages")
        require(len(stages) == len(expected_join["owner_stages"]), "correlations.stage_count")
        for actual_stage, expected_stage in zip(stages, expected_join["owner_stages"]):
            require(isinstance(actual_stage, dict) and
                    all(key in actual_stage and actual_stage[key] == value
                        for key, value in expected_stage.items()), "correlations.stage_bindings")
        for anchor in stages:
            require(anchor.get("comparison_id") in references, "correlations.stage_reference")
            gap = anchor.get("calendar_day_gap")
            if gap is not None:
                require(type(gap) is int, "correlations.gap_type")
                require(anchor["announcement_date"][:10] == purchases[identifier]["announced"][:10],
                        "correlations.purchase_date_binding")
                observed = (date.fromisoformat(anchor["announcement_date"][:10]) -
                            date.fromisoformat(anchor["recorded_date"][:10])).days
                require(observed == gap, "correlations.day_gap")
                date_gaps += 1
    first_ids = set(groups["financial/international-first/evidence.json"])
    follow_ids = set(groups["financial/international-followthrough/evidence.json"])
    expected_companies = ids_exact(contract.get("companyBindings"),
                                   list(groups["company-financial-index.json"]),
                                   "contract.companies", "company")
    for group in load_json(safe_path(root, "company-financial-index.json")).get("groups", []):
        for field, allowed in (("purchase_ids", set(purchases)), ("financial_first_ids", first_ids),
                               ("financial_followthrough_ids", follow_ids)):
            refs = group.get(field)
            require(isinstance(refs, list) and set(refs) <= allowed, "company_index.reference")
            require(len(set(refs)) == len(refs) and
                    set(refs) == set(expected_companies[group["company"]][field]),
                    "company_index.required_membership")
    arithmetic = verify_arithmetic(load_json(safe_path(root, "calculation-index.json")), contract)
    leaf_count = verify_coverage(root, comparisons)
    sources = verify_source_index(root, paths, contract)
    relocations = verify_relocation(root, contract)
    spec = importlib.util.spec_from_file_location("new_payment_verifier", HERE / "verify-payments.py")
    require(spec is not None and spec.loader is not None, "payments.helper_missing")
    payments_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(payments_module)
    payments = payments_module.verify_payments(root, contract)
    corporate = []
    for name in ("verify_manifest.py", "verify.py"):
        relative = "corporate-investigation/corporate/" + name
        script = safe_path(root, relative)
        # -E ignores PYTHONOPTIMIZE; omit -O even when this verifier uses -O.
        run = subprocess.run([sys.executable, "-B", "-E", str(script)], cwd=script.parent,
                             capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
        require(run.returncode == 0, "corporate.validator_failed: " + name + ": " + run.stderr[-1000:])
        corporate.append({"script": relative, "exit_code": run.returncode,
                          "stdout": run.stdout.strip(), "stderr": run.stderr.strip()})
    return {"schema": SCHEMA, "status": "PASS", "publicationPerformed": False,
            "counts": {"manifest_payload_files": len(paths), "edition_files": len(actual),
                       "purchase_rows": len(purchases), "comparison_rows": len(comparisons),
                       "conclusion_leaves": leaf_count, "verified_day_gaps": date_gaps,
                       **arithmetic, **sources, "payment_csvs": payments["csv_files"],
                       "payment_rows": payments["payment_rows"], "license_relocations": relocations,
                       "corporate_validator_processes": len(corporate)},
            "record_group_counts": group_counts, "payments": payments, "corporate": corporate,
            "limits": ["Internal content, reference and calculation verification, not independent external source re-verification.",
                       "Hashes establish byte consistency, not truth, authorship, legality or causal influence.",
                       "Historical datasets and their qualified conclusions remain attributed; this verifier does not authorize publication."]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    arguments = parser.parse_args()
    try:
        print(json.dumps(verify_release(arguments.root), ensure_ascii=False, sort_keys=True))
    except (VerificationError, OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        print(json.dumps({"schema": SCHEMA, "status": "FAIL", "error": str(error)}, ensure_ascii=False),
              file=sys.stderr)
        sys.exit(1)
