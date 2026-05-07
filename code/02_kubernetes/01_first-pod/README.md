# Πρώτη άσκηση: δημιουργία ενός Pod

Στην πρώτη αυτή άσκηση εκτελούμε ένα απλό Pod με Nginx, ώστε να εξοικειωθούμε με τη βασική μορφή ενός manifest και με τις ελάχιστες εντολές παρακολούθησης που παρέχει το `kubectl`. Σκοπός δεν είναι ακόμη η δικτύωση ή η κλιμάκωση, αλλά η κατανόηση του κύκλου ζωής ενός μεμονωμένου workload.

## Παιδαγωγικοί στόχοι

- Να εφαρμόσετε το πρώτο σας manifest με `kubectl apply -f` και να αναγνωρίζετε τα τέσσερα βασικά πεδία ενός Kubernetes object: `apiVersion`, `kind`, `metadata`, `spec`.
- Να παρατηρήσετε τον κύκλο ζωής ενός Pod (`Pending → ContainerCreating → Running`).
- Να εξοικειωθείτε με τις βασικές εντολές παρατήρησης `kubectl get` και `kubectl describe`.
- Να συνδέσετε την έννοια του Pod με τον container που είδατε στο μέρος Docker: ένα Pod είναι το περιτύλιγμα ενός (συνήθως) container μέσα στο Kubernetes.

## Σύνδεση με την ακολουθία

Το Pod είναι η ελάχιστη μονάδα ανάπτυξης στο Kubernetes — οτιδήποτε μεγαλύτερο (`ReplicaSet`, `Deployment`, `StatefulSet`) τελικά δημιουργεί Pods. Στο επόμενο βήμα θα δούμε ότι ένα Pod από μόνο του δεν προσφέρει σταθερό σημείο πρόσβασης, και θα προσθέσουμε `Service`.

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

## Επιβεβαίωση επιτυχίας και κοινά λάθη

- Επιτυχία: `kubectl get pod my-nginx` επιστρέφει `STATUS=Running` και `READY=1/1`.
- Αν το Pod μένει σε `Pending`: συνήθως λάθος όνομα image ή έλλειψη πόρων στο namespace. Το `kubectl describe pod my-nginx` εμφανίζει το ακριβές `Events`.
- Αν μένει σε `ContainerCreating` πάνω από 30s: το cluster πιθανώς κατεβάζει την image. Δείτε ξανά με `describe`.
- Συχνή σύγχυση: το Pod δεν διαθέτει σταθερή IP από τον έξω κόσμο. Γι' αυτό υπάρχει το `Service` στο επόμενο βήμα — μην προσπαθήσετε να συνδεθείτε απευθείας στην IP του Pod.

## Καθαρισμός

Μετά την ολοκλήρωση της άσκησης διαγράφουμε το Pod:

```bash
kubectl delete -f nginx-pod.yaml
```
