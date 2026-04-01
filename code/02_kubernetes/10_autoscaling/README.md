# Οριζόντια αυτόματη κλιμάκωση με HPA

Στο σημείο αυτό περνάμε από τη στατική κλιμάκωση στη δυναμική προσαρμογή του αριθμού των replicas. Ο `HorizontalPodAutoscaler` παρακολουθεί μετρικές χρήσης και αυξομειώνει τα Pods του `Deployment` ανάλογα με το φορτίο που δέχεται η εφαρμογή.

## Αρχεία του παραδείγματος

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

## Εκτέλεση

Μεταβαίνουμε πρώτα στον κατάλογο της άσκησης:

```bash
cd ~/cloud-uth/code/02_kubernetes/10_autoscaling
```

Στη συνέχεια δημιουργούμε το `Deployment` και τον `HorizontalPodAutoscaler`:

```bash
kubectl apply -f deployment.yaml
kubectl apply -f hpa.yaml
kubectl rollout status deployment/php-apache
kubectl get hpa php-apache
```

Κατά τα πρώτα δευτερόλεπτα είναι πιθανό η τρέχουσα μετρική να εμφανιστεί ως `<unknown>`, έως ότου το σύστημα metrics συλλέξει τα πρώτα δείγματα.

Αν θέλουμε να δούμε την κλιμάκωση σε πραγματικό χρόνο, παρακολουθούμε το HPA σε ένα terminal:

```bash
kubectl get hpa php-apache -w
```

και σε δεύτερο terminal δημιουργούμε τεχνητό φορτίο:

```bash
kubectl run -i --tty load-generator --rm --image=busybox:1.36 --restart=Never -- /bin/sh
while true; do wget -q -O- http://php-apache; done
```

Όταν τερματιστεί το loop με `Ctrl+C`, το HPA θα αρχίσει σταδιακά να επαναφέρει τον αριθμό των replicas σε χαμηλότερα επίπεδα.

## Καθαρισμός

Μετά την ολοκλήρωση της άσκησης διαγράφουμε τόσο το HPA όσο και το `Deployment`:

```bash
kubectl delete -f hpa.yaml
kubectl delete -f deployment.yaml
```
