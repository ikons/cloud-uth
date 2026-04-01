# Docker Compose — Reverse Proxy & Load Balancing

Σύνθετο παράδειγμα: Nginx reverse proxy μπροστά από πολλαπλούς web servers.

## Τι θα μάθουμε

- Reverse proxy pattern
- Load balancing μεταξύ containers
- Custom Docker networks
- Πολλαπλά services σε ένα compose αρχείο

## Αρχεία

- `docker-compose.yml` — 3 services: nginx proxy + web1 + web2
- `nginx.conf` — ρύθμιση reverse proxy με upstream load balancing
- `web1/index.html` — σελίδα του Web1
- `web2/index.html` — σελίδα του Web2

## Αρχιτεκτονική

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
              └────────-┘  └────────┘
```

Ο proxy δέχεται αιτήματα στη θύρα 8080 και τα μοιράζει εναλλάξ στο web1 και web2 (round-robin).

## Βήματα

### 1. Εξέταση nginx.conf

```nginx
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

- `upstream backend` : ορίζει ομάδα servers — χρησιμοποιεί τα ονόματα των services
- `proxy_pass` : προωθεί τα requests στην ομάδα
- Round-robin: κάθε request πάει εναλλάξ σε web1 και web2

### 2. Εκκίνηση

```bash
cd ~/cloud-uth/code/01_docker/07_compose-multi-web

docker compose up -d
```

### 3. Δοκιμή

Ανοίξτε τον browser στο [http://localhost:8080](http://localhost:8080).

Κάντε refresh πολλές φορές — θα βλέπετε εναλλάξ "Welcome to Web1" και "Welcome to Web2"!

Εναλλακτικά, από το terminal:

```bash
# Κάθε κλήση μπορεί να πάει σε διαφορετικό server
curl http://localhost:8080
curl http://localhost:8080
curl http://localhost:8080
```

### 4. Εξέταση του δικτύου

```bash
# Δες τα δίκτυα που δημιούργησε ο Docker
docker network ls

# Δες ποια containers είναι στο δίκτυο
docker network inspect 07_compose-multi-web_mynetwork
```

### 5. Τερματισμός

```bash
docker compose down
```
