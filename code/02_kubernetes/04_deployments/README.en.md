# Deployment: updates and rollback

In practice, most stateless workloads are not managed directly through `ReplicaSet`, but through `Deployment`. A `Deployment` adds controlled rollout behavior, revision history, and rollback support so that new application versions can be introduced safely.

## Example files

The first manifest shows the basic form of a `Deployment`:

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

The second manifest declares an explicit rolling update strategy:

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

## Execution

Begin by moving into the exercise directory:

```bash
cd ~/cloud-uth/code/02_kubernetes/04_deployments
```

First create the basic `Deployment` and verify that its replicas became available:

```bash
kubectl apply -f basic-deployment.yaml
kubectl rollout status deployment/nginx-deployment
kubectl get deployment nginx-deployment
kubectl get pods -l app=nginx-deploy
```

Then apply the second example and perform a controlled image update:

```bash
kubectl apply -f rolling-update.yaml
kubectl rollout status deployment/nginx-rolling
kubectl set image deployment/nginx-rolling nginx=nginx:1.25
kubectl rollout status deployment/nginx-rolling
kubectl rollout history deployment/nginx-rolling
```

If necessary, the previous revision can be restored:

```bash
kubectl rollout undo deployment/nginx-rolling
kubectl rollout status deployment/nginx-rolling
```

## Cleanup

After the exercise is complete, delete both `Deployment` examples:

```bash
kubectl delete -f basic-deployment.yaml
kubectl delete -f rolling-update.yaml
```
