# Πρόσβαση σε εφαρμογή μέσω Service

Αφού δημιουργήσουμε ένα Pod, το αμέσως επόμενο ερώτημα είναι με ποιον τρόπο θα αποκτήσει ένα σταθερό σημείο πρόσβασης μέσα στο cluster. Στην άσκηση αυτή εισάγουμε το αντικείμενο `Service`, το οποίο συνδέεται με τα Pods μέσω labels και selectors και προσφέρει ένα σταθερό όνομα για δικτυακή πρόσβαση.

Για συνεπή ελληνική ορολογία στους οδηγούς του μαθήματος, ανατρέξτε στο [glossary.md](../../../glossary.md).

## Παιδαγωγικοί στόχοι

- Να καταλάβετε γιατί ένα Pod δεν επαρκεί ως σημείο πρόσβασης (φευγαλέα IP) και να αναγνωρίζετε τη λύση: `Service`.
- Να συνδέσετε ένα `Service` με ένα Pod μέσω του ζεύγους **labels–selector**.
- Να διακρίνετε `port` (θύρα του Service) από `targetPort` (θύρα του container).
- Να αποκτάτε τοπική πρόσβαση σε εσωτερική υπηρεσία του cluster μέσω `kubectl port-forward`.

## Σύνδεση με την ακολουθία

Στο 01 είχαμε ένα μεμονωμένο Pod χωρίς σταθερό σημείο πρόσβασης. Εδώ ξεκλειδώνεται η δικτυακή πλευρά του Kubernetes: το `Service` είναι το πρώτο αντικείμενο που χρησιμοποιεί τη μηχανική **labels & selectors** που θα δείτε ξανά σε `ReplicaSet`, `Deployment` και `StatefulSet`.

## Αρχεία του παραδείγματος

Το Pod που θα εξυπηρετεί HTTP αιτήσεις ορίζεται ως εξής:

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

Το `Service` που θα προωθεί την κίνηση προς το Pod είναι το ακόλουθο:

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

## Εκτέλεση

Μεταβαίνουμε πρώτα στον κατάλογο της άσκησης:

```bash
cd ~/cloud-uth/code/02_kubernetes/02_services
```

Έπειτα δημιουργούμε τόσο το Pod όσο και το `Service`:

```bash
kubectl apply -f nginx-pod.yaml
kubectl apply -f nginx-service.yaml
```

Για να διαπιστώσουμε ότι οι πόροι δημιουργήθηκαν σωστά και ότι ο selector του `Service` αντιστοιχεί στο σωστό Pod, ελέγχουμε τα ακόλουθα:

```bash
kubectl get pod web-pod
kubectl get svc web-service
kubectl describe svc web-service
```

Η απλούστερη μέθοδος για να δοκιμάσουμε το αποτέλεσμα από τοπικό browser είναι το `port-forward`:

```bash
kubectl port-forward svc/web-service 8080:80
```

Στη συνέχεια ανοίγουμε τη διεύθυνση `http://127.0.0.1:8080`. Αν η τοπική θύρα `8080` χρησιμοποιείται ήδη από άλλη εφαρμογή, αλλάζουμε μόνο το αριστερό μέρος της αντιστοίχισης:

```bash
kubectl port-forward svc/web-service 8081:80
```

## Επιβεβαίωση επιτυχίας και κοινά λάθη

- Επιτυχία: ο browser στο `http://127.0.0.1:8080` εμφανίζει τη σελίδα υποδοχής του Nginx.
- `kubectl get endpoints web-service` πρέπει να δείχνει την IP του Pod. **Άδειο `ENDPOINTS`** σημαίνει ότι ο `selector` του Service δεν αντιστοιχεί σε κανένα Pod — ελέγξτε ότι τα labels ταιριάζουν ακριβώς (case-sensitive).
- Αν εμφανίζεται `connection refused`: συχνότερη αιτία είναι λάθος `targetPort`. Πρέπει να ταυτίζεται με το `containerPort` του Pod.
- Το `kubectl port-forward` τερματίζεται όταν κλείσει το terminal — κρατήστε δεύτερο terminal για το `curl`/browser.

## Καθαρισμός

Μετά την ολοκλήρωση της δοκιμής, και από νέο terminal εφόσον το `port-forward` παραμένει ενεργό, διαγράφουμε τους πόρους:

```bash
kubectl delete -f nginx-service.yaml
kubectl delete -f nginx-pod.yaml
```
