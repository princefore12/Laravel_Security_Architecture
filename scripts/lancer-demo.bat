@echo off
title Portail Academique UT LOKO - Demo Expose Groupe 5
color 0F
echo ============================================================================
echo   UT LOKO - LICENCE 3 INFORMATIQUE - GROUPE 5 (Prof. M. CAMARA)
echo   XAMPP (Apache + MariaDB) + Portail UT LOKO (:8000) + Site Externe (:8001)
echo ============================================================================
echo.

cd /d "%~dp0\..\laravel-security-lab"

echo [1/6] Verification d'Apache (XAMPP / phpMyAdmin) sur le port 80...
netstat -ano | findstr ":80 " | findstr "LISTENING" >nul
if %errorlevel% neq 0 (
    echo     Demarrage d'Apache via C:\xampp\apache_start.bat ...
    start "" /MIN "C:\xampp\apache_start.bat"
    timeout /t 2 /nobreak >nul
) else (
    echo     Apache est deja actif sur le port 80.
)

echo [2/6] Verification de MariaDB (XAMPP) sur le port 3306...
netstat -ano | findstr ":3306 " | findstr "LISTENING" >nul
if %errorlevel% neq 0 (
    echo     Demarrage de MariaDB via C:\xampp\mysql_start.bat ...
    start "" /MIN "C:\xampp\mysql_start.bat"
    timeout /t 4 /nobreak >nul
) else (
    echo     MariaDB est deja actif sur le port 3306.
)

echo [3/6] Creation de la base loko_security_lab si absente...
"C:\xampp\mysql\bin\mysql.exe" -u root -e "CREATE DATABASE IF NOT EXISTS loko_security_lab CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
if %errorlevel% neq 0 (
    echo [ERREUR] Impossible de joindre MariaDB XAMPP. Verifiez XAMPP Control Panel.
    pause
    exit /b 1
)

echo [4/6] Nettoyage du cache de config (lecture .env en direct) et migrations...
"C:\xampp\php\php.exe" artisan config:clear >nul
"C:\xampp\php\php.exe" artisan view:clear >nul
"C:\xampp\php\php.exe" artisan migrate --seed --force

echo [5/6] Demarrage du site tiers piege CSRF sur http://127.0.0.1:8001 ...
netstat -ano | findstr ":8001 " | findstr "LISTENING" >nul
if %errorlevel% neq 0 (
    start "Site Externe CSRF (8001)" /MIN "C:\xampp\php\php.exe" -S 127.0.0.1:8001 -t "%~dp0\..\evil-site"
    timeout /t 1 /nobreak >nul
) else (
    echo     Serveur :8001 deja actif.
)

echo [6/6] Demarrage du Portail Academique UT LOKO sur http://127.0.0.1:8000 ...
start "" "http://127.0.0.1:8000"
"C:\xampp\php\php.exe" artisan serve --host=127.0.0.1 --port=8000
pause
