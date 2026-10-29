#!/usr/bin/env python3
"""
SHANU CYBER SHIELD — XOS 16 Companion
Phone-first Termux companion for:
- XOS/Android feature discovery and safe Settings shortcuts (manual)
- Defensive security checklist and report
- Best-effort diagnostics that work without root
No hidden codes are executed, no settings are changed automatically.
"""
import json
import os
import platform
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
BASE = HOME / "shanu-cyber-shield"
REPORT_DIR = BASE / "reports"
REPORT_DIR.mkdir(parents=True, exist_ok=True)

def utc():
    return datetime.now(timezone.utc).isoformat()

def run(args, timeout=8):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        out = (p.stdout or "").strip()
        err = (p.stderr or "").strip()
        return out or err or f"exit code {p.returncode}"
    except FileNotFoundError:
        return "Command unavailable"
    except subprocess.TimeoutExpired:
        return "Command timed out"
    except Exception as e:
        return f"Unavailable: {type(e).__name__}: {e}"

def prop(key):
    value = run(["getprop", key], 4)
    return value if value and not value.startswith(("Command unavailable", "Unavailable:", "exit code")) else "Unavailable"

def pause():
    input("\nEnter dabao menu par wapas jane ke liye...")

def header():
    print("\n" + "=" * 58)
    print(" SHANU CYBER SHIELD — XOS 16 COMPANION")
    print("=" * 58)

def device_diagnostics():
    rows = {
        "Manufacturer": prop("ro.product.manufacturer"),
        "Model": prop("ro.product.model"),
        "Device codename": prop("ro.product.device"),
        "Android version": prop("ro.build.version.release"),
        "Android SDK": prop("ro.build.version.sdk"),
        "XOS/build fingerprint": prop("ro.build.display.id"),
        "Security patch": prop("ro.build.version.security_patch"),
        "Verified Boot indicator": prop("ro.boot.verifiedbootstate"),
        "Bootloader lock indicator": prop("ro.boot.flash.locked"),
        "Encryption indicator": prop("ro.crypto.state"),
        "CPU architecture": platform.machine(),
        "Python": platform.python_version(),
        "Termux user": run(["id"], 3),
        "Disk usage for Termux home": shutil.disk_usage(HOME)._asdict().__str__(),
        "Battery status (if Android dumpsys is accessible)": run(["dumpsys", "battery"], 4),
        "Network interfaces (best effort)": run(["ip", "-brief", "address"], 4),
        "DNS resolver (best effort)": run(["getprop", "net.dns1"], 4),
        "ADB executable": shutil.which("adb") or "Not installed",
        "Root command in PATH": shutil.which("su") or "Not found in PATH (not proof of no root)"
    }
    print("\n=== DEVICE DIAGNOSTICS ===")
    for k, v in rows.items():
        print(f"\n{k}:\n  {v}")
    save_report("diagnostics", {"created_utc": utc(), "type": "device diagnostics", "results": rows})
    print("\nDiagnostics report reports/ mein save kar di gayi.")
    pause()

def save_report(kind, payload):
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = REPORT_DIR / f"xos-companion-{kind}-{stamp}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path

def feature_guide():
    items = [
        ("Game Mode / Game Assistant", "Settings mein 'Game Mode', 'XArena' ya 'Game Assistant' search karo. Availability XOS build par depend karti hai."),
        ("Battery usage by app", "Settings > Battery; background battery use aur unfamiliar apps review karo."),
        ("App permissions", "Settings > Privacy / Permission manager; Camera, Microphone, Location, SMS aur Contacts review karo."),
        ("Special app access", "Settings mein 'Display over other apps', 'Install unknown apps', 'Notification access' aur 'Usage access' search karo."),
        ("Accessibility services", "Settings > Accessibility; sirf woh services enabled rakho jinhein tum pehchante ho aur use karte ho."),
        ("Device admin apps", "Settings mein 'Device admin apps' ya 'Device administrators' search karo."),
        ("Private DNS and VPN", "Settings > Network/Internet; VPN aur Private DNS provider ko verify karo."),
        ("Find My Device", "Settings > Google > Find My Device; availability/account options verify karo."),
        ("App pinning", "Settings > Security / Privacy mein 'App pinning' search karo; agar available ho to enable karne se pehle instructions parho."),
        ("Emergency / SOS options", "Settings mein 'Emergency SOS' search karo; available options aur emergency contacts review karo."),
        ("System updates", "Settings > System update; sirf official OTA updates install karo."),
        ("Play Protect", "Play Store > profile icon > Play Protect > Scan.")
    ]
    print("\n=== XOS / ANDROID FEATURE DISCOVERY ===")
    print("Ye safe discovery guide hai, guaranteed hidden-code list nahi. Menu names region/build ke mutabiq badal sakte hain.")
    for i, (name, desc) in enumerate(items, 1):
        print(f"\n{i}. {name}\n   {desc}")
    save_report("feature-guide", {"created_utc": utc(), "features": [{"name": n, "how_to_check": d} for n, d in items]})
    pause()

def security_review():
    checklist = [
        ("Screen lock", "Strong PIN/password; lock-screen notification privacy."),
        ("System patch", "Settings mein Android security patch aur official updates check karo."),
        ("Play Protect", "Play Store se scan chalao."),
        ("Unknown apps", "Settings > Apps mein unfamiliar apps ko verify karo; sirf yaqeen hone par uninstall karo."),
        ("Accessibility", "Unfamiliar enabled services ko investigate karo."),
        ("Device admin", "Unfamiliar device-admin entries verify karo."),
        ("Install unknown apps", "Jin apps ko APK install karne ki zaroorat nahi, unka permission off rakho."),
        ("Notification/usage access", "Special app access mein unfamiliar entries review karo."),
        ("VPN/Private DNS", "Unknown provider/profile ko verify karo."),
        ("Google account sessions", "Google Account > Security > Your devices mein unknown sessions review/sign out karo."),
        ("2-step verification", "Google Account security mein enable karo; one-time codes kisi ko na do."),
        ("Backups", "Important files ka trusted backup rakho aur restore method test karo.")
    ]
    print("\n=== DEFENSIVE SECURITY REVIEW ===")
    for i, (name, desc) in enumerate(checklist, 1):
        print(f"{i:2}. [ ] {name}: {desc}")
    path = save_report("security-checklist", {
        "created_utc": utc(),
        "note": "Checklist is a guide; it does not mean checks have passed.",
        "items": [{"item": n, "action": d, "status": "NOT YET VERIFIED"} for n, d in checklist]
    })
    print("\nChecklist report save hui:", path)
    pause()

def network_diagnostics():
    print("\n=== NETWORK DIAGNOSTICS (BEST EFFORT) ===")
    checks = {
        "Wi-Fi/IP interfaces": run(["ip", "-brief", "address"], 4),
        "Routes": run(["ip", "route"], 4),
        "DNS property 1": prop("net.dns1"),
        "DNS property 2": prop("net.dns2"),
        "Wi-Fi state (may be restricted)": run(["cmd", "wifi", "status"], 4),
        "HTTPS reachability (if curl installed)": run(["curl", "-I", "--max-time", "5", "https://www.google.com"], 7) if shutil.which("curl") else "curl not installed; skipped"
    }
    for k, v in checks.items():
        print(f"\n{k}:\n{v}")
    path = save_report("network", {"created_utc": utc(), "results": checks})
    print("\nReport save hui:", path)
    print("Network results se har app ka traffic ya phone compromise prove nahi hota.")
    pause()

def safe_notes():
    print("""
=== SAFE USE NOTES ===
- Ye tool diagnostic companion hai, antivirus/root scanner nahi.
- Android 16/XOS restricted commands ko block kar sakta hai; 'Unavailable' ka matlab hacked phone nahi.
- Koi hidden dialer code, bootloader command, root exploit ya secret setting automatically execute nahi hoti.
- Unknown app ko sirf naam se malware na samjho.
- Agar real account compromise ka shak ho: trusted device se password change, active sessions revoke,
  2-step verification enable, aur recovery email/phone check karo.
- Incident evidence ke original files ko edit/delete na karo; copy par kaam karo.
""")
    pause()

def main():
    while True:
        header()
        print("1. XOS / Android feature discovery guide")
        print("2. Device diagnostics + JSON report")
        print("3. Defensive security review checklist")
        print("4. Network diagnostics")
        print("5. Safe use and incident-response notes")
        print("0. Exit")
        choice = input("\nSelect: ").strip()
        if choice == "1":
            feature_guide()
        elif choice == "2":
            device_diagnostics()
        elif choice == "3":
            security_review()
        elif choice == "4":
            network_diagnostics()
        elif choice == "5":
            safe_notes()
        elif choice == "0":
            print("Exiting. This companion did not change device settings.")
            break
        else:
            print("Valid option select karo.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopped safely.")
