<#
.SYNOPSIS
    Banana2 image API - direct call (no Parallel), for posters and single/multi image.
.DESCRIPTION
    Same as invoke-banana2.ps1 but uses direct API calls only to avoid PowerShell parsing issues.
    Set env: BANANA2_ACCESS_KEY_ID, BANANA2_ACCESS_KEY_SECRET
#>
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string] $Prompt,
    [string] $AspectRatio = "1:1",
    [string] $Resolution = "1K",
    [ValidateSet("png", "jpeg")]
    [string] $OutputFormat = "png",
    [string[]] $ReferenceImageUrls = @(),
    [string] $OutputPath = "",
    [int] $Count = 1,
    [switch] $NoDownload,
    [int] $TimeoutSeconds = 120
)

$ErrorActionPreference = "Stop"
$apiUrl = "https://openapi-pre.uqualities.com/AIGCChatOpenServ/saas/gemini-3.1-flash-image-preview/image/generation"

if (-not $env:BANANA2_ACCESS_KEY_ID -or -not $env:BANANA2_ACCESS_KEY_SECRET) {
    Write-Error "Set BANANA2_ACCESS_KEY_ID and BANANA2_ACCESS_KEY_SECRET"
    exit 1
}

$effectivePrompt = $Prompt
$refList = @($ReferenceImageUrls | Where-Object { $_ -match "\S" })
if ($refList.Count -gt 0) {
    $suffix = ". Generate an image based on the above prompt words and reference pictures"
    if (-not $effectivePrompt.TrimEnd().EndsWith($suffix.TrimStart("."))) {
        $effectivePrompt = $effectivePrompt.TrimEnd() + $suffix
    }
}

$bodyObj = @{
    prompt            = $effectivePrompt
    aspectRatio        = $AspectRatio
    resolution         = $Resolution
    outputFormat       = $OutputFormat
    imageUrlList       = $refList
    enableGoogleSearch = $false
}
$body = $bodyObj | ConvertTo-Json

$scriptDir = $PSScriptRoot
$defaultOutputDir = Join-Path $scriptDir "output"
if (-not (Test-Path $defaultOutputDir)) {
    New-Item -ItemType Directory -Force -Path $defaultOutputDir | Out-Null
}

Write-Host "Generating $Count image(s) via direct API..."

$results = @()
for ($i = 1; $i -le $Count; $i++) {
    try {
        $response = Invoke-RestMethod -Uri $apiUrl -Method POST `
            -Headers @{
                "Content-Type"                   = "application/json"
                "X-Request-req-accessKeyId"      = $env:BANANA2_ACCESS_KEY_ID
                "X-Request-req-accessKeySecret"  = $env:BANANA2_ACCESS_KEY_SECRET
            } `
            -Body $body `
            -TimeoutSec $TimeoutSeconds

        if ($response.code -ne "200") {
            $errMsg = $response.msg
            if ($response.data.errorMessage) { $errMsg += " | " + $response.data.errorMessage }
            $results += [PSCustomObject]@{ Status = "Error"; Index = $i; Message = $errMsg }
            continue
        }

        $imageList = $response.data.imageList
        if (-not $imageList -or $imageList.Count -eq 0) {
            $results += [PSCustomObject]@{ Status = "Error"; Index = $i; Message = "No image returned" }
            continue
        }

        $img = $imageList[0]
        $imageUrl = $img.url
        $imageSize = $img.width.ToString() + "x" + $img.height.ToString()

        if ($NoDownload) {
            $results += [PSCustomObject]@{ Status = "Success"; Index = $i; Url = $imageUrl; Size = $imageSize; OutputPath = "" }
            continue
        }

        if (-not $OutputPath) {
            $ext = if ($OutputFormat -eq "jpeg") { "jpg" } else { "png" }
            $timestamp = (Get-Date).ToString('yyyyMMdd-HHmmss')
            $finalPath = Join-Path $defaultOutputDir "banana2_${timestamp}_${i}.$ext"
        } else {
            if ($Count -eq 1) {
                $finalPath = $OutputPath
            } else {
                $ext = [System.IO.Path]::GetExtension($OutputPath)
                $dir = [System.IO.Path]::GetDirectoryName($OutputPath)
                $name = [System.IO.Path]::GetFileNameWithoutExtension($OutputPath)
                if (-not $dir) { $dir = "." }
                $finalPath = Join-Path $dir "${name}_${i}${ext}"
            }
        }

        Invoke-WebRequest -Uri $imageUrl -OutFile $finalPath -UseBasicParsing
        $results += [PSCustomObject]@{ Status = "Success"; Index = $i; Url = $imageUrl; Size = $imageSize; OutputPath = $finalPath }
    } catch {
        $results += [PSCustomObject]@{ Status = "Error"; Index = $i; Message = ("Request failed: " + $_.Exception.Message) }
    }
}

$hasError = $false
foreach ($res in $results) {
    if ($res.Status -eq "Success") {
        Write-Host "BANANA2_IMAGE_URL_$($res.Index)=$($res.Url)"
        Write-Host "BANANA2_IMAGE_SIZE_$($res.Index)=$($res.Size)"
        if (-not $NoDownload) {
            Write-Host "BANANA2_OUTPUT_PATH_$($res.Index)=$($res.OutputPath)"
        }
    } else {
        Write-Error "Task $($res.Index) failed: $($res.Message)"
        $hasError = $true
    }
}

if ($hasError) { exit 1 } else { exit 0 }
