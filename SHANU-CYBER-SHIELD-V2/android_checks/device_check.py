#!/usr/bin/env python3
"""Safe, read-only Android security diagnostics for Termux."""

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def run_readonly(command):
    """Run a read-only diagnostic command with a short timeout."""
    if not shutil.which(command[0]):
        return {"status": "unavailable", "detail": f"{command[0]} not installed"}

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
        output = (result.stdout or result.stderr).strip()
        return {
            "status": "available" if result.returncode == 0 else "check_incomplete",
            "return_code": result.returncode,
            "detail": output[:1500] if output else "No output returned",
        }
    except subprocess.TimeoutExpired:
        return {"status": "timeout", "detail": "Command exceeded 8 seconds"}
    except OSError as exc:
        return {"status": "error", "detail": str(exc)}


def main():
    checks = {
        "android_release": run_readonly(["getprop", "ro.build.version.release"]),
        "android_sdk": run_readonly(["getprop", "ro.build.version.sdk"]),
        "device_model": run_readonly(["getprop", "ro.product.model"]),
        "security_patch": run_readonly(["getprop", "ro.build.version.security_patch"]),
        "verified_boot_state": run_readonly(["getprop", "ro.boot.verifiedbootstate"]),
        "bootloader_lock_state": run_readonly(["getprop", "ro.boot.flash.locked"]),
        "encryption_state": run_readonly(["getprop", "ro.crypto.state"]),
        "package_inventory": run_readonly(["cmd", "package", "list", "packages"]),
    }

    report = {
        "tool": "SHANU CYBER SHIELD V2 Android Checks",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "manual_checks_required": [
            "Google Play Store > Play Protect > Scan",
            "Android Settings > Accessibility > review enabled services",
            "Android Settings > Security/Privacy > Device admin apps",
            "Android Settings > Apps > review unfamiliar installed apps",
            "Android Settings > Network & Internet > VPN and Private DNS",
            "Android Settings > Security & privacy > Android security update",
        ],
        "limitations": [
            "Termux may be blocked from reading some Android system services.",
            "Missing values do not prove the device is compromised.",
            "This report is diagnostic, not a malware verdict.",
            "No settings are changed by this script.",
        ],
    }

    output_dir = Path(__file__).resolve().parents[1] / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_file = output_dir / f"android-check-{stamp}.json"
    output_file.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\n=== SHANU CYBER SHIELD V2 ===")
    print("ANDROID SECURITY DIAGNOSTICS\n")

    for name, result in checks.items():
        detail = result.get("detail", "")
        detail = " | ".join(detail.splitlines())
        print(f"{name}: {result['status']}")
        if detail:
            print(f"  {detail[:220]}")

    print("\nManual checks are still required in Android Settings.")
    print(f"JSON report saved: {output_file}")


if __name__ == "__main__":
    main()
