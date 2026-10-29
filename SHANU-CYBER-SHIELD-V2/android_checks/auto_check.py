#!/usr/bin/env python3
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

def check(name, command):
    if not shutil.which(command[0]):
        return {"name": name, "status": "UNAVAILABLE"}

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=8,
            check=False
        )
        value = (result.stdout or "").strip()

        if result.returncode != 0 or not value:
            return {
                "name": name,
                "status": "INCONCLUSIVE",
                "detail": (result.stderr or "No readable result")[:250]
            }

        return {
            "name": name,
            "status": "CHECKED",
            "value": value[:1000]
        }

    except (OSError, subprocess.TimeoutExpired) as exc:
        return {
            "name": name,
            "status": "INCONCLUSIVE",
            "detail": str(exc)
        }

def main():
    checks = [
        ("Android version", ["getprop", "ro.build.version.release"]),
        ("Android SDK", ["getprop", "ro.build.version.sdk"]),
        ("Device model", ["getprop", "ro.product.model"]),
        ("Security patch", ["getprop", "ro.build.version.security_patch"]),
        ("Verified Boot indicator", ["getprop", "ro.boot.verifiedbootstate"]),
        ("Bootloader lock indicator", ["getprop", "ro.boot.flash.locked"]),
        ("Encryption indicator", ["getprop", "ro.crypto.state"]),
        ("Installed packages access", ["cmd", "package", "list", "packages"]),
        ("ADB availability", ["adb", "version"]),
    ]

    results = [check(name, command) for name, command in checks]

    base = Path(__file__).resolve().parents[1]
    report_dir = base / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "tool": "SHANU CYBER SHIELD V2 Auto Check",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "results": results,
        "manual_checks": [
            "Play Protect scan",
            "Accessibility services",
            "Device admin apps",
            "VPN and Private DNS settings",
            "Review unfamiliar apps in Android Settings",
        ],
        "warning": (
            "This is a limited diagnostic, not antivirus software. "
            "CHECKED means a value was readable, not that it is safe."
        ),
    }

    filename = report_dir / (
        "auto-check-" +
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") +
        ".json"
    )
    filename.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\n=== SHANU CYBER SHIELD V2 | AUTO CHECK ===")
    for item in results:
        print(f"\n[{item['status']}] {item['name']}")
        if "value" in item:
            print(item["value"][:250])
        elif "detail" in item:
            print(item["detail"])

    print("\nManual checks Android permissions ki wajah se abhi bhi zaroori hain.")
    print(f"Report: {filename}")

if __name__ == "__main__":
    main()
