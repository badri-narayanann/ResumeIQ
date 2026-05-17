# Run the ResumeIQ test suite from the repository root
$projectRoot = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
Set-Location $projectRoot
python -m pytest -q
