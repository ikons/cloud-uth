# Deployment: ενημερώσεις και επαναφορά

Στην πράξη τα περισσότερα φορτία εργασίας χωρίς κατάσταση δεν διαχειρίζονται απευθείας με `ReplicaSet`, αλλά με `Deployment`. Το `Deployment` προσθέτει μηχανισμούς αναβάθμισης, ιστορικού εκδόσεων και επαναφοράς, ώστε η διαχείριση νέων εκδόσεων να γίνεται ελεγχόμενα.

Για συνεπή ελληνική ορολογία στους οδηγούς του μαθήματος, ανατρέξτε στο [glossary.md](../../../glossary.md).

## Παιδαγωγικοί στόχοι

- Να αναβαθμίσετε εφαρμογή σε νέα έκδοση image με `kubectl set image` και να παρακολουθήσετε rolling update.
- Να εξετάσετε ιστορικό εκδόσεων με `kubectl rollout history` και να επαναφέρετε προηγούμενη με `kubectl rollout undo`.
- Να ρυθμίσετε `maxSurge`/`maxUnavailable` και να καταλάβετε πώς επηρεάζουν τη διαθεσιμότητα κατά την αναβάθμιση.
- Να επιλέγετε `Deployment` (όχι σκέτο ReplicaSet) ως προεπιλογή για όλα τα φορτία εργασίας χωρίς κατάσταση.

## Σύνδεση με την ακολουθία

Το `Deployment` είναι ο **πρακτικός** τρόπος να δηλώσετε εφαρμογές χωρίς κατάσταση. Δημιουργεί και διαχειρίζεται ReplicaSets για εσάς, και είναι το αντικείμενο που θα χρησιμοποιήσετε στα επόμενα παραδείγματα (`09_stateless-app`, `10_autoscaling`, `12_app-from-source`). Στα επόμενα δύο βήματα θα δούμε πώς εξωτερικοποιούμε ρύθμιση (`ConfigMap`) και μυστικά (`Secret`) — τα δύο πιο συνηθισμένα δεδομένα που "μπαίνουν" σε ένα Deployment.

## Αρχεία του παραδείγματος

Το πρώτο manifest δείχνει την απλή μορφή ενός `Deployment`:

<!-- AUTO-CODE: code/02_kubernetes/04_deployments/basic-deployment.yaml -->
``` yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  # Deploy three interchangeable Nginx replicas.
  replicas: 3
  selector:
    matchLabels:
      app: nginx-deploy
  template:
    metadata:
      labels:
        app: nginx-deploy
    spec:
      containers:
        - name: nginx
          image: nginx:1.24
          ports:
            # The container serves HTTP traffic on port 80.
            - containerPort: 80
```
<!-- END AUTO-CODE -->

Το δεύτερο manifest δηλώνει ρητά στρατηγική rolling update:

<!-- AUTO-CODE: code/02_kubernetes/04_deployments/rolling-update.yaml -->
``` yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-rolling
spec:
  replicas: 3
  strategy:
    # Replace Pods gradually to avoid full downtime during updates.
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 1
  selector:
    matchLabels:
      app: nginx-rolling
  template:
    metadata:
      labels:
        app: nginx-rolling
    spec:
      containers:
        - name: nginx
          image: nginx:1.24
          ports:
            # Keep the same container port across rollout revisions.
            - containerPort: 80
```
<!-- END AUTO-CODE -->

## Εκτέλεση

Μεταβαίνουμε πρώτα στον κατάλογο της άσκησης:

```bash
cd ~/cloud-uth/code/02_kubernetes/04_deployments
```

Δημιουργούμε αρχικά το βασικό `Deployment` και ελέγχουμε ότι τα replicas έγιναν διαθέσιμα:

```bash
kubectl apply -f basic-deployment.yaml
kubectl rollout status deployment/nginx-deployment
kubectl get deployment nginx-deployment
kubectl get pods -l app=nginx-deploy
```

Στη συνέχεια εφαρμόζουμε το δεύτερο παράδειγμα και εκτελούμε μια ελεγχόμενη αλλαγή εικόνας:

```bash
kubectl apply -f rolling-update.yaml
kubectl rollout status deployment/nginx-rolling
kubectl set image deployment/nginx-rolling nginx=nginx:1.25
kubectl rollout status deployment/nginx-rolling
kubectl rollout history deployment/nginx-rolling
```

Εφόσον χρειαστεί, μπορούμε να επαναφέρουμε την προηγούμενη έκδοση:

```bash
kubectl rollout undo deployment/nginx-rolling
kubectl rollout status deployment/nginx-rolling
```

## Επιβεβαίωση επιτυχίας και κοινά λάθη

- Επιτυχία: `kubectl rollout status` τερματίζει με `successfully rolled out` και `kubectl get deployment nginx-rolling` δείχνει `READY=3/3 UP-TO-DATE=3 AVAILABLE=3`.
- Το `kubectl rollout history` πρέπει να δείχνει τουλάχιστον δύο εκδόσεις (revisions) μετά το `set image`.
- Αν η νέα έκδοση παρουσιάζει `CrashLoopBackOff`, το Deployment θα κρατήσει τα παλιά Pods να εξυπηρετούν κίνηση μέχρι να γίνει `kubectl rollout undo`. **Μην** προσπαθήσετε να τα διαγράψετε χειροκίνητα.
- Συχνή παρανόηση: το `kubectl edit deployment` τριγγάρει νέο rollout — δεν είναι "πλάγια αλλαγή" στα ήδη υπάρχοντα Pods.
- Με `maxUnavailable: 0` εξασφαλίζετε zero-downtime αναβάθμιση, αλλά χρειάζεστε επαρκή πόρους για επιπλέον Pods κατά τη διάρκεια.

## Καθαρισμός

Μετά την ολοκλήρωση της άσκησης διαγράφουμε και τα δύο `Deployment` παραδείγματα:

```bash
kubectl delete -f basic-deployment.yaml
kubectl delete -f rolling-update.yaml
```
