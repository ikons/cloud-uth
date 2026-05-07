# Από τον κώδικα στο cluster: πλήρης ροή ανάπτυξης Python εφαρμογής

Στο τελευταίο αυτό βήμα ολοκληρώνεται η αλυσίδα που είδαμε ως τώρα: γράφουμε δικό μας κώδικα, τον δοκιμάζουμε τοπικά, τον χτίζουμε σε Docker image, τον ανεβάζουμε σε registry (Docker Hub) και τον αναπτύσσουμε ως κανονικό `Deployment` που συνδέεται στην ίδια PostgreSQL βάση που στήσαμε στο `11_web-app`. Σκοπός δεν είναι μόνο η εξοικείωση με το Kubernetes, αλλά η συνολική εμπειρία **commit → build → push → deploy → iterate** χωρίς εξωτερική υποδομή συνεχούς ολοκλήρωσης (CI), όπως Jenkins ή GitHub Actions.

Για συνεπή ελληνική ορολογία στους οδηγούς του μαθήματος, ανατρέξτε στο [glossary.md](../../../glossary.md).

## Παιδαγωγικοί στόχοι

- Να γράψετε μια απλή εφαρμογή Python (Flask) που επικοινωνεί με την υπάρχουσα βάση από το `11`.
- Να συντάξετε ένα `Dockerfile` που ακολουθεί βέλτιστες πρακτικές (καρφωμένη έκδοση της βασικής εικόνας, μη προνομιούχος χρήστης, μικρά layers, WSGI server παραγωγής).
- Να χρησιμοποιήσετε **immutable image tags** (καμία χρήση `:latest`) για να αποκτήσετε προβλέψιμα rollouts και rollbacks.
- Να εφαρμόσετε στην πράξη liveness/readiness probes που διαχωρίζουν το αν η διεργασία είναι ζωντανή από το αν είναι έτοιμη να δεχτεί κίνηση.
- Να δείτε ότι μια ροή τύπου CI μπορεί να είναι ένα απλό `Makefile` με σαφή βήματα: `test → build → push → deploy → rollback`.

## Σύνδεση με την ακολουθία

Μέχρι το `11` η εφαρμογή ήταν είτε έτοιμη εικόνα (nginx, postgres, php-apache) είτε κώδικας ενσωματωμένος σε `ConfigMap`. Εδώ το επίπεδο εξυπηρέτησης είναι πλέον δικό σας: ο κώδικας βρίσκεται σε αρχεία του αποθετηρίου σας, είναι υπό έλεγχο εκδόσεων, δοκιμάζεται με `pytest` και χτίζεται σε image που ζει σε registry. Αυτός είναι ακριβώς ο δρόμος που θα ακολουθήσετε σε κάθε επαγγελματικό περιβάλλον.

## Προϋποθέσεις

1. Έχετε ολοκληρώσει το `11_web-app` και η Postgres του τρέχει στο namespace σας. Συγκεκριμένα, χρειάζεστε διαθέσιμα:
   - `Service/postgres`
   - `ConfigMap/db-config`
   - `Secret/db-secret`
   - τη βάση `myappdb` με τον πίνακα `my_table` (έχει ήδη γεμίσει το `04-init-sql.yaml` στο `11`).

   Αν δεν τρέχουν, εκτελέστε από τον κατάλογο `11_web-app`:

   ```bash
   make deploy
   ```

   Δεν χρειάζεται το web κομμάτι του `11`· μπορείτε να αφήσετε ή να αφαιρέσετε **μόνο** το `webserver`/`webserver-service`/`web-content` αν θέλετε.

2. Έχετε λογαριασμό στο [Docker Hub](https://hub.docker.com/) και τοπικά Docker Engine ή Docker Desktop. Συνδεθείτε:

   ```bash
   docker login
   ```

3. Έχετε Python 3.10+ τοπικά (για να τρέξετε τα tests πριν το build).

## Δομή φακέλου

| Αρχείο | Σκοπός |
|--------|--------|
| `app.py` | Η Flask εφαρμογή (4 endpoints). |
| `requirements.txt` | Καρφωμένες (pinned) εξαρτήσεις. |
| `test_app.py` | Δύο pytest tests που τρέχουν πριν από κάθε build. |
| `Dockerfile` | Εικόνα παραγωγής· non-root, gunicorn. |
| `.dockerignore` | Αρχεία που δεν χρειάζονται μέσα στην εικόνα. |
| `01-deployment.yaml` | `Deployment` με 2 replicas, probes, resources. |
| `02-service.yaml` | `Service` τύπου ClusterIP που εκθέτει την εφαρμογή στο cluster. |
| `Makefile` | Targets για τη ροή ανάπτυξης. |

## Αρχεία της εφαρμογής

### `app.py`

<!-- AUTO-CODE: code/02_kubernetes/12_app-from-source/app.py -->
``` python
"""Minimal Flask service that reads names from the PostgreSQL backend of example 11."""

import os
import socket

import psycopg2
from flask import Flask, jsonify

APP_VERSION = os.environ.get("APP_VERSION", "0.1.0")

app = Flask(__name__)


def db_connect():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        connect_timeout=3,
    )


@app.get("/healthz")
def healthz():
    # Liveness probe: process is alive and Flask responds. No DB access here.
    return jsonify(status="ok"), 200


@app.get("/readyz")
def readyz():
    # Readiness probe: the app should only receive traffic when the DB is reachable.
    try:
        with db_connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
        return jsonify(status="ready"), 200
    except Exception as exc:
        return jsonify(status="not-ready", reason=str(exc)[:200]), 503


@app.get("/version")
def version():
    return jsonify(version=APP_VERSION)


@app.get("/")
def index():
    served_by = socket.gethostname()
    try:
        with db_connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT name FROM my_table ORDER BY id;")
            names = [row[0] for row in cur.fetchall()]
        return jsonify(
            message="Hello from Python on Kubernetes!",
            version=APP_VERSION,
            served_by=served_by,
            names=names,
        )
    except Exception as exc:
        return jsonify(error=str(exc)[:200], served_by=served_by), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```
<!-- END AUTO-CODE -->

### `requirements.txt`

<!-- AUTO-CODE: code/02_kubernetes/12_app-from-source/requirements.txt -->
``` text
Flask==3.0.3
psycopg2-binary==2.9.9
gunicorn==22.0.0
pytest==8.3.2
```
<!-- END AUTO-CODE -->

### `test_app.py`

<!-- AUTO-CODE: code/02_kubernetes/12_app-from-source/test_app.py -->
``` python
"""Minimal tests that run before every build, without needing a real database."""

from app import app


def test_healthz_returns_ok():
    client = app.test_client()
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_version_returns_version_field():
    client = app.test_client()
    response = client.get("/version")
    assert response.status_code == 200
    body = response.get_json()
    assert "version" in body
    assert isinstance(body["version"], str)
```
<!-- END AUTO-CODE -->

### `Dockerfile`

<!-- AUTO-CODE: code/02_kubernetes/12_app-from-source/Dockerfile -->
``` dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies in a separate layer so code changes do not invalidate them.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Drop privileges before copying application code.
RUN useradd --create-home --shell /usr/sbin/nologin appuser
COPY app.py .
USER appuser

EXPOSE 8080

# Use a production WSGI server, not the Flask development server.
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:8080", "app:app"]
```
<!-- END AUTO-CODE -->

### `.dockerignore`

<!-- AUTO-CODE: code/02_kubernetes/12_app-from-source/.dockerignore -->
```
__pycache__
*.pyc
.pytest_cache
.git
.venv
test_app.py
README*.md
Makefile
*.yaml
.dockerignore
```
<!-- END AUTO-CODE -->

## Manifests Kubernetes

### `01-deployment.yaml`

<!-- AUTO-CODE: code/02_kubernetes/12_app-from-source/01-deployment.yaml -->
``` yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pyapp
  labels:
    app: pyapp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: pyapp
  template:
    metadata:
      labels:
        app: pyapp
    spec:
      containers:
        - name: pyapp
          # The Makefile rewrites this placeholder with your DOCKER_USER and VERSION.
          image: REPLACE_ME_USER/cloud-uth-pyapp:0.1.0
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8080
          env:
            # Reuse the ConfigMap and Secret already created by example 11.
            - name: APP_VERSION
              value: "0.1.0"
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
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 200m
              memory: 256Mi
          livenessProbe:
            # Restart the container if /healthz stops responding.
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
          readinessProbe:
            # Stop sending traffic when the database is unreachable.
            httpGet:
              path: /readyz
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 5
```
<!-- END AUTO-CODE -->

### `02-service.yaml`

<!-- AUTO-CODE: code/02_kubernetes/12_app-from-source/02-service.yaml -->
``` yaml
apiVersion: v1
kind: Service
metadata:
  name: pyapp
spec:
  selector:
    # Same label as the Deployment template above.
    app: pyapp
  ports:
    - port: 80
      targetPort: 8080
  type: ClusterIP
```
<!-- END AUTO-CODE -->

### `Makefile`

<!-- AUTO-CODE: code/02_kubernetes/12_app-from-source/Makefile -->
```
DOCKER_USER ?= your-dockerhub-username
APP_NAME    := cloud-uth-pyapp
VERSION     ?= 0.1.0
IMAGE       := $(DOCKER_USER)/$(APP_NAME):$(VERSION)

.PHONY: help test build push deploy status logs rollback clean

help:
	@echo "Targets:"
	@echo "  test      Run pytest locally before any build."
	@echo "  build     Build the Docker image as $(IMAGE)."
	@echo "  push      Push the image to Docker Hub."
	@echo "  deploy    Apply manifests with the IMAGE substituted in."
	@echo "  status    Show Deployment, Pods, and Service for this app."
	@echo "  logs      Tail logs from all replicas."
	@echo "  rollback  Roll back to the previous Deployment revision."
	@echo "  clean     Delete the Deployment and Service."
	@echo ""
	@echo "Variables: DOCKER_USER=<dockerhub-user> VERSION=<tag>"

test:
	python -m pytest -q

build:
	docker build -t $(IMAGE) .

push:
	docker push $(IMAGE)

deploy:
	# Substitute the image placeholder, then apply the rendered manifest.
	sed "s|REPLACE_ME_USER/cloud-uth-pyapp:0.1.0|$(IMAGE)|g" 01-deployment.yaml | kubectl apply -f -
	kubectl apply -f 02-service.yaml
	kubectl rollout status deployment/pyapp --timeout=180s
	@echo "Application deployed. Use: kubectl port-forward svc/pyapp 8080:80"

status:
	kubectl get deployment pyapp
	kubectl get pods -l app=pyapp -o wide
	kubectl get svc pyapp

logs:
	kubectl logs -l app=pyapp --tail=100 --prefix

rollback:
	kubectl rollout undo deployment/pyapp
	kubectl rollout status deployment/pyapp --timeout=180s

clean:
	kubectl delete -f 02-service.yaml --ignore-not-found
	kubectl delete deployment/pyapp --ignore-not-found
```
<!-- END AUTO-CODE -->

## Ροή ανάπτυξης

Η συνολική ροή είναι **πέντε διακριτά βήματα**: τοπικές δοκιμές, build της εικόνας, push στο registry, εφαρμογή των manifests και επαλήθευση. Ο `Makefile` αυτοματοποιεί κάθε βήμα.

Πρώτα μεταβαίνουμε στον κατάλογο και ορίζουμε το όνομα χρήστη του Docker Hub σε μεταβλητή, ώστε να μην το πληκτρολογείτε κάθε φορά:

```bash
cd ~/cloud-uth/code/02_kubernetes/12_app-from-source
export DOCKER_USER=<dockerhub-user>
```

### 0. Αυθεντικοποίηση με Docker Hub (μία φορά)

Πριν μπορέσετε να κάνετε push εικόνες, πρέπει να συνδεθείτε στο Docker Hub:

```bash
docker login -u <dockerhub-user>
```

Θα σας ζητηθεί κωδικός. Έχετε δύο επιλογές:

- **Χρησιμοποιήστε τον κωδικό πρόσβασης του Docker Hub** (απλό, αλλά λιγότερο ασφαλές).
- **Χρησιμοποιήστε Personal Access Token** (συνιστώμενο):
  1. Πηγαίνετε στο https://hub.docker.com/settings/security
  2. Κάντε κλικ "New Access Token"
  3. Αντιγράψτε το token και επικολλήστε το όταν το `docker login` ζητήσει κωδικό

Η σύνδεση αποθηκεύεται τοπικά, οπότε χρειάζεται να το κάνετε μόνο μία φορά (ή όταν το token λήξει).

### 1. Τοπικές δοκιμές

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make test
```

Τα tests τρέχουν χωρίς πραγματική βάση — χρησιμοποιούν τον test client του Flask. Αυτό είναι ηθελημένο: το βασικό κριτήριο πριν από build είναι "ο κώδικας ξεκινά και τα endpoints απαντούν".

### 2. Δημιουργία της εικόνας

```bash
make build VERSION=0.1.0
```

Το αποτέλεσμα είναι μια τοπική εικόνα `<DOCKER_USER>/cloud-uth-pyapp:0.1.0`.

### 3. Ανέβασμα στο Docker Hub

```bash
make push VERSION=0.1.0
```

Από τη στιγμή που η εικόνα είναι δημόσια στο Docker Hub, το cluster μπορεί να την κατεβάσει χωρίς `imagePullSecret`.

> Σε πραγματικό περιβάλλον θα χρησιμοποιούσατε **ιδιωτικό** registry με κατάλληλο `imagePullSecret`. Η δημόσια χρήση εδώ είναι μόνο για παιδαγωγική απλότητα.

### 4. Ανάπτυξη στο cluster

```bash
make deploy VERSION=0.1.0
```

Στο παρασκήνιο, ο `Makefile` κάνει `sed` στο `01-deployment.yaml` και αντικαθιστά το placeholder `REPLACE_ME_USER/cloud-uth-pyapp:0.1.0` με την πραγματική σας εικόνα. Το αρχείο στο αποθετήριο παραμένει ανέπαφο, έτσι αποφεύγετε να περάσει κατά λάθος το προσωπικό σας image tag στο ιστορικό εκδόσεων.

### 5. Επαλήθευση

```bash
make status
```

Αναμένουμε `READY 2/2` και δύο Pods σε `Running`. Στη συνέχεια:

```bash
kubectl port-forward svc/pyapp 8080:80
```

Σε δεύτερο terminal:

```bash
curl http://127.0.0.1:8080/healthz
curl http://127.0.0.1:8080/version
curl http://127.0.0.1:8080/
```

Αναμενόμενες απαντήσεις:

**`/healthz`** (liveness probe):
```json
{"status":"ok"}
```

**`/version`**:
```json
{"version":"0.1.0"}
```

**`/`** (κύριο endpoint):
```json
{
  "message": "Hello from Python on Kubernetes!",
  "version": "0.1.0",
  "served_by": "pyapp-6584b6cd48-qxvz6",
  "names": ["Alice", "Bob", "Charlie"]
}
```

Το πεδίο `names` περιέχει δεδομένα που διαβάστηκαν από τη βάση PostgreSQL που ρυθμίστηκε στο παράδειγμα `11`. Το πεδίο `served_by` δείχνει ποιο Pod χειρίστηκε το αίτημα (δοκιμάστε να κάνετε περισσότερες κλήσεις για να δείτε διαφορετικά ονόματα Pods λόγω εξισορρόπησης φόρτου).

## Iterate: αλλαγή κώδικα και νέα έκδοση

Αυτό είναι το πιο σημαντικό βήμα παιδαγωγικά. Ανοίξτε το `app.py`, αλλάξτε το string του `message` (π.χ. προσθέστε το όνομά σας), και τρέξτε:

```bash
make test
make build push deploy VERSION=0.2.0
```

Παρακολουθήστε σε άλλο terminal:

```bash
kubectl rollout status deployment/pyapp
kubectl get pods -l app=pyapp -w
```

Θα δείτε rolling update, δηλαδή σταδιακή αντικατάσταση των παλιών Pods (`0.1.0`) από καινούργια (`0.2.0`) χωρίς downtime, χάρη στο readiness probe.

## Επίδειξη επαναφοράς (rollback)

Αν θέλετε να επιστρέψετε στην προηγούμενη έκδοση χωρίς νέο build:

```bash
make rollback
```

Δείτε τι προσφέρουν τα immutable tags: το `0.1.0` εξακολουθεί να υπάρχει στο registry, οπότε η επαναφορά είναι θέμα δευτερολέπτων. Αν είχατε χρησιμοποιήσει `:latest`, αυτή η εγγύηση **θα έλειπε**.

## Βέλτιστες πρακτικές που ενσωματώνει το παράδειγμα

- **Immutable image tags** (`0.1.0`, `0.2.0`, ...) ώστε τα rolling updates και τα rollbacks να είναι προβλέψιμα.
- **Καρφωμένες εξαρτήσεις** (`requirements.txt` με συγκεκριμένες εκδόσεις) ώστε δύο διαδοχικά builds να παράγουν την ίδια image.
- **Multi-replica Deployment** + **liveness probe** (επανεκκίνηση ενός container που έχει κολλήσει) + **readiness probe** (να μη δρομολογείται κίνηση σε Pod που δεν φτάνει ακόμη τη βάση).
- **Resource requests/limits** ώστε ο scheduler να μπορεί να τοποθετήσει τα Pods και το cluster να μη μοιράζει απεριόριστους πόρους.
- **Non-root container** στο Dockerfile.
- **Διαχωρισμός κώδικα/ρύθμισης/μυστικών**: ο κώδικας στην image, η ρύθμιση από `ConfigMap` (`db-config`), τα διαπιστευτήρια από `Secret` (`db-secret`).
- **Βρόχος ανάπτυξης χωρίς υποδομή CI**: ο `Makefile` εκτελεί τη ροή τοπικά. Όταν αργότερα προστεθεί GitHub Actions ή Jenkins, αυτά τα ίδια βήματα απλώς τρέχουν εκεί αντί για το laptop σας.

## Επιβεβαίωση επιτυχίας και κοινά λάθη

- Επιτυχία: όλα τα Pods `Running` και `READY=1/1`, η `/` επιστρέφει JSON με `names`, `served_by` (το hostname του Pod) και `version`.
- Αν τα Pods μένουν στο `0/1 Running` και μπαίνουν σε `Restart`: συνήθως αποτυγχάνει το readiness ή το liveness probe επειδή η βάση δεν είναι προσβάσιμη. Δοκιμάστε `kubectl logs deployment/pyapp` και `kubectl get pods -l app=postgres`.
- Αν δείτε `ImagePullBackOff`: συνήθως δεν έχετε τρέξει `make push`, ή το αποθετήριο δεν είναι δημόσιο, ή υπάρχει τυπογραφικό λάθος στο `DOCKER_USER`.
- Αν `make deploy` εφαρμόζει το manifest με ακόμη το placeholder image (παρατηρείτε `REPLACE_ME_USER` στο `kubectl describe`): ξεχάσατε να ορίσετε `DOCKER_USER` ή η αντικατάσταση με `sed` δεν ταίριαξε ακριβώς στη γραφή.
- **Ποτέ** μη χρησιμοποιήσετε `:latest`. Αν αλλάξετε τον πηγαίο κώδικα και κάνετε `make build push` με το ίδιο tag, το cluster μπορεί να μη δει τη νέα image γιατί το digest δεν αλλάζει με το `IfNotPresent` policy — και ένα `kubectl rollout undo` δεν έχει ιστορικό επαναφοράς.

## Καθαρισμός

Διαγραφή μόνο της εφαρμογής Python (διατηρώντας τη βάση του `11`):

```bash
make clean
```

Αν θέλετε να διαγράψετε και τη βάση:

```bash
cd ../11_web-app && make clean
```
