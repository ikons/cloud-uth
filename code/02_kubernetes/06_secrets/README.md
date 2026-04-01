# Secret: διαχείριση ευαίσθητων δεδομένων

Τα `Secrets` εξυπηρετούν παρόμοιο σκοπό με τα `ConfigMaps`, αλλά χρησιμοποιούνται όταν τα δεδομένα δεν πρέπει να αντιμετωπίζονται ως απλή γενική παραμετροποίηση. Τυπικά παραδείγματα είναι κωδικοί πρόσβασης, tokens ή άλλα στοιχεία πρόσβασης που πρέπει να διαχωρίζονται από τον υπόλοιπο κώδικα και τις ρυθμίσεις.

## Αρχεία του παραδείγματος

Το `Secret` του παραδείγματος ορίζει δύο απλά credentials:

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

Το επόμενο Pod χρησιμοποιεί το ίδιο `Secret` με δύο τρόπους: ως mounted αρχείο και ως environment variable:

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

## Εκτέλεση

Μεταβαίνουμε πρώτα στον κατάλογο της άσκησης:

```bash
cd ~/cloud-uth/code/02_kubernetes/06_secrets
```

Στη συνέχεια δημιουργούμε το `Secret` και το Pod που το καταναλώνει:

```bash
kubectl apply -f db-credentials.yaml
kubectl apply -f pod-with-secret.yaml
kubectl wait --for=condition=Ready pod/app-with-secret --timeout=120s
```

Η συμπεριφορά του παραδείγματος φαίνεται στα logs:

```bash
kubectl logs app-with-secret
```

Στην έξοδο θα εμφανιστεί το ίδιο `Secret` τόσο ως mounted περιεχόμενο στον κατάλογο `/etc/db-credentials` όσο και ως environment variable.

Αν θέλουμε να εξετάσουμε τον πόρο από την οπτική του Kubernetes API, χρησιμοποιούμε:

```bash
kubectl get secret db-credentials -o yaml
```

Σημειώνεται ότι στο manifest χρησιμοποιούμε `stringData`, ενώ στο API το Kubernetes αποθηκεύει τις ίδιες τιμές σε base64-encoded μορφή.

## Καθαρισμός

Μετά την ολοκλήρωση της άσκησης διαγράφουμε το Pod και το `Secret`:

```bash
kubectl delete -f pod-with-secret.yaml
kubectl delete -f db-credentials.yaml
```
