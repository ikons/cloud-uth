# ConfigMap: external configuration

An application often requires settings or text files that should not be permanently embedded in the container image. For this purpose Kubernetes provides `ConfigMaps`, which allow a workload to be configured externally.

## Example files

The `ConfigMap` in this exercise stores two simple variables and one text file:

<!-- AUTO-CODE: code/02_kubernetes/05_configmaps/app-config.yaml -->
``` yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  # Keys can be consumed as environment variables.
  APP_COLOR: blue
  APP_MODE: production
  # Multi-line values can also be mounted as files.
  welcome.txt: |
    Welcome to our Kubernetes application!
    This message is stored in a ConfigMap.
```
<!-- END AUTO-CODE -->

The Pod below consumes the same `ConfigMap` both as environment variables and as a mounted file:

<!-- AUTO-CODE: code/02_kubernetes/05_configmaps/pod-with-config.yaml -->
``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-config
spec:
  containers:
    - name: app
      image: alpine:latest
      command: ["sh", "-c"]
      args:
        - |
          # Print both the injected environment variables and the mounted file.
          echo "=== Environment Variables from ConfigMap ==="
          echo "APP_COLOR: $APP_COLOR"
          echo "APP_MODE: $APP_MODE"
          echo ""
          echo "=== File from ConfigMap ==="
          cat /config/welcome.txt
          echo ""
          echo "Sleeping..."
          sleep 3600
      env:
        - name: APP_COLOR
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: APP_COLOR
        - name: APP_MODE
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: APP_MODE
      volumeMounts:
        # Mount the ConfigMap as regular files under /config.
        - name: config-volume
          mountPath: /config
  volumes:
    - name: config-volume
      configMap:
        name: app-config
```
<!-- END AUTO-CODE -->

## Execution

Begin by moving into the exercise directory:

```bash
cd ~/cloud-uth/code/02_kubernetes/05_configmaps
```

Then create the `ConfigMap` and the Pod that consumes it:

```bash
kubectl apply -f app-config.yaml
kubectl apply -f pod-with-config.yaml
kubectl wait --for=condition=Ready pod/app-with-config --timeout=120s
```

The behavior of the example becomes visible in the Pod logs:

```bash
kubectl logs app-with-config
```

The output will include both the values injected as environment variables and the contents of the `welcome.txt` file mounted under `/config`.

If we want to inspect the resource as stored by the Kubernetes API, we use:

```bash
kubectl get configmap app-config -o yaml
```

## Cleanup

After the exercise is complete, delete the Pod and the `ConfigMap`:

```bash
kubectl delete -f pod-with-config.yaml
kubectl delete -f app-config.yaml
```
