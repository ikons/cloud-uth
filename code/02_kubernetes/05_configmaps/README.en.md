# ConfigMap: external configuration

An application often requires settings or text files that should not be permanently embedded in the container image. For this purpose Kubernetes provides `ConfigMaps`, which allow a workload to be configured externally.

For consistent terminology across the course guides, consult [glossary.md](../../../glossary.md).

## Learning objectives

- Externalize configuration so that the same image can run in different environments.
- Choose between the two consumption modes of a `ConfigMap`: **environment variables** (simple values) and **mounted files** (text files or multi-line content).
- Recognize that a `ConfigMap` is meant only for **non-sensitive** data. Use `Secret` for credentials (next step).
- Understand that updating a ConfigMap does **not** automatically restart the Pods that consume it as env vars.

## How this fits in the sequence

Until now all application behavior was baked into the image. This step lets you change settings without rebuilding. The next step does the same for sensitive data using the proper resource type (`Secret`).

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

## Verification and common pitfalls

- Success: `kubectl logs app-with-config` shows the env-var values (`APP_COLOR: blue`, `APP_MODE: production`) and the contents of `welcome.txt`.
- If the Pod is stuck in `ContainerCreating` with `MountVolume.SetUp failed`, the ConfigMap is usually missing — apply `app-config.yaml` first, then the Pod.
- Important behavior difference for updates:
  - **Env vars** sourced from a ConfigMap are **not** refreshed in a running Pod. A restart (new rollout) is required.
  - **Mounted files** are eventually consistent — they update a few seconds after the ConfigMap edit.
- Common mistake: putting sensitive data (passwords, tokens) into a ConfigMap. That is a poor practice — use `Secret`.

## Cleanup

After the exercise is complete, delete the Pod and the `ConfigMap`:

```bash
kubectl delete -f pod-with-config.yaml
kubectl delete -f app-config.yaml
```
