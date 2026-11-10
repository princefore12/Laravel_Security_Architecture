@echo off
title LOKO-Vault CyberLab - Exposé Groupe 5 (UT LOKO)
color 0F
echo ============================================================================
echo   UT LOKO - LICENCE 3 INFORMATIQUE - GROUPE 5 (Prof. M. CAMARA)
echo   Lancement de XAMPP (Apache + MariaDB) et du laboratoire Laravel
echo ============================================================================
echo.

cd /d "%~dp0\..\laravel-security-lab"

echo [1/5] Verification d'Apache (XAMPP / phpMyAdmin) sur le port 80...
netstat -ano | findstr ":80 " | findstr "LISTENING" >nul
if %errorlevel% neq 0 (
    echo     Apache est arrete. Demarrage via C:\xampp\apache_start.bat ...
    start "" /MIN "C:\xampp\apache_start.bat"
    timeout /t 2 /nobreak >nul
) else (
    echo     Apache est deja actif sur le port 80.
)

echo [2/5] Verification de MariaDB (XAMPP) sur le port 3306...
netstat -ano | findstr ":3306 " | findstr "LISTENING" >nul
if %errorlevel% neq 0 (
    echo     MariaDB est arrete. Demarrage via C:\xampp\mysql_start.bat ...
    start "" /MIN "C:\xampp\mysql_start.bat"
    timeout /t 4 /nobreak >nul
) else (
    echo     MariaDB est deja actif sur le port 3306.
)

echo [3/5] Creation de la base loko_security_lab si absente...
"C:\xampp\mysql\bin\mysql.exe" -u root -e "CREATE DATABASE IF NOT EXISTS loko_security_lab CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
if %errorlevel% neq 0 (
    echo [ERREUR] Impossible de joindre MariaDB XAMPP. Verifiez XAMPP Control Panel.
    pause
    exit /b 1
)

echo [4/5] Verification des tables et des donnees de demonstration...
"C:\xampp\php\php.exe" artisan migrate --seed --force

echo [5/5] Demarrage du serveur Laravel sur http://127.0.0.1:8000 ...
start "" "http://127.0.0.1:8000"
"C:\xampp\php\php.exe" artisan serve --host=127.0.0.1 --port=8000
pause
