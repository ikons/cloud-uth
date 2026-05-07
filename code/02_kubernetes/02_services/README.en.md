# Accessing an application through a Service

Once a Pod has been created, the next question is how it can be reached through a stable network endpoint inside the cluster. In this exercise we introduce the `Service` object, which connects to Pods through labels and selectors and provides a stable name for network access.

## Learning objectives

- Understand why a Pod is not enough as an access point (its IP is ephemeral) and recognize the solution: `Service`.
- Connect a `Service` to a Pod through the **labels–selector** pair.
- Distinguish `port` (Service port) from `targetPort` (container port).
- Reach an in-cluster service from your machine using `kubectl port-forward`.

## How this fits in the sequence

Step 01 produced a single Pod with no stable access point. This step unlocks the networking side of Kubernetes: `Service` is the first object to use the **labels & selectors** mechanism that you will see again in `ReplicaSet`, `Deployment`, and `StatefulSet`.

## Example files

The Pod that will serve HTTP requests is defined as follows:

<!-- AUTO-CODE: code/02_kubernetes/02_services/nginx-pod.yaml -->
``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-pod
  labels:
    # The Service selects this Pod through the app label.
    app: web
    tier: frontend
spec:
  containers:
    - name: nginx
      image: nginx:latest
      ports:
        # Nginx listens on port 80 inside the container.
        - containerPort: 80
```
<!-- END AUTO-CODE -->

The `Service` that forwards traffic to the Pod is the following:

<!-- AUTO-CODE: code/02_kubernetes/02_services/nginx-service.yaml -->
``` yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  selector:
    # Match the Pod label declared in nginx-pod.yaml.
    app: web
  ports:
    # Expose the same HTTP port through a stable Service name.
    - port: 80
      targetPort: 80
  type: ClusterIP
```
<!-- END AUTO-CODE -->

## Execution

Begin by moving into the exercise directory:

```bash
cd ~/cloud-uth/code/02_kubernetes/02_services
```

Then create both the Pod and the `Service`:

```bash
kubectl apply -f nginx-pod.yaml
kubectl apply -f nginx-service.yaml
```

To confirm that the resources were created correctly and that the `Service` selector matches the intended Pod, inspect the following:

```bash
kubectl get pod web-pod
kubectl get svc web-service
kubectl describe svc web-service
```

The simplest way to test the result from a local browser is to use `port-forward`:

```bash
kubectl port-forward svc/web-service 8080:80
```

After that, open `http://127.0.0.1:8080`. If local port `8080` is already in use, change only the left-hand side of the mapping:

```bash
kubectl port-forward svc/web-service 8081:80
```

## Verification and common pitfalls

- Success: `http://127.0.0.1:8080` shows the Nginx welcome page in your browser.
- `kubectl get endpoints web-service` should show the Pod's IP. **Empty `ENDPOINTS`** means the Service `selector` does not match any Pod — check that labels match exactly (case-sensitive).
- If the browser shows `connection refused`: the most common cause is a wrong `targetPort`. It must equal the `containerPort` of the Pod.
- `kubectl port-forward` terminates when its terminal exits — keep a second terminal open for `curl`/browser.

## Cleanup

Once the test is complete, and from a new terminal if `port-forward` is still running, delete the resources:

```bash
kubectl delete -f nginx-service.yaml
kubectl delete -f nginx-pod.yaml
```
