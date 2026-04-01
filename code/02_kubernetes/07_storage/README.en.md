# Persistent and ephemeral storage

This exercise connects Kubernetes storage with the Docker volume concepts discussed earlier. We compare two Pods: the first uses a `PersistentVolumeClaim` and therefore retains its data after recreation, while the second relies entirely on the temporary filesystem of the container.

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

## Cleanup

After the exercise is complete, delete the Pods and the `PersistentVolumeClaim`:

```bash
kubectl delete -f nginx-ephemeral.yaml
kubectl delete -f nginx-persistent.yaml
kubectl delete -f nginx-pvc.yaml
```
