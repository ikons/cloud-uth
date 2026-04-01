# Horizontal autoscaling with HPA

At this stage we move from static scaling to the dynamic adjustment of replica count. The `HorizontalPodAutoscaler` monitors resource usage and increases or decreases the number of Pods in a `Deployment` according to the load handled by the application.

## Example files

### `deployment.yaml`

<!-- AUTO-CODE: code/02_kubernetes/10_autoscaling/deployment.yaml -->
``` yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: php-apache
spec:
  replicas: 1
  selector:
    matchLabels:
      app: php-apache
  template:
    metadata:
      labels:
        app: php-apache
    spec:
      containers:
        - name: php-apache
          image: registry.k8s.io/hpa-example
          ports:
            - containerPort: 80
          resources:
            # HPA uses CPU requests as the baseline for utilization targets.
            requests:
              cpu: 200m
            limits:
              cpu: 500m
---
apiVersion: v1
kind: Service
metadata:
  name: php-apache
spec:
  selector:
    # Keep the Service label in sync with the Deployment selector.
    app: php-apache
  ports:
    - port: 80
      targetPort: 80
```
<!-- END AUTO-CODE -->

### `hpa.yaml`

<!-- AUTO-CODE: code/02_kubernetes/10_autoscaling/hpa.yaml -->
``` yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: php-apache
spec:
  # Scale the php-apache Deployment between one and five replicas.
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: php-apache
  minReplicas: 1
  maxReplicas: 5
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          # Aim for an average CPU utilization of 50% across replicas.
          type: Utilization
          averageUtilization: 50
```
<!-- END AUTO-CODE -->

## Execution

Begin by moving into the exercise directory:

```bash
cd ~/cloud-uth/code/02_kubernetes/10_autoscaling
```

Then create the `Deployment` and the `HorizontalPodAutoscaler`:

```bash
kubectl apply -f deployment.yaml
kubectl apply -f hpa.yaml
kubectl rollout status deployment/php-apache
kubectl get hpa php-apache
```

During the first few seconds, the current metric may appear as `<unknown>` until the metrics system has collected its initial samples.

If you want to observe scaling in real time, watch the HPA in one terminal:

```bash
kubectl get hpa php-apache -w
```

and generate artificial load from a second terminal:

```bash
kubectl run -i --tty load-generator --rm --image=busybox:1.36 --restart=Never -- /bin/sh
while true; do wget -q -O- http://php-apache; done
```

Once the loop is stopped with `Ctrl+C`, the HPA will gradually reduce the number of replicas again.

## Cleanup

After the exercise is complete, delete both the HPA and the `Deployment`:

```bash
kubectl delete -f hpa.yaml
kubectl delete -f deployment.yaml
```
