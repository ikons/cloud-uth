# StatefulSet: σταθερή ταυτότητα και αποθήκευση ανά Pod

Όταν κάθε replica πρέπει να έχει σταθερό όνομα, σταθερή δικτυακή ταυτότητα και δικό της ανεξάρτητο volume, ένα `Deployment` δεν επαρκεί. Σε αυτή την περίπτωση χρησιμοποιούμε `StatefulSet`, σε συνδυασμό με headless `Service` και `volumeClaimTemplates`.

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

## Καθαρισμός

Μετά το τέλος της άσκησης διαγράφουμε το `StatefulSet`, το headless `Service` και τα PVCs που δημιουργήθηκαν:

```bash
kubectl delete -f statefulset.yaml
kubectl delete -f headless-service.yaml
kubectl delete pvc data-web-0 data-web-1 data-web-2 --ignore-not-found
```
