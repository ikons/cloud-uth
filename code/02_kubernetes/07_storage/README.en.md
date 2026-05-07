# Persistent and ephemeral storage

This exercise connects Kubernetes storage with the Docker volume concepts discussed earlier. We compare two Pods: the first uses a `PersistentVolumeClaim` and therefore retains its data after recreation, while the second relies entirely on the temporary filesystem of the container.

For consistent terminology across the course guides, consult [glossary.md](../../../glossary.md).

## Learning objectives

- Request persistent storage through a `PersistentVolumeClaim` and understand the relationship PVC ↔ PV ↔ StorageClass.
- Compare a Pod backed by an ephemeral filesystem with one backed by a PVC.
- Recognize access modes (`ReadWriteOnce`, `ReadWriteMany`) and pick the right one for the use case.
- Verify experimentally that data on a PVC survives Pod recreation.

## How this fits in the sequence

All previous examples were stateless: if the Pod was lost, its local data went with it — and that was acceptable. This step introduces the distinction that is a prerequisite for databases (next: `08_statefulsets`, and later `11_web-app` with PostgreSQL).

## Example files

The `PersistentVolumeClaim` used by the persistent example is the following:

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

The Pod that uses persistent storage is defined as follows:

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

By contrast, the following Pod uses no persistent volume at all:

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

## Execution

Begin by moving into the exercise directory:

```bash
cd ~/cloud-uth/code/02_kubernetes/07_storage
```

Then create the `PersistentVolumeClaim` and both Pods:

```bash
kubectl apply -f nginx-pvc.yaml
kubectl apply -f nginx-persistent.yaml
kubectl apply -f nginx-ephemeral.yaml
kubectl wait --for=jsonpath='{.status.phase}'=Bound pvc/web-data --timeout=120s
kubectl wait --for=condition=Ready pod/nginx-persistent --timeout=180s
kubectl wait --for=condition=Ready pod/nginx-ephemeral --timeout=180s
```

To make the difference visible, write different content into each Pod:

```bash
kubectl exec nginx-persistent -- sh -c 'echo persistent-data > /usr/share/nginx/html/index.html'
kubectl exec nginx-ephemeral -- sh -c 'echo ephemeral-data > /usr/share/nginx/html/index.html'
```

Next, delete and recreate both Pods:

```bash
kubectl delete pod nginx-persistent nginx-ephemeral
kubectl apply -f nginx-persistent.yaml
kubectl apply -f nginx-ephemeral.yaml
kubectl wait --for=condition=Ready pod/nginx-persistent --timeout=180s
kubectl wait --for=condition=Ready pod/nginx-ephemeral --timeout=180s
```

Finally, compare the result:

```bash
kubectl exec nginx-persistent -- cat /usr/share/nginx/html/index.html
kubectl exec nginx-ephemeral -- sh -c "grep -q 'ephemeral-data' /usr/share/nginx/html/index.html && echo still-there || echo reset"
```

We expect `nginx-persistent` to retain `persistent-data`, while `nginx-ephemeral` should return to its initial state.

## Verification and common pitfalls

- Success: after recreation, `nginx-persistent` still returns `persistent-data` while `nginx-ephemeral` reports `reset` — confirming that the PVC kept the data and the ephemeral filesystem did not.
- The PVC must reach `STATUS=Bound` before `nginx-persistent` can start. Use `kubectl get pvc` to check.
- If the PVC stays `Pending` for a long time: there is no StorageClass that can satisfy the claim. Rare in this lab but a common failure point on other clusters.
- `ReadWriteOnce` means "one node at a time", **not** "one Pod at a time". Pods on the same node can share the volume.

## Cleanup

After the exercise is complete, delete the Pods and the `PersistentVolumeClaim`:

```bash
kubectl delete -f nginx-ephemeral.yaml
kubectl delete -f nginx-persistent.yaml
kubectl delete -f nginx-pvc.yaml
```
