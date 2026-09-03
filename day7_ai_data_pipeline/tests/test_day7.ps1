$ErrorActionPreference = "Stop"

Write-Host "======================================"
Write-Host "DAY 7 PIPELINE TEST"
Write-Host "======================================"

$requiredSchemas = @(
    "schemas\resume_schema.json",
    "schemas\candidate_profile_schema.json",
    "schemas\ats_score_schema.json",
    "schemas\screening_report_schema.json",
    "schemas\interview_result_schema.json"
)

$requiredExamples = @(
    "examples\resume_example.json",
    "examples\candidate_profile_example.json",
    "examples\ats_score_example.json",
    "examples\screening_report_example.json",
    "examples\interview_result_example.json",
    "examples\dataset_version_example.json",
    "examples\model_version_example.json"
)

$passed = 0
$total = 0

foreach ($file in $requiredSchemas) {

    $total++

    if (Test-Path $file) {

        Get-Content $file -Raw | ConvertFrom-Json | Out-Null

        Write-Host "[PASS] Schema: $file"

        $passed++
    }
    else {

        Write-Host "[FAIL] Schema: $file"
    }
}

foreach ($file in $requiredExamples) {

    $total++

    if (Test-Path $file) {

        Get-Content $file -Raw | ConvertFrom-Json | Out-Null

        Write-Host "[PASS] Example: $file"

        $passed++
    }
    else {

        Write-Host "[FAIL] Example: $file"
    }
}

Write-Host ""
Write-Host "======================================"
Write-Host "RESULT: $passed / $total PASSED"
Write-Host "======================================"

if ($passed -eq $total) {
    Write-Host "DAY 7 TEST STATUS: PASSED"
}
else {
    Write-Host "DAY 7 TEST STATUS: FAILED"
    exit 1
}
