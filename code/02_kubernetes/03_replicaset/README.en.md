# ReplicaSet: maintaining multiple replicas

The next concept we introduce is the `ReplicaSet`, that is, the Kubernetes mechanism that keeps a fixed number of identical Pods in existence. This example demonstrates both scaling and self-healing, because the system automatically replaces a Pod that is deleted.

For consistent terminology across the course guides, consult [glossary.md](../../../glossary.md).

## Learning objectives

- Declare a desired number of replicas (`replicas`) and confirm that Kubernetes maintains it.
- Observe self-healing: when you delete a Pod, a new one is created automatically.
- Recognize that the ReplicaSet `selector` must match the labels in its `template`.
- Know that **in practice** we do not use a bare `ReplicaSet`, but a `Deployment` (which manages ReplicaSets for us) — this exercise is the foundation for the next step.

## How this fits in the sequence

Until now we had a single Pod with no survival guarantee. The `ReplicaSet` introduces the **controller** concept: an object that continuously watches the cluster and reconciles it back to the desired state. This control pattern is fundamental throughout Kubernetes — the `Deployment` of the next step is built on top of it.

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

## Verification and common pitfalls

- Success: `kubectl get rs nginx-replicaset` reports `DESIRED=3 CURRENT=3 READY=3` and three Pods are `Running`.
- After deleting one Pod, `kubectl get pods -w` should display a new Pod within a few seconds.
- Common mistake: changing the image in the `template` does **not** trigger a rolling update on a bare `ReplicaSet` — existing Pods keep the old image. This is exactly why `Deployment` exists in the next step.
- If the labels in the `template` do not match the `selector`, the API server rejects the manifest with a clear error.

## Cleanup

At the end of the exercise, delete the `ReplicaSet` and all the Pods it manages:

```bash
kubectl delete -f my-replicaset.yaml
```
