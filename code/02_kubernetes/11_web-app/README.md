# Συνθετικό παράδειγμα: εφαρμογή ιστού με βάση δεδομένων

Το παράδειγμα αυτό λειτουργεί ως **σύνθεση** των εννοιών που είδατε χωριστά στα βήματα 01–10: εφαρμόζεται μια ολόκληρη μικρή εφαρμογή ιστού με βάση PostgreSQL, επίπεδο εξυπηρέτησης (PHP/Apache), εξωτερική παραμετροποίηση μέσω `ConfigMap`, μυστικά μέσω `Secret`, μόνιμη αποθήκευση μέσω `PersistentVolumeClaim` και σταθερή δικτυακή πρόσβαση μέσω αντικειμένων `Service`.

Για συνεπή ελληνική ορολογία στους οδηγούς του μαθήματος, ανατρέξτε στο [glossary.md](../../../glossary.md).

## Παιδαγωγικοί στόχοι

- Να συνδυάσετε τις έξι κατηγορίες πόρων που είδατε χωριστά (Pod, Service, ConfigMap, Secret, PVC, manifest τύπου Deployment) σε μια ολοκληρωμένη εφαρμογή δύο επιπέδων.
- Να δείτε πώς το επίπεδο εξυπηρέτησης συνδέεται με τη βάση μέσω **σταθερού DNS ονόματος** (`postgres`) και env vars που προέρχονται από `ConfigMap` + `Secret`.
- Να αναγνωρίσετε τη σωστή **σειρά εφαρμογής** (config → storage → database → application) και γιατί ο `Makefile` περιμένει τη βάση να γίνει `Ready`.
- Να αντιληφθείτε τη διαφορά μεταξύ "**διαμόρφωσης** μιας υπάρχουσας image" και "**συγγραφής** του δικού σας κώδικα" — η γέφυρα προς το επόμενο βήμα 12.

## Σύνδεση με την ακολουθία

Όλα τα προηγούμενα παραδείγματα παρουσίαζαν **έναν** πόρο τη φορά. Εδώ συνθέτουμε εννέα manifests σε ένα λειτουργικό σύστημα. Ωστόσο, υπάρχει μια συνειδητή απλοποίηση: ο **κώδικας** της εφαρμογής (το `index.php`) μπαίνει ως πεδίο σε `ConfigMap`. Αυτό μας επιτρέπει να αποφύγουμε τη δημιουργία image μέχρι εδώ — αλλά **δεν είναι σωστό για παραγωγή**. Το επόμενο βήμα (`12_app-from-source`) διορθώνει αυτό το ζήτημα: ο φοιτητής γράφει εφαρμογή, τη χτίζει σε image, την ανεβάζει σε registry και την αναπτύσσει.

## Αρχεία του παραδείγματος

### `01-secret.yaml`

<!-- AUTO-CODE: code/02_kubernetes/11_web-app/01-secret.yaml -->
``` yaml
apiVersion: v1
kind: Secret
metadata:
  name: db-secret
type: Opaque
stringData:
  # Keep the database password outside image and source code logic.
  password: supersecret
```
<!-- END AUTO-CODE -->

### `02-configmap.yaml`

<!-- AUTO-CODE: code/02_kubernetes/11_web-app/02-configmap.yaml -->
``` yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: db-config
data:
  # Share non-sensitive connection settings between Pods.
  username: postgres
  dbname: myappdb
  host: postgres
```
<!-- END AUTO-CODE -->

### `03-pvc.yaml`

<!-- AUTO-CODE: code/02_kubernetes/11_web-app/03-pvc.yaml -->
``` yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
spec:
  # PostgreSQL needs persistent storage to keep data across Pod recreation.
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```
<!-- END AUTO-CODE -->

### `04-init-sql.yaml`

<!-- AUTO-CODE: code/02_kubernetes/11_web-app/04-init-sql.yaml -->
``` yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: init-sql-script
data:
  # PostgreSQL runs scripts from /docker-entrypoint-initdb.d on first initialization.
  init.sql: |
    CREATE TABLE IF NOT EXISTS my_table (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL
    );
    INSERT INTO my_table (name) VALUES ('Alice'), ('Bob'), ('Charlie');
```
<!-- END AUTO-CODE -->

### `05-postgres.yaml`

<!-- AUTO-CODE: code/02_kubernetes/11_web-app/05-postgres.yaml -->
``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: postgres
  labels:
    app: postgres
spec:
  containers:
    - name: postgres
      image: postgres:17
      ports:
        - containerPort: 5432
      env:
        # Read non-sensitive settings from the shared ConfigMap.
        - name: POSTGRES_USER
          valueFrom:
            configMapKeyRef:
              name: db-config
              key: username
        - name: POSTGRES_DB
          valueFrom:
            configMapKeyRef:
              name: db-config
              key: dbname
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
      volumeMounts:
        # Persist the database data directory on a PVC.
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
        # Mount the initialization SQL script for first-time setup.
        - name: init-sql
          mountPath: /docker-entrypoint-initdb.d
  volumes:
    - name: postgres-data
      persistentVolumeClaim:
        claimName: postgres-pvc
    - name: init-sql
      configMap:
        name: init-sql-script
```
<!-- END AUTO-CODE -->

### `06-postgres-svc.yaml`

<!-- AUTO-CODE: code/02_kubernetes/11_web-app/06-postgres-svc.yaml -->
``` yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  selector:
    # Expose the database Pod under a stable in-cluster DNS name.
    app: postgres
  ports:
    - port: 5432
      targetPort: 5432
```
<!-- END AUTO-CODE -->

### `07-web-content.yaml`

<!-- AUTO-CODE: code/02_kubernetes/11_web-app/07-web-content.yaml -->
``` yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: web-content
data:
  # Mount the PHP application code from a ConfigMap for teaching purposes.
  index.php: |
    <?php
    $host     = getenv('DB_HOST');
    $dbname   = getenv('DB_NAME');
    $user     = getenv('DB_USER');
    $password = getenv('DB_PASSWORD');

    echo "<h1>Kubernetes Web Application</h1>";

    try {
        $pdo = new PDO("pgsql:host=$host;dbname=$dbname", $user, $password);
        $stmt = $pdo->query("SELECT * FROM my_table");
        echo "<h2>Data from PostgreSQL:</h2><ul>";
        while ($row = $stmt->fetch()) {
            echo "<li>" . htmlspecialchars($row['name']) . "</li>";
        }
        echo "</ul>";
    } catch (PDOException $e) {
        echo "<p>Connection error: " . htmlspecialchars($e->getMessage()) . "</p>";
    }
    ?>
```
<!-- END AUTO-CODE -->

### `08-webserver.yaml`

<!-- AUTO-CODE: code/02_kubernetes/11_web-app/08-webserver.yaml -->
``` yaml
apiVersion: v1
kind: Pod
metadata:
  name: webserver
  labels:
    app: webserver
spec:
  containers:
    - name: php-apache
      image: webdevops/php-apache:8.1
      ports:
        - containerPort: 80
      env:
        # Resolve the database endpoint and credentials from ConfigMap and Secret resources.
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: db-config
              key: host
        - name: DB_NAME
          valueFrom:
            configMapKeyRef:
              name: db-config
              key: dbname
        - name: DB_USER
          valueFrom:
            configMapKeyRef:
              name: db-config
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
      volumeMounts:
        # Serve the PHP file mounted from the ConfigMap under /app.
        - name: web-content
          mountPath: /app
  volumes:
    - name: web-content
      configMap:
        name: web-content
```
<!-- END AUTO-CODE -->

### `09-webserver-svc.yaml`

<!-- AUTO-CODE: code/02_kubernetes/11_web-app/09-webserver-svc.yaml -->
``` yaml
apiVersion: v1
kind: Service
metadata:
  name: webserver-service
spec:
  selector:
    # Publish the web frontend through a stable ClusterIP Service.
    app: webserver
  ports:
    - port: 80
      targetPort: 80
  type: ClusterIP
```
<!-- END AUTO-CODE -->

### `Makefile`

<!-- AUTO-CODE: code/02_kubernetes/11_web-app/Makefile -->
``` makefile
.PHONY: deploy clean

deploy:
	# Create configuration, storage, and database resources first.
	kubectl apply -f 01-secret.yaml
	kubectl apply -f 02-configmap.yaml
	kubectl apply -f 03-pvc.yaml
	kubectl apply -f 04-init-sql.yaml
	kubectl apply -f 05-postgres.yaml
	kubectl apply -f 06-postgres-svc.yaml
	@echo "Waiting for PostgreSQL to start..."
	kubectl wait --for=condition=Ready pod/postgres --timeout=120s
	# Deploy the application tier only after the database is ready.
	kubectl apply -f 07-web-content.yaml
	kubectl apply -f 08-webserver.yaml
	kubectl apply -f 09-webserver-svc.yaml
	kubectl wait --for=condition=Ready pod/webserver --timeout=60s
	@echo "Application deployed! Use: kubectl port-forward svc/webserver-service 8080:80"

clean:
	kubectl delete -f 09-webserver-svc.yaml --ignore-not-found
	kubectl delete -f 08-webserver.yaml --ignore-not-found
	kubectl delete -f 07-web-content.yaml --ignore-not-found
	kubectl delete -f 06-postgres-svc.yaml --ignore-not-found
	kubectl delete -f 05-postgres.yaml --ignore-not-found
	kubectl delete -f 04-init-sql.yaml --ignore-not-found
	kubectl delete -f 03-pvc.yaml --ignore-not-found
	kubectl delete -f 02-configmap.yaml --ignore-not-found
	kubectl delete -f 01-secret.yaml --ignore-not-found
```
<!-- END AUTO-CODE -->

## Εκτέλεση

Μεταβαίνουμε πρώτα στον κατάλογο του παραδείγματος:

```bash
cd ~/cloud-uth/code/02_kubernetes/11_web-app
```

Για την ανάπτυξη όλων των πόρων χρησιμοποιούμε το παρεχόμενο `Makefile`, το οποίο εφαρμόζει τα manifests με τη σωστή σειρά και περιμένει να γίνουν διαθέσιμα τα βασικά Pods:

```bash
make deploy
kubectl get pods,svc,pvc
```

Αν όλα έχουν αναπτυχθεί σωστά, η πρόσβαση στη web εφαρμογή γίνεται μέσω `port-forward`:

```bash
kubectl port-forward svc/webserver-service 8080:80
```

Στη συνέχεια ανοίγουμε τη διεύθυνση `http://127.0.0.1:8080`. Αν η τοπική θύρα `8080` χρησιμοποιείται ήδη, αλλάζουμε μόνο το αριστερό μέρος της αντιστοίχισης:

```bash
kubectl port-forward svc/webserver-service 8081:80
```

Σε ορισμένες περιπτώσεις η πρώτη HTTP αίτηση αμέσως μετά το `Ready` μπορεί να αποτύχει, οπότε αρκεί μια μικρή αναμονή και μια νέα προσπάθεια.

Για προαιρετικό διαγνωστικό έλεγχο μπορούμε να εξετάσουμε τα logs του database και του web tier:

```bash
kubectl logs postgres
kubectl logs webserver
```

## Επιβεβαίωση επιτυχίας και κοινά λάθη

- Επιτυχία: στον browser εμφανίζεται ο τίτλος `Kubernetes Web Application` και μια λίστα ονομάτων (`Alice`, `Bob`, `Charlie`) από τη βάση.
- `kubectl get pods,svc,pvc` πρέπει να δείχνει: `postgres` και `webserver` σε `Running`, δύο `Service` (`postgres`, `webserver-service`), και `postgres-pvc` σε `Bound`.
- Αν εμφανιστεί `Connection error: ... could not translate host name "postgres"`: συνήθως το web tier ξεκίνησε πριν το `Service` της βάσης· περιμένετε λίγο, ή τρέξτε ξανά `make deploy`.
- Αν η σελίδα δείχνει `Connection error: password authentication failed`: τα ονόματα στο `Secret` και `ConfigMap` πρέπει να ταιριάζουν με τα ίδια keys που διαβάζονται στο `08-webserver.yaml` και στο `index.php`.
- Η σειρά διαγραφής στο `make clean` είναι **αντίστροφη** της σειράς δημιουργίας — δεν είναι τυχαία· εξασφαλίζει ότι αφαιρούμε κάτι που εξαρτάται από κάτι άλλο πριν αφαιρέσουμε αυτό από το οποίο εξαρτάται.

## Τι μαθαίνετε εδώ και τι **ακόμη λείπει**

Σκεφθείτε τι κάνατε ως τώρα: συνδυάσατε **εικόνες τρίτων** (`postgres:17`, `webdevops/php-apache:8.1`) με ρυθμίσεις, μυστικά, αποθηκευτικό χώρο και δικτύωση. Αυτό είναι το μεγαλύτερο μέρος της δουλειάς ενός μηχανικού που αναπτύσσει υπηρεσίες, αλλά λείπει το πρώτο μισό: η συγγραφή δικής σας εφαρμογής. Στο σημερινό παράδειγμα ο κώδικας PHP βρίσκεται μέσα σε `ConfigMap`. Αυτό ήταν χρήσιμο διδακτικά (κανένα build, καμία image), αλλά δεν είναι σωστό σε πραγματικό σύστημα: δεν είναι υπό έλεγχο εκδόσεων με τους ίδιους κανόνες με τον υπόλοιπο κώδικα, δεν δοκιμάζεται σε CI, και ο φοιτητής δεν βιώνει την αλυσίδα **commit → build → push → deploy**.

Στο επόμενο βήμα (`12_app-from-source`) γράφετε δική σας Python εφαρμογή, τη χτίζετε σε Docker image, την ανεβάζετε σε Docker Hub και την αναπτύσσετε ως κανονικό `Deployment` που συνδέεται **στην ίδια βάση Postgres** που έχετε ήδη εδώ.

## Καθαρισμός

Μετά την ολοκλήρωση της άσκησης απομακρύνουμε όλους τους πόρους του παραδείγματος:

```bash
make clean
```
