# Smart Resume Screener

Compare a PDF or DOCX resume with a job description. The app reports a keyword
match score, matched skills, missing skills, and basic education and experience
details. No account or credentials are needed. Uploaded resumes are processed
in memory and are not saved.

## Run locally

Requirements: Python 3.10 or later and Node.js with npm.

Open PowerShell in this folder. Install the dependencies once:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup.ps1
```

Start the local Flask API and Vite frontend:

```powershell
.\start-local.ps1
```

The app opens at <http://localhost:8080>. The Flask API health check is
<http://localhost:5000/api/health>. The launcher opens two PowerShell windows;
close both windows to stop the local servers.

To run the API and frontend separately, use two terminals:

```powershell
Set-Location frontend\src\backend
..\..\..\.venv\Scripts\python.exe app.py
```

```powershell
Set-Location frontend
npm.cmd run dev
```

## Build the frontend

```powershell
Set-Location frontend
npm.cmd run build
```

The match score is an informational keyword-overlap result, not a hiring
recommendation. Scanned PDFs without selectable text are not OCR-processed.
