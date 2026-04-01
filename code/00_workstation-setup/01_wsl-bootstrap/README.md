# Ρύθμιση WSL και Ubuntu

Αυτό το βήμα προετοιμάζει το βασικό περιβάλλον εργασίας στα Windows και στο Ubuntu του WSL. Με την ολοκλήρωσή του θα έχετε διαθέσιμο WSL2, εγκατεστημένο Ubuntu και τα ελάχιστα εργαλεία που χρειάζονται για να συνεχίσετε στον οδηγό Docker.

## Αρχεία

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

## Εκτέλεση

```bash
cd ~/cloud-uth/code/00_workstation-setup/01_wsl-bootstrap
```

1. Ανοίξτε PowerShell ως διαχειριστής και εκτελέστε το περιεχόμενο του `enable-wsl.ps1`.
2. Επανεκκινήστε τα Windows.
3. Επιστρέψτε σε PowerShell και εκτελέστε το περιεχόμενο του `install-ubuntu.ps1`.
4. Ανοίξτε το Ubuntu, δημιουργήστε λογαριασμό χρήστη και εκτελέστε `bash ubuntu-first-update.sh`.
5. Εκτελέστε ξανά σε PowerShell το περιεχόμενο του `check-wsl.ps1`.

## Κριτήριο ολοκλήρωσης

- Η εντολή `wsl --list --verbose` εμφανίζει το `Ubuntu` με έκδοση `2`.
- Το `VirtualMachinePlatform` εμφανίζεται ως `Enabled`.
- Στο Ubuntu λειτουργούν κανονικά οι εντολές `git --version` και `curl --version`.
