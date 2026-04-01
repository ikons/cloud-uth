# Deployment: ενημερώσεις και επαναφορά

Στην πράξη τα περισσότερα stateless workloads δεν διαχειρίζονται απευθείας με `ReplicaSet`, αλλά με `Deployment`. Το `Deployment` προσθέτει μηχανισμούς αναβάθμισης, ιστορικού εκδόσεων και επαναφοράς, ώστε η διαχείριση νέων εκδόσεων να γίνεται ελεγχόμενα.

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

## Καθαρισμός

Μετά την ολοκλήρωση της άσκησης διαγράφουμε και τα δύο `Deployment` παραδείγματα:

```bash
kubectl delete -f basic-deployment.yaml
kubectl delete -f rolling-update.yaml
```
