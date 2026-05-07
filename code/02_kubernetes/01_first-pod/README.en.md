# First exercise: creating a Pod

In this first exercise we run a simple Nginx Pod in order to become familiar with the basic structure of a Kubernetes manifest and with the minimum inspection commands provided by `kubectl`. At this stage the emphasis is not yet on networking or scaling, but on understanding the lifecycle of a single workload.

## Learning objectives

- Apply your first manifest with `kubectl apply -f` and recognize the four core fields of a Kubernetes object: `apiVersion`, `kind`, `metadata`, `spec`.
- Observe the Pod lifecycle (`Pending → ContainerCreating → Running`).
- Become comfortable with the basic inspection commands `kubectl get` and `kubectl describe`.
- Connect the Pod concept to the container you used in the Docker part: a Pod is a Kubernetes wrapper around (usually) one container.

## How this fits in the sequence

A Pod is the minimum deployable unit in Kubernetes — every higher-level object (`ReplicaSet`, `Deployment`, `StatefulSet`) eventually produces Pods. The next step shows that a Pod by itself does not offer a stable access point, which motivates the introduction of `Service`.

## Example file

The manifest used in this exercise is the following:

<!-- AUTO-CODE: code/02_kubernetes/01_first-pod/nginx-pod.yaml -->
``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-nginx
  labels:
    # Keep a simple application label for later kubectl selectors.
    app: nginx
spec:
  containers:
    - name: nginx
      image: nginx:latest
      ports:
        # Expose HTTP inside the Pod network namespace.
        - containerPort: 80
```
<!-- END AUTO-CODE -->

## Execution

Begin by moving into the example directory:

```bash
cd ~/cloud-uth/code/02_kubernetes/01_first-pod
```

Then apply the manifest:

```bash
kubectl apply -f nginx-pod.yaml
```

To verify that the Pod was created correctly and reached a healthy running state, inspect both its summary and, when needed, its detailed event history:

```bash
kubectl get pod my-nginx -o wide
kubectl describe pod my-nginx
```

The `STATUS` field is expected to become `Running`. If a different state appears, `describe` is the first command you should consult.

## Verification and common pitfalls

- Success: `kubectl get pod my-nginx` shows `STATUS=Running` and `READY=1/1`.
- If the Pod stays in `Pending`: usually a wrong image name or insufficient resources in the namespace. `kubectl describe pod my-nginx` shows the precise `Events`.
- If it stays in `ContainerCreating` for more than 30s: the cluster is probably pulling the image. Check `describe` again.
- Common confusion: a Pod does not expose a stable IP to the outside world. The `Service` introduced in the next step solves this — do not try to connect directly to the Pod's IP.

## Cleanup

After completing the exercise, remove the Pod:

```bash
kubectl delete -f nginx-pod.yaml
```
