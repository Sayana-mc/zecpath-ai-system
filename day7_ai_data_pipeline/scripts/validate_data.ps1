$ErrorActionPreference = "Stop"

Write-Host "========================================="
Write-Host "Zecpath Day 7 Data Validation"
Write-Host "========================================="

$schemaFiles = Get-ChildItem ".\schemas\*.json"

Write-Host ""
Write-Host "Validating schemas..."

foreach ($file in $schemaFiles) {
    try {
        $content = Get-Content $file.FullName -Raw | ConvertFrom-Json
        Write-Host "[PASS] $($file.Name)"
    }
    catch {
        Write-Host "[FAIL] $($file.Name)"
        throw
    }
}

$exampleFiles = Get-ChildItem ".\examples\*.json"

Write-Host ""
Write-Host "Validating example data..."

foreach ($file in $exampleFiles) {
    try {
        $content = Get-Content $file.FullName -Raw | ConvertFrom-Json
        Write-Host "[PASS] $($file.Name)"
    }
    catch {
        Write-Host "[FAIL] $($file.Name)"
        throw
    }
}

Write-Host ""
Write-Host "Checking required directories..."

$directories = @(
    "docs",
    "diagrams",
    "schemas",
    "examples",
    "storage",
    "storage\resumes",
    "storage\parsed_profiles",
    "storage\ats_scores",
    "storage\screening_reports",
    "storage\interview_results",
    "storage\datasets",
    "storage\datasets\training",
    "storage\datasets\validation",
    "storage\datasets\evaluation"
)

foreach ($directory in $directories) {
    if (Test-Path $directory) {
        Write-Host "[PASS] $directory"
    }
    else {
        Write-Host "[FAIL] $directory"
        throw "Missing directory: $directory"
    }
}

Write-Host ""
Write-Host "========================================="
Write-Host "ALL DAY 7 VALIDATIONS PASSED"
Write-Host "========================================="
