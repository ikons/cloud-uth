# ReplicaSet: διατήρηση πολλαπλών αντιγράφων

Η επόμενη έννοια που εισάγουμε είναι το `ReplicaSet`, δηλαδή ο μηχανισμός με τον οποίο το Kubernetes διατηρεί σταθερό πλήθος όμοιων Pods. Το παράδειγμα αυτό δείχνει τόσο την έννοια της κλιμάκωσης όσο και την έννοια της αυτοΐασης, αφού το σύστημα αναπληρώνει αυτόματα ένα Pod που διαγράφεται.

## Αρχείο παραδείγματος

Το manifest του `ReplicaSet` είναι το ακόλουθο:

<!-- AUTO-CODE: code/02_kubernetes/03_replicaset/my-replicaset.yaml -->
``` yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: nginx-replicaset
spec:
  # Keep three identical Pods running at all times.
  replicas: 3
  selector:
    matchLabels:
      app: nginx-rs
  template:
    metadata:
      labels:
        app: nginx-rs
    spec:
      containers:
        - name: nginx
          image: nginx:latest
          ports:
            # Expose HTTP inside each replica.
            - containerPort: 80
```
<!-- END AUTO-CODE -->

## Εκτέλεση

Μεταβαίνουμε πρώτα στον κατάλογο του παραδείγματος:

```bash
cd ~/cloud-uth/code/02_kubernetes/03_replicaset
```

Στη συνέχεια δημιουργούμε το `ReplicaSet`:

```bash
kubectl apply -f my-replicaset.yaml
```

Για να επιβεβαιώσουμε ότι ο ζητούμενος αριθμός αντιγράφων τηρείται, ελέγχουμε τόσο το ίδιο το `ReplicaSet` όσο και τα Pods που δημιούργησε:

```bash
kubectl get rs nginx-replicaset
kubectl get pods -l app=nginx-rs -o wide
```

Η αναμενόμενη κατάσταση είναι η παρουσία τριών Pods.

Για να φανεί η συμπεριφορά αυτοΐασης, διαγράφουμε ένα από αυτά και παρακολουθούμε άμεσα το αποτέλεσμα:

```bash
kubectl delete pod $(kubectl get pods -l app=nginx-rs -o jsonpath='{.items[0].metadata.name}')
kubectl get pods -l app=nginx-rs -w
```

Το Kubernetes θα δημιουργήσει νέο Pod, ώστε ο συνολικός αριθμός αντιγράφων να παραμείνει αμετάβλητος.

## Καθαρισμός

Μετά το τέλος της άσκησης διαγράφουμε το `ReplicaSet` και όλα τα Pods που ελέγχει:

```bash
kubectl delete -f my-replicaset.yaml
```
