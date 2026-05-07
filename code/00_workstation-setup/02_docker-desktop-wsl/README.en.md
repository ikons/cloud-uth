# Docker Desktop with WSL integration

This is the recommended path for most students. The Docker daemon runs through Docker Desktop on Windows, while the `docker` and `docker compose` commands are used from the Ubuntu terminal inside WSL.

For consistent terminology across the course guides, consult [glossary.md](../../../glossary.md).

## Files

### `verify-docker-desktop.sh`

<!-- AUTO-CODE: code/00_workstation-setup/02_docker-desktop-wsl/verify-docker-desktop.sh -->
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
cd ~/cloud-uth/code/00_workstation-setup/02_docker-desktop-wsl
```

1. Install Docker Desktop from the official Docker page.
2. During the installation, enable `Use the WSL 2 based engine`.
3. In `Settings -> Resources -> WSL Integration`, enable the Ubuntu distribution you use for the course.
4. Open a new Ubuntu terminal and run `bash verify-docker-desktop.sh`.

## Completion criteria

- `docker version` and `docker compose version` return both client and server details.
- The `hello-world` container runs successfully.
