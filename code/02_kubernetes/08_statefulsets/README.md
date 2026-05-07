# StatefulSet: σταθερή ταυτότητα και αποθήκευση ανά Pod

Όταν κάθε replica πρέπει να έχει σταθερό όνομα, σταθερή δικτυακή ταυτότητα και δικό της ανεξάρτητο volume, ένα `Deployment` δεν επαρκεί. Σε αυτή την περίπτωση χρησιμοποιούμε `StatefulSet`, σε συνδυασμό με headless `Service` και `volumeClaimTemplates`.

Για συνεπή ελληνική ορολογία στους οδηγούς του μαθήματος, ανατρέξτε στο [glossary.md](../../../glossary.md).

## Παιδαγωγικοί στόχοι

- Να αναγνωρίζετε πότε ένα `Deployment` δεν επαρκεί: όταν τα replicas χρειάζονται μοναδική, σταθερή ταυτότητα.
- Να συνδέσετε `StatefulSet` με headless `Service` για DNS-based discovery (`web-0.web-headless`, `web-1.web-headless`, …).
- Να καταλάβετε τη χρήση `volumeClaimTemplates`: ένα PVC ανά replica, αυτόματα.
- Να επιβεβαιώσετε με δοκιμή ότι κάθε replica διατηρεί το όνομα και το αποθηκευτικό του χώρο μετά από διαγραφή.

## Σύνδεση με την ακολουθία

Μέχρι το 04_deployments τα replicas ήταν εναλλάξιμα — αυτό αρκεί για εφαρμογές χωρίς κατάσταση. Πραγματικές βάσεις δεδομένων όμως απαιτούν ξεχωριστή ταυτότητα και αποθηκευτικό χώρο ανά instance (π.χ. ο leader μιας replication topology). Στο 11 θα δούμε ότι μια απλή Postgres του παραδείγματος μπορεί να τρέξει και σε σκέτο Pod, αλλά για clustered databases το `StatefulSet` είναι ο σωστός τρόπος.

## Αρχεία του παραδείγματος

Το headless `Service`, το οποίο προσφέρει σταθερή DNS ονοματοδοσία στα Pods του `StatefulSet`, ορίζεται ως εξής:

<!-- AUTO-CODE: code/02_kubernetes/08_statefulsets/headless-service.yaml -->
``` yaml
apiVersion: v1
kind: Service
metadata:
  name: web-headless
spec:
  # A headless Service gives stable DNS names to StatefulSet Pods.
  clusterIP: None
  selector:
    app: web-sts
  ports:
    - port: 80
      name: http
```
<!-- END AUTO-CODE -->

Το ίδιο το `StatefulSet` περιγράφεται από το ακόλουθο manifest:

<!-- AUTO-CODE: code/02_kubernetes/08_statefulsets/statefulset.yaml -->
``` yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  # This must match the headless Service name used for stable network identity.
  serviceName: web-headless
  replicas: 3
  selector:
    matchLabels:
      app: web-sts
  template:
    metadata:
      labels:
        app: web-sts
    spec:
      containers:
        - name: nginx
          image: nginx:latest
          ports:
            - containerPort: 80
          volumeMounts:
            # Each Pod receives its own PVC from the template below.
            - name: data
              mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
    # Kubernetes creates one PVC per replica: data-web-0, data-web-1, and so on.
    - metadata:
        name: data
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 256Mi
```
<!-- END AUTO-CODE -->

## Εκτέλεση

Μεταβαίνουμε πρώτα στον κατάλογο της άσκησης:

```bash
cd ~/cloud-uth/code/02_kubernetes/08_statefulsets
```

Στη συνέχεια δημιουργούμε το headless `Service` και το `StatefulSet`:

```bash
kubectl apply -f headless-service.yaml
kubectl apply -f statefulset.yaml
kubectl rollout status statefulset/web --timeout=240s
```

Για να φανεί η σταθερή ταυτότητα των replicas, ελέγχουμε τα Pods και τα αντίστοιχα `PersistentVolumeClaims`:

```bash
kubectl get pods -l app=web-sts
kubectl get pvc
```

Θα εμφανιστούν ονόματα όπως `web-0`, `web-1` και `web-2`, καθώς και ξεχωριστά PVCs για κάθε replica.

Αν θέλουμε να επιβεβαιώσουμε ότι κάθε Pod διατηρεί το δικό του αποθηκευτικό χώρο, μπορούμε να εκτελέσουμε την ακόλουθη προαιρετική δοκιμή:

```bash
for pod in web-0 web-1 web-2; do kubectl exec "$pod" -- sh -c "echo $pod > /usr/share/nginx/html/index.html"; done
kubectl delete pod web-1
kubectl wait --for=condition=Ready pod/web-1 --timeout=180s
kubectl exec web-1 -- cat /usr/share/nginx/html/index.html
```

Το `web-1` θα αναδημιουργηθεί με το ίδιο όνομα και θα εξακολουθεί να βλέπει το δικό του volume.

## Επιβεβαίωση επιτυχίας και κοινά λάθη

- Επιτυχία: `kubectl get pods -l app=web-sts` δείχνει `web-0`, `web-1`, `web-2` σε `Running`. Στο `kubectl get pvc` εμφανίζονται `data-web-0`, `data-web-1`, `data-web-2`.
- Τα Pods δημιουργούνται **σειριακά** (`web-0` → `web-1` → `web-2`), όχι παράλληλα. Αυτό είναι σχεδιαστικό για state-aware συστήματα και κάνει το startup πιο αργό από ένα `Deployment`.
- Διαγραφή ενός Pod (π.χ. `web-1`) επαναφέρει **το ίδιο όνομα** και επανασυνδέει το **ίδιο PVC**. Αυτή η διασφάλιση είναι το κύριο διαχωριστικό από το Deployment.
- **Σημαντικό**: η διαγραφή του StatefulSet **δεν** διαγράφει τα PVCs — γι' αυτό τα διαγράφουμε ρητά. Αυτή η σχεδίαση προστατεύει τα δεδομένα σε περίπτωση λάθους.

## Καθαρισμός

Μετά το τέλος της άσκησης διαγράφουμε το `StatefulSet`, το headless `Service` και τα PVCs που δημιουργήθηκαν:

```bash
kubectl delete -f statefulset.yaml
kubectl delete -f headless-service.yaml
kubectl delete pvc data-web-0 data-web-1 data-web-2 --ignore-not-found
```
