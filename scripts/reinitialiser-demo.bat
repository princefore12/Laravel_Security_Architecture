@echo off
title Reinitialisation Demo - Portail UT LOKO
echo ============================================================================
echo   REINITIALISATION PROPRE DE LA DEMO (Base MariaDB + .env vulnerable)
echo ============================================================================
echo.

cd /d "%~dp0\..\laravel-security-lab"

powershell -Command "$p = (Resolve-Path '.env').Path; $t = [System.IO.File]::ReadAllText($p) -replace '(?m)^SECURITY_HARDENED\s*=.*','SECURITY_HARDENED=false'; [System.IO.File]::WriteAllText($p, $t, (New-Object System.Text.UTF8Encoding($false)))"
"C:\xampp\php\php.exe" artisan config:clear >nul
"C:\xampp\php\php.exe" artisan view:clear >nul
"C:\xampp\php\php.exe" artisan migrate:fresh --seed --force

echo.
echo [OK] Base loko_security_lab reinitialisee et SECURITY_HARDENED=false retabli.
pause
