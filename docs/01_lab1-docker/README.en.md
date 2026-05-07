# Docker container usage examples

## Introduction

This guide will help you learn the basics of **Docker** through 7 examples of increasing complexity. We start from the first `docker run` and work our way up to multi-container applications with Docker Compose.

This guide is intended to run from an Ubuntu/WSL terminal. It assumes that `00_workstation-setup` has already been completed, so `docker version`, `docker compose version`, and `docker run hello-world` work normally from WSL and the repository already exists locally at `~/cloud-uth`.

For consistent terminology across the course guides, consult [`glossary.md`](../../glossary.md).

All examples are located in the `code/01_docker/` directory of the repository:

| # | Directory | Topic |
|---|-----------|-------|
| 01 | `01_hello-docker` | First contact — `docker run`, `ps`, `rm` |
| 02 | `02_web-server` | Web server — port mapping, logs, exec |
| 03 | `03_volumes` | Volumes — ephemeral vs persistent storage |
| 04 | `04_custom-image` | Dockerfile — building a custom image |
| 05 | `05_environment` | Environment variables — configuration |
| 06 | `06_compose-basics` | Docker Compose — multiple containers |
| 07 | `07_compose-multi-web` | Reverse proxy — load balancing |

## 01. Hello Docker — First contact

```bash
cd ~/cloud-uth/code/01_docker/01_hello-docker
```

### 01.1 Your first container

```bash
docker run hello-world
```

What happens:

1. Docker looks for the `hello-world` image locally.
2. If not found, it pulls it from Docker Hub.
3. It creates a container from that image.
4. It runs the container, which prints a message and exits.

### 01.2 Running a command inside a container

```bash
docker run alpine echo "Hello from Alpine Linux!"
```

`alpine` is a very small Linux image (~5 MB). We run an `echo` command inside it.

### 01.3 Interactive container

```bash
docker run -it alpine sh
```

This opens a shell inside the container. Try:

```bash
hostname
cat /etc/os-release
ls /
exit
```

Flags:

- `-i` : interactive — keeps stdin open
- `-t` : allocate pseudo-TTY (terminal)

### 01.4 Inspecting containers

```bash
# Currently running containers
docker ps

# All containers (including stopped)
docker ps -a
```

### 01.5 Cleanup

```bash
# Remove a stopped container
docker rm <container_id>

# Remove all stopped containers
docker container prune

# List images
docker images

# Remove an image
docker rmi hello-world
```

## 02. Web Server — Port mapping, logs, exec

```bash
cd ~/cloud-uth/code/01_docker/02_web-server
```

### 02.1 Start Nginx

```bash
docker run -d -p 8080:80 --name my-nginx nginx
```

- `-d` : detached mode — runs in the background
- `-p 8080:80` : maps port 8080 on the host to port 80 inside the container
- `--name my-nginx` : gives the container a name

Open your browser at http://localhost:8080 — you should see the default Nginx page.

### 02.2 Logs

```bash
# View logs
docker logs my-nginx

# Follow logs in real time (Ctrl+C to stop)
docker logs -f my-nginx
```

### 02.3 Executing commands inside the container

```bash
# Open a shell inside the running container
docker exec -it my-nginx bash

# Inside the container:
cat /usr/share/nginx/html/index.html
exit
```

### 02.4 Stop and remove

```bash
docker stop my-nginx
docker rm my-nginx
```

## 03. Volumes — Ephemeral vs persistent storage

```bash
cd ~/cloud-uth/code/01_docker/03_volumes
```

In Docker there are **two types of storage**:

- **Ephemeral** — data is lost when the container is removed
- **Persistent** — data survives independently of the container

### 03.1 Ephemeral storage — data is lost

```bash
# Create a file inside a container
docker run --name temp-nginx -d nginx
docker exec temp-nginx bash -c "echo 'My custom page' > /usr/share/nginx/html/test.html"

# Verify it exists
docker exec temp-nginx cat /usr/share/nginx/html/test.html

# Remove the container
docker stop temp-nginx
docker rm temp-nginx

# New container — the file is gone
docker run --name temp-nginx2 -d nginx
docker exec temp-nginx2 cat /usr/share/nginx/html/test.html
docker stop temp-nginx2
docker rm temp-nginx2
```

### 03.2 Bind mount — linking a file from the host

A bind mount links a host file or directory into the container:

```bash
docker run -d -p 8080:80 --name web-volumes \
  -v ./index.html:/usr/share/nginx/html/index.html:ro \
  nginx
```

Open http://localhost:8080 — you should see our custom page:

<!-- AUTO-CODE: code/01_docker/03_volumes/index.html -->
``` html
<!DOCTYPE html>
<html lang="el">
<head>
    <meta charset="UTF-8">
    <title>Docker Volumes Demo</title>
</head>
<body>
    <h1>Volumes Demo</h1>
    <p>This page is served from a bind mount!</p>
    <p>Try editing this file on your host machine and refresh the browser.</p>
</body>
</html>
```
<!-- END AUTO-CODE -->

Edit the `index.html` file in your editor, change the text, and refresh the browser. The change appears immediately!

- Flag `:ro` = read-only — the container can only read, not write.

```bash
docker stop web-volumes
docker rm web-volumes
```

### 03.3 Named volume — persistent storage

```bash
# Create a named volume
docker volume create my-data

# Container that writes to the volume
docker run -d --name vol-demo \
  -v my-data:/data alpine \
  sh -c "echo 'Hello from volume' > /data/message.txt && sleep 3600"

# Read the file
docker exec vol-demo cat /data/message.txt

# Remove the container
docker stop vol-demo
docker rm vol-demo

# New container — the data is still there!
docker run --rm -v my-data:/data alpine cat /data/message.txt
```

### 03.4 Cleanup

```bash
docker volume rm my-data
```

## 04. Custom Image — Building an image with a Dockerfile

```bash
cd ~/cloud-uth/code/01_docker/04_custom-image
```

In this example we build our own Docker image using a `Dockerfile`.

### 04.1 `app.sh`

A simple shell script that will run inside the container:

<!-- AUTO-CODE: code/01_docker/04_custom-image/app.sh -->
``` bash
#!/bin/sh
echo "=== Custom Docker Image ==="
echo "Hostname: $(hostname)"
echo "Date: $(date)"
echo ""
echo "Container is running..."

count=1
while true; do
    echo "[${count}] Still running at $(date '+%H:%M:%S')"
    count=$((count + 1))
    sleep 5
done
```
<!-- END AUTO-CODE -->

### 04.2 `Dockerfile`

The `Dockerfile` contains the instructions for building the image:

<!-- AUTO-CODE: code/01_docker/04_custom-image/Dockerfile -->
``` dockerfile
FROM alpine:latest

# Copy our script into the image
COPY app.sh /app.sh

# Make it executable
RUN chmod +x /app.sh

# Default command when the container starts
CMD ["/app.sh"]
```
<!-- END AUTO-CODE -->

- `FROM` : base image we build upon
- `COPY` : copies files from the host into the image
- `RUN` : executes a command during build
- `CMD` : command that runs when the container starts

### 04.3 Build

```bash
docker build -t my-app .
```

- `-t my-app` : names the image `my-app`
- `.` : the current directory is the build context

### 04.4 Run

```bash
docker run -d --name my-app-container my-app

# Follow logs (Ctrl+C to stop)
docker logs -f my-app-container
```

You will see output every 5 seconds:

```
=== Custom Docker Image ===
Hostname: bc01dce2fb4d
Date: Wed Apr  1 12:00:00 UTC 2026

Container is running...
[1] Still running at 12:00:00
[2] Still running at 12:00:05
...
```

### 04.5 Inspect the image

```bash
# List images
docker images | grep my-app

# View image layers
docker history my-app
```

### 04.6 Cleanup

```bash
docker stop my-app-container
docker rm my-app-container
docker rmi my-app
```

## 05. Environment Variables — Configuring containers

```bash
cd ~/cloud-uth/code/01_docker/05_environment
```

Environment variables let us change the behavior of a container **without modifying code or rebuilding the image**.

### 05.1 Files

**`app.sh`** — a script that reads environment variables:

<!-- AUTO-CODE: code/01_docker/05_environment/app.sh -->
``` bash
#!/bin/sh
echo "=== Application Configuration ==="
echo "APP_NAME: ${APP_NAME:-not set}"
echo "APP_ENV:  ${APP_ENV:-not set}"
echo "APP_PORT: ${APP_PORT:-not set}"
echo "================================="
echo ""
echo "Application is running..."

while true; do
    echo "[${APP_NAME:-app}] Running in ${APP_ENV:-unknown} mode on port ${APP_PORT:-?}"
    sleep 5
done
```
<!-- END AUTO-CODE -->

**`Dockerfile`** — defines default values with `ENV`:

<!-- AUTO-CODE: code/01_docker/05_environment/Dockerfile -->
``` dockerfile
FROM alpine:latest

# Default values for environment variables
ENV APP_NAME=my-app
ENV APP_ENV=development
ENV APP_PORT=8080

COPY app.sh /app.sh
RUN chmod +x /app.sh

CMD ["/app.sh"]
```
<!-- END AUTO-CODE -->

### 05.2 Build and run with defaults

```bash
docker build -t env-app .
docker run --rm --name env-demo env-app
```

You will see the default values: `APP_NAME=my-app`, `APP_ENV=development`, `APP_PORT=8080`.

Press `Ctrl+C` to stop.

### 05.3 Override variables

```bash
docker run --rm --name env-demo \
  -e APP_NAME=cloud-app \
  -e APP_ENV=production \
  -e APP_PORT=3000 \
  env-app
```

The values change without rebuilding!

### 05.4 Inspect container variables

```bash
docker run -d --name env-inspect env-app
docker exec env-inspect env
docker stop env-inspect
docker rm env-inspect
```

### 05.5 Cleanup

```bash
docker rmi env-app
```

## 06. Docker Compose — Multiple containers together

```bash
cd ~/cloud-uth/code/01_docker/06_compose-basics
```

So far we have been running containers individually. In practice, an application consists of multiple services (web server, database, cache, etc.). **Docker Compose** lets us define them together in a single `docker-compose.yml` file.

### 06.1 `docker-compose.yml`

<!-- AUTO-CODE: code/01_docker/06_compose-basics/docker-compose.yml -->
``` yaml
services:
  web:
    image: nginx
    ports:
      - "8080:80"
    depends_on:
      - db

  db:
    image: postgres:17
    environment:
      POSTGRES_USER: student
      POSTGRES_PASSWORD: secret123
      POSTGRES_DB: mydb
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  db-data:
```
<!-- END AUTO-CODE -->

What we see:

- **2 services**: `web` (Nginx) and `db` (PostgreSQL)
- **ports**: the web server is accessible at `localhost:8080`
- **environment**: the database is configured via environment variables
- **volumes**: database data is stored in a named volume
- **depends_on**: web starts after the database

### 06.2 Start

```bash
docker compose up -d
```

### 06.3 Verify

```bash
# Running containers
docker compose ps

# Logs
docker compose logs

# Logs for a single service
docker compose logs db
```

### 06.4 Connect to the database

```bash
docker compose exec db psql -U student -d mydb
```

Inside `psql` try:

```sql
\l
\q
```

### 06.5 Service discovery

Containers in the same compose network can communicate using the **service name** as a hostname. For example, the web server can reach the database at hostname `db`.

### 06.6 Shutdown

```bash
# Stop containers
docker compose down

# Stop and remove volumes (data is lost)
docker compose down -v
```

## 07. Reverse Proxy — Load balancing with Docker Compose

```bash
cd ~/cloud-uth/code/01_docker/07_compose-multi-web
```

Advanced example: an **Nginx reverse proxy** in front of **two web servers**, with load balancing.

### 07.1 Architecture

```
                    ┌──────────┐
  Browser ──:8080──▶│  nginx   │
                    │  proxy   │
                    └────┬─────┘
                         │
                    ┌────┴─────┐
                    │ mynetwork│
                    ┌────┴─────┐
              ┌─────┴──┐  ┌───┴────┐
              │  web1   │  │  web2  │
              └─────────┘  └────────┘
```

The proxy receives requests on port 8080 and distributes them alternately to web1 and web2 (round-robin).

### 07.2 `docker-compose.yml`

<!-- AUTO-CODE: code/01_docker/07_compose-multi-web/docker-compose.yml -->
``` yaml
services:
  web1:
    image: nginx
    container_name: web1
    volumes:
      - ./web1:/usr/share/nginx/html
    networks:
      - mynetwork

  web2:
    image: nginx
    container_name: web2
    volumes:
      - ./web2:/usr/share/nginx/html
    networks:
      - mynetwork

  nginx:
    image: nginx
    container_name: nginx-proxy
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "8080:80"
    depends_on:
      - web1
      - web2
    networks:
      - mynetwork

networks:
  mynetwork:
```
<!-- END AUTO-CODE -->

### 07.3 HTML files

**Web1:**

<!-- AUTO-CODE: code/01_docker/07_compose-multi-web/web1/index.html -->
``` html
<h1>Welcome to Web1</h1>
```
<!-- END AUTO-CODE -->

**Web2:**

<!-- AUTO-CODE: code/01_docker/07_compose-multi-web/web2/index.html -->
``` html
<h1>Welcome to Web2</h1>
```
<!-- END AUTO-CODE -->

### 07.4 `nginx.conf`

<!-- AUTO-CODE: code/01_docker/07_compose-multi-web/nginx.conf -->
``` nginx
events {}

http {
    upstream backend {
        server web1;
        server web2;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://backend;
        }
    }
}
```
<!-- END AUTO-CODE -->

- `upstream backend` : defines a server group — uses the service names as hostnames
- `proxy_pass` : forwards requests to the group
- Round-robin: each request goes alternately to web1 and web2

### 07.5 Start and test

```bash
docker compose up -d
```

Open http://localhost:8080 and refresh multiple times — you should see "Welcome to Web1" and "Welcome to Web2" alternating.

Alternatively, from the terminal:

```bash
curl http://localhost:8080
curl http://localhost:8080
curl http://localhost:8080
```

### 07.6 Inspect the network

```bash
# Docker networks
docker network ls

# Containers in the network
docker network inspect 07_compose-multi-web_mynetwork
```

### 07.7 Shutdown

```bash
docker compose down
```
