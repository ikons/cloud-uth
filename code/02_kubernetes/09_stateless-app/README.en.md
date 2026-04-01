# Stateless web application

In this step we combine three concepts that have already been introduced separately: `ConfigMap`, `Deployment`, and `Service`. The result is a small stateless web application in which the page content remains externalized as configuration and the requests are served by multiple interchangeable replicas.

## Example files

The HTML content of the application is stored in a `ConfigMap`:

<!-- AUTO-CODE: code/02_kubernetes/09_stateless-app/app-html.yaml -->
``` yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: web-html
data:
  # Serve a small static page without rebuilding the container image.
  index.html: |
    <!DOCTYPE html>
    <html>
    <head><title>Stateless App</title></head>
    <body>
      <h1>Hello from Kubernetes!</h1>
      <p>This is a stateless web application.</p>
      <p>Each request may be served by a different Pod.</p>
    </body>
    </html>
```
<!-- END AUTO-CODE -->

The `Deployment` ensures that two replicas run with the same content:

<!-- AUTO-CODE: code/02_kubernetes/09_stateless-app/deployment.yaml -->
``` yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
        - name: nginx
          image: nginx:latest
          ports:
            - containerPort: 80
          resources:
            # Requests and limits document the expected footprint of the Pod.
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 200m
              memory: 128Mi
          volumeMounts:
            # Mount the HTML content provided by the ConfigMap.
            - name: html
              mountPath: /usr/share/nginx/html
      volumes:
        - name: html
          configMap:
            name: web-html
```
<!-- END AUTO-CODE -->

Finally, the `Service` exposes the workload through a stable endpoint:

<!-- AUTO-CODE: code/02_kubernetes/09_stateless-app/service.yaml -->
``` yaml
apiVersion: v1
kind: Service
metadata:
  name: web-app
spec:
  selector:
    # Route traffic to the Deployment Pods through their shared app label.
    app: web-app
  ports:
    - port: 80
      targetPort: 80
  type: ClusterIP
```
<!-- END AUTO-CODE -->

## Execution

Begin by moving into the exercise directory:

```bash
cd ~/cloud-uth/code/02_kubernetes/09_stateless-app
```

Then create all resources and wait for the `Deployment` rollout to complete:

```bash
kubectl apply -f app-html.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl rollout status deployment/web-app
```

To confirm that both the replicas and the `Service` behave as expected, inspect:

```bash
kubectl get pods -l app=web-app -o wide
kubectl get svc web-app
```

Local browser access is provided through `port-forward`:

```bash
kubectl port-forward svc/web-app 8080:80
```

Then open `http://127.0.0.1:8080`. If local port `8080` is not available, use another port instead, for example:

```bash
kubectl port-forward svc/web-app 8081:80
```

## Cleanup

After the exercise is complete, delete the `Service`, the `Deployment`, and the `ConfigMap`:

```bash
kubectl delete -f service.yaml
kubectl delete -f deployment.yaml
kubectl delete -f app-html.yaml
```
