"""Regression checks for publication manifests and protection coverage."""
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import verify_publications as v


class ManifestChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "data.txt").write_bytes(b"public research\n")
        self.row = {"path": "data.txt", "bytes": 16,
                    "sha256": hashlib.sha256(b"public research\n").hexdigest()}
        self.write([self.row])

    def write(self, rows):
        (self.root / "MANIFEST.json").write_text(json.dumps({"files": rows}), encoding="utf-8")

    def test_both_existing_size_schemas(self):
        self.assertEqual(v.verify_manifest(self.root), 1)
        row = dict(self.row); row["size"] = row.pop("bytes")
        self.write([row])
        self.assertEqual(v.verify_manifest(self.root), 1)

    def test_changed_payload_same_size(self):
        (self.root / "data.txt").write_bytes(b"public changed!\n")
        with self.assertRaisesRegex(ValueError, "Hash mismatch"):
            v.verify_manifest(self.root)

    def test_unlisted_payload(self):
        (self.root / "extra.txt").write_text("extra")
        with self.assertRaisesRegex(ValueError, "unlisted"):
            v.verify_manifest(self.root)

    def test_missing_payload(self):
        (self.root / "data.txt").unlink()
        with self.assertRaises(OSError):
            v.verify_manifest(self.root)

    def test_conflicting_sizes(self):
        row = dict(self.row, size=99); self.write([row])
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            v.verify_manifest(self.root)

    def test_duplicate_rows(self):
        self.write([self.row, self.row])
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            v.verify_manifest(self.root)

    def test_json_duplicate_keys(self):
        with self.assertRaisesRegex(ValueError, "Duplicate JSON"):
            v.parse_json(b'{"files":[],"files":[]}')

    def test_path_escapes(self):
        for name in ("../data.txt", "/data.txt", "C:/data.txt", "a\\data.txt", "a/../data.txt"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                v.local_file(self.root, name)

    def test_negative_or_boolean_size(self):
        for size in (-1, True, None):
            self.write([dict(self.row, bytes=size)])
            with self.subTest(size=size), self.assertRaises(ValueError):
                v.verify_manifest(self.root)

    def test_missing_edition_is_not_silent_success(self):
        (self.root / "records").mkdir()
        with self.assertRaisesRegex(ValueError, "required edition"):
            v.verify_publications(self.root)

    def test_symlinked_parent_rejected(self):
        original = Path.is_symlink
        with patch.object(Path, "is_symlink", lambda p: p.name == "nested" or original(p)):
            with self.assertRaisesRegex(ValueError, "Symlink"):
                v.local_file(self.root, "nested/data.txt")


class AttestationChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.directory = self.root / "records/2026-10-18-publication-attestation"
        self.directory.mkdir(parents=True)
        source = Path(__file__).resolve().parent / "records/2026-10-18-publication-attestation"
        for name in ("publication-manifest.json", "publication-manifest.json.asc", "owner-signing-public.asc"):
            shutil.copyfile(source / name, self.directory / name)

    def test_changed_historical_manifest_rejected(self):
        path = self.directory / "publication-manifest.json"
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "Historical signed manifest changed"):
            v.verify_attestation(self.root)

    @unittest.skipIf(os.name == "nt", "GnuPG integration runs on the Linux CI job")
    def test_invalid_signature_rejected_by_gnupg(self):
        (self.directory / "publication-manifest.json.asc").write_text("invalid signature\n")
        with self.assertRaisesRegex(ValueError, "Detached signature"):
            v.verify_attestation(self.root)


class ProtectionChecks(unittest.TestCase):
    def setUp(self):
        self.rule = {"target": "branch", "enforcement": "active",
                     "conditions": {"ref_name": {"include": ["~ALL"], "exclude": []}},
                     "bypass_actors": [],
                     "rules": [{"type": t} for t in ("deletion", "non_fast_forward", "required_signatures")]}
        self.branches = [{"name": "main", "protected": True},
                         {"name": "archive/old", "protected": True}]

    def test_all_branches_pass(self):
        self.assertEqual(v.check_protection(self.rule, self.branches), 2)

    def test_default_only_regression_rejected(self):
        self.rule["conditions"]["ref_name"]["include"] = ["~DEFAULT_BRANCH"]
        with self.assertRaises(ValueError): v.check_protection(self.rule, self.branches)

    def test_public_api_omission_is_reported_as_limitation(self):
        self.rule.pop("bypass_actors")
        self.rule["id"] = 123
        with patch.object(v, "api_json", side_effect=[self.branches, [self.rule], self.rule]):
            result = v.verify_protection("owner/repository")
        self.assertIn("not exposed", result["bypass_audit"])

    def test_bypass_exclusion_disabled_or_missing_rule(self):
        for mutation in ("bypass", "exclusion", "disabled", "missing"):
            rule = copy.deepcopy(self.rule)
            if mutation == "bypass": rule["bypass_actors"] = [{"actor_id": 1}]
            if mutation == "exclusion": rule["conditions"]["ref_name"]["exclude"] = ["refs/heads/archive/*"]
            if mutation == "disabled": rule["enforcement"] = "disabled"
            if mutation == "missing": rule["rules"].pop()
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                v.check_protection(rule, self.branches)

    def test_unprotected_or_empty_inventory(self):
        for branches in ([], [{"name": "old", "protected": False}]):
            with self.subTest(branches=branches), self.assertRaises(ValueError):
                v.check_protection(self.rule, branches)


if __name__ == "__main__":
    unittest.main(verbosity=2)
