#!/usr/bin/env python3
"""
SHANU CYBER SHIELD — Advanced Android Phone Security Auditor
Defensive, read-only checks for Termux. Standard library only.
Does not claim to detect all malware or inspect all app traffic.
"""
import os
import sys
import json
import hashlib
import shutil
import subprocess
import platform
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
BASE = HOME / "shanu-cyber-shield"
REPORTS = BASE / "reports"
EVIDENCE = BASE / "evidence"
REPORTS.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(parents=True, exist_ok=True)
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
REPORT_JSON = REPORTS / f"phone-audit-{STAMP}.json"
REPORT_TXT = REPORTS / f"phone-audit-{STAMP}.txt"
MAX_SCAN_FILES = 5000
MAX_SCAN_BYTES = 2 * 1024 * 1024

def now():
    return datetime.now(timezone.utc).isoformat()

def run(args, timeout=10):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        out = (p.stdout or "").strip()
        err = (p.stderr or "").strip()
        return {"ok": p.returncode == 0, "code": p.returncode,
                "output": out if out else err}
    except FileNotFoundError:
        return {"ok": False, "code": None, "output": "Command not available"}
    except subprocess.TimeoutExpired:
        return {"ok": False, "code": None, "output": "Timed out"}
    except Exception as e:
        return {"ok": False, "code": None, "output": f"{type(e).__name__}: {e}"}

def prop(name):
    r = run(["getprop", name], 4)
    return r["output"] if r["ok"] and r["output"] else "Unavailable"

def add(items, area, name, status, result, action):
    items.append({"area": area, "check": name, "status": status,
                  "result": str(result), "recommended_action": action})

def read_setting(namespace, key):
    r = run(["settings", "get", namespace, key], 4)
    return r["output"] if r["ok"] and r["output"] else "Unavailable"

def package_inventory():
    # Try third-party apps first, then all visible packages.
    r = run(["pm", "list", "packages", "-3"], 15)
    scope = "third-party apps"
    if not r["ok"] or not r["output"]:
        r = run(["pm", "list", "packages"], 15)
        scope = "visible packages"
    packages = sorted({line.split(":", 1)[-1].strip()
                       for line in r["output"].splitlines()
                       if line.startswith("package:")})
    return scope, packages, r

def check_system(items, device):
    model = prop("ro.product.model")
    android = prop("ro.build.version.release")
    patch = prop("ro.build.version.security_patch")
    bootstate = prop("ro.boot.verifiedbootstate")
    bootlocked = prop("ro.boot.flash.locked")
    crypto = prop("ro.crypto.state")
    device.update({
        "model": model, "manufacturer": prop("ro.product.manufacturer"),
        "android_version": android, "security_patch": patch,
        "build_fingerprint": prop("ro.build.fingerprint"),
        "verified_boot_state": bootstate, "bootloader_lock_indicator": bootlocked,
        "encryption_indicator": crypto, "architecture": platform.machine(),
        "python_version": platform.python_version()
    })
    add(items, "System", "Device model", "INFO", model,
        "Confirm the model matches your phone.")
    add(items, "System", "Android version", "INFO", android,
        "Install official Android/XOS updates when offered.")
    if patch != "Unavailable":
        try:
            d = datetime.strptime(patch, "%Y-%m-%d").date()
            age = (datetime.now().date() - d).days
            add(items, "System", "Security patch age",
                "WARNING" if age > 120 else "INFO",
                f"{patch}; approximately {age} days old",
                "Check Settings > About phone > Android version > Android security update. "
                "Patch age alone is not proof of compromise.")
        except ValueError:
            add(items, "System", "Security patch date", "INFO", patch,
                "Verify the displayed date in Android Settings.")
    else:
        add(items, "System", "Security patch date", "NOT CHECKABLE", patch,
            "Check the Android security update field in Settings.")
    for label, val, action in [
        ("Verified Boot indicator", bootstate,
         "Do not unlock the bootloader just to run this audit; verify official device status."),
        ("Bootloader lock indicator", bootlocked,
         "Confirm status using official device settings or manufacturer guidance."),
        ("Encryption indicator", crypto,
         "Check Android Security settings; this property may not fully describe file encryption.")
    ]:
        add(items, "System", label,
            "INFO" if val != "Unavailable" else "NOT CHECKABLE", val, action)
    add(items, "System", "Root command presence",
        "INFO", shutil.which("su") or "su not found in PATH",
        "This is not a root detector; absence of su does not prove the phone is unrooted.")
    add(items, "System", "ADB utility",
        "INFO", shutil.which("adb") or "adb not installed",
        "ADB is optional and is not required for normal phone use.")

def check_privacy_settings(items):
    checks = [
        ("Secure settings", "Accessibility services enabled",
         "secure", "enabled_accessibility_services",
         "Review Settings > Accessibility. Disable services you do not recognize; some legitimate tools use this."),
        ("Secure settings", "Notification listener access",
         "secure", "enabled_notification_listeners",
         "Review special app access for notification access and revoke anything unfamiliar."),
        ("Secure settings", "Enabled input methods",
         "secure", "enabled_input_methods",
         "Review installed keyboards and use only trusted keyboards."),
        ("Secure settings", "Default input method",
         "secure", "default_input_method",
         "Confirm your default keyboard is the one you intentionally use."),
        ("Secure settings", "Device provisioned state",
         "secure", "device_provisioned",
         "Informational system setting; do not change it manually."),
        ("Global settings", "Private DNS mode",
         "global", "private_dns_mode",
         "Review Settings > Network & Internet > Private DNS. Use a provider you trust."),
        ("Global settings", "Private DNS provider",
         "global", "private_dns_specifier",
         "If a hostname is set, confirm you recognize and trust the provider."),
        ("Global settings", "Always-on VPN app",
         "global", "always_on_vpn_app",
         "Review VPN settings and confirm any configured VPN is intentional."),
        ("Global settings", "VPN lockdown",
         "global", "always_on_vpn_lockdown",
         "This is informational; review VPN settings rather than changing it blindly.")
    ]
    for area, name, ns, key, action in checks:
        value = read_setting(ns, key)
        status = "INFO" if value != "Unavailable" else "NOT CHECKABLE"
        add(items, area, name, status, value, action)

    # Device-admin output may be restricted or contain OEM-specific text.
    r = run(["dumpsys", "device_policy"], 10)
    if r["ok"] and r["output"]:
        out = r["output"]
        # Avoid dumping the entire potentially lengthy service output into report.
        lines = [x.strip() for x in out.splitlines()
                 if any(k in x.lower() for k in
                        ("admin", "owner", "device owner", "profile owner", "enabled"))]
        summary = "\n".join(lines[:35]) if lines else "Service responded; no simple summary extracted"
        add(items, "Special access", "Device policy/admin indicators",
            "INFO", summary, "Review Settings > Security > Device admin apps. Keep only expected admins.")
    else:
        add(items, "Special access", "Device policy/admin indicators",
            "NOT CHECKABLE", r["output"],
            "Review Settings > Security > Device admin apps manually.")

    r = run(["dumpsys", "accessibility"], 10)
    if r["ok"] and r["output"]:
        lines = [x.strip() for x in r["output"].splitlines()
                 if any(k in x.lower() for k in
                        ("enabled services", "bound services", "servicecomponent", "enabled=true"))]
        summary = "\n".join(lines[:30]) if lines else "Service responded; summary unavailable"
        add(items, "Special access", "Accessibility service indicators",
            "INFO", summary, "Compare with Settings > Accessibility and disable unrecognized services.")
    else:
        add(items, "Special access", "Accessibility service indicators",
            "NOT CHECKABLE", r["output"],
            "Open Settings > Accessibility and review installed/enabled services.")

def check_apps(items, data):
    scope, packages, r = package_inventory()
    data["package_inventory_scope"] = scope
    data["visible_packages"] = packages
    add(items, "Apps", "Installed package inventory",
        "INFO" if r["ok"] and packages else "NOT CHECKABLE",
        f"{len(packages)} package names returned ({scope})" if packages else r["output"],
        "Use Settings > Apps to inspect unfamiliar apps. Package names alone cannot prove an app is malicious.")
    if packages:
        # Heuristic only: name fragments that deserve manual review, not a malware verdict.
        terms = ("spy", "stalker", "keylog", "stealer", "rattool", "hiddenrecorder")
        flagged = [p for p in packages if any(t in p.lower() for t in terms)]
        add(items, "Apps", "Suspicious-name heuristic",
            "WARNING" if flagged else "INFO",
            ", ".join(flagged) if flagged else "No package names matched simple keyword heuristics",
            "Manually verify each result. Names can be misleading and legitimate apps can use unusual names.")
    else:
        add(items, "Apps", "Suspicious-name heuristic", "NOT CHECKABLE",
            "No package inventory available",
            "Review apps manually in Android Settings.")

def scan_files(items, data):
    print("\nFile scan checks names and selected text indicators only.")
    print("It does not execute files, delete files, or prove malware infection.")
    raw = input("Folder to scan (Enter for ~/Download): ").strip()
    target = Path(raw).expanduser() if raw else HOME / "storage" / "shared" / "Download"
    if not target.exists() or not target.is_dir():
        add(items, "Files", "Suspicious-file scan", "NOT CHECKABLE",
            f"Folder unavailable: {target}",
            "Check the folder path. For shared storage, run termux-setup-storage if you choose to grant access.")
        print("Folder not found or not a directory.")
        return
    suspicious_names = (".apk", ".xapk", ".dex", ".jar", ".sh", ".py", ".js")
    text_ext = {".py", ".sh", ".js", ".html", ".txt", ".json", ".xml", ".php"}
    markers = ("eval(", "exec(", "base64 -d", "subprocess", "chmod 777",
               "curl ", "wget ", "Runtime.getRuntime", "AccessibilityService")
    found = []
    scanned = 0
    errors = 0
    try:
        for root, dirs, files in os.walk(target):
            dirs[:] = [d for d in dirs if d not in {".git", "node_modules", ".cache"}]
            for fn in files:
                if scanned >= MAX_SCAN_FILES:
                    break
                p = Path(root) / fn
                scanned += 1
                try:
                    if p.is_symlink():
                        continue
                    if p.suffix.lower() in suspicious_names:
                        found.append({"path": str(p), "reason": "File type for manual review"})
                    if p.suffix.lower() in text_ext and p.stat().st_size <= MAX_SCAN_BYTES:
                        content = p.read_text(errors="ignore")
                        hits = [m for m in markers if m.lower() in content.lower()]
                        if hits:
                            found.append({"path": str(p), "reason": "Text indicators: " + ", ".join(hits)})
                except (OSError, PermissionError):
                    errors += 1
            if scanned >= MAX_SCAN_FILES:
                break
    except Exception as e:
        errors += 1
    data["file_scan"] = {"folder": str(target), "files_examined": scanned,
                         "errors": errors, "findings": found[:200]}
    add(items, "Files", "Suspicious-file heuristic",
        "WARNING" if found else "INFO",
        f"{len(found)} review indicator(s); examined {scanned} file(s); errors {errors}",
        "Open each listed file safely and verify its origin. These are heuristics, not malware detections.")
    print(f"Examined {scanned} files; {len(found)} review indicator(s); {errors} read errors.")
    for entry in found[:30]:
        print(f"- {entry['path']}: {entry['reason']}")
    if len(found) > 30:
        print(f"... plus {len(found)-30} more; see report.")

def hash_evidence():
    raw = input("Exact file path to hash: ").strip()
    if not raw:
        print("Cancelled.")
        return
    path = Path(raw).expanduser()
    if not path.is_file():
        print("File not found or not a regular file.")
        return
    try:
        h = hashlib.sha256()
        size = 0
        with path.open("rb") as f:
            for block in iter(lambda: f.read(1024 * 1024), b""):
                h.update(block)
                size += len(block)
        entry = {"recorded_utc": now(), "path": str(path.resolve()),
                 "size_bytes": size, "sha256": h.hexdigest(),
                 "note": "Hash confirms later file equality only; it does not prove who created the file or that it is malicious."}
        log = EVIDENCE / "evidence-hashes.jsonl"
        with log.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        print(json.dumps(entry, indent=2))
        print("Saved to:", log)
    except OSError as e:
        print("Could not hash file:", e)

def add_incident_note():
    note = input("Incident note (date, what you noticed, affected account/device; no passwords/codes): ").strip()
    if not note:
        print("Cancelled.")
        return
    log = EVIDENCE / "incident-timeline.jsonl"
    entry = {"recorded_utc": now(), "note": note}
    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("Incident note saved to:", log)

def manual_checklist():
    checklist = [
        ("Install official system updates", "Settings > System update"),
        ("Run Play Protect scan", "Google Play Store > profile icon > Play Protect > Scan"),
        ("Review installed apps", "Settings > Apps; uninstall only apps you recognize as unwanted"),
        ("Review Accessibility services", "Settings > Accessibility > downloaded/installed services"),
        ("Review device admin apps", "Settings > Security > Device admin apps"),
        ("Review VPN and Private DNS", "Settings > Network & Internet > VPN / Private DNS"),
        ("Review app permissions", "Settings > Privacy > Permission manager"),
        ("Review install unknown apps", "Settings > Apps > Special app access > Install unknown apps"),
        ("Review notification access", "Settings > Special app access > Notification access"),
        ("Set strong screen lock", "Settings > Security / Screen lock"),
        ("Review Google account devices", "Google Account > Security > Your devices"),
        ("Enable 2-Step Verification", "Google Account > Security > 2-Step Verification"),
        ("Secure email and recovery options", "Use official account security pages; never share one-time codes"),
        ("Back up important files", "Use a trusted backup destination and test recovery")
    ]
    print("\nMANUAL SECURITY CHECKLIST")
    for i, (task, where) in enumerate(checklist, 1):
        print(f"{i:2}. [ ] {task}\n    {where}")

def build_report():
    items = []
    device = {}
    data = {"tool": "SHANU CYBER SHIELD Advanced Phone Security Auditor",
            "created_utc": now(), "platform": platform.platform(),
            "device": device, "checks": items,
            "limitations": [
                "Non-root, best-effort checks; Android/OEM may restrict commands.",
                "This tool does not scan every app's network traffic.",
                "No heuristic can prove malware or spyware by itself.",
                "Account compromise must be reviewed through official account security pages.",
                "No settings, accounts, apps, or files were changed by the audit."
            ]}
    check_system(items, device)
    check_privacy_settings(items)
    check_apps(items, data)
    print("\nRun selected-folder scan now? (y/N)")
    if input("> ").strip().lower() == "y":
        scan_files(items, data)
    REPORT_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        data["tool"], "=" * 64, "Created UTC: " + data["created_utc"],
        "Device: " + device.get("model", "Unknown"),
        "Android: " + device.get("android_version", "Unknown"),
        "Security patch: " + device.get("security_patch", "Unknown"), ""
    ]
    for item in items:
        lines.extend([f"[{item['status']}] {item['area']} — {item['check']}",
                      "Result: " + item["result"],
                      "Recommended action: " + item["recommended_action"], ""])
    lines.extend(["LIMITATIONS"] + ["- " + x for x in data["limitations"]])
    REPORT_TXT.write_text("\n".join(lines), encoding="utf-8")
    print("\nAudit complete.")
    print("Text report:", REPORT_TXT)
    print("JSON report:", REPORT_JSON)
    print(f"Checks recorded: {len(items)}")
    print("WARNING: INFO is not a guarantee of safety; NOT CHECKABLE means manual verification is needed.")

def main():
    while True:
        print("\n" + "=" * 50)
        print(" SHANU CYBER SHIELD — ADVANCED PHONE AUDITOR")
        print("=" * 50)
        print("1. Run full phone security audit + report")
        print("2. Scan a selected folder for suspicious indicators")
        print("3. Hash an evidence file (SHA-256)")
        print("4. Add incident timeline note")
        print("5. Show manual phone-security checklist")
        print("6. Open report folder")
        print("0. Exit")
        choice = input("Select: ").strip()
        if choice == "1":
            build_report()
        elif choice == "2":
            items, data = [], {}
            scan_files(items, data)
            p = REPORTS / f"file-scan-{STAMP}.json"
            p.write_text(json.dumps({"created_utc": now(), "checks": items, **data},
                                    indent=2, ensure_ascii=False), encoding="utf-8")
            print("File-scan report:", p)
        elif choice == "3":
            hash_evidence()
        elif choice == "4":
            add_incident_note()
        elif choice == "5":
            manual_checklist()
        elif choice == "6":
            print("Reports:", REPORTS)
            print("Evidence:", EVIDENCE)
            print("Latest report files:")
            for p in sorted(REPORTS.glob("*"))[-10:]:
                print("-", p.name)
        elif choice == "0":
            print("Exiting. No device settings were changed.")
            break
        else:
            print("Choose one of the listed options.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped safely.")
