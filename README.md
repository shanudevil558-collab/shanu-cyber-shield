🛡️ SHANU CYBER SHIELD

DEFEND THE DEVICE. PROTECT THE DIGITAL WORLD.

Android Security • Cyber Defense • XOS Diagnostics • Smart File Scanning

SHANU CYBER SHIELD is a Python-based defensive security toolkit designed for Android and Termux. It brings together basic device-security checks, XOS diagnostics, suspicious-pattern file scanning, SHA-256 hashing, and security reports in one project.

The repository includes the original SHANU CYBER SHIELD tools and SHANU CYBER SHIELD V2, with a modular scanner, Android diagnostic scripts, automated tests, and a terminal dashboard.

⚡ Core Features

- 🛡️ Security Diagnostics — review available Android security indicators.
- 📱 XOS Companion — inspect supported Android and XOS settings.
- 🔎 Smart File Scanner — flag selected suspicious code patterns in supported files for manual review.
- 🔐 SHA-256 Hashing — calculate file hashes for integrity checks.
- 📊 Local Reports — save supported diagnostic results locally.
- 💻 V2 Terminal Dashboard — launch available modules through one menu.
- 🧪 Automated Tests — test key scanner functions.
- 📝 Incident Documentation — maintain security notes where supported by the relevant tool.

📂 Repository Structure

shanu-cyber-shield/
├── SHANU-CYBER-SHIELD-V2/
│   ├── android_checks/
│   │   ├── auto_check.py
│   │   └── device_check.py
│   ├── scanner/
│   │   ├── __init__.py
│   │   └── smart_scanner.py
│   ├── tests/
│   │   └── test_smart_scanner.py
│   ├── reports/
│   ├── main.py
│   ├── shanu_dashboard.py
│   ├── README.md
│   ├── LICENSE
│   └── .gitignore
├── shanu_cyber_shield_advanced.py
├── shanu_xos16_companion.py
├── LICENSE
├── .gitignore
└── README.md

📱 Requirements

- Android device or another compatible Python environment
- Termux recommended for Android
- Python 3
- Git for cloning the repository

🚀 Installation

Clone the repository:

git clone https://github.com/shanudevil558-collab/shanu-cyber-shield.git
cd shanu-cyber-shield

▶️ Run the Original Cyber Shield

python shanu_cyber_shield_advanced.py

📱 Run the XOS Companion

python shanu_xos16_companion.py

🛡️ Run SHANU CYBER SHIELD V2

Enter the V2 directory:

cd SHANU-CYBER-SHIELD-V2

Launch the dashboard:

python shanu_dashboard.py

Run the smart scanner:

python scanner/smart_scanner.py

Run automated tests:

python -m unittest discover -s tests -v

Follow each script's prompts and review its results manually.

🔐 Security & Privacy

- Use the toolkit only on devices and files you own or are authorized to assess.
- Review reports before sharing; they may contain device or file information.
- Never commit passwords, API keys, access tokens, private logs, or sensitive evidence.
- Keep generated reports local unless you have reviewed and intentionally approved their publication.
- Android and Termux restrictions may limit the diagnostic information available.

⚠️ Limitations

SHANU CYBER SHIELD is an educational defensive toolkit, not a certified antivirus, complete malware detector, or professional forensic platform.

Scanner matches are indicators for manual review, not proof of compromise. A clean scan does not guarantee that a file is safe. Features and device visibility depend on the scripts, Android version, and available permissions.

🤝 Responsible Use

Learn, audit, and protect responsibly. Do not use this toolkit to access devices, accounts, networks, or files without permission.

📄 License

This project is distributed under the MIT License. See "LICENSE" (LICENSE).

👨‍💻 Built By

SHANU AI LABS

GitHub: "@shanudevil558-collab" (https://github.com/shanudevil558-collab)

LEARN. AUDIT. PROTECT.

⚡ BUILD SMART. STAY SECURE. ⚡
