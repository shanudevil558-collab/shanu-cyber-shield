#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

MENU = """
╔══════════════════════════════════════╗
║      SHANU CYBER SHIELD V2           ║
║      DEFENSIVE SECURITY TOOLKIT      ║
╚══════════════════════════════════════╝

  1. Smart File Scanner
  2. Automatic Android Checks
  3. Run Automated Tests
  4. Open Reports Folder
  5. Show Project Status
  0. Exit
"""

def run_script(relative_path):
    script = BASE / relative_path

    if not script.is_file():
        print(f"\nModule missing: {relative_path}")
        input("Enter dabao...")
        return

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(BASE)
    )

    if result.returncode != 0:
        print(f"\nModule exited with code {result.returncode}")

    input("\nEnter dabao menu par wapas jane ke liye...")

def open_reports():
    folder = BASE / "reports"
    folder.mkdir(parents=True, exist_ok=True)
    print(f"\nReports folder:\n{folder}")
    print("\nReport files:")
    files = list(folder.iterdir())
    if not files:
        print("Abhi koi report nahi.")
    else:
        for item in sorted(files, key=lambda p: p.name):
            print(f" - {item.name}")
    input("\nEnter dabao...")

def project_status():
    checks = {
        "Smart Scanner": BASE / "scanner" / "smart_scanner.py",
        "Android Auto Check": BASE / "android_checks" / "auto_check.py",
        "Android Diagnostics": BASE / "android_checks" / "device_check.py",
        "Automated Tests": BASE / "tests" / "test_smart_scanner.py",
    }

    print("\n=== PROJECT STATUS ===")
    for name, path in checks.items():
        status = "READY" if path.is_file() else "MISSING"
        print(f"[{status}] {name}")

    input("\nEnter dabao...")

def main():
    while True:
        print(MENU)
        choice = input("Select option: ").strip()

        if choice == "1":
            run_script("scanner/smart_scanner.py")
        elif choice == "2":
            run_script("android_checks/auto_check.py")
        elif choice == "3":
            run_script("tests/test_smart_scanner.py")
        elif choice == "4":
            open_reports()
        elif choice == "5":
            project_status()
        elif choice == "0":
            print("SHANU CYBER SHIELD V2 closed.")
            break
        else:
            print("Invalid option.")
            input("Enter dabao...")

if __name__ == "__main__":
    main()
