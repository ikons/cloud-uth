# From source code to cluster: end-to-end Python app deployment

This final step closes the chain we have been building so far: you write your own code, test it locally, build it into a Docker image, push it to a registry (Docker Hub), and deploy it as a regular `Deployment` that connects to the same PostgreSQL database we set up in `11_web-app`. The goal is not only Kubernetes practice but the full **commit → build → push → deploy → iterate** experience without any external CI infrastructure (no Jenkins, no GitHub Actions).

For consistent terminology across the course guides, consult [glossary.md](../../../glossary.md).

## Learning objectives

- Write a small Python (Flask) application that talks to the existing database from `11`.
- Author a `Dockerfile` that follows best practices (pinned base image, non-root user, small layers, production WSGI server).
- Use **immutable image tags** (no `:latest`) to gain predictable rollouts and rollbacks.
- Apply liveness and readiness probes that distinguish "alive" from "ready for traffic".
- Realize that a "CI-style" workflow can be a plain `Makefile` with clear steps: `test → build → push → deploy → rollback`.

## How this fits in the sequence

Up to step `11`, the application was either a ready image (nginx, postgres, php-apache) or PHP code injected through a `ConfigMap`. Here the web tier is **yours**: the code lives in files in your repository, is version-controlled, tested with `pytest`, and built into an image that lives in a registry. This is exactly the path you will follow in any professional environment.

## Prerequisites

1. You have completed `11_web-app` and Postgres is running in your namespace. Specifically you need:
   - `Service/postgres`
   - `ConfigMap/db-config`
   - `Secret/db-secret`
   - the `myappdb` database with the `my_table` table (already populated by `04-init-sql.yaml` in `11`).

   If they are not running, deploy them from the `11_web-app` directory:

   ```bash
   make deploy
   ```

   The web tier of `11` is not required; you can leave it or remove only `webserver`/`webserver-service`/`web-content` if you prefer.

2. You have a [Docker Hub](https://hub.docker.com/) account and a local Docker Engine or Docker Desktop. Log in:

   ```bash
   docker login
   ```

3. You have Python 3.10+ locally to run the tests before each build.

## File layout

| File | Purpose |
|------|---------|
| `app.py` | The Flask application (4 endpoints). |
| `requirements.txt` | Pinned dependencies. |
| `test_app.py` | Two pytest tests run before every build. |
| `Dockerfile` | Image build; non-root, gunicorn. |
| `.dockerignore` | Files excluded from the image. |
| `01-deployment.yaml` | `Deployment` with 2 replicas, probes, resources. |
| `02-service.yaml` | `Service ClusterIP` exposing the app inside the cluster. |
| `Makefile` | Targets for the development workflow. |

## Application files

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

## Kubernetes manifests

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

## Deployment workflow

The full workflow is **five distinct steps**: local tests, build the image, push it to the registry, apply manifests, verify. The `Makefile` automates each step.

First, move into the directory and export your Docker Hub username so you do not retype it:

```bash
cd ~/cloud-uth/code/02_kubernetes/12_app-from-source
export DOCKER_USER=<dockerhub-user>
```

### 0. Authenticate with Docker Hub (one-time setup)

Before you can push images, authenticate with Docker Hub:

```bash
docker login -u <dockerhub-user>
```

You will be prompted for a password. You have two options:

- **Use your Docker Hub password** (simple, but less secure).
- **Use a Personal Access Token** (recommended):
  1. Go to https://hub.docker.com/settings/security
  2. Click "New Access Token"
  3. Copy the token and paste it when `docker login` prompts for a password
  
This authentication is cached locally, so you only need to do it once (or when the token expires).

### 1. Local tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
make test
```

The tests run without a real database — they use the Flask test client. This is intentional: the basic gate before a build is "the code starts and the endpoints respond".

### 2. Build the image

```bash
make build VERSION=0.1.0
```

The result is a local image `<DOCKER_USER>/cloud-uth-pyapp:0.1.0`.

### 3. Push to Docker Hub

```bash
make push VERSION=0.1.0
```

Once the image is public on Docker Hub, the cluster can pull it without an `imagePullSecret`.

> In a real environment you would use a **private** registry with an appropriate `imagePullSecret`. Going public here is purely for pedagogical simplicity.

### 4. Deploy to the cluster

```bash
make deploy VERSION=0.1.0
```

Behind the scenes the `Makefile` runs `sed` over `01-deployment.yaml` and replaces the placeholder `REPLACE_ME_USER/cloud-uth-pyapp:0.1.0` with your actual image. The file in the repository remains unchanged, so you do not accidentally commit your personal image tag.

### 5. Verification

```bash
make status
```

Expected: `READY 2/2` and two Pods in `Running`. Then:

```bash
kubectl port-forward svc/pyapp 8080:80
```

In a second terminal:

```bash
curl http://127.0.0.1:8080/healthz
curl http://127.0.0.1:8080/version
curl http://127.0.0.1:8080/
```

Expected responses:

**`/healthz`** (liveness probe):
```json
{"status":"ok"}
```

**`/version`**:
```json
{"version":"0.1.0"}
```

**`/`** (main endpoint):
```json
{
  "message": "Hello from Python on Kubernetes!",
  "version": "0.1.0",
  "served_by": "pyapp-6584b6cd48-qxvz6",
  "names": ["Alice", "Bob", "Charlie"]
}
```

The `names` field contains data read from the PostgreSQL database set up in example `11`. The `served_by` field shows which Pod handled the request (try calling multiple times to see the requests distributed across Pods).

## Iterate: change the code and ship a new version

This is the most important step pedagogically. Open `app.py`, change the `message` string (e.g., add your name), and run:

```bash
make test
make build push deploy VERSION=0.2.0
```

Watch in another terminal:

```bash
kubectl rollout status deployment/pyapp
kubectl get pods -l app=pyapp -w
```

You will see a rolling update: gradual replacement of old Pods (`0.1.0`) with new ones (`0.2.0`) without downtime, thanks to the readiness probe.

## Rollback demo

If you want to revert to the previous version without a new build:

```bash
make rollback
```

This is where immutable tags pay off: `0.1.0` still exists in the registry, so the rollback is a matter of seconds. Had you used `:latest`, that guarantee would be **gone**.

## Best practices baked into this example

- **Immutable image tags** (`0.1.0`, `0.2.0`, ...) so rolling updates and rollbacks are deterministic.
- **Pinned dependencies** (`requirements.txt` with explicit versions) so two consecutive builds produce the same image.
- **Multi-replica Deployment** + **liveness probe** (restart a stuck container) + **readiness probe** (do not route traffic to a Pod that cannot reach the database).
- **Resource requests and limits** so the scheduler can place Pods and the cluster does not hand out unbounded resources.
- **Non-root container** in the Dockerfile.
- **Separation of code, config, and secrets**: code in the image, configuration in a `ConfigMap` (`db-config`), credentials in a `Secret` (`db-secret`).
- **Inner-loop without CI infrastructure**: the `Makefile` runs the workflow locally. When GitHub Actions or Jenkins is added later, the same steps simply run there instead of on your laptop.

## Verification and common pitfalls

- Success: all Pods `Running` and `READY=1/1`, `/` returns JSON with `names`, `served_by` (the Pod hostname), and `version`.
- If Pods stay at `0/1 Running` and flap with `Restart`: usually a failing readiness or liveness probe because the database is unreachable. Try `kubectl logs deployment/pyapp` and `kubectl get pods -l app=postgres`.
- If you see `ImagePullBackOff`: usually you forgot `make push`, or the repository is not public, or there is a typo in `DOCKER_USER`.
- If `make deploy` applies a manifest still containing the placeholder image (you see `REPLACE_ME_USER` in `kubectl describe`): you forgot to set `DOCKER_USER`, or the `sed` substitution did not match the exact text in the file.
- **Never** use `:latest`. If you change the source and run `make build push` with the same tag, the cluster might not see the new image because the digest does not change under the `IfNotPresent` policy — and `kubectl rollout undo` then has no history to roll back to.

## Cleanup

Delete only the Python app, leaving the database from `11` running:

```bash
make clean
```

To also delete the database:

```bash
cd ../11_web-app && make clean
```
