# WSL and Ubuntu bootstrap

This step prepares the baseline workstation environment on Windows and inside Ubuntu on WSL. When it is complete, you will have WSL2 available, Ubuntu installed, and the minimum tools required to continue with the Docker setup guide.

## Files

### `enable-wsl.ps1`

<!-- AUTO-CODE: code/00_workstation-setup/01_wsl-bootstrap/enable-wsl.ps1 -->
``` powershell
# Run this script from an elevated PowerShell window.
wsl --install --no-distribution
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```
<!-- END AUTO-CODE -->

### `install-ubuntu.ps1`

<!-- AUTO-CODE: code/00_workstation-setup/01_wsl-bootstrap/install-ubuntu.ps1 -->
``` powershell
# Install Ubuntu after the first restart.
wsl --install -d Ubuntu
```
<!-- END AUTO-CODE -->

### `ubuntu-first-update.sh`

<!-- AUTO-CODE: code/00_workstation-setup/01_wsl-bootstrap/ubuntu-first-update.sh -->
``` bash
#!/usr/bin/env bash
set -euo pipefail

sudo apt update
sudo apt upgrade -y
sudo apt install -y git curl ca-certificates

git --version
curl --version
```
<!-- END AUTO-CODE -->

### `check-wsl.ps1`

<!-- AUTO-CODE: code/00_workstation-setup/01_wsl-bootstrap/check-wsl.ps1 -->
``` powershell
# Show the installed distributions and their WSL versions.
wsl --list --verbose

# Confirm that the Virtual Machine Platform feature is enabled.
Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
```
<!-- END AUTO-CODE -->

## Execution

```bash
cd ~/cloud-uth/code/00_workstation-setup/01_wsl-bootstrap
```

1. Open PowerShell as administrator and run the contents of `enable-wsl.ps1`.
2. Restart Windows.
3. Return to PowerShell and run the contents of `install-ubuntu.ps1`.
4. Open Ubuntu, create your user account, and run `bash ubuntu-first-update.sh`.
5. Run the contents of `check-wsl.ps1` from PowerShell.

## Completion criteria

- `wsl --list --verbose` shows `Ubuntu` with WSL version `2`.
- `VirtualMachinePlatform` appears as `Enabled`.
- `git --version` and `curl --version` work normally inside Ubuntu.
