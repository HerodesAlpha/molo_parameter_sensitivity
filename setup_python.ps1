# PowerShell script to load .env file and set Python path
# This script reads PYTHON_PATH from .env and sets it as an environment variable

if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*)\s*=\s*(.*)$') {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
            Write-Host "Set $name = $value"
        }
    }
    
    if ($env:PYTHON_PATH) {
        Write-Host "Python path set to: $env:PYTHON_PATH"
    } else {
        Write-Host "Warning: PYTHON_PATH not found in .env file"
    }
} else {
    Write-Host "Warning: .env file not found"
}

