# Native Docker Engine inside WSL

This path is for students who prefer to work entirely from Ubuntu without Docker Desktop on Windows. The lab supports it, but it requires slightly more careful environment management.

For consistent terminology across the course guides, consult [glossary.md](../../../glossary.md).

## Files

### `wsl.conf.example`

<!-- AUTO-CODE: code/00_workstation-setup/03_native-docker-engine/wsl.conf.example -->
``` ini
[boot]
systemd=true
```
<!-- END AUTO-CODE -->

### `restart-wsl.ps1`

<!-- AUTO-CODE: code/00_workstation-setup/03_native-docker-engine/restart-wsl.ps1 -->
``` powershell
# Restart WSL after editing /etc/wsl.conf.
wsl --shutdown
```
<!-- END AUTO-CODE -->

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

## Execution

```bash
cd ~/cloud-uth/code/00_workstation-setup/03_native-docker-engine
```

1. Check whether Ubuntu already runs with `systemd` enabled by executing `systemctl is-system-running`.
2. If needed, copy the contents of `wsl.conf.example` into `/etc/wsl.conf`.
3. From PowerShell, run the contents of `restart-wsl.ps1` and open a new Ubuntu terminal.
4. Run `bash install-docker-engine.sh`.
5. Close and reopen the Ubuntu terminal, or run `newgrp docker` once.
6. Run `bash verify-docker.sh`.

## Completion criteria

- `docker version` returns server details without requiring `sudo`.
- `docker compose version` works normally.
- The `hello-world` test completes successfully.
