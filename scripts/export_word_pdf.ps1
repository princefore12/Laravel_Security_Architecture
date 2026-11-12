param(
    [switch]$IncludeWebPdf
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$docxPath = [string](Join-Path $root "livrables\office\Rapport_Securite_Laravel_Groupe5.docx")
$pdfPath = [string](Join-Path $root "livrables\office\Rapport_Securite_Laravel_Groupe5.pdf")
$tmpPdf = [string](Join-Path $env:TEMP ("loko_word_export_" + $PID + ".pdf"))
$webHtml = [string](Join-Path $root "livrables\web-interactif\rapport.html")
$webPdf = [string](Join-Path $root "livrables\web-interactif\Rapport_Web_Groupe5.pdf")

if (-not (Test-Path $docxPath)) {
    throw "Fichier Word introuvable : $docxPath"
}

$word = $null
$doc = $null
try {
    Write-Host "1. Ouverture de Microsoft Word..."
    $word = New-Object -ComObject Word.Application
    $word.Visible = $true
    $word.DisplayAlerts = 0
    $word.AutomationSecurity = 3
    Write-Host "2. Chargement de $docxPath..."
    $doc = $word.Documents.Open($docxPath, $false, $true)
    $doc.Repaginate()
    $pages = $doc.ComputeStatistics(2)
    if (Test-Path $tmpPdf) { Remove-Item $tmpPdf -Force }
    Write-Host "3. Export PDF ($pages pages)..."
    $fmtPdf = [int]17
    $doc.SaveAs2([ref]$tmpPdf, [ref]$fmtPdf)
} finally {
    if ($doc) {
        try {
            $doc.Saved = $true
            $doc.Close()
        } catch {}
        try { [System.Runtime.Interopservices.Marshal]::ReleaseComObject($doc) | Out-Null } catch {}
    }
    if ($word) {
        try {
            $word.Quit()
        } catch {}
        try { [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null } catch {}
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

Copy-Item -Path $tmpPdf -Destination $pdfPath -Force
Remove-Item $tmpPdf -Force -ErrorAction SilentlyContinue
Write-Host "4. PDF Office pret : $pdfPath ($((Get-Item $pdfPath).Length) octets)"

if ($IncludeWebPdf) {
    $edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if (Test-Path $edge) {
        $ud = Join-Path $env:TEMP ("edge-webpdf-" + (Get-Random))
        $uri = "file:///" + ($webHtml.Replace("\", "/"))
        Start-Process -FilePath $edge -ArgumentList "--headless","--no-sandbox","--disable-gpu","--user-data-dir=$ud","--no-pdf-header-footer","--print-to-pdf=$webPdf",$uri -Wait | Out-Null
        Remove-Item $ud -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "5. PDF Web pret : $webPdf ($((Get-Item $webPdf).Length) octets)"
    }
}
