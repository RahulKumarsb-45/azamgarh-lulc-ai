# Diagnostic and Troubleshooting Guide

This guide compiles common technical errors, operational pitfalls, and verified solutions across environment configuration, satellite data processing, and dashboard deployment.

---

## 1. PowerShell & Windows Environment Issues

### Issue 1.1: `cannot be loaded because running scripts is disabled on this system`
- **Cause:** Windows PowerShell security policy blocks execution of unsigned scripts by default.
- **Solution:** Run this command once in PowerShell:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
  ```

### Issue 1.2: `UnicodeEncodeError: 'charmap' codec can't encode character...`
- **Cause:** Standard Windows command prompt (cmd.exe or PowerShell) often defaults to legacy code page `cp1252`, which cannot render certain Greek or scientific Unicode symbols (e.g., $\kappa$).
- **Solution:** 
  1. We replaced Greek unicode symbols in console print statements with ASCII equivalents (`kappa`).
  2. Alternatively, force UTF-8 output encoding in PowerShell before running scripts:
     ```powershell
     $OutputEncoding = [System.Text.Encoding]::UTF8
     [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
     ```

---

## 2. Earth Engine API & Authentication Issues

### Issue 2.1: `EE_PROJECT is not set`
- **Cause:** `.env` file is missing or has not been configured.
- **Solution:**
  ```powershell
  Copy-Item .env.example .env
  notepad .env
  ```
  Ensure `EE_PROJECT=your-actual-gcp-project-id` is specified.

### Issue 2.2: `ee.ee_exception.EEException: Not a registered Earth Engine user`
- **Cause:** Your Google account has not completed non-commercial research/education registration.
- **Solution:** Visit [https://code.earthengine.google.com/register](https://code.earthengine.google.com/register) and register.

### Issue 2.3: `ee.ee_exception.EEException: Computation timed out`
- **Cause:** Executing spatial reductions over the entire 4,000+ sq km district at 10-meter resolution in interactive mode exceeds GEE's 5-minute synchronous limit.
- **Solution:**
  1. For audit and exploration, use `coverage_scale_m: 100` or `200` in `config/settings.yaml`.
  2. For final 10–20 m district classifications, use asynchronous batch exports:
     ```python
     task = ee.batch.Export.image.toDrive(...)
     task.start()
     ```

---

## 3. Streamlit Dashboard Issues

### Issue 3.1: Port 8501 Already in Use
- **Cause:** Another Streamlit session is currently running on the default port.
- **Solution:** Specify an alternative port:
  ```powershell
  streamlit run dashboard/app.py --server.port 8502
  ```

### Issue 3.2: `ModuleNotFoundError: No module named 'src'` when launching Streamlit
- **Cause:** Launching streamlit from inside the `dashboard/` subfolder rather than the project root.
- **Solution:** Always run from the project root:
  ```powershell
  cd C:\Users\kumar\Desktop\azamgarh-lulc
  .\.venv\Scripts\Activate.ps1
  streamlit run dashboard/app.py
  ```
