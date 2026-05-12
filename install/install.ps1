# install.ps1 — one-shot setup for the Obsidian × Claude Desktop quiz workflow.
#
# Usage (PowerShell):
#   cd <repo>\install
#   .\install.ps1                                      # interactive
#   .\install.ps1 -VaultPath "C:\...\Vault" -ApiKey ".." -NoPrompt
#
# Safe to re-run: merges into any existing claude_desktop_config.json
# instead of overwriting it.

[CmdletBinding()]
param(
    [string]$VaultPath,
    [string]$ApiKey,
    [string]$ObsidianHost = "127.0.0.1",
    [int]$ObsidianPort = 27124,
    [switch]$NoPrompt,
    [switch]$SkipObsidianMcp
)

$ErrorActionPreference = 'Stop'

function Write-Step  { param($m) Write-Host "`n→ $m" -ForegroundColor Cyan }
function Write-Ok    { param($m) Write-Host "  ✓ $m" -ForegroundColor Green }
function Write-Warn  { param($m) Write-Host "  ! $m" -ForegroundColor Yellow }
function Write-Fail  { param($m) Write-Host "  ✗ $m" -ForegroundColor Red }

# ───────────────────────────────────────────────────────────────
# 0. Locate self
# ───────────────────────────────────────────────────────────────
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir

Write-Host "`nObsidian × Claude Desktop quiz workflow installer" -ForegroundColor White
Write-Host "------------------------------------------------" -ForegroundColor DarkGray
Write-Host "repo:    $repoRoot"
Write-Host "scripts: $scriptDir"

# ───────────────────────────────────────────────────────────────
# 1. Prereqs
# ───────────────────────────────────────────────────────────────
Write-Step "Checking prerequisites"
$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
    Write-Fail "Node.js not found in PATH."
    Write-Host "    Install with: winget install OpenJS.NodeJS.LTS"
    Write-Host "    Then reopen PowerShell and re-run this script."
    exit 1
}
$nodeVer = (& node -v).Trim()
Write-Ok "Node.js $nodeVer"

$claudeDir = Join-Path $env:APPDATA "Claude"
if (-not (Test-Path $claudeDir)) {
    Write-Fail "Claude Desktop config dir not found at $claudeDir"
    Write-Host "    Install Claude Desktop first: https://claude.ai/download"
    exit 1
}
Write-Ok "Claude Desktop config dir: $claudeDir"

# ───────────────────────────────────────────────────────────────
# 2. Resolve vault path
# ───────────────────────────────────────────────────────────────
Write-Step "Locating Obsidian vault"
if (-not $VaultPath) {
    if ($NoPrompt) {
        Write-Fail "-VaultPath is required when -NoPrompt is set."
        exit 1
    }
    $default = Join-Path $env:USERPROFILE "Documents\ObsidianVault"
    $hint = if (Test-Path $default) { " (Enter for default: $default)" } else { "" }
    $input = Read-Host "Vault absolute path${hint}"
    $VaultPath = if ([string]::IsNullOrWhiteSpace($input)) { $default } else { $input.Trim('"') }
}
if (-not (Test-Path $VaultPath)) {
    Write-Fail "Vault path does not exist: $VaultPath"
    Write-Host "    Create the folder in Obsidian first (or fix the path)."
    exit 1
}
$VaultPath = (Resolve-Path $VaultPath).Path
Write-Ok "Vault: $VaultPath"

# ───────────────────────────────────────────────────────────────
# 3. Resolve Obsidian API key (optional)
# ───────────────────────────────────────────────────────────────
$installObsidian = -not $SkipObsidianMcp
if ($installObsidian -and -not $ApiKey) {
    if ($NoPrompt) {
        Write-Warn "No API key supplied; skipping obsidian MCP server."
        $installObsidian = $false
    } else {
        Write-Host ""
        Write-Host "    Obsidian REST API key (from the Local REST API plugin)."
        Write-Host "    Leave empty to skip the obsidian MCP server — filesystem MCP alone"
        Write-Host "    is enough to read/write the vault."
        $ApiKey = (Read-Host "API key").Trim()
        if ([string]::IsNullOrWhiteSpace($ApiKey)) {
            $installObsidian = $false
            Write-Warn "No API key entered; will configure filesystem MCP only."
        }
    }
}

# ───────────────────────────────────────────────────────────────
# 4. Merge claude_desktop_config.json
# ───────────────────────────────────────────────────────────────
Write-Step "Updating claude_desktop_config.json"
$cfgPath = Join-Path $claudeDir "claude_desktop_config.json"

# Read existing, or start from empty
if (Test-Path $cfgPath) {
    # Back up before touching
    $backup = "$cfgPath.bak.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Copy-Item $cfgPath $backup
    Write-Ok "Backed up existing config → $(Split-Path -Leaf $backup)"
    try {
        $cfg = Get-Content $cfgPath -Raw | ConvertFrom-Json
    } catch {
        Write-Fail "Existing config is not valid JSON. Aborting to preserve your file."
        Write-Host "    Inspect: $cfgPath"
        exit 1
    }
} else {
    $cfg = [pscustomobject]@{}
}

if (-not ($cfg.PSObject.Properties.Name -contains 'mcpServers')) {
    $cfg | Add-Member -NotePropertyName 'mcpServers' -NotePropertyValue ([pscustomobject]@{})
}

# Helper: idempotent set on a PSCustomObject
function Set-Property {
    param($Object, [string]$Name, $Value)
    if ($Object.PSObject.Properties.Name -contains $Name) {
        $Object.PSObject.Properties.Remove($Name)
    }
    $Object | Add-Member -NotePropertyName $Name -NotePropertyValue $Value
}

# filesystem MCP
$fsEntry = [pscustomobject]@{
    command = 'npx'
    args    = @('-y', '@modelcontextprotocol/server-filesystem', $VaultPath)
}
Set-Property $cfg.mcpServers 'filesystem' $fsEntry
Write-Ok "mcpServers.filesystem → $VaultPath"

# obsidian MCP (optional)
if ($installObsidian) {
    $obsEntry = [pscustomobject]@{
        command = 'uvx'
        args    = @('mcp-obsidian')
        env     = [pscustomobject]@{
            OBSIDIAN_API_KEY = $ApiKey
            OBSIDIAN_HOST    = $ObsidianHost
            OBSIDIAN_PORT    = "$ObsidianPort"
        }
    }
    Set-Property $cfg.mcpServers 'obsidian' $obsEntry
    Write-Ok "mcpServers.obsidian → ${ObsidianHost}:${ObsidianPort}"
} else {
    Write-Warn "Skipped obsidian MCP server."
}

# Write back (preserve any unrelated keys)
$json = $cfg | ConvertTo-Json -Depth 10
# PowerShell adds BOM by default; Claude reads UTF-8 — write without BOM
$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($cfgPath, $json, $utf8NoBom)
Write-Ok "Wrote $cfgPath"

# ───────────────────────────────────────────────────────────────
# 5. Copy templates into vault
# ───────────────────────────────────────────────────────────────
Write-Step "Copying templates into vault"
$pairs = @(
    @{ src = (Join-Path $scriptDir 'quiz-prompt.md');       dst = 'Templates\quiz-prompt.md' }
    @{ src = (Join-Path $scriptDir 'quiz-template.html');   dst = 'AI\templates\quiz-template.html' }
    @{ src = (Join-Path $scriptDir 'sample-econ-quiz.html');dst = 'AI\quizzes\sample-econ-quiz.html' }
)
foreach ($p in $pairs) {
    $dstFull = Join-Path $VaultPath $p.dst
    $dstDir = Split-Path -Parent $dstFull
    if (-not (Test-Path $dstDir)) { New-Item -ItemType Directory -Force -Path $dstDir | Out-Null }
    if (Test-Path $dstFull) {
        Write-Warn "Already exists, skipping: $($p.dst)"
    } else {
        Copy-Item $p.src $dstFull
        Write-Ok "Copied → $($p.dst)"
    }
}

# ───────────────────────────────────────────────────────────────
# 6. Verify the MCP package exists on the npm registry
# ───────────────────────────────────────────────────────────────
Write-Step "Verifying filesystem MCP package availability"
try {
    $ver = (& npm view '@modelcontextprotocol/server-filesystem' version 2>$null).Trim()
    if ($ver) {
        Write-Ok "@modelcontextprotocol/server-filesystem v$ver available"
    } else {
        Write-Warn "Could not verify package version (npm registry unreachable?). Claude Desktop will retry on first launch."
    }
} catch {
    Write-Warn "npm view failed; first Claude Desktop launch may take 1-2 min while it fetches the package."
}

# ───────────────────────────────────────────────────────────────
# Done
# ───────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "Done." -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "  1. Quit Claude Desktop completely (system tray → Quit), then relaunch."
Write-Host "  2. Open a new chat → click the 🔌 icon → confirm 'filesystem' (and 'obsidian') are connected."
Write-Host "  3. Test:  vault 루트의 파일 목록을 보여줘"
Write-Host "  4. Generate a quiz:"
Write-Host "       Vault\Macro\week-3.md 내용으로 Vault\AI\quizzes\macro-week3.html 만들어줘."
Write-Host ""
Write-Host "Smoke test:  .\test-setup.ps1" -ForegroundColor DarkGray
