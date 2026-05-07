# ConfigMap: εξωτερική παραμετροποίηση

Μια εφαρμογή χρειάζεται συχνά ρυθμίσεις ή αρχεία κειμένου που δεν είναι σκόπιμο να ενσωματωθούν μόνιμα στο container image. Για τον σκοπό αυτό το Kubernetes παρέχει τα `ConfigMaps`, τα οποία επιτρέπουν την εξωτερική παραμετροποίηση ενός workload.

## Παιδαγωγικοί στόχοι

- Να εξωτερικοποιήσετε ρυθμίσεις από την image, ώστε ίδιο image να τρέχει σε διαφορετικά περιβάλλοντα.
- Να επιλέγετε ανάμεσα στις δύο μορφές κατανάλωσης ενός `ConfigMap`: **environment variables** (απλές τιμές) και **mounted files** (αρχεία ή πολυγραμμικό κείμενο).
- Να αναγνωρίζετε ότι το `ConfigMap` προορίζεται μόνο για **μη ευαίσθητα** δεδομένα. Για credentials υπάρχει το `Secret` στο επόμενο βήμα.
- Να καταλαβαίνετε ότι η αλλαγή ενός ConfigMap **δεν** προκαλεί αυτόματα restart των Pods που το χρησιμοποιούν ως env vars.

## Σύνδεση με την ακολουθία

Μέχρι τώρα όλη η συμπεριφορά της εφαρμογής ήταν "καρφωμένη" στην image. Εδώ μαθαίνουμε να αλλάζουμε ρυθμίσεις χωρίς rebuild. Στο επόμενο βήμα κάνουμε το ίδιο για ευαίσθητα δεδομένα με τον σωστό τύπο πόρου (`Secret`).

## Αρχεία του παραδείγματος

Το `ConfigMap` του παραδείγματος αποθηκεύει δύο απλές μεταβλητές και ένα αρχείο κειμένου:

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

Το Pod που ακολουθεί καταναλώνει το ίδιο `ConfigMap` τόσο ως environment variables όσο και ως mounted αρχείο:

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

## Εκτέλεση

Μεταβαίνουμε πρώτα στον κατάλογο της άσκησης:

```bash
cd ~/cloud-uth/code/02_kubernetes/05_configmaps
```

Έπειτα δημιουργούμε το `ConfigMap` και το Pod που το χρησιμοποιεί:

```bash
kubectl apply -f app-config.yaml
kubectl apply -f pod-with-config.yaml
kubectl wait --for=condition=Ready pod/app-with-config --timeout=120s
```

Η συμπεριφορά του παραδείγματος φαίνεται στα logs του Pod:

```bash
kubectl logs app-with-config
```

Στην έξοδο θα εμφανιστούν τόσο οι τιμές που πέρασαν ως environment variables όσο και το περιεχόμενο του αρχείου `welcome.txt` που έγινε mount στον κατάλογο `/config`.

Αν θέλουμε να δούμε τον ίδιο τον πόρο όπως τον γνωρίζει το API του Kubernetes, χρησιμοποιούμε:

```bash
kubectl get configmap app-config -o yaml
```

## Επιβεβαίωση επιτυχίας και κοινά λάθη

- Επιτυχία: στα `kubectl logs app-with-config` βλέπετε τις τιμές των env vars (`APP_COLOR: blue`, `APP_MODE: production`) και το περιεχόμενο του `welcome.txt`.
- Αν το Pod μένει σε `ContainerCreating` με event `MountVolume.SetUp failed`, συχνά λείπει το ConfigMap — εφαρμόστε πρώτα το `app-config.yaml` και μετά το Pod.
- Σημαντική διάκριση συμπεριφοράς ενημέρωσης:
  - **Env vars** που προέρχονται από ConfigMap **δεν** ενημερώνονται όσο τρέχει το Pod. Χρειάζεται restart (νέο rollout).
  - **Mounted files** ενημερώνονται eventually (καθυστέρηση μερικών δευτερολέπτων μετά το edit).
- Συχνό λάθος: τοποθέτηση ευαίσθητων δεδομένων (κωδικοί, tokens) σε ConfigMap. Είναι κακή πρακτική — χρησιμοποιήστε `Secret`.

## Καθαρισμός

Μετά την ολοκλήρωση της άσκησης διαγράφουμε το Pod και το `ConfigMap`:

```bash
kubectl delete -f pod-with-config.yaml
kubectl delete -f app-config.yaml
```
