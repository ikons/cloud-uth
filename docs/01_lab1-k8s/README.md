# Kubernetes στο εργαστήριο VDCLOUD

Ο παρών οδηγός λειτουργεί ως κεντρική είσοδος για το μέρος του μαθήματος που αφορά το Kubernetes. Η πρακτική άσκηση έχει οργανωθεί σε διαδοχικά, αυτοτελή παραδείγματα κάτω από τον κατάλογο `code/02_kubernetes`, ώστε οι φοιτητές να εργάζονται πάνω στα ίδια ακριβώς αρχεία που παρουσιάζονται στους οδηγούς και όχι σε αποσπασματικά αντίγραφα κώδικα.

## Τι λαμβάνεις με email

Μετά τη συμπλήρωση της φόρμας πρόσβασης, λαμβάνεις:

- ένα username για το προσωπικό σου namespace στο εργαστήριο
- το αρχείο `vdcloud-k8s.ovpn`
- το αρχείο `config` για το `kubectl`

Το username αυτό αντιστοιχεί συνήθως σε context και namespace της μορφής `<username>-priv`.

## Τοπικό clone του repository

Η βασική υπόθεση του οδηγού είναι ότι δουλεύεις από WSL και έχεις το repository στο home directory σου. Αν έχεις ήδη ολοκληρώσει το `00_workstation-setup`, αυτό το clone υπάρχει ήδη και αρκεί να μπεις ξανά στον ίδιο κατάλογο. Αν όχι, μπορείς να χρησιμοποιήσεις την παρακάτω idempotent μορφή:

```bash
cd ~
if [ ! -d cloud-uth/.git ]; then
  git clone https://github.com/ikons/cloud-uth.git
fi
cd cloud-uth
```

Για να το κρατάς ενημερωμένο:

```bash
git pull
```

## OpenVPN και kubeconfig

### Σύνδεση στο VPN

Στα Windows εγκατέστησε τον [OpenVPN client](https://openvpn.net/community-downloads/), εισήγαγε το `vdcloud-k8s.ovpn` και συνδέσου.

### Αντιγραφή του `config` στο WSL

Υποθέτοντας ότι το κατέβασες στο `Downloads` του χρήστη των Windows:

```bash
mkdir -p ~/.kube
cp /mnt/c/Users/<windows-username>/Downloads/config ~/.kube/config
chmod 600 ~/.kube/config
```

## Γρήγορος έλεγχος σύνδεσης

```bash
kubectl config current-context
kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}{"\n"}'
kubectl get pods
```

Τα αναμενόμενα αποτελέσματα είναι τα εξής:

- ενεργό context: `<username>-priv`
- διεύθυνση του cluster: `https://source-code-master.cluster.local:6443`

Στον συγκεκριμένο cluster εργαζόμαστε με εντολές περιορισμένες στο προσωπικό namespace. Δεν πρέπει να βασιζόμαστε σε διαχειριστικές εντολές συστοιχίας όπως `kubectl get nodes`.

## Εργαλεία

Ελάχιστο σύνολο:

- `kubectl`
- προαιρετικά `k9s`

Εγκατάσταση `kubectl` σε Ubuntu/WSL:

```bash
sudo apt-get install -y apt-transport-https ca-certificates curl gnupg
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.32/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
sudo chmod 644 /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.32/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo chmod 644 /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl
```

Προαιρετικά, για `k9s`:

```bash
wget https://github.com/derailed/k9s/releases/download/v0.40.10/k9s_linux_amd64.deb
sudo dpkg -i k9s_linux_amd64.deb
echo "export KUBE_EDITOR=nano" >> ~/.bashrc
```

## Δομή της ακολουθίας ασκήσεων

| Βήμα | Κατάλογος | Έννοια |
|------|-----------|---------|
| 01 | `code/02_kubernetes/01_first-pod` | Pod + `kubectl` |
| 02 | `code/02_kubernetes/02_services` | Υπηρεσίες πρόσβασης |
| 03 | `code/02_kubernetes/03_replicaset` | Διατήρηση πολλαπλών αντιγράφων |
| 04 | `code/02_kubernetes/04_deployments` | Αναβαθμίσεις και επαναφορά |
| 05 | `code/02_kubernetes/05_configmaps` | Εξωτερική παραμετροποίηση |
| 06 | `code/02_kubernetes/06_secrets` | Ευαίσθητα δεδομένα |
| 07 | `code/02_kubernetes/07_storage` | Μόνιμη αποθήκευση και PVC |
| 08 | `code/02_kubernetes/08_statefulsets` | Σταθερή ταυτότητα και αποθήκευση ανά Pod |
| 09 | `code/02_kubernetes/09_stateless-app` | Εφαρμογή ιστού χωρίς κατάσταση |
| 10 | `code/02_kubernetes/10_autoscaling` | Οριζόντια αυτόματη κλιμάκωση με HPA |
| 11 | `code/02_kubernetes/11_web-app` | Συνθετικό παράδειγμα εφαρμογής ιστού |
| 12 | `code/02_kubernetes/12_app-from-source` | End-to-end ανάπτυξη Python εφαρμογής (code → image → deploy) |

Τα βήματα `01` έως `09` αποτελούν τον βασικό διδακτικό κορμό του εργαστηρίου. Τα `10` και `11` βασίζονται στις ίδιες έννοιες και λειτουργούν ως προχωρημένες εφαρμογές τους. Το `12` κλείνει την ακολουθία δείχνοντας πώς γράφετε δική σας εφαρμογή, την κάνετε build/push σε registry και την αναπτύσσετε στο cluster.

## Κανόνες εκτέλεσης

- Δούλευε από το WSL clone σου, συνήθως `~/cloud-uth`
- Μπες κάθε φορά στον αντίστοιχο κατάλογο του βήματος πριν τρέξεις εντολές
- Όταν χρησιμοποιείς `kubectl port-forward`, αν η τοπική πόρτα είναι πιασμένη άλλαξε μόνο το αριστερό μέρος της αντιστοίχισης, π.χ. `8081:80`
- Μετά από κάθε βήμα κάνε cleanup για να μην αφήνεις πόρους στο namespace σου

## Πρώτη δοκιμή

Για την πρώτη άσκηση:

```bash
cd ~/cloud-uth/code/02_kubernetes/01_first-pod
kubectl apply -f nginx-pod.yaml
kubectl get pod my-nginx -o wide
kubectl delete -f nginx-pod.yaml
```

Από εκεί και πέρα η συνιστώμενη πορεία είναι να συνεχιστεί η μελέτη σειριακά, ακολουθώντας τα `README.md` και `README.en.md` των επόμενων καταλόγων.
