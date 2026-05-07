# Native Docker Engine μέσα στο WSL

Αυτό το μονοπάτι απευθύνεται σε όσους θέλουν να εργαστούν αποκλειστικά μέσα από το Ubuntu, χωρίς Docker Desktop στα Windows. Το εργαστήριο το υποστηρίζει, αλλά απαιτεί λίγο προσεκτικότερη διαχείριση του περιβάλλοντος.

Για συνεπή ελληνική ορολογία στους οδηγούς του μαθήματος, ανατρέξτε στο [glossary.md](../../../glossary.md).

## Αρχεία

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

## Εκτέλεση

```bash
cd ~/cloud-uth/code/00_workstation-setup/03_native-docker-engine
```

1. Ελέγξτε αν το Ubuntu τρέχει ήδη με ενεργό `systemd`, εκτελώντας `systemctl is-system-running`.
2. Αν χρειάζεται, αντιγράψτε το περιεχόμενο του `wsl.conf.example` στο `/etc/wsl.conf`.
3. Από PowerShell εκτελέστε το περιεχόμενο του `restart-wsl.ps1` και ανοίξτε νέο Ubuntu terminal.
4. Εκτελέστε `bash install-docker-engine.sh`.
5. Κλείστε και ανοίξτε ξανά το Ubuntu terminal ή εκτελέστε μία φορά `newgrp docker`.
6. Εκτελέστε `bash verify-docker.sh`.

## Κριτήριο ολοκλήρωσης

- Το `docker version` επιστρέφει στοιχεία server χωρίς να απαιτείται `sudo`.
- Το `docker compose version` λειτουργεί κανονικά.
- Η δοκιμή `hello-world` ολοκληρώνεται επιτυχώς.
