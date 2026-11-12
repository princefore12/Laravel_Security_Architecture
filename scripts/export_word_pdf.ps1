param(
    [switch]$IncludeWebPdf
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$docxPath = Join-Path $root "livrables\office\Rapport_Securite_Laravel_Groupe5.docx"
$pdfPath = Join-Path $root "livrables\office\Rapport_Securite_Laravel_Groupe5.pdf"
$webHtml = Join-Path $root "livrables\web-interactif\rapport.html"
$webPdf = Join-Path $root "livrables\web-interactif\Rapport_Web_Groupe5.pdf"

if (-not (Test-Path $docxPath)) {
    throw "Fichier Word introuvable : $docxPath"
}

$word = $null
$doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $doc = $word.Documents.Open($docxPath, $false, $true)
    $doc.Repaginate()
    $doc.Fields.Update() | Out-Null
    foreach ($sec in $doc.Sections) {
        $sec.Headers.Item(1).Range.Fields.Update() | Out-Null
        $sec.Footers.Item(1).Range.Fields.Update() | Out-Null
    }
    $doc.ExportAsFixedFormat($pdfPath, 17)
    Write-Host "PDF exporte depuis Word : $pdfPath"
} finally {
    if ($doc) {
        $doc.Close(0) | Out-Null
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($doc) | Out-Null
    }
    if ($word) {
        $word.Quit(0) | Out-Null
        [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}

if ($IncludeWebPdf) {
    $edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if (Test-Path $edge) {
        $ud = Join-Path $env:TEMP ("edge-webpdf-" + (Get-Random))
        $uri = "file:///" + ($webHtml.Replace("\", "/"))
        Start-Process -FilePath $edge -ArgumentList "--headless","--no-sandbox","--disable-gpu","--user-data-dir=$ud","--no-pdf-header-footer","--print-to-pdf=$webPdf",$uri -Wait | Out-Null
        Remove-Item $ud -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "PDF Web exporte depuis rapport.html : $webPdf"
    }
}
