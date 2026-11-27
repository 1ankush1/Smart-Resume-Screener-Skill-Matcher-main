# Backend

The Flask API exposes a health check and a public resume analysis endpoint.
It parses PDF and DOCX files in memory and returns a skills comparison. It
does not provide account, sign-in, registration, or data-storage APIs.

Install dependencies from the project root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r frontend\src\backend\requirements.txt
```

Run the API:

```powershell
Set-Location frontend\src\backend
..\..\..\.venv\Scripts\python.exe app.py
```

The API listens at <http://localhost:5000>. Resume uploads are processed in
memory and discarded after the analysis response is created.
