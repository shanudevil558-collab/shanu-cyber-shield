#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
from pathlib import Path

BASE = Path(__file__).resolve().parent
REPORTS = BASE / "reports"

R = "\033[0m"
C = "\033[96m"
G = "\033[92m"
Y = "\033[93m"
P = "\033[95m"
W = "\033[97m"
D = "\033[90m"

def clear():
    os.system("clear")

def header():
    print(C + "╔══════════════════════════════════════════════╗")
    print("║" + G + "        SHANU CYBER SHIELD V2                 " + C + "║")
    print("║" + W + "          ALL-IN-ONE SECURITY                 " + C + "║")
    print("╚══════════════════════════════════════════════╝" + R)
    print(D + "       SECURE  •  DETECT  •  VERIFY  •  PROTECT" + R)
    print(f"\n{D} Android | {platform.machine()} | Python {platform.python_version()}{R}")
    print(C + "────────────────────────────────────────────────" + R)

def run_file(relative_path):
    path = BASE / relative_path
    if not path.is_file():
        print(f"\n{Y}Module missing: {relative_path}{R}")
        return

    subprocess.run([sys.executable, str(path)], cwd=str(BASE))

def tests():
    path = BASE / "tests" / "test_smart_scanner.py"
    if not path.is_file():
        print("Test file missing.")
        return
    subprocess.run([
        sys.executable, "-m", "unittest", "discover",
        "-s", str(BASE / "tests"), "-v"
    ], cwd=str(BASE))

def reports():
    REPORTS.mkdir(parents=True, exist_ok=True)
    files = sorted(REPORTS.iterdir())
    print(f"\nReports folder: {REPORTS}")
    if not files:
        print("No reports created yet.")
    for f in files:
        print(" •", f.name)

def status():
    modules = {
        "Smart Scanner": "scanner/smart_scanner.py",
        "Android Auto Check": "android_checks/auto_check.py",
        "Android Diagnostics": "android_checks/device_check.py",
        "Automated Tests": "tests/test_smart_scanner.py",
        "Main Launcher": "main.py",
    }
    print("\nMODULE STATUS")
    for name, rel in modules.items():
        exists = (BASE / rel).is_file()
        print(f" {G}[READY]{R if exists else Y + '[MISSING]' + R} {name}")

def main():
    actions = {
        "1": lambda: run_file("scanner/smart_scanner.py"),
        "2": lambda: run_file("android_checks/auto_check.py"),
        "3": lambda: run_file("android_checks/device_check.py"),
        "4": tests,
        "5": reports,
        "6": status,
    }

    while True:
        clear()
        header()
        print(f"\n{W}  [1] {G}SMART FILE SCANNER{R}")
        print(f"  {D}Scan selected folder for review indicators{R}")
        print(f"\n{W}  [2] {C}ANDROID AUTO CHECK{R}")
        print(f"  {D}Read available Android security information{R}")
        print(f"\n{W}  [3] {P}ANDROID DIAGNOSTICS{R}")
        print(f"  {D}Generate detailed device diagnostics{R}")
        print(f"\n{W}  [4] {Y}RUN AUTOMATED TESTS{R}")
        print(f"  {D}Check basic scanner functions{R}")
        print(f"\n{W}  [5] {C}REPORTS MANAGER{R}")
        print(f"  {D}List generated reports{R}")
        print(f"\n{W}  [6] {G}MODULE STATUS{R}")
        print(f"  {D}Check which project files exist{R}")
        print(f"\n{W}  [0] {Y}EXIT{R}")
        print(C + "\n────────────────────────────────────────────────" + R)

        choice = input(f"\n{G}  shanu@shield {C}➜ {R}").strip()
        if choice == "0":
            print(f"\n{G}Shield closed. Stay secure!{R}")
            break

        action = actions.get(choice)
        if action:
            clear()
            header()
            try:
                action()
            except (OSError, ValueError) as exc:
                print(f"\n{Y}Operation error: {exc}{R}")
        else:
            print(f"{Y}Invalid option.{R}")

        input(f"\n{D}Enter dabao menu par wapas jane ke liye...{R}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDashboard closed.")
