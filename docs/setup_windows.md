# Windows PowerShell Setup & Environment Guide

This guide provides step-by-step instructions to set up the **Azamgarh LULC Classification and Future Prediction System** on Windows using PowerShell.

---

## 1. Prerequisites

- **Operating System:** Windows 10 / Windows 11 (64-bit)
- **PowerShell:** Version 5.1 or PowerShell 7+
- **Python:** Python 3.11 or Python 3.12 (Python 3.12.7 is pre-configured in this repository)
- **Git:** Git for Windows

Verify your Python installation:
```powershell
python --version
```
Expected output: `Python 3.12.x` (or `3.11.x`).

---

## 2. Setting PowerShell Execution Policy

If script execution is blocked on your system, allow signed local scripts in the current user scope:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

---

## 3. Virtual Environment Setup

Navigate to your project root:
```powershell
cd C:\Users\kumar\Desktop\azamgarh-lulc
```

Create and activate a dedicated virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(Your prompt will now display `(.venv)`).*

---

## 4. Upgrading Pip & Installing Dependencies

Upgrade pip to ensure reliable wheel checksum handling:
```powershell
python -m pip install --upgrade pip
```

Install the pinned, reproducible production dependencies:
```powershell
pip install -r requirements.txt
```

Alternatively, to reproduce the exact environment lock:
```powershell
pip install -r requirements.lock.txt
```

---

## 5. Environment Configuration (.env)

The repository uses an environment file to securely read your Google Cloud Project ID without hardcoding credentials in Git:

```powershell
Copy-Item .env.example .env
```

Open `.env` in Notepad or your preferred code editor:
```powershell
notepad .env
```

Set your Google Cloud Project ID:
```env
# Copy to .env (never commit .env). Put YOUR Google Cloud project ID here.
EE_PROJECT=your-gcp-project-id
```

> **Security Rule:** Never commit `.env` or any `.json` service account keys to version control. The `.gitignore` file is already configured to block these files.

---

## 6. Verifying the Setup

Verify that all scientific and geospatial libraries import correctly:
```powershell
python -c "import ee, pandas, geopandas, rasterio, sklearn, streamlit, plotly, folium, matplotlib; print('All libraries verified successfully!')"
```

Check the Earth Engine environment configuration:
```powershell
python -m src.data.gee_init
```
If `.env` is set and you have authenticated, this will output `[SUCCESS] Successfully initialized Earth Engine`.
