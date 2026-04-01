# StatefulSet: stable identity and per-Pod storage

When each replica must keep a stable name, a stable network identity, and its own independent volume, a `Deployment` is no longer sufficient. In that case we use a `StatefulSet`, together with a headless `Service` and `volumeClaimTemplates`.

## Example files

The headless `Service`, which provides stable DNS naming for the Pods in the `StatefulSet`, is defined as follows:

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

The `StatefulSet` itself is described by the following manifest:

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

## Execution

Begin by moving into the exercise directory:

```bash
cd ~/cloud-uth/code/02_kubernetes/08_statefulsets
```

Then create the headless `Service` and the `StatefulSet`:

```bash
kubectl apply -f headless-service.yaml
kubectl apply -f statefulset.yaml
kubectl rollout status statefulset/web --timeout=240s
```

To observe the stable identity of the replicas, inspect the Pods and the associated `PersistentVolumeClaims`:

```bash
kubectl get pods -l app=web-sts
kubectl get pvc
```

You should see names such as `web-0`, `web-1`, and `web-2`, together with distinct PVCs for each replica.

If you want to confirm that each Pod keeps its own storage, you may run the following optional check:

```bash
for pod in web-0 web-1 web-2; do kubectl exec "$pod" -- sh -c "echo $pod > /usr/share/nginx/html/index.html"; done
kubectl delete pod web-1
kubectl wait --for=condition=Ready pod/web-1 --timeout=180s
kubectl exec web-1 -- cat /usr/share/nginx/html/index.html
```

`web-1` will be recreated with the same name and will continue to see its own dedicated volume.

## Cleanup

At the end of the exercise, delete the `StatefulSet`, the headless `Service`, and the PVCs that were created:

```bash
kubectl delete -f statefulset.yaml
kubectl delete -f headless-service.yaml
kubectl delete pvc data-web-0 data-web-1 data-web-2 --ignore-not-found
```
