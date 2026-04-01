# Μόνιμη και προσωρινή αποθήκευση

Η άσκηση αυτή συνδέει το Kubernetes με όσα είδαμε ήδη στα Docker volumes. Συγκρίνουμε δύο Pods: το πρώτο χρησιμοποιεί `PersistentVolumeClaim` και επομένως διατηρεί τα δεδομένα του μετά από αναδημιουργία, ενώ το δεύτερο βασίζεται αποκλειστικά στο προσωρινό filesystem του container.

## Αρχεία του παραδείγματος

Το `PersistentVolumeClaim` που θα χρησιμοποιηθεί από το μόνιμο παράδειγμα είναι το εξής:

<!-- AUTO-CODE: code/02_kubernetes/07_storage/nginx-pvc.yaml -->
``` yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: web-data
spec:
  # One node can mount this volume read-write at a time.
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```
<!-- END AUTO-CODE -->

Το Pod που χρησιμοποιεί μόνιμο αποθηκευτικό χώρο ορίζεται ως εξής:

<!-- AUTO-CODE: code/02_kubernetes/07_storage/nginx-persistent.yaml -->
``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-persistent
spec:
  containers:
    - name: nginx
      image: nginx:latest
      ports:
        - containerPort: 80
      volumeMounts:
        # Store the default Nginx content on a persistent volume.
        - name: web-storage
          mountPath: /usr/share/nginx/html
  volumes:
    - name: web-storage
      persistentVolumeClaim:
        # Reuse the PVC defined in nginx-pvc.yaml.
        claimName: web-data
```
<!-- END AUTO-CODE -->

Αντίθετα, το παρακάτω Pod δεν χρησιμοποιεί κανένα μόνιμο volume:

<!-- AUTO-CODE: code/02_kubernetes/07_storage/nginx-ephemeral.yaml -->
``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-ephemeral
spec:
  containers:
    - name: nginx
      image: nginx:latest
      ports:
        # This Pod uses only the container filesystem, so data is temporary.
        - containerPort: 80
```
<!-- END AUTO-CODE -->

## Εκτέλεση

Μεταβαίνουμε πρώτα στον κατάλογο της άσκησης:

```bash
cd ~/cloud-uth/code/02_kubernetes/07_storage
```

Έπειτα δημιουργούμε το `PersistentVolumeClaim` και τα δύο Pods:

```bash
kubectl apply -f nginx-pvc.yaml
kubectl apply -f nginx-persistent.yaml
kubectl apply -f nginx-ephemeral.yaml
kubectl wait --for=jsonpath='{.status.phase}'=Bound pvc/web-data --timeout=120s
kubectl wait --for=condition=Ready pod/nginx-persistent --timeout=180s
kubectl wait --for=condition=Ready pod/nginx-ephemeral --timeout=180s
```

Για να φανεί καθαρά η διαφορά, γράφουμε διαφορετικό περιεχόμενο σε κάθε Pod:

```bash
kubectl exec nginx-persistent -- sh -c 'echo persistent-data > /usr/share/nginx/html/index.html'
kubectl exec nginx-ephemeral -- sh -c 'echo ephemeral-data > /usr/share/nginx/html/index.html'
```

Στη συνέχεια διαγράφουμε και αναδημιουργούμε και τα δύο Pods:

```bash
kubectl delete pod nginx-persistent nginx-ephemeral
kubectl apply -f nginx-persistent.yaml
kubectl apply -f nginx-ephemeral.yaml
kubectl wait --for=condition=Ready pod/nginx-persistent --timeout=180s
kubectl wait --for=condition=Ready pod/nginx-ephemeral --timeout=180s
```

Τέλος συγκρίνουμε το αποτέλεσμα:

```bash
kubectl exec nginx-persistent -- cat /usr/share/nginx/html/index.html
kubectl exec nginx-ephemeral -- sh -c "grep -q 'ephemeral-data' /usr/share/nginx/html/index.html && echo still-there || echo reset"
```

Αναμένουμε ότι το `nginx-persistent` θα διατηρεί το `persistent-data`, ενώ το `nginx-ephemeral` θα έχει επανέλθει στην αρχική του κατάσταση.

## Καθαρισμός

Μετά την ολοκλήρωση της άσκησης διαγράφουμε τα Pods και το `PersistentVolumeClaim`:

```bash
kubectl delete -f nginx-ephemeral.yaml
kubectl delete -f nginx-persistent.yaml
kubectl delete -f nginx-pvc.yaml
```
