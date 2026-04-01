# Workstation setup (WSL + Docker)

The laboratory part of the course assumes that each student can work from an Ubuntu environment inside WSL and execute Docker commands from that same shell. This guide covers only that preparatory phase. When it is complete, the workstation will be ready for the Docker guide and for the Kubernetes onboarding material.

The canonical code and helper files of the preparatory workflow now live under `code/00_workstation-setup`. If you are reading this material before creating your first local clone, treat the snippets below as the authoritative execution steps and continue to step `04`, where the repository clone is also created.

## Preparation structure

| # | Directory | Goal |
|---|-----------|------|
| 01 | `code/00_workstation-setup/01_wsl-bootstrap` | Enable WSL2, install Ubuntu, and prepare the baseline tools |
| 02 | `code/00_workstation-setup/02_docker-desktop-wsl` | Recommended setup with Docker Desktop and WSL integration |
| 03 | `code/00_workstation-setup/03_native-docker-engine` | Optional setup with a native Docker Engine inside WSL |
| 04 | `code/00_workstation-setup/04_validation` | Final validation and local repository clone |

## 01. WSL and Ubuntu

Before using Docker, Windows must provide a working `WSL2` environment and an Ubuntu distribution. This step enables the required Windows features, installs Ubuntu, and prepares the shell with the minimum tools needed immediately afterward.

Open PowerShell as administrator from the Start menu.

![Figure 1](images/img1.png)

### `enable-wsl.ps1`

Run the following contents first from an elevated PowerShell session. A Windows restart is required afterward.

<!-- AUTO-CODE: code/00_workstation-setup/01_wsl-bootstrap/enable-wsl.ps1 -->
``` powershell
# Run this script from an elevated PowerShell window.
wsl --install --no-distribution
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```
<!-- END AUTO-CODE -->

![Figure 2](images/img23.png)

![Figure 3](images/img20.png)

### `install-ubuntu.ps1`

After the restart, complete the Ubuntu installation.

<!-- AUTO-CODE: code/00_workstation-setup/01_wsl-bootstrap/install-ubuntu.ps1 -->
``` powershell
# Install Ubuntu after the first restart.
wsl --install -d Ubuntu
```
<!-- END AUTO-CODE -->

Then open Ubuntu from the Start menu and create the WSL user account.

![Figure 4](images/img4.png)

![Figure 5](images/img7.png)

### `ubuntu-first-update.sh`

From the Ubuntu terminal, update the system and install the first required tools. Having `git` available already at this stage is useful because the local repository clone can then happen immediately without an extra preparatory step.

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

Finally, return to PowerShell to verify that WSL and `VirtualMachinePlatform` are configured correctly.

<!-- AUTO-CODE: code/00_workstation-setup/01_wsl-bootstrap/check-wsl.ps1 -->
``` powershell
# Show the installed distributions and their WSL versions.
wsl --list --verbose

# Confirm that the Virtual Machine Platform feature is enabled.
Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
```
<!-- END AUTO-CODE -->

If the installation completed correctly, `Ubuntu` appears with version `2` and `VirtualMachinePlatform` appears as `Enabled`.

## 02. Docker Desktop with WSL integration

For most students, this is the recommended path. The Docker daemon remains managed by Docker Desktop, while everyday work is performed from the Ubuntu terminal inside WSL, which is also the shell environment used by the following guides.

Download Docker Desktop from the official Docker page for Windows x86_64:

https://docs.docker.com/desktop/setup/install/windows-install/

During installation, make sure that `Use the WSL 2 based engine` remains enabled.

![Figure 6](images/img18.png)

![Figure 7](images/img11.png)

After installation, open Docker Desktop, confirm that the `WSL 2 based engine` is still enabled, and enable the Ubuntu distribution under `Resources -> WSL Integration`.

![Figure 8](images/img21.png)

![Figure 9](images/img12.png)

If Docker Desktop asks for an account, you may skip that step.

![Figure 10](images/img3.png)

### `verify-docker-desktop.sh`

Once Docker Desktop is ready, open a new Ubuntu terminal and run the following validation.

<!-- AUTO-CODE: code/00_workstation-setup/02_docker-desktop-wsl/verify-docker-desktop.sh -->
``` bash
#!/usr/bin/env bash
set -euo pipefail

docker version
docker compose version
docker run --rm hello-world
```
<!-- END AUTO-CODE -->

The successful execution of `hello-world` shows that the integration between Docker Desktop and WSL is working normally.

![Figure 11](images/img5.png)

![Figure 12](images/img25.png)

## 03. Native Docker Engine inside WSL

This path is optional and is intended for students who prefer to work entirely from Ubuntu without Docker Desktop on Windows. The course supports it, but it requires slightly more careful local environment management.

Before installation, check whether the Ubuntu shell already runs with `systemd` enabled by executing:

```bash
systemctl is-system-running
```

If you need to enable `systemd`, use the following contents in `/etc/wsl.conf`.

### `wsl.conf.example`

<!-- AUTO-CODE: code/00_workstation-setup/03_native-docker-engine/wsl.conf.example -->
``` ini
[boot]
systemd=true
```
<!-- END AUTO-CODE -->

After the change, restart WSL from PowerShell.

### `restart-wsl.ps1`

<!-- AUTO-CODE: code/00_workstation-setup/03_native-docker-engine/restart-wsl.ps1 -->
``` powershell
# Restart WSL after editing /etc/wsl.conf.
wsl --shutdown
```
<!-- END AUTO-CODE -->

Open Ubuntu again and continue with the Docker Engine installation.

### `install-docker-engine.sh`

<!-- AUTO-CODE: code/00_workstation-setup/03_native-docker-engine/install-docker-engine.sh -->
``` bash
#!/usr/bin/env bash
set -euo pipefail

sudo apt update
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"
```
<!-- END AUTO-CODE -->

After the script completes, close and reopen the Ubuntu terminal or run `newgrp docker` once so that the new group membership becomes active.

### `verify-docker.sh`

<!-- AUTO-CODE: code/00_workstation-setup/03_native-docker-engine/verify-docker.sh -->
``` bash
#!/usr/bin/env bash
set -euo pipefail

docker version
docker compose version
docker run --rm hello-world
```
<!-- END AUTO-CODE -->

If this validation completes without `sudo`, then the native installation is ready for the Docker guide.

## 04. Final validation and local clone

Once `docker version`, `docker compose version`, and `docker run --rm hello-world` work, the workstation preparation is essentially complete. The final step is to ensure that the repository also exists as a local clone inside WSL so that the examples from the guides can be executed directly.

### `clone-cloud-uth.sh`

<!-- AUTO-CODE: code/00_workstation-setup/04_validation/clone-cloud-uth.sh -->
``` bash
#!/usr/bin/env bash
set -euo pipefail

cd ~

if [ ! -d cloud-uth/.git ]; then
  git clone https://github.com/ikons/cloud-uth.git
fi

cd cloud-uth
```
<!-- END AUTO-CODE -->

### `verify-workstation.sh`

<!-- AUTO-CODE: code/00_workstation-setup/04_validation/verify-workstation.sh -->
``` bash
#!/usr/bin/env bash
set -euo pipefail

cd ~/cloud-uth
git rev-parse --show-toplevel
docker version
docker compose version
docker run --rm hello-world
```
<!-- END AUTO-CODE -->

After this check succeeds, you can continue to [docs/01_lab1-docker/README.en.md](../01_lab1-docker/README.en.md).

## What counts as complete

- WSL2 and Ubuntu work normally.
- One of the two Docker paths has been completed and the `docker` / `docker compose` commands work from the Ubuntu shell.
- The repository exists locally at `~/cloud-uth`.
- The environment is ready for the examples under `code/01_docker` and for the Kubernetes onboarding material that follows.
