# Docker Desktop με WSL integration

Αυτό είναι το προτεινόμενο μονοπάτι για τους περισσότερους φοιτητές. Ο Docker daemon εκτελείται από το Docker Desktop στα Windows, ενώ οι εντολές `docker` και `docker compose` χρησιμοποιούνται από το Ubuntu terminal του WSL.

Για συνεπή ελληνική ορολογία στους οδηγούς του μαθήματος, ανατρέξτε στο [glossary.md](../../../glossary.md).

## Αρχεία

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

## Εκτέλεση

```bash
cd ~/cloud-uth/code/00_workstation-setup/02_docker-desktop-wsl
```

1. Εγκαταστήστε το Docker Desktop από την επίσημη σελίδα του Docker.
2. Κατά την εγκατάσταση, ενεργοποιήστε την επιλογή `Use the WSL 2 based engine`.
3. Στο `Settings -> Resources -> WSL Integration`, ενεργοποιήστε τη διανομή Ubuntu που χρησιμοποιείτε στο μάθημα.
4. Ανοίξτε νέο Ubuntu terminal και εκτελέστε `bash verify-docker-desktop.sh`.

## Κριτήριο ολοκλήρωσης

- Οι εντολές `docker version` και `docker compose version` επιστρέφουν στοιχεία client και server.
- Η εκτέλεση του `hello-world` ολοκληρώνεται χωρίς σφάλμα.
