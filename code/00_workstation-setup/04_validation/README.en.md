# Final validation and local clone

At the end of the workstation setup, two conditions should be true: the repository should exist locally inside WSL, and the baseline Docker commands should work from the same shell environment. This step verifies exactly those two conditions.

## Files

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

## Execution

```bash
cd ~/cloud-uth/code/00_workstation-setup/04_validation
```

1. If you do not already have a local WSL clone, run `bash clone-cloud-uth.sh`.
2. Run `bash verify-workstation.sh`.

## Completion criteria

- The repository exists at `~/cloud-uth`.
- `git rev-parse --show-toplevel` prints the expected working directory.
- `docker version`, `docker compose version`, and `docker run --rm hello-world` succeed from the same Ubuntu shell.
