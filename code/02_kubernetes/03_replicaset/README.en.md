# ReplicaSet: maintaining multiple replicas

The next concept we introduce is the `ReplicaSet`, that is, the Kubernetes mechanism that keeps a fixed number of identical Pods in existence. This example demonstrates both scaling and self-healing, because the system automatically replaces a Pod that is deleted.

## Example file

The `ReplicaSet` manifest used in this exercise is the following:

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

## Execution

Begin by moving into the example directory:

```bash
cd ~/cloud-uth/code/02_kubernetes/03_replicaset
```

Then create the `ReplicaSet`:

```bash
kubectl apply -f my-replicaset.yaml
```

To confirm that the requested number of replicas is being maintained, inspect both the `ReplicaSet` itself and the Pods it created:

```bash
kubectl get rs nginx-replicaset
kubectl get pods -l app=nginx-rs -o wide
```

The expected result is the presence of three Pods.

To observe self-healing in practice, delete one of them and watch the set immediately reconcile:

```bash
kubectl delete pod $(kubectl get pods -l app=nginx-rs -o jsonpath='{.items[0].metadata.name}')
kubectl get pods -l app=nginx-rs -w
```

Kubernetes will create a replacement Pod so that the total number of replicas remains unchanged.

## Cleanup

At the end of the exercise, delete the `ReplicaSet` and all the Pods it manages:

```bash
kubectl delete -f my-replicaset.yaml
```
