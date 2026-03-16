# 🌩️ Νεφοϋπολογιστική

Καλωσορίσατε στο αποθετήριο του μαθήματος **Νεφοϋπολογιστική** του Τμήματος Πληροφορικής και Τηλεπικοινωνιών του Πανεπιστημίου Θεσσαλίας. Το αποθετήριο αυτό περιέχει:

✅ Παραδείγματα με χρήση Docker & Docker Compose  
✅ Πλήρη οδηγό για σύνδεση με την υποδομή Kubernetes του εργαστηρίου μέσω OpenVPN  
✅ Υλοποιήσεις σε Kubernetes: Pods, Deployments, StatefulSets, Volumes, ConfigMaps, Secrets και Services
✅ Τεκμηρίωση σε μορφή Markdown με παραγόμενους οδηγούς Word

## 📁 Δομή Οδηγιών

| Ενότητα | Περιγραφή |
|--------|-----------|
| [00_Preparatory-lab](docs/00_Preparatory-lab/) | Ρύθμιση Docker Desktop με WSL2 |
| [01_lab1-docker](docs/01_lab1-docker/) | Εισαγωγή στο Docker με πρακτικά παραδείγματα |
| [01_lab1-k8s](docs/01_lab1-k8s/) | Kubernetes, kubectl, k9s, Deployments, PVCs, StatefulSets, Volumes, ConfigMaps, Secrets και Services |

## 🚀 Εκκίνηση

```bash
git clone https://github.com/ikons/cloud-uth.git
cd cloud-uth
```

> 💡 Βεβαιωθείτε ότι έχετε εγκαταστήσει:
> - Docker Desktop (με WSL2 backend)
> - OpenVPN Client
> - `kubectl` και `k9s`

## 📝 Οδηγοί Word

Οι οδηγοί Word στον φάκελο `odigoi/` παράγονται από τα Markdown αρχεία του `docs/` μέσω Pandoc.
Σε Windows, το `scripts/export-docx.ps1` και το `make -C docs docx` χρησιμοποιούν επίσης το Microsoft Word για να ανανεώσουν αυτόματα τον πίνακα περιεχομένων.
