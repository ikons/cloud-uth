# 🌩️ Νεφοϋπολογιστική

Καλωσορίσατε στο αποθετήριο του μαθήματος **Νεφοϋπολογιστική** του Τμήματος Πληροφορικής και Τηλεπικοινωνιών του Πανεπιστημίου Θεσσαλίας. Το αποθετήριο αυτό περιέχει:

✅ Παραδείγματα με χρήση Docker & Docker Compose  
✅ Πλήρη οδηγό για σύνδεση με την υποδομή Kubernetes του εργαστηρίου μέσω OpenVPN  
✅ Υλοποιήσεις σε Kubernetes: Pods, Deployments, StatefulSets, Volumes, ConfigMaps, Secrets και Services
✅ Τεκμηρίωση σε μορφή Markdown με παραγόμενους οδηγούς Word

## 📁 Δομή Οδηγιών

| Ενότητα | Περιγραφή |
|--------|-----------|
| [00_Preparatory-lab](docs/00_Preparatory-lab/) | Προετοιμασία σταθμού εργασίας με WSL2 και Docker |
| [01_lab1-docker](docs/01_lab1-docker/) | Εισαγωγή στο Docker με πρακτικά παραδείγματα |
| [01_lab1-k8s](docs/01_lab1-k8s/) | Είσοδος στο μέρος του Kubernetes, με kubectl, k9s, Deployments, PVCs, StatefulSets, Volumes, ConfigMaps, Secrets και Services |

## 🚀 Εκκίνηση

```bash
git clone https://github.com/ikons/cloud-uth.git
cd cloud-uth
```

Ο κανονικός κώδικας των παραδειγμάτων βρίσκεται στον φάκελο `code/`. Όπου οι οδηγοί εμφανίζουν ολόκληρα αρχεία παραδείγματος, τα blocks συγχρονίζονται από αυτά τα αρχεία ώστε το README και ο εκτελέσιμος κώδικας να μένουν ταυτόσημα.

## 🧭 Δομή Προετοιμασίας

- `code/00_workstation-setup`: τα κανονικά βήματα για WSL, Docker Desktop, εγγενή Docker Engine και τελικό έλεγχο του σταθμού εργασίας

## 🧭 Δομή Παραδειγμάτων

- `code/01_docker`: η προοδευτική ακολουθία των Docker παραδειγμάτων
- `code/02_kubernetes`: η προοδευτική ακολουθία των Kubernetes παραδειγμάτων, από το πρώτο Pod και τις υπηρεσίες πρόσβασης μέχρι τον HPA και το συνθετικό παράδειγμα εφαρμογής ιστού

Στη διαδρομή της προετοιμασίας, το `docs/00_Preparatory-lab` λειτουργεί ως κεντρικός οδηγός και τα κανονικά scripts και snippets βρίσκονται στα επιμέρους `README.md` και `README.en.md` του `code/00_workstation-setup/*`.

Στη διαδρομή του Kubernetes, το `docs/01_lab1-k8s` λειτουργεί ως κεντρικός οδηγός προετοιμασίας και πλοήγησης, ενώ η αναλυτική εκτέλεση πραγματοποιείται μέσα από τα επιμέρους `README.md` και `README.en.md` των καταλόγων `code/02_kubernetes/*`.

Για συνεπή ελληνική ορολογία στους οδηγούς του μαθήματος, συμβουλευτείτε το [`glossary.md`](glossary.md).

> 💡 Βεβαιωθείτε ότι έχετε εγκαταστήσει:
> - `Docker Desktop` (με WSL2 backend), ή προαιρετικά native `Docker Engine` μέσα στο WSL
> - OpenVPN Client
> - `kubectl` και `k9s`

## 📝 Οδηγοί Word

Οι οδηγοί Word στον φάκελο `odigoi/` παράγονται από τα Markdown αρχεία του `docs/` μέσω Pandoc.
Σε Windows, το `scripts/export-docx.ps1` και το `make -C docs docx` προσπαθούν πρώτα να χρησιμοποιήσουν το Microsoft Word για αυτόματη ανανέωση του πίνακα περιεχομένων και, αν δεν είναι διαθέσιμο, κάνουν fallback σε LibreOffice.
