# 🛡️ SHANU CYBER SHIELD V2

**A lightweight, defensive security toolkit for Android and Python.**

SHANU CYBER SHIELD V2 combines local file review, Android diagnostics,
SHA-256 hashing, basic automated tests, and JSON reporting in one
terminal-based dashboard.

## Features

- **Smart File Scanner** — flags selected code patterns for manual review.
- **Android Diagnostics** — reads security-related properties when Android permits.
- **SHA-256 Hashing** — calculates file hashes for integrity comparisons.
- **Automated Tests** — checks basic scanner functionality.
- **JSON Reports** — stores local diagnostic results.
- **Neon Terminal Dashboard** — simple menu-driven interface.

## Requirements

- Android with Termux, or another compatible Python environment
- Python 3.10 or later recommended
- No third-party Python packages required for the current toolkit

## Run

From this directory:

```bash
python shanu_dashboard.py
```

You can also run individual modules:

```bash
python scanner/smart_scanner.py
python android_checks/auto_check.py
python android_checks/device_check.py
python -m unittest discover -s tests -v
```

## Limitations

This project is a learning and defensive diagnostic tool, not a certified
antivirus or a complete malware detection system.

- Pattern matches can produce false positives.
- No findings do not prove that a file or device is safe.
- Android may block access to installed-app information and protected settings.
- Some device checks require manual verification in Android Settings.
- Network monitoring and comprehensive malware detection are not currently
  claimed as implemented features.

## Privacy

Reports may contain device information, file paths, hashes, or scan results.
Review generated reports before sharing or publishing them. Do not commit
private evidence, credentials, API keys, or personal information.

## Responsible Use

Use this toolkit only on your own device, files, or systems you are
authorized to assess.

## License

MIT License. See [LICENSE](LICENSE).
