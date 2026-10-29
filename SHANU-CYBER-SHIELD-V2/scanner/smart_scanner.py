#!/usr/bin/env python3
"""SHANU CYBER SHIELD V2 — conservative local file scanner."""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

TEXT_EXTENSIONS = {
    ".py", ".sh", ".js", ".html", ".php", ".java",
    ".txt", ".json", ".xml", ".yaml", ".yml", ".bat"
}

REVIEW_PATTERNS = {
    "dynamic_code_execution": ("eval(", "exec("),
    "download_then_execute": ("curl ", "wget ", "urllib.request"),
    "shell_execution": ("subprocess.", "os.system(", "popen("),
    "encoded_payload_handling": ("base64.b64decode", "base64 -d"),
}

def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()

def scan_file(path):
    result = {
        "file": str(path),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "findings": [],
        "status": "no_review_indicators_found",
    }

    if path.suffix.lower() not in TEXT_EXTENSIONS:
        result["status"] = "not_scanned_binary_or_unknown_type"
        return result

    try:
        content = path.read_text(encoding="utf-8", errors="replace").lower()
    except OSError as exc:
        result["status"] = "read_error"
        result["error"] = str(exc)
        return result

    for category, patterns in REVIEW_PATTERNS.items():
        matches = [pattern for pattern in patterns if pattern in content]
        if matches:
            result["findings"].append({
                "category": category,
                "matched_indicators": matches,
                "severity": "manual_review",
            })

    if result["findings"]:
        result["status"] = "review_recommended"

    return result

def main():
    raw = input("Folder path to scan: ").strip()
    folder = Path(raw).expanduser()

    if not folder.is_dir():
        print("ERROR: Folder does not exist.")
        return

    results = []
    errors = 0

    for path in folder.rglob("*"):
        if not path.is_file():
            continue
        try:
            results.append(scan_file(path))
        except (OSError, PermissionError) as exc:
            errors += 1
            results.append({
                "file": str(path),
                "status": "read_error",
                "error": str(exc),
            })

    report_dir = Path(__file__).resolve().parents[1] / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = report_dir / f"scanner-{timestamp}.json"

    report = {
        "tool": "SHANU CYBER SHIELD V2 Smart Scanner",
        "generated_utc": timestamp,
        "scanned_folder": str(folder.resolve()),
        "files_examined": len(results),
        "read_errors": errors,
        "limitations": [
            "Heuristic indicators can produce false positives.",
            "No findings does not prove a file is safe.",
            "This tool does not claim to detect all malware.",
        ],
        "results": results,
    }

    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    flagged = sum(item["status"] == "review_recommended" for item in results)

    print(f"\nFiles examined: {len(results)}")
    print(f"Files recommended for manual review: {flagged}")
    print(f"Read errors: {errors}")
    print(f"Report saved: {report_path}")
    print("Note: indicators are clues for review, not proof of malware.")

if __name__ == "__main__":
    main()
