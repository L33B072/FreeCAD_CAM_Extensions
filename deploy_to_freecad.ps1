# Deploy FreeCAD CAM Extensions to FreeCAD Mod Directory
# Run this script after making changes to update the active extension

$source = "c:\FreeCAD_CAM_Extensions"
$dest = "$env:APPDATA\FreeCAD\v1-1\Mod\FreeCAD_CAM_Extensions"

Write-Host "Deploying FreeCAD CAM Extensions..." -ForegroundColor Cyan
Write-Host "From: $source" -ForegroundColor Gray
Write-Host "To:   $dest" -ForegroundColor Gray
Write-Host ""

# Ensure destination directory exists
if (!(Test-Path $dest)) {
    New-Item -ItemType Directory -Path $dest -Force | Out-Null
    Write-Host "Created destination directory" -ForegroundColor Green
}

# Copy Python files
$pythonFiles = Get-ChildItem -Path $source -Filter "*.py" -File
foreach ($file in $pythonFiles) {
    Copy-Item -Path $file.FullName -Destination $dest -Force
    Write-Host "✓ Copied: $($file.Name)" -ForegroundColor Green
}

# Copy other important files (MD and XML)
$mdFiles = Get-ChildItem -Path $source -Filter "*.md" -File
foreach ($file in $mdFiles) {
    Copy-Item -Path $file.FullName -Destination $dest -Force
    Write-Host "✓ Copied: $($file.Name)" -ForegroundColor Green
}

$xmlFiles = Get-ChildItem -Path $source -Filter "*.xml" -File
foreach ($file in $xmlFiles) {
    Copy-Item -Path $file.FullName -Destination $dest -Force
    Write-Host "✓ Copied: $($file.Name)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Deployment complete! Restart FreeCAD to see changes." -ForegroundColor Cyan
Write-Host ""
