# test-setup.ps1 — smoke test for the Obsidian × Claude Desktop quiz workflow.
# Run after install.ps1 (and after restarting Claude Desktop).
#
# Returns exit code 0 if everything looks healthy, 1 if any check failed.

[CmdletBinding()]
param(
    [string]$VaultPath
)

$ErrorActionPreference = 'Continue'
$failed = 0

function Pass { param($m) Write-Host "  ✓ $m" -ForegroundColor Green }
function Fail { param($m) Write-Host "  ✗ $m" -ForegroundColor Red; $script:failed++ }
function Step { param($m) Write-Host "`n→ $m" -ForegroundColor Cyan }

Write-Host "`nQuiz workflow smoke test" -ForegroundColor White
Write-Host "------------------------" -ForegroundColor DarkGray

# 1. Config file exists and parses
Step "claude_desktop_config.json"
$cfgPath = Join-Path $env:APPDATA "Claude\claude_desktop_config.json"
if (-not (Test-Path $cfgPath)) {
    Fail "Not found at $cfgPath  (run install.ps1)"
} else {
    Pass "Exists: $cfgPath"
    try {
        $cfg = Get-Content $cfgPath -Raw | ConvertFrom-Json
        Pass "Valid JSON"
        if ($cfg.mcpServers.PSObject.Properties.Name -contains 'filesystem') {
            $fsArgs = $cfg.mcpServers.filesystem.args
            $resolvedVault = $fsArgs | Where-Object { $_ -like '*:\*' -or $_ -like '/*' } | Select-Object -First 1
            Pass "filesystem MCP configured → $resolvedVault"
            if (-not $VaultPath) { $VaultPath = $resolvedVault }
        } else {
            Fail "mcpServers.filesystem missing"
        }
        if ($cfg.mcpServers.PSObject.Properties.Name -contains 'obsidian') {
            $key = $cfg.mcpServers.obsidian.env.OBSIDIAN_API_KEY
            if ($key -and $key -ne 'YOUR_OBSIDIAN_API_KEY_HERE') {
                Pass "obsidian MCP configured (key present)"
            } else {
                Fail "obsidian MCP has placeholder/missing key"
            }
        } else {
            Write-Host "  · obsidian MCP not configured (filesystem MCP alone is fine)" -ForegroundColor DarkGray
        }
    } catch {
        Fail "Invalid JSON: $($_.Exception.Message)"
    }
}

# 2. Vault accessible and templates in place
Step "Vault templates"
if (-not $VaultPath -or -not (Test-Path $VaultPath)) {
    Fail "Vault path not resolvable: $VaultPath"
} else {
    Pass "Vault: $VaultPath"
    $expected = @(
        'Templates\quiz-prompt.md',
        'AI\templates\quiz-template.html',
        'AI\quizzes\sample-econ-quiz.html'
    )
    foreach ($rel in $expected) {
        $p = Join-Path $VaultPath $rel
        if (Test-Path $p) { Pass "Found $rel" } else { Fail "Missing $rel  (run install.ps1)" }
    }
}

# 3. Node / npx ready
Step "Tooling"
$node = Get-Command node -ErrorAction SilentlyContinue
if ($node) { Pass "node $(& node -v)" } else { Fail "Node.js not in PATH" }
$npx = Get-Command npx -ErrorAction SilentlyContinue
if ($npx) { Pass "npx available" } else { Fail "npx not in PATH" }

# 4. Optional: ping Obsidian Local REST API
Step "Obsidian Local REST API (optional)"
$port = 27124
try {
    # The plugin uses a self-signed cert; allow it for this probe only.
    if ($PSVersionTable.PSVersion.Major -ge 6) {
        $resp = Invoke-WebRequest -Uri "https://127.0.0.1:$port/" -SkipCertificateCheck -TimeoutSec 3 -ErrorAction Stop
    } else {
        # PowerShell 5.x: temporarily relax cert validation
        $orig = [System.Net.ServicePointManager]::ServerCertificateValidationCallback
        [System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $true }
        try {
            $resp = Invoke-WebRequest -Uri "https://127.0.0.1:$port/" -TimeoutSec 3 -ErrorAction Stop
        } finally {
            [System.Net.ServicePointManager]::ServerCertificateValidationCallback = $orig
        }
    }
    Pass "Reachable on port $port (status $($resp.StatusCode))"
} catch {
    Write-Host "  · Not reachable on port $port — plugin may be disabled or Obsidian not running. Skipping." -ForegroundColor DarkGray
}

# Summary
Write-Host ""
if ($failed -eq 0) {
    Write-Host "All checks passed." -ForegroundColor Green
    exit 0
} else {
    Write-Host "$failed check(s) failed." -ForegroundColor Red
    exit 1
}
