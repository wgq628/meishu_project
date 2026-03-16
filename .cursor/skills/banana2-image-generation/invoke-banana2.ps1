<#
.SYNOPSIS
    Banana2 绘图 API 通用调用脚本（文生图 / 图生图）
.DESCRIPTION
    通过环境变量 BANANA2_ACCESS_KEY_ID、BANANA2_ACCESS_KEY_SECRET 认证，调用 Banana2 接口生成图片。
    支持纯文生图或传入参考图 URL 的图生图。供 SKILL/Agent 或命令行直接调用。
.PARAMETER Prompt
    英文提示词，必填。图生图时脚本会自动在末尾追加参考图说明句。
.PARAMETER AspectRatio
    画面比例，如 "1:1"、"9:16"、"16:9"，默认 "1:1"。
.PARAMETER Resolution
    分辨率档位，默认 "1K"。
.PARAMETER OutputFormat
    输出格式 "png" 或 "jpeg"，默认 "png"。
.PARAMETER ReferenceImageUrls
    参考图 URL 列表（图生图）。多个可用逗号分隔或多次传参。不传或空则为文生图。
.PARAMETER OutputPath
    保存图片的完整路径。如果生成多张图，会自动在文件名后加上序号。不传则保存到桌面。
.PARAMETER Count
    生成图片数量，默认为 1。使用直接 API 调用（顺序执行），避免 -Parallel 解析问题。
.PARAMETER NoDownload
    仅输出图片 URL，不下载到本地。
.PARAMETER TimeoutSeconds
    请求超时秒数，默认 120。
.EXAMPLE
    .\invoke-banana2.ps1 -Prompt "A sunset over the sea"
.EXAMPLE
    .\invoke-banana2.ps1 -Prompt "Turn into cyberpunk style" -ReferenceImageUrls "https://example.com/ref.png" -AspectRatio "1:1"
.EXAMPLE
    .\invoke-banana2.ps1 -Prompt "A cat" -Count 5
#>
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string] $Prompt,

    [Parameter(Mandatory = $false)]
    [string] $AspectRatio = "1:1",

    [Parameter(Mandatory = $false)]
    [string] $Resolution = "1K",

    [Parameter(Mandatory = $false)]
    [ValidateSet("png", "jpeg")]
    [string] $OutputFormat = "png",

    [Parameter(Mandatory = $false)]
    [string[]] $ReferenceImageUrls = @(),

    [Parameter(Mandatory = $false)]
    [string] $OutputPath = "",

    [Parameter(Mandatory = $false)]
    [int] $Count = 1,

    [Parameter(Mandatory = $false)]
    [switch] $NoDownload,

    [Parameter(Mandatory = $false)]
    [int] $TimeoutSeconds = 120
)

$ErrorActionPreference = "Stop"
$apiUrl = "https://openapi-pre.uqualities.com/AIGCChatOpenServ/saas/gemini-3.1-flash-image-preview/image/generation"

# 检查环境变量
if (-not $env:BANANA2_ACCESS_KEY_ID -or -not $env:BANANA2_ACCESS_KEY_SECRET) {
    Write-Error "请先设置环境变量: BANANA2_ACCESS_KEY_ID, BANANA2_ACCESS_KEY_SECRET"
    exit 1
}

# 图生图时在 prompt 末尾追加固定句
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

Write-Host "Generating $Count image(s) via direct API call(s)..."

$defaultOutputDir = Join-Path $PSScriptRoot "output"
if (-not (Test-Path $defaultOutputDir)) {
    New-Item -ItemType Directory -Force -Path $defaultOutputDir | Out-Null
}

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
        Write-Host "BANANA2_IMAGE_URL_${res.Index}=$($res.Url)"
        Write-Host "BANANA2_IMAGE_SIZE_${res.Index}=$($res.Size)"
        if (-not $NoDownload) {
            Write-Host "BANANA2_OUTPUT_PATH_${res.Index}=$($res.OutputPath)"
        }
    } else {
        Write-Error "Task $($res.Index) failed: $($res.Message)"
        $hasError = $true
    }
}

if ($hasError) {
    exit 1
} else {
    exit 0
}