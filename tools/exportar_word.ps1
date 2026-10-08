$ErrorActionPreference = 'Stop'
$raizProyecto = Split-Path -Parent $PSScriptRoot
$documentoRuta = Join-Path $raizProyecto 'entrega/Informe_Parcial_Fuga_Prision.docx'
$pdfRuta = Join-Path $raizProyecto 'entrega/Informe_Parcial_Fuga_Prision.pdf'
$word = $null
$documento = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $documento = $word.Documents.Open($documentoRuta, $false, $true)
    $documento.Repaginate()
    $paginas = $documento.ComputeStatistics(2)
    $documento.ExportAsFixedFormat($pdfRuta, 17)
    Write-Output "PDF exportado desde Word. Paginas: $paginas"
} finally {
    if ($null -ne $documento) {
        $documento.Close(0)
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($documento)
    }
    if ($null -ne $word) {
        $word.Quit()
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
    }
}
