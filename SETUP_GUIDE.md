# Setup Guide

This guide explains how to install and run the Driveflow Bot locally on Windows.

## 1. Prerequisites

Before you start, make sure you have:
- Python 3.10 or newer
- Google Chrome or Microsoft Edge installed
- Internet access
- A GOV.UK account for the driving test booking service

## 2. Clone or open the project

If you are using the GitHub repository:

```bash
git clone https://github.com/imtiyazmygit/driveflow-bot.git
cd driveflow-bot
```

If you already have the folder open in VS Code, continue from there.

## 3. Create a Python virtual environment

Open PowerShell in the project folder and run:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks the script, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 4. Install dependencies

Run:

```powershell
pip install -r requirements.txt
```

## 5. Install Playwright browser support

Run:

```powershell
python -m playwright install chromium
```

## 6. Configure credentials

Create or update the file `config.yaml` in the project root with your GOV.UK login details:

```yaml
credentials:
  user_id: "YOUR_GOVUK_USERNAME"
  password: "YOUR_GOVUK_PASSWORD"
```

You can also use environment variables instead:

```powershell
$env:DVSA_USERNAME="YOUR_GOVUK_USERNAME"
$env:DVSA_PASSWORD="YOUR_GOVUK_PASSWORD"
```

## 7. Set preferred test centres

Edit `centres.yaml` to choose the centres you want the bot to search:

```yaml
centres:
  - Southall (London)
  - Watford
  - Sidcup (London)
```

## 8. Run the bot

Start the automation with:

```powershell
python main.py
```

The bot will:
- open the browser,
- sign in to the booking system,
- fill the initial booking form,
- search for available slots,
- and notify you if configured.

## 9. Troubleshooting

### Chrome or Edge not found
If the browser is not detected, update the paths in `src/auth.py`.

### Playwright errors
Reinstall browser support:

```powershell
python -m playwright install --force chromium
```

### Missing credentials
Make sure `config.yaml` exists and contains valid values.

### Script fails to start
Check that the virtual environment is activated and all packages were installed successfully.

## 10. Security note

Do not share your login credentials or commit sensitive information to GitHub. The project is configured to ignore `config.yaml` and environment secrets.
