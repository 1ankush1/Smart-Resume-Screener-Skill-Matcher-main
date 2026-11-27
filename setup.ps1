# Purpose: Prepares the local development environment by installing backend and frontend dependencies.
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $projectRoot "frontend\src\backend"
$frontend = Join-Path $projectRoot "frontend"
$python = Get-Command python -ErrorAction SilentlyContinue
$npm = Get-Command npm -ErrorAction SilentlyContinue

if (-not $python) {
    throw "Python 3.10 or later is required. Install Python and enable 'Add Python to PATH'."
}
if (-not $npm) {
    throw "Node.js and npm are required. Install the current Node.js LTS release."
}

$venvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    & $python.Source -m venv (Join-Path $projectRoot ".venv")
    if ($LASTEXITCODE -ne 0) { throw "Could not create the Python virtual environment." }
}

& $venvPython -m pip install -r (Join-Path $backend "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "Backend dependencies could not be installed." }

Push-Location $frontend
try {
    & $npm.Source install
    if ($LASTEXITCODE -ne 0) { throw "Frontend dependencies could not be installed." }
}
finally {
    Pop-Location
}

Write-Output "Setup complete. Run .\start-local.ps1 to launch the app."
