# Πρώτη άσκηση: δημιουργία ενός Pod

Στην πρώτη αυτή άσκηση εκτελούμε ένα απλό Pod με Nginx, ώστε να εξοικειωθούμε με τη βασική μορφή ενός manifest και με τις ελάχιστες εντολές παρακολούθησης που παρέχει το `kubectl`. Σκοπός δεν είναι ακόμη η δικτύωση ή η κλιμάκωση, αλλά η κατανόηση του κύκλου ζωής ενός μεμονωμένου workload.

## Αρχείο παραδείγματος

Το manifest του παραδείγματος είναι το ακόλουθο:

<!-- AUTO-CODE: code/02_kubernetes/01_first-pod/nginx-pod.yaml -->
``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-nginx
  labels:
    # Keep a simple application label for later kubectl selectors.
    app: nginx
spec:
  containers:
    - name: nginx
      image: nginx:latest
      ports:
        # Expose HTTP inside the Pod network namespace.
        - containerPort: 80
```
<!-- END AUTO-CODE -->

## Εκτέλεση

Αρχικά μεταβαίνουμε στον κατάλογο του παραδείγματος:

```bash
cd ~/cloud-uth/code/02_kubernetes/01_first-pod
```

Έπειτα εφαρμόζουμε το manifest:

```bash
kubectl apply -f nginx-pod.yaml
```

Για να επιβεβαιώσουμε ότι το Pod δημιουργήθηκε και πέρασε σε κατάσταση λειτουργίας, ελέγχουμε συνοπτικά την κατάστασή του και, όπου χρειάζεται, τα αναλυτικά συμβάντα του:

```bash
kubectl get pod my-nginx -o wide
kubectl describe pod my-nginx
```

Το πεδίο `STATUS` αναμένεται να γίνει `Running`. Αν εμφανιστεί διαφορετική κατάσταση, το `describe` είναι η πρώτη εντολή στην οποία πρέπει να ανατρέξουμε.

## Καθαρισμός

Μετά την ολοκλήρωση της άσκησης διαγράφουμε το Pod:

```bash
kubectl delete -f nginx-pod.yaml
```
