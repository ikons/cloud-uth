# Composite web application example with a database backend

This final example acts as a synthesis of the concepts introduced earlier. The application consists of a PostgreSQL database, a PHP/Apache web tier, a `Secret` for the password, a `ConfigMap` for non-sensitive configuration, a `PersistentVolumeClaim` for durable database storage, and `Service` objects that provide stable network access.

## Example files

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

## Execution

Begin by moving into the example directory:

```bash
cd ~/cloud-uth/code/02_kubernetes/11_web-app
```

To deploy all resources, use the provided `Makefile`, which applies the manifests in the correct order and waits until the key Pods are available:

```bash
make deploy
kubectl get pods,svc,pvc
```

If the deployment completed successfully, access to the web application is provided through `port-forward`:

```bash
kubectl port-forward svc/webserver-service 8080:80
```

Then open `http://127.0.0.1:8080`. If local port `8080` is already in use, change only the left-hand side of the mapping:

```bash
kubectl port-forward svc/webserver-service 8081:80
```

In some cases the first HTTP request immediately after the Pod becomes `Ready` may fail, in which case a short wait followed by a retry is sufficient.

For optional diagnostic inspection, you may examine the logs of both the database and the web tier:

```bash
kubectl logs postgres
kubectl logs webserver
```

## Cleanup

After the exercise is complete, remove all resources that belong to the example:

```bash
make clean
```
