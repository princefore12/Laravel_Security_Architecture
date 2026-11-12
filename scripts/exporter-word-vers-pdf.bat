@echo off
title Export Word -> PDF (Groupe 5 - UT LOKO)
echo ============================================================================
echo   EXPORT DEPUIS WORD (.docx) VERS PDF (.pdf) - GROUPE 5 (UT LOKO)
echo   Garantit une copie exacte 100 %% identique au document Word edite.
echo ============================================================================
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0export_word_pdf.ps1"
if %errorlevel% neq 0 (
    echo [ERREUR] Fermez d'abord le PDF s'il est ouvert dans le navigateur, puis reessayez.
    pause
    exit /b 1
)
echo.
echo [OK] livrables\office\Rapport_Securite_Laravel_Groupe5.pdf mis a jour depuis le Word !
pause
