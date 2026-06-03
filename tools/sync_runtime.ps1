param(
  [string]$RuntimeRoot = "C:\Users\wtzhang12\.codex\skills",
  [string]$Skill = ""
)

$ErrorActionPreference = "Stop"
$WorkspaceRoot = Split-Path -Parent $PSScriptRoot

$skills = @{
  "ftshare-market-data" = "skills\market-data\ftshare-market-data"
  "yc-buy-selector" = "skills\stock-selection\yc-buy-selector"
  "watchlist-tracker" = "skills\tracking\watchlist-tracker"
  "wechat-official-collector" = "skills\content-collection\wechat-official-collector"
}

if ($Skill -and -not $skills.ContainsKey($Skill)) {
  throw "Unknown skill: $Skill"
}

$selected = if ($Skill) { @($Skill) } else { $skills.Keys }
foreach ($name in $selected) {
  $src = Join-Path $WorkspaceRoot $skills[$name]
  $dst = Join-Path $RuntimeRoot $name
  if (-not (Test-Path $src)) {
    throw "Missing source: $src"
  }
  New-Item -ItemType Directory -Force -Path $RuntimeRoot | Out-Null
  Copy-Item -Recurse -Force -LiteralPath $src -Destination $dst
  Write-Host "Synced $name -> $dst"
}
