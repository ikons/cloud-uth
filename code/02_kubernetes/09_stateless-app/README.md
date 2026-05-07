# Εφαρμογή ιστού χωρίς κατάσταση

Σε αυτό το βήμα συνθέτουμε τρεις έννοιες που έχουν ήδη παρουσιαστεί χωριστά: `ConfigMap`, `Deployment` και `Service`. Το αποτέλεσμα είναι μια μικρή εφαρμογή ιστού χωρίς κατάσταση, στην οποία το περιεχόμενο της σελίδας παραμένει εξωτερικό ως configuration και η εξυπηρέτηση γίνεται από πολλαπλά εναλλάξιμα replicas.

Για συνεπή ελληνική ορολογία στους οδηγούς του μαθήματος, ανατρέξτε στο [glossary.md](../../../glossary.md).

## Παιδαγωγικοί στόχοι

- Να συνθέσετε τρεις πόρους (`ConfigMap` + `Deployment` + `Service`) σε μια μικρή λειτουργική εφαρμογή.
- Να ορίσετε resource `requests` και `limits` και να κατανοήσετε τη χρήση τους από τον scheduler.
- Να επιβεβαιώσετε ότι πολλαπλά replicas μπορούν να εξυπηρετούν την ίδια κίνηση χωρίς κατάσταση.

## Σύνδεση με την ακολουθία

Πρώτη φορά συνδυάζουμε τρεις πόρους σε ένα παράδειγμα — αυτό είναι το πραγματικό πρότυπο για web εφαρμογές χωρίς κατάσταση στο Kubernetes. Είναι το θεμέλιο πάνω στο οποίο θα προστεθεί αυτόματη κλιμάκωση (`10_autoscaling`) και βάση δεδομένων (`11_web-app`).

## Αρχεία του παραδείγματος

Το HTML περιεχόμενο της εφαρμογής αποθηκεύεται σε `ConfigMap`:

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

Το `Deployment` εξασφαλίζει την εκτέλεση δύο replicas που χρησιμοποιούν το ίδιο περιεχόμενο:

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

Τέλος, το `Service` εκθέτει την εφαρμογή με σταθερό τρόπο:

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

## Εκτέλεση

Μεταβαίνουμε πρώτα στον κατάλογο της άσκησης:

```bash
cd ~/cloud-uth/code/02_kubernetes/09_stateless-app
```

Έπειτα δημιουργούμε όλους τους πόρους και περιμένουμε να ολοκληρωθεί το rollout του `Deployment`:

```bash
kubectl apply -f app-html.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl rollout status deployment/web-app
```

Για να επιβεβαιώσουμε ότι τα replicas και το `Service` λειτουργούν όπως αναμένεται, ελέγχουμε:

```bash
kubectl get pods -l app=web-app -o wide
kubectl get svc web-app
```

Η τοπική πρόσβαση στον browser γίνεται με `port-forward`:

```bash
kubectl port-forward svc/web-app 8080:80
```

Στη συνέχεια ανοίγουμε τη διεύθυνση `http://127.0.0.1:8080`. Αν η τοπική θύρα `8080` δεν είναι διαθέσιμη, χρησιμοποιούμε κάποια άλλη, για παράδειγμα:

```bash
kubectl port-forward svc/web-app 8081:80
```

## Επιβεβαίωση επιτυχίας και κοινά λάθη

- Επιτυχία: `kubectl get pods -l app=web-app` δείχνει 2 Pods σε `Running`. Στον browser βλέπετε τη σελίδα με τίτλο `Stateless App`.
- Αν εφαρμοστεί το `Deployment` πριν το `ConfigMap`, τα Pods μπορεί να μείνουν σε `ContainerCreating` με event `MountVolume.SetUp failed: configmap "web-html" not found`. Λύση: εφαρμόστε πρώτα το ConfigMap.
- Πολλαπλά reloads στο browser μπορεί να εξυπηρετηθούν από διαφορετικά replicas — αυτό είναι το ζητούμενο για εφαρμογές χωρίς κατάσταση. Δεν πρέπει να βασίζεστε σε in-memory state μεταξύ requests.
- Τα `requests` καθορίζουν πού θα προγραμματιστεί το Pod· τα `limits` αν θα γίνει throttling/`OOMKilled` υπό φορτίο.

## Καθαρισμός

Μετά την ολοκλήρωση της άσκησης διαγράφουμε το `Service`, το `Deployment` και το `ConfigMap`:

```bash
kubectl delete -f service.yaml
kubectl delete -f deployment.yaml
kubectl delete -f app-html.yaml
```
