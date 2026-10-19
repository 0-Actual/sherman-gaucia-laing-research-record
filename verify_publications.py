"""Reproduce bounded publication-integrity and repository-policy checks.

These checks do not establish scientific validity, original discovery dates,
ownership of third-party work, or attestation of later commits.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import tempfile
import urllib.request

EDITIONS = (
    "2026-10-16-priority-zero-preview",
    "2026-10-17-github-actions-output-review",
    "2026-10-17-openai-mathematics-review",
    "2026-10-17-openai-severity-review",
    "2026-10-17-openai-stream-ownership",
    "2026-10-17-optax-multisteps-review",
    "2026-10-17-priority-zero-expanded",
)
OWNER_FINGERPRINT = "FA8C7305ABE0E48D4CECEF700097816F47090DA3"
ATTESTATION_HASH = "9914d0cec786dc711b2d20a5cfadcb016a651f46b7d85059d14ba16e17006556"
MAX_FILE = 256 * 1024 * 1024
MAX_JSON = 16 * 1024 * 1024
MAX_ENTRIES = 100000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "Duplicate JSON key: " + key)
        result[key] = value
    return result


def parse_json(data):
    require(len(data) <= MAX_JSON, "JSON size limit exceeded")
    return json.loads(data, object_pairs_hook=unique_object)


def local_file(root, name):
    require(isinstance(name, str) and bool(name), "Missing relative path")
    relative = PurePosixPath(name)
    require(not relative.is_absolute() and str(relative) == name
            and ".." not in relative.parts and name != "."
            and not any(c in name for c in ("\\", ":", "\0")),
            "Unsafe relative path: " + name)
    path = root
    for part in relative.parts:
        path = path / part
        require(not path.is_symlink(), "Symlink rejected: " + name)
    require(path.resolve().is_relative_to(root.resolve()), "Path escapes root")
    require(stat.S_ISREG(path.stat().st_mode), "Not a regular file: " + name)
    return path


def file_hash(path, size):
    require(type(size) is int and 0 <= size <= MAX_FILE, "Invalid payload size")
    require(path.stat().st_size == size, "Size mismatch: " + path.name)
    digest = hashlib.sha256()
    actual = 0
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            actual += len(chunk)
            require(actual <= size, "Payload grew beyond declared size")
            digest.update(chunk)
    require(actual == size, "Payload changed size while reading")
    return digest.hexdigest()


def verify_manifest(directory):
    directory = Path(directory).resolve()
    manifest_path = local_file(directory, "MANIFEST.json")
    require(manifest_path.stat().st_size <= MAX_JSON, "Manifest too large")
    with manifest_path.open("rb") as stream:
        manifest = parse_json(stream.read(MAX_JSON + 1))
    require(isinstance(manifest, dict), "Manifest must be an object")
    rows = manifest.get("files")
    require(isinstance(rows, list) and len(rows) <= MAX_ENTRIES, "Invalid file list")
    names, folded = set(), set()
    total = 0
    for row in rows:
        require(isinstance(row, dict), "Invalid file record")
        name = row.get("path")
        path = local_file(directory, name)
        require(name != "MANIFEST.json", "Manifest must be self-excluded")
        require(name.casefold() not in folded, "Duplicate/colliding payload path")
        names.add(name)
        folded.add(name.casefold())
        if "bytes" in row and "size" in row:
            require(row["bytes"] == row["size"], "Conflicting size fields")
        size = row.get("bytes", row.get("size"))
        expected = row.get("sha256")
        require(isinstance(expected, str) and re.fullmatch("[0-9a-f]{64}", expected),
                "Invalid SHA-256")
        require(file_hash(path, size) == expected, "Hash mismatch: " + name)
        total += size
        require(total <= 1024 * 1024 * 1024, "Combined payload size limit exceeded")
    actual = set()
    for path in directory.rglob("*"):
        require(not path.is_symlink(), "Unlisted symlink in release")
        if path.is_file():
            actual.add(path.relative_to(directory).as_posix())
        require(len(actual) <= MAX_ENTRIES + 1, "Excessive payload count")
    require(actual == names | {"MANIFEST.json"}, "Missing or unlisted release payload")
    return len(rows)


def verify_publications(root):
    records = Path(root).resolve() / "records"
    require(records.is_dir() and not records.is_symlink(), "Missing or symlinked records directory")
    manifests = set(records.glob("*/MANIFEST.json"))
    expected = {records / edition / "MANIFEST.json" for edition in EDITIONS}
    require(expected <= manifests, "A required edition manifest is missing")
    counts = {}
    for manifest in sorted(manifests):
        require(not manifest.parent.is_symlink(), "Symlinked edition rejected")
        counts[manifest.parent.name] = verify_manifest(manifest.parent)
    return counts


def verify_attestation(root, gpg="gpg"):
    root = Path(root).resolve()
    prefix = "records/2026-10-18-publication-attestation/"
    manifest = local_file(root, prefix + "publication-manifest.json")
    signature = local_file(root, prefix + "publication-manifest.json.asc")
    key = local_file(root, prefix + "owner-signing-public.asc")
    for path in (manifest, signature, key):
        require(path.stat().st_size <= MAX_JSON, "Attestation input too large")
    require(hashlib.sha256(manifest.read_bytes()).hexdigest() == ATTESTATION_HASH,
            "Historical signed manifest changed; do not regenerate it automatically")
    with tempfile.TemporaryDirectory(prefix="qel-public-key-") as home:
        command = [gpg, "--no-options", "--batch", "--homedir", home,
                   "--no-auto-key-retrieve"]
        imported = subprocess.run(command + ["--import", str(key)],
                                  capture_output=True, text=True, timeout=30)
        require(imported.returncode == 0, "Public key import failed")
        verified = subprocess.run(command + ["--status-fd=1", "--verify",
                                               str(signature), str(manifest)],
                                  capture_output=True, text=True, timeout=30)
        signers = [line.split()[2] for line in verified.stdout.splitlines()
                   if line.startswith("[GNUPG:] VALIDSIG ")]
        require(verified.returncode == 0 and signers == [OWNER_FINGERPRINT],
                "Detached signature or expected signer verification failed")
    return {"fingerprint": OWNER_FINGERPRINT, "manifest_sha256": ATTESTATION_HASH,
            "scope": "Exact October 18 historical manifest only; later commits excluded"}


def check_protection(rule, branches):
    require(isinstance(rule, dict) and isinstance(branches, list) and branches,
            "Missing protection evidence")
    require(rule.get("enforcement") == "active" and rule.get("target") == "branch",
            "Branch ruleset is not active")
    refs = rule.get("conditions", {}).get("ref_name", {})
    require(refs.get("include") == ["~ALL"] and refs.get("exclude") == [],
            "Protection must cover all branches without exclusions")
    # GitHub omits bypass actors from responses without sufficient permission.
    # Omission is an explicit audit limitation, not evidence of an empty list.
    if "bypass_actors" in rule:
        require(rule["bypass_actors"] == [], "Unexpected bypass actors")
    types = {item.get("type") for item in rule.get("rules", [])}
    require({"deletion", "non_fast_forward", "required_signatures"} <= types,
            "Required preservation/signature rules missing")
    require(all(branch.get("protected") is True for branch in branches),
            "An unprotected branch was found")
    return len(branches)


def api_json(path):
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "QEL-publication-integrity"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = "Bearer " + token
    request = urllib.request.Request("https://api.github.com/" + path, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        data = response.read(MAX_JSON + 1)
    return parse_json(data)


def verify_protection(repository):
    require(bool(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository)),
            "Expected owner/repository")
    base = "repos/" + repository
    branches = []
    for page in range(1, 101):
        batch = api_json(base + "/branches?per_page=100&page=" + str(page))
        require(isinstance(batch, list), "Invalid branches response")
        branches.extend(batch)
        if len(batch) < 100:
            break
    else:
        raise ValueError("Branch pagination limit exceeded")
    # Public rule details expose conditions and rules without granting write access.
    rules = api_json(base + "/rulesets?per_page=100")
    require(isinstance(rules, list) and len(rules) < 100, "Ruleset listing unavailable or truncated")
    for summary in rules:
        if summary.get("enforcement") != "active" or summary.get("target") != "branch":
            continue
        rule = api_json(base + "/rulesets/" + str(summary["id"]))
        try:
            count = check_protection(rule, branches)
        except ValueError:
            continue
        return {"repository": repository, "protected_branches": count, "ruleset": rule["id"],
                "bypass_audit": "verified empty" if "bypass_actors" in rule
                else "not exposed by API; authorized administration review required"}
    raise ValueError("No verified all-branch preservation ruleset")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("check", choices=("manifests", "attestation", "protection"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--gpg", default="gpg")
    parser.add_argument("--repository", default="0-Actual/sherman-gaucia-laing-research-record")
    args = parser.parse_args()
    try:
        if args.check == "manifests":
            result = verify_publications(args.root)
        elif args.check == "attestation":
            result = verify_attestation(args.root, args.gpg)
        else:
            result = verify_protection(args.repository)
        print(json.dumps({"result": "PASS", "check": args.check, "details": result}, indent=2))
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, "Verification failed: " + str(error) + "\n")
