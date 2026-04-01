# Προετοιμασία σταθμού εργασίας (WSL + Docker)

Το εργαστηριακό μέρος του μαθήματος προϋποθέτει ότι ο φοιτητής μπορεί να εργαστεί από περιβάλλον Ubuntu στο WSL και να εκτελεί εντολές Docker από το ίδιο shell. Ο παρών οδηγός καλύπτει μόνο αυτή την προπαρασκευαστική φάση. Με την ολοκλήρωσή του, το σύστημα θα είναι έτοιμο για τον οδηγό Docker και για το onboarding του μέρους Kubernetes.

Ο κανονικός κώδικας και τα βοηθητικά αρχεία της προπαρασκευαστικής διαδρομής βρίσκονται πλέον στον κατάλογο `code/00_workstation-setup`. Αν διαβάζετε το υλικό πριν αποκτήσετε το πρώτο τοπικό αντίγραφο του αποθετηρίου, χρησιμοποιήστε τα παρακάτω snippets ως τα έγκυρα βήματα εκτέλεσης και συνεχίστε με το βήμα `04`, όπου γίνεται και το clone του repository.

## Δομή της προετοιμασίας

| # | Φάκελος | Στόχος |
|---|---------|--------|
| 01 | `code/00_workstation-setup/01_wsl-bootstrap` | Ενεργοποίηση WSL2, εγκατάσταση Ubuntu και βασικά εργαλεία |
| 02 | `code/00_workstation-setup/02_docker-desktop-wsl` | Προτεινόμενη εγκατάσταση με Docker Desktop και ενσωμάτωση στο WSL |
| 03 | `code/00_workstation-setup/03_native-docker-engine` | Προαιρετική εγκατάσταση εγγενούς Docker Engine μέσα στο WSL |
| 04 | `code/00_workstation-setup/04_validation` | Τελικός έλεγχος και τοπικό clone του repository |

## 01. WSL και Ubuntu

Πριν από οποιαδήποτε χρήση Docker, τα Windows πρέπει να παρέχουν λειτουργικό περιβάλλον `WSL2` και μια διανομή Ubuntu. Το βήμα αυτό ενεργοποιεί τις απαραίτητες δυνατότητες των Windows, εγκαθιστά το Ubuntu και προετοιμάζει το shell με τα βασικά εργαλεία που θα χρειαστούν αμέσως μετά.

Ανοίξτε PowerShell ως διαχειριστής από το μενού Έναρξη.

![Εικόνα 1](images/img1.png)

### `enable-wsl.ps1`

Εκτελέστε πρώτα το παρακάτω περιεχόμενο από ανυψωμένο PowerShell. Μετά την εκτέλεσή του απαιτείται επανεκκίνηση των Windows.

<!-- AUTO-CODE: code/00_workstation-setup/01_wsl-bootstrap/enable-wsl.ps1 -->
``` powershell
# Run this script from an elevated PowerShell window.
wsl --install --no-distribution
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```
<!-- END AUTO-CODE -->

![Εικόνα 2](images/img23.png)

![Εικόνα 3](images/img20.png)

### `install-ubuntu.ps1`

Μετά την επανεκκίνηση, ολοκληρώστε την εγκατάσταση της διανομής Ubuntu.

<!-- AUTO-CODE: code/00_workstation-setup/01_wsl-bootstrap/install-ubuntu.ps1 -->
``` powershell
# Install Ubuntu after the first restart.
wsl --install -d Ubuntu
```
<!-- END AUTO-CODE -->

Στη συνέχεια, ανοίξτε το Ubuntu από το μενού Έναρξη και δημιουργήστε τον λογαριασμό χρήστη του WSL.

![Εικόνα 4](images/img4.png)

![Εικόνα 5](images/img7.png)

### `ubuntu-first-update.sh`

Από το Ubuntu terminal, ενημερώστε το σύστημα και εγκαταστήστε τα πρώτα απαραίτητα εργαλεία. Η παρουσία του `git` ήδη από αυτό το στάδιο είναι χρήσιμη, ώστε το τοπικό clone του repository να γίνει αμέσως μετά χωρίς δεύτερο προπαρασκευαστικό βήμα.

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

Τέλος, επιστρέψτε σε PowerShell για να επιβεβαιώσετε ότι το WSL και το `VirtualMachinePlatform` είναι σωστά ρυθμισμένα.

<!-- AUTO-CODE: code/00_workstation-setup/01_wsl-bootstrap/check-wsl.ps1 -->
``` powershell
# Show the installed distributions and their WSL versions.
wsl --list --verbose

# Confirm that the Virtual Machine Platform feature is enabled.
Get-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
```
<!-- END AUTO-CODE -->

Αν η εγκατάσταση έχει ολοκληρωθεί σωστά, η διανομή `Ubuntu` εμφανίζεται με έκδοση `2` και το `VirtualMachinePlatform` εμφανίζεται ως `Enabled`.

## 02. Docker Desktop με WSL integration

Για τους περισσότερους φοιτητές, αυτή είναι η προτεινόμενη διαδρομή. Ο Docker daemon παραμένει στη διαχείριση του Docker Desktop, αλλά η καθημερινή χρήση γίνεται από το Ubuntu terminal του WSL, που είναι και το shell περιβάλλον των επόμενων οδηγών.

Κατεβάστε το Docker Desktop από την επίσημη σελίδα του Docker για Windows x86_64:

https://docs.docker.com/desktop/setup/install/windows-install/

Κατά την εγκατάσταση, βεβαιωθείτε ότι είναι ενεργή η επιλογή `Use the WSL 2 based engine`.

![Εικόνα 6](images/img18.png)

![Εικόνα 7](images/img11.png)

Μετά την εγκατάσταση, ανοίξτε το Docker Desktop, ελέγξτε ότι το `WSL 2 based engine` παραμένει ενεργό και ενεργοποιήστε τη διανομή Ubuntu στην ενότητα `Resources -> WSL Integration`.

![Εικόνα 8](images/img21.png)

![Εικόνα 9](images/img12.png)

Αν το Docker Desktop ζητήσει λογαριασμό, μπορείτε να παρακάμψετε αυτό το βήμα.

![Εικόνα 10](images/img3.png)

### `verify-docker-desktop.sh`

Όταν το Docker Desktop είναι έτοιμο, ανοίξτε νέο Ubuntu terminal και εκτελέστε τον ακόλουθο έλεγχο.

<!-- AUTO-CODE: code/00_workstation-setup/02_docker-desktop-wsl/verify-docker-desktop.sh -->
``` bash
#!/usr/bin/env bash
set -euo pipefail

docker version
docker compose version
docker run --rm hello-world
```
<!-- END AUTO-CODE -->

Η επιτυχής εκτέλεση του `hello-world` δείχνει ότι το integration μεταξύ Docker Desktop και WSL λειτουργεί κανονικά.

![Εικόνα 11](images/img5.png)

![Εικόνα 12](images/img25.png)

## 03. Native Docker Engine μέσα στο WSL

Η διαδρομή αυτή είναι προαιρετική και απευθύνεται σε όσους θέλουν να εργαστούν αποκλειστικά μέσα από το Ubuntu, χωρίς Docker Desktop στα Windows. Το μάθημα την υποστηρίζει, αλλά απαιτεί λίγο προσεκτικότερη διαχείριση του τοπικού περιβάλλοντος.

Πριν από την εγκατάσταση, ελέγξτε αν το Ubuntu shell τρέχει ήδη με ενεργό `systemd`, εκτελώντας:

```bash
systemctl is-system-running
```

Αν χρειάζεται να ενεργοποιήσετε το `systemd`, χρησιμοποιήστε το παρακάτω περιεχόμενο στο `/etc/wsl.conf`.

### `wsl.conf.example`

<!-- AUTO-CODE: code/00_workstation-setup/03_native-docker-engine/wsl.conf.example -->
``` ini
[boot]
systemd=true
```
<!-- END AUTO-CODE -->

Μετά την αλλαγή, επανεκκινήστε το WSL από PowerShell.

### `restart-wsl.ps1`

<!-- AUTO-CODE: code/00_workstation-setup/03_native-docker-engine/restart-wsl.ps1 -->
``` powershell
# Restart WSL after editing /etc/wsl.conf.
wsl --shutdown
```
<!-- END AUTO-CODE -->

Ανοίξτε ξανά το Ubuntu και προχωρήστε στην εγκατάσταση του Docker Engine.

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

Μετά την ολοκλήρωση του script, κλείστε και ανοίξτε ξανά το Ubuntu terminal ή εκτελέστε μία φορά `newgrp docker`, ώστε να ενεργοποιηθεί η νέα ομάδα χρήστη.

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

Αν ο έλεγχος αυτός ολοκληρωθεί χωρίς `sudo`, τότε η native εγκατάσταση είναι έτοιμη για χρήση στον οδηγό Docker.

## 04. Τελικός έλεγχος και τοπικό clone

Από τη στιγμή που λειτουργούν οι εντολές `docker version`, `docker compose version` και `docker run --rm hello-world`, η προπαρασκευή του περιβάλλοντος είναι ουσιαστικά ολοκληρωμένη. Το τελευταίο βήμα είναι να υπάρχει και τοπικό clone του repository μέσα στο WSL, ώστε τα παραδείγματα των οδηγών να μπορούν να εκτελεστούν απευθείας.

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

Μετά την επιτυχή ολοκλήρωση του ελέγχου αυτού, μπορείτε να συνεχίσετε στον οδηγό [docs/01_lab1-docker/README.md](../01_lab1-docker/README.md).

## Τι θεωρείται ολοκληρωμένο

- Το WSL2 και το Ubuntu λειτουργούν κανονικά.
- Έχει επιλεγεί μία από τις δύο διαδρομές Docker και οι εντολές `docker` / `docker compose` λειτουργούν από το Ubuntu shell.
- Το repository υπάρχει τοπικά στο `~/cloud-uth`.
- Το περιβάλλον είναι έτοιμο για την εκτέλεση των παραδειγμάτων του `code/01_docker` και για το Kubernetes onboarding που ακολουθεί.
