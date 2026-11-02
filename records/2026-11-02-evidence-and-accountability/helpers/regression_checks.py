"""Focused regression checks. SOURCE ONLY until the coordinator schedules execution.
Copies the candidate into an explicitly selected scratch directory; originals stay unchanged.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def read(root, name):
    return json.loads((root / name).read_text(encoding="utf-8-sig"))


def write(root, name, value):
    (root / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def rehash(root):
    manifest = read(root, "publication-manifest.json")
    for item in manifest["files"]:
        raw = (root / item["path"]).read_bytes()
        item["bytes"] = len(raw)
        item["sha256"] = hashlib.sha256(raw).hexdigest()
        if "git_blob_sha1" in item:
            item["git_blob_sha1"] = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    write(root, "publication-manifest.json", manifest)


def mutate(root, case):
    if case in ("omit_financial", "omit_slavery"):
        data = read(root, "calculation-index.json")
        data["financial" if case == "omit_financial" else "slavery"] = []
        write(root, "calculation-index.json", data)
    elif case == "omit_required_file":
        missing = "financial/history/evidence.json"
        (root / missing).unlink()
        data = read(root, "publication-manifest.json")
        data["files"] = [row for row in data["files"] if row["path"] != missing]
        write(root, "publication-manifest.json", data)
    elif case == "empty_correlation_links":
        data = read(root, "correlation-matrix.json")
        data["rows"][0]["comparison_ids"] = []
        data["rows"][0]["owner_stages"] = []
        write(root, "correlation-matrix.json", data)
    elif case == "empty_company_links":
        data = read(root, "company-financial-index.json")
        for field in ("purchase_ids", "financial_first_ids", "financial_followthrough_ids"):
            data["groups"][0][field] = []
        write(root, "company-financial-index.json", data)
    elif case in ("whitespace_reference", "url_not_in_reference"):
        data = read(root, "source-index.json")
        data["sources"][0]["occurs_in"] = (
            [" " + data["sources"][0]["occurs_in"][0]]
            if case == "whitespace_reference" else ["LICENSE-MIT.txt"])
        write(root, "source-index.json", data)
    elif case == "omit_conclusion":
        data = read(root, "comparison-coverage.json")
        data["conclusions"].pop(0)
        data["conclusionLeafCount"] = len(data["conclusions"])
        write(root, "comparison-coverage.json", data)
    elif case == "alter_report_payload":
        data = read(root, "comparison-coverage.json")
        first = data["conclusions"][0]
        report = root / data["report"]["path"]
        lines = report.read_text(encoding="utf-8").split("\n")
        require(first["startLine"] == first["endLine"], "First fixture leaf must be one JSON line")
        lines[first["startLine"] - 1] = json.dumps("REGRESSION-MUTATED-CONTENT")
        raw = "\n".join(lines).encode("utf-8")
        report.write_bytes(raw)
        data["report"]["bytes"] = len(raw)
        data["report"]["sha256"] = hashlib.sha256(raw).hexdigest()
        write(root, "comparison-coverage.json", data)
    elif case == "payment_sum":
        name = "financial/international-followthrough/cjc-payment-analysis.json"
        data = read(root, name)
        data["snapshots"][0]["summary"]["sum_cents"] += 1
        write(root, name, data)
    else:
        raise RuntimeError("Unknown mutation")
    rehash(root)  # Deliberately defeats a hash-only verifier; semantic checks must reject.


def run_case(root, optimized, expected_marker=None, payments=False):
    helper = HERE / ("verify-payments.py" if payments else "verify_release.py")
    command = [sys.executable, "-B", "-E"]
    if optimized:
        command.append("-O")
    command += [str(helper), "--root", str(root)]
    process = subprocess.run(command, capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=600)
    if expected_marker is None:
        require(process.returncode == 0, "Valid edition rejected: " + process.stderr[-2000:])
        result = json.loads(process.stdout)
        require(result.get("status") == "PASS", "Missing positive baseline result")
    else:
        require(process.returncode != 0, "Corrupted edition incorrectly passed")
        require(expected_marker in process.stderr,
                "Corruption failed for an unexpected reason: " + process.stderr[-2000:])
    return {"optimized": optimized, "expected_rejection": expected_marker,
            "exit_code": process.returncode}


def regression_checks(root, scratch):
    root, scratch = Path(root).resolve(), Path(scratch).resolve()
    require(root.is_dir() and scratch.is_dir(), "Root and explicit scratch directory must exist")
    require(not scratch.is_relative_to(root) and not root.is_relative_to(scratch),
            "Scratch and candidate must be separate directory trees")
    results = []
    for optimized in (False, True):
        results.append({"case": "valid_baseline", **run_case(root, optimized)})
    cases = [
        ("omit_financial", "arithmetic.financial.ids"),
        ("omit_slavery", "arithmetic.slavery.ids"),
        ("omit_required_file", "manifest.required_original_or_new_file_omitted"),
        ("empty_correlation_links", "correlations.required_membership"),
        ("empty_company_links", "company_index.required_membership"),
        ("whitespace_reference", "reference.path_whitespace_or_missing"),
        ("url_not_in_reference", "sources.url_absent_in_reference"),
        ("omit_conclusion", "coverage.leaf_count"),
        ("alter_report_payload", "coverage.report_payload_differs"),
    ]
    # Only these newly created fixture directories are removed by TemporaryDirectory.
    # No source file or publication directory is modified.
    with tempfile.TemporaryDirectory(prefix="research-verifier-", dir=scratch) as workspace:
        require(Path(workspace).resolve().is_relative_to(scratch), "Fixture path escaped scratch")
        for case, marker in cases + [("payment_sum", "payments.sum_cents")]:
            fixture = Path(workspace) / case
            shutil.copytree(root, fixture, symlinks=True)
            mutate(fixture, case)
            for optimized in (False, True):
                results.append({"case": case, **run_case(fixture, optimized, marker,
                                                          payments=case == "payment_sum")})
    return {"schema": "qel.research-verifier-regressions.v1", "status": "PASS",
            "checks_executed": len(results), "results": results,
            "originalCandidateModified": False, "publicationPerformed": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    arguments = parser.parse_args()
    try:
        print(json.dumps(regression_checks(arguments.root, arguments.scratch), sort_keys=True))
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError) as error:
        print(json.dumps({"status": "FAIL", "error": str(error)}), file=sys.stderr)
        sys.exit(1)
