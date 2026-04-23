@echo off
REM Wrapper to run deploy_to_freecad.ps1 without execution policy restrictions
powershell -ExecutionPolicy Bypass -File "%~dp0deploy_to_freecad.ps1"
pause
