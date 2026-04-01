# First exercise: creating a Pod

In this first exercise we run a simple Nginx Pod in order to become familiar with the basic structure of a Kubernetes manifest and with the minimum inspection commands provided by `kubectl`. At this stage the emphasis is not yet on networking or scaling, but on understanding the lifecycle of a single workload.

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

## Cleanup

After completing the exercise, remove the Pod:

```bash
kubectl delete -f nginx-pod.yaml
```
