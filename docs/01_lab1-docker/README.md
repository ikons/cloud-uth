
# Παραδείγματα χρήσης Docker containers

## Εισαγωγή

Αυτός ο οδηγός θα σας βοηθήσει να μάθετε τα βασικά του **Docker** μέσα από 7 παραδείγματα με αυξανόμενη πολυπλοκότητα. Ξεκινάμε από το πρώτο `docker run` και φτάνουμε μέχρι multi-container εφαρμογές με Docker Compose.

Ο οδηγός εκτελείται από τερματικό Ubuntu/WSL. Προϋποθέτει ότι έχει ήδη ολοκληρωθεί ο οδηγός `00_workstation-setup`, άρα οι εντολές `docker version`, `docker compose version` και `docker run hello-world` λειτουργούν κανονικά από το WSL και το repository υπάρχει ήδη τοπικά στο `~/cloud-uth`.

Για συνεπή ελληνική ορολογία στους οδηγούς του μαθήματος, ανατρέξτε στο [`glossary.md`](../../glossary.md).

Τα παραδείγματα βρίσκονται στον φάκελο `code/01_docker/` του αποθετηρίου:

| # | Φάκελος | Θέμα |
|---|---------|------|
| 01 | `01_hello-docker` | Πρώτη επαφή — `docker run`, `ps`, `rm` |
| 02 | `02_web-server` | Web server — port mapping, logs, exec |
| 03 | `03_volumes` | Volumes — ephemeral vs persistent storage |
| 04 | `04_custom-image` | Dockerfile — δημιουργία custom image |
| 05 | `05_environment` | Environment variables — παραμετροποίηση |
| 06 | `06_compose-basics` | Docker Compose — πολλαπλά containers |
| 07 | `07_compose-multi-web` | Reverse proxy — load balancing |

## 01. Hello Docker — Πρώτη επαφή

```bash
cd ~/cloud-uth/code/01_docker/01_hello-docker
```

### 01.1 Το πρώτο container

```bash
docker run hello-world
```

Τι συμβαίνει:

1. Ο Docker ψάχνει τοπικά το image `hello-world`.
2. Αν δεν το βρει, το κατεβάζει από το Docker Hub (`pull`).
3. Δημιουργεί ένα container από αυτό το image.
4. Τρέχει το container, που τυπώνει ένα μήνυμα και τερματίζει.

### 01.2 Εκτέλεση εντολής μέσα σε container

```bash
docker run alpine echo "Hello from Alpine Linux!"
```

Το `alpine` είναι ένα πολύ μικρό Linux image (~5 MB). Τρέχουμε μια εντολή `echo` μέσα σε αυτό.

### 01.3 Διαδραστικό container

```bash
docker run -it alpine sh
```

Ανοίγει ένα shell μέσα στο container. Δοκιμάστε:

```bash
hostname
cat /etc/os-release
ls /
exit
```

Flags:

- `-i` : interactive — κρατάει ανοιχτό το stdin
- `-t` : allocate pseudo-TTY (terminal)

### 01.4 Εξέταση containers

```bash
# Τρέχοντα containers
docker ps

# Όλα τα containers (και τα σταματημένα)
docker ps -a
```

### 01.5 Καθαρισμός

```bash
# Διαγραφή ενός σταματημένου container
docker rm <container_id>

# Διαγραφή όλων των σταματημένων containers
docker container prune

# Λίστα images
docker images

# Διαγραφή image
docker rmi hello-world
```

## 02. Web Server — Port mapping, logs, exec

```bash
cd ~/cloud-uth/code/01_docker/02_web-server
```

### 02.1 Εκκίνηση Nginx

```bash
docker run -d -p 8080:80 --name my-nginx nginx
```

- `-d` : detached mode — τρέχει στο background
- `-p 8080:80` : συνδέει τη θύρα 8080 του host με τη θύρα 80 του container
- `--name my-nginx` : δίνει όνομα στο container

Ανοίξτε τον browser στο http://localhost:8080 — θα δείτε τη default σελίδα του Nginx.

### 02.2 Logs

```bash
# Εμφάνιση logs
docker logs my-nginx

# Παρακολούθηση logs σε πραγματικό χρόνο (Ctrl+C για διακοπή)
docker logs -f my-nginx
```

### 02.3 Εκτέλεση εντολής μέσα στο container

```bash
# Άνοιγμα shell στο container που τρέχει
docker exec -it my-nginx bash

# Μέσα στο container:
cat /usr/share/nginx/html/index.html
exit
```

### 02.4 Σταμάτημα και διαγραφή

```bash
docker stop my-nginx
docker rm my-nginx
```

## 03. Volumes — Ephemeral vs persistent storage

```bash
cd ~/cloud-uth/code/01_docker/03_volumes
```

Στο Docker υπάρχουν **δύο τύποι αποθήκευσης**:

- **Ephemeral (προσωρινή)** — τα δεδομένα χάνονται όταν το container διαγραφεί
- **Persistent (μόνιμη)** — τα δεδομένα διατηρούνται ανεξάρτητα από το container

### 03.1 Ephemeral storage — τα δεδομένα χάνονται

```bash
# Δημιουργούμε αρχείο μέσα στο container
docker run --name temp-nginx -d nginx
docker exec temp-nginx bash -c "echo 'My custom page' > /usr/share/nginx/html/test.html"

# Επιβεβαίωση
docker exec temp-nginx cat /usr/share/nginx/html/test.html

# Διαγραφή container
docker stop temp-nginx
docker rm temp-nginx

# Νέο container — το αρχείο δεν υπάρχει πια
docker run --name temp-nginx2 -d nginx
docker exec temp-nginx2 cat /usr/share/nginx/html/test.html
docker stop temp-nginx2
docker rm temp-nginx2
```

### 03.2 Bind mount — σύνδεση αρχείου από τον host

Ένα bind mount συνδέει ένα αρχείο ή φάκελο του host μέσα στο container:

```bash
docker run -d -p 8080:80 --name web-volumes \
  -v ./index.html:/usr/share/nginx/html/index.html:ro \
  nginx
```

Ανοίξτε http://localhost:8080 — θα δείτε τη δική μας σελίδα:

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

Επεξεργαστείτε το αρχείο `index.html` στον editor σας, αλλάξτε το κείμενο και κάντε refresh τον browser. Η αλλαγή εμφανίζεται αμέσως!

- Flag `:ro` = read-only — το container μπορεί μόνο να διαβάσει, όχι να γράψει.

```bash
docker stop web-volumes
docker rm web-volumes
```

### 03.3 Named volume — μόνιμη αποθήκευση

```bash
# Δημιουργία named volume
docker volume create my-data

# Container που γράφει στο volume
docker run -d --name vol-demo \
  -v my-data:/data alpine \
  sh -c "echo 'Hello from volume' > /data/message.txt && sleep 3600"

# Ανάγνωση
docker exec vol-demo cat /data/message.txt

# Διαγραφή container
docker stop vol-demo
docker rm vol-demo

# Νέο container — τα δεδομένα είναι ακόμα εκεί!
docker run --rm -v my-data:/data alpine cat /data/message.txt
```

### 03.4 Καθαρισμός

```bash
docker volume rm my-data
```

## 04. Custom Image — Δημιουργία image με Dockerfile

```bash
cd ~/cloud-uth/code/01_docker/04_custom-image
```

Σε αυτό το παράδειγμα φτιάχνουμε το δικό μας Docker image χρησιμοποιώντας ένα `Dockerfile`.

### 04.1 Αρχείο `app.sh`

Ένα απλό shell script που θα τρέχει μέσα στο container:

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

### 04.2 Αρχείο `Dockerfile`

Το `Dockerfile` περιέχει τις οδηγίες για το χτίσιμο του image:

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

- `FROM` : βασικό image πάνω στο οποίο χτίζουμε
- `COPY` : αντιγράφει αρχεία από τον host στο image
- `RUN` : εκτελεί εντολή κατά το build
- `CMD` : εντολή που τρέχει όταν ξεκινάει το container

### 04.3 Build

```bash
docker build -t my-app .
```

- `-t my-app` : ονομάζει το image `my-app`
- `.` : ο τρέχων φάκελος είναι το build context

### 04.4 Run

```bash
docker run -d --name my-app-container my-app

# Παρακολούθηση logs (Ctrl+C για διακοπή)
docker logs -f my-app-container
```

Θα δείτε output κάθε 5 δευτερόλεπτα:

```
=== Custom Docker Image ===
Hostname: bc01dce2fb4d
Date: Wed Apr  1 12:00:00 UTC 2026

Container is running...
[1] Still running at 12:00:00
[2] Still running at 12:00:05
...
```

### 04.5 Εξέταση image

```bash
# Λίστα images
docker images | grep my-app

# Layers του image
docker history my-app
```

### 04.6 Καθαρισμός

```bash
docker stop my-app-container
docker rm my-app-container
docker rmi my-app
```

## 05. Environment Variables — Παραμετροποίηση containers

```bash
cd ~/cloud-uth/code/01_docker/05_environment
```

Τα environment variables μας επιτρέπουν να αλλάζουμε τη συμπεριφορά ενός container **χωρίς να αλλάζουμε τον κώδικα ή να χτίζουμε νέο image**.

### 05.1 Αρχεία

**`app.sh`** — script που διαβάζει μεταβλητές περιβάλλοντος:

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

**`Dockerfile`** — ορίζει default τιμές με `ENV`:

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

### 05.2 Build και run με defaults

```bash
docker build -t env-app .
docker run --rm --name env-demo env-app
```

Θα δείτε τις default τιμές: `APP_NAME=my-app`, `APP_ENV=development`, `APP_PORT=8080`.

Πατήστε `Ctrl+C` για διακοπή.

### 05.3 Override μεταβλητών

```bash
docker run --rm --name env-demo \
  -e APP_NAME=cloud-app \
  -e APP_ENV=production \
  -e APP_PORT=3000 \
  env-app
```

Οι τιμές αλλάζουν χωρίς rebuild!

### 05.4 Εξέταση μεταβλητών ενός container

```bash
docker run -d --name env-inspect env-app
docker exec env-inspect env
docker stop env-inspect
docker rm env-inspect
```

### 05.5 Καθαρισμός

```bash
docker rmi env-app
```

## 06. Docker Compose — Πολλαπλά containers μαζί

```bash
cd ~/cloud-uth/code/01_docker/06_compose-basics
```

Μέχρι τώρα τρέχαμε containers μεμονωμένα. Στην πράξη, μια εφαρμογή αποτελείται από πολλά services (web server, database, cache κλπ.). Το **Docker Compose** μας επιτρέπει να τα ορίσουμε μαζί σε ένα αρχείο `docker-compose.yml`.

### 06.1 Αρχείο `docker-compose.yml`

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

Τι βλέπουμε:

- **2 services**: `web` (Nginx) και `db` (PostgreSQL)
- **ports**: ο web server είναι προσβάσιμος στο `localhost:8080`
- **environment**: η βάση ρυθμίζεται μέσω μεταβλητών περιβάλλοντος
- **volumes**: τα δεδομένα της βάσης αποθηκεύονται σε named volume
- **depends_on**: ο web ξεκινάει μετά τη βάση

### 06.2 Εκκίνηση

```bash
docker compose up -d
```

### 06.3 Επιβεβαίωση

```bash
# Containers που τρέχουν
docker compose ps

# Logs
docker compose logs

# Logs μόνο ενός service
docker compose logs db
```

### 06.4 Σύνδεση στη βάση δεδομένων

```bash
docker compose exec db psql -U student -d mydb
```

Μέσα στο `psql` δοκιμάστε:

```sql
\l
\q
```

### 06.5 Service discovery

Τα containers στο ίδιο compose network μπορούν να επικοινωνούν χρησιμοποιώντας το **όνομα του service** ως hostname. Για παράδειγμα, ο web server μπορεί να βρει τη βάση στο hostname `db`.

### 06.6 Τερματισμός

```bash
# Σταμάτημα containers
docker compose down

# Σταμάτημα και διαγραφή volumes (τα δεδομένα χάνονται)
docker compose down -v
```

## 07. Reverse Proxy — Load balancing με Docker Compose

```bash
cd ~/cloud-uth/code/01_docker/07_compose-multi-web
```

Σύνθετο παράδειγμα: ένας **Nginx reverse proxy** μπροστά από **δύο web servers**, με load balancing.

### 07.1 Αρχιτεκτονική

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

Ο proxy δέχεται αιτήματα στη θύρα 8080 και τα μοιράζει εναλλάξ στο web1 και web2 (round-robin).

### 07.2 Αρχείο `docker-compose.yml`

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

### 07.3 HTML αρχεία

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

### 07.4 Αρχείο `nginx.conf`

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

- `upstream backend` : ορίζει ομάδα servers — χρησιμοποιεί τα ονόματα των services ως hostnames
- `proxy_pass` : προωθεί τα requests στην ομάδα
- Round-robin: κάθε request πάει εναλλάξ σε web1 και web2

### 07.5 Εκκίνηση και δοκιμή

```bash
docker compose up -d
```

Ανοίξτε http://localhost:8080 και κάντε refresh πολλές φορές — θα βλέπετε εναλλάξ "Welcome to Web1" και "Welcome to Web2".

Εναλλακτικά, από το terminal:

```bash
curl http://localhost:8080
curl http://localhost:8080
curl http://localhost:8080
```

### 07.6 Εξέταση δικτύου

```bash
# Docker networks
docker network ls

# Ποια containers είναι στο δίκτυο
docker network inspect 07_compose-multi-web_mynetwork
```

### 07.7 Τερματισμός

```bash
docker compose down
```
