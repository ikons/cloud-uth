# Secret: handling sensitive data

`Secrets` serve a purpose similar to that of `ConfigMaps`, but they are meant for data that should not be treated as ordinary application configuration. Typical examples include passwords, tokens, and other access credentials that should remain separate from both source code and non-sensitive settings.

For consistent terminology across the course guides, consult [glossary.md](../../../glossary.md).

## Learning objectives

- Distinguish `Secret` from `ConfigMap` and know **when** to pick each one.
- Use `stringData` for ergonomic authoring while knowing the API stores values **base64-encoded**.
- Consume a Secret both as an env var and as a read-only file mount.
- Recognize that base64 is **not encryption** — it is just encoding. Protection comes from RBAC and access policies on the Kubernetes API.

## How this fits in the sequence

Step 05 externalized general configuration. This step does the same for credentials, with the proper resource type. Secrets will be paired with Pods/Deployments in every later example that involves a database (`11_web-app`, `12_app-from-source`).

## Example files

The `Secret` in this exercise defines two simple credentials:

<!-- AUTO-CODE: code/02_kubernetes/06_secrets/db-credentials.yaml -->
``` yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
type: Opaque
stringData:
  # stringData is convenient in examples; Kubernetes stores it encoded.
  username: postgres
  password: supersecret
```
<!-- END AUTO-CODE -->

The next Pod uses the same `Secret` in two different ways: as a mounted file and as an environment variable:

<!-- AUTO-CODE: code/02_kubernetes/06_secrets/pod-with-secret.yaml -->
``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-secret
spec:
  containers:
    - name: app
      image: alpine:latest
      command: ["sh", "-c"]
      args:
        - |
          # Demonstrate the Secret both as files and as environment variables.
          echo "=== Credentials from Secret ==="
          echo "Username: $(cat /etc/db-credentials/username)"
          echo "Password: $(cat /etc/db-credentials/password)"
          echo ""
          echo "=== As environment variables ==="
          echo "DB_USER: $DB_USER"
          echo ""
          echo "Sleeping..."
          sleep 3600
      env:
        - name: DB_USER
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: username
      volumeMounts:
        # Mount the Secret read-only to avoid accidental writes.
        - name: secret-volume
          mountPath: /etc/db-credentials
          readOnly: true
  volumes:
    - name: secret-volume
      secret:
        secretName: db-credentials
```
<!-- END AUTO-CODE -->

## Execution

Begin by moving into the exercise directory:

```bash
cd ~/cloud-uth/code/02_kubernetes/06_secrets
```

Then create the `Secret` and the Pod that consumes it:

```bash
kubectl apply -f db-credentials.yaml
kubectl apply -f pod-with-secret.yaml
kubectl wait --for=condition=Ready pod/app-with-secret --timeout=120s
```

The behavior of the example becomes visible in the logs:

```bash
kubectl logs app-with-secret
```

The output will show the same `Secret` both as mounted content under `/etc/db-credentials` and as an environment variable.

If we want to inspect the resource from the perspective of the Kubernetes API, we use:

```bash
kubectl get secret db-credentials -o yaml
```

Note that the manifest uses `stringData`, whereas the Kubernetes API stores the resulting values in base64-encoded form.

## Verification and common pitfalls

- Success: the logs show `Username: postgres`, `Password: supersecret`, and the same value as `DB_USER=postgres` env var.
- `kubectl get secret -o yaml` shows values in **base64-encoded** form. That is correct, not an error. To decode: `echo <encoded> | base64 -d`.
- **Critical**: never commit a Secret YAML containing real values to a public git repo. In real workflows these are produced by tools such as `kubectl create secret`, sealed-secrets, or external secret managers.
- Secret mounts use `readOnly: true` to prevent accidental writes from the application.

## Cleanup

After the exercise is complete, delete the Pod and the `Secret`:

```bash
kubectl delete -f pod-with-secret.yaml
kubectl delete -f db-credentials.yaml
```
