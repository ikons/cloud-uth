# Οριζόντια αυτόματη κλιμάκωση με HPA

Στο σημείο αυτό περνάμε από τη στατική κλιμάκωση στη δυναμική προσαρμογή του αριθμού των replicas. Ο `HorizontalPodAutoscaler` παρακολουθεί μετρικές χρήσης και αυξομειώνει τα Pods του `Deployment` ανάλογα με το φορτίο που δέχεται η εφαρμογή.

## Παιδαγωγικοί στόχοι

- Να ορίσετε `HorizontalPodAutoscaler` που στοχεύει `Deployment` βάσει χρήσης CPU.
- Να καταλάβετε γιατί το HPA απαιτεί `requests.cpu` ως baseline.
- Να παρατηρήσετε scale-up υπό φορτίο και (πιο αργό) scale-down μετά.
- Να αναγνωρίσετε ότι το HPA είναι ο πρώτος **κλειστός βρόχος ελέγχου** που συναντάτε: παρατηρεί μετρικές και αλλάζει επιθυμητή κατάσταση χωρίς ανθρώπινη παρέμβαση.

## Σύνδεση με την ακολουθία

Έως τώρα ορίζατε χειροκίνητα `replicas` στο `Deployment`. Εδώ ο cluster αποφασίζει αυτόματα πόσα Pods χρειάζονται. Αν στο 04 δούλευε ο rolling update ως "ελεγχόμενη αλλαγή έκδοσης", εδώ προστίθεται "ελεγχόμενη αλλαγή χωρητικότητας".

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

## Επιβεβαίωση επιτυχίας και κοινά λάθη

- Επιτυχία: στο `kubectl get hpa -w` βλέπετε `TARGETS` να ξεπερνά το 50% και τα `REPLICAS` να αυξάνονται σταδιακά μέχρι το `maxReplicas`.
- `<unknown>` στις πρώτες ενδείξεις είναι φυσιολογικό — το `metrics-server` χρειάζεται μερικά δευτερόλεπτα για το πρώτο sample.
- **Χωρίς `requests.cpu`** το HPA δεν μπορεί να υπολογίσει `Utilization` — είναι υποχρεωτικό. Αν παραλείψετε το `requests`, το HPA μένει σε `<unknown>` μόνιμα.
- Το scale-down είναι αργό σχεδιαστικά (default σταθεροποίηση 5 λεπτών) για να αποφεύγεται thrashing — μην το συγχέετε με βλάβη.
- Το HPA επεμβαίνει στο `replicas`. Αν στο `Deployment` έχετε ορίσει σταθερό `replicas: N`, το HPA το παρακάμπτει — μην το αλλάζετε ταυτόχρονα και από τα δύο σημεία.

## Καθαρισμός

Μετά την ολοκλήρωση της άσκησης διαγράφουμε τόσο το HPA όσο και το `Deployment`:

```bash
kubectl delete -f hpa.yaml
kubectl delete -f deployment.yaml
```
