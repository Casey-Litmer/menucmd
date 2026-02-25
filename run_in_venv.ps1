# PowerShell wrapper to run the project's python from .venv if available.
param([Parameter(ValueFromRemainingArguments=$true)] $Args)

$repoDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPy = Join-Path $repoDir '.venv\Scripts\python.exe'

if (Test-Path $venvPy) {
  & $venvPy @Args
} else {
  if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error 'Python not found. Activate a virtualenv or install Python.'
    exit 1
  }
  python @Args
}
