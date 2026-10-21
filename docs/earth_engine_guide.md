# Google Earth Engine Registration, Authentication & Troubleshooting Guide

This guide walks through registering for Google Earth Engine, linking a Google Cloud project, authenticating in Windows PowerShell, and resolving common operational errors.

---

## 1. Non-Commercial Academic Registration

Google Earth Engine requires registration under an eligible academic/research account for free educational access:

1. Visit the registration portal in your web browser:
   👉 **[https://code.earthengine.google.com/register](https://code.earthengine.google.com/register)**
2. Sign in with your institutional or personal Google account.
3. Select **Unpaid usage / Noncommercial** (e.g. *Academic Research / Education*).
4. Fill in your project description:
   - **Institution:** Your University / College
   - **Project Description:** *B.Tech Minor Project: Spatio-Temporal LULC Monitoring and Future Prediction for Azamgarh District, Uttar Pradesh, India.*
5. Accept the terms of service and submit. Approval is typically granted immediately or within a few hours.

---

## 2. Google Cloud Project & API Enablement

Earth Engine Python API (v1.x+) requires an associated Google Cloud project:

1. Open the **[Google Cloud Console](https://console.cloud.google.com/)**.
2. Create a new project or select an existing one:
   - Example Project Name: `azamgarh-lulc`
   - Note the **Project ID** (e.g., `azamgarh-lulc-412308`). *Note: Project ID is lowercase with hyphens, distinct from the display name.*
3. Enable the **Earth Engine API**:
   👉 **[https://console.cloud.google.com/apis/library/earthengine.googleapis.com](https://console.cloud.google.com/apis/library/earthengine.googleapis.com)**
   - Click **ENABLE** for your selected project.

---

## 3. Local Authentication via PowerShell

Once registered and your Cloud Project is configured:

1. Activate your virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
2. Run the official authentication command:
   ```powershell
   earthengine authenticate
   ```
3. A browser window will open automatically. Sign in with your registered Google account, review permissions, and grant access.
4. Your authentication token is securely stored in your local Windows user profile:
   `C:\Users\<YourUsername>\.config\earthengine\credentials`
   *(This file remains strictly on your local machine and is never committed to Git).*

---

## 4. Configuring `.env`

Copy `.env.example` to `.env` and set your Project ID:
```powershell
Copy-Item .env.example .env
notepad .env
```

Content:
```env
EE_PROJECT=your-actual-gcp-project-id
```

Test your connection:
```powershell
python -m src.data.gee_init
```
Expected output:
```
Checking Earth Engine environment...
  Local credentials found: True
  .env file present: True
  EE_PROJECT: your-actual-gcp-project-id

[SUCCESS] Successfully initialized Earth Engine with project: your-actual-gcp-project-id
earthengine-api version: 1.7.49
```

---

## 5. Running the Data-Availability Audit

To query live collection availability over Azamgarh District across 40 seasonal windows:
```powershell
python -m src.data.data_audit
```
Generated reports are stored in `data/outputs/audit/`:
- `boundary_report.csv`: GAUL boundary area vs official baseline
- `s2_year_season_audit.csv`: Sentinel-2 scene counts, clear observation fractions, and heuristic flags (GOOD, PARTIAL, POOR)
- `collection_ranges.csv`: First and last acquisition dates over Azamgarh
- `landsat_yearly.csv`: Landsat 7/8/9 cloud-screened scene counts
- `audit_summary.md`: Summary markdown table

---

## 6. Troubleshooting Common Errors

### Error A: `EE_PROJECT is not set`
- **Cause:** `.env` file does not exist or `EE_PROJECT` has placeholder text.
- **Fix:** Copy `.env.example` to `.env` and specify your exact Cloud Project ID.

### Error B: `Earth Engine API has not been used in project... or it is disabled`
- **Cause:** The Earth Engine API is not enabled on your Google Cloud Project.
- **Fix:** Go to [https://console.cloud.google.com/apis/library/earthengine.googleapis.com](https://console.cloud.google.com/apis/library/earthengine.googleapis.com), select your project ID, and click **ENABLE**.

### Error C: `Computation timed out` or `User memory limit exceeded`
- **Cause:** Requesting complex regional reductions at excessively fine spatial resolutions (e.g. 10 m over 4,000 km² simultaneously).
- **Fix:** In `config/settings.yaml`, raise `coverage_scale_m` (e.g., from 100 to 200) or adjust `tileScale` (e.g., 4 or 8) in reduction calls.

### Error D: `Not a registered Earth Engine user`
- **Cause:** Google account has not completed noncommercial registration.
- **Fix:** Visit [https://code.earthengine.google.com/register](https://code.earthengine.google.com/register) and register.
