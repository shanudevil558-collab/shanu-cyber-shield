import hashlib
import tempfile
import unittest
from pathlib import Path

from scanner.smart_scanner import scan_file, sha256_file


class SmartScannerTests(unittest.TestCase):

    def test_sha256_matches_known_value(self):
        with tempfile.TemporaryDirectory() as temp:
            file_path = Path(temp) / "sample.txt"
            file_path.write_text("hello", encoding="utf-8")

            self.assertEqual(
                sha256_file(file_path),
                hashlib.sha256(b"hello").hexdigest()
            )

    def test_plain_text_has_no_review_indicators(self):
        with tempfile.TemporaryDirectory() as temp:
            file_path = Path(temp) / "notes.txt"
            file_path.write_text(
                "This is an ordinary note.",
                encoding="utf-8"
            )

            result = scan_file(file_path)
            self.assertEqual(
                result["status"],
                "no_review_indicators_found"
            )

    def test_eval_indicator_is_flagged_for_review(self):
        with tempfile.TemporaryDirectory() as temp:
            file_path = Path(temp) / "example.py"
            file_path.write_text(
                "result = eval(user_input)",
                encoding="utf-8"
            )

            result = scan_file(file_path)
            self.assertEqual(result["status"], "review_recommended")
            self.assertTrue(result["findings"])

    def test_unknown_file_type_is_not_scanned(self):
        with tempfile.TemporaryDirectory() as temp:
            file_path = Path(temp) / "sample.unknown"
            file_path.write_bytes(b"sample data")

            result = scan_file(file_path)
            self.assertEqual(
                result["status"],
                "not_scanned_binary_or_unknown_type"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
