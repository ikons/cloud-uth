# Docker Compose — Βασικά

Τρέχουμε πολλαπλά containers μαζί με Docker Compose.

Για συνεπή ελληνική ορολογία στους οδηγούς του μαθήματος, ανατρέξτε στο [glossary.md](../../../glossary.md).

## Τι θα μάθουμε

- Τι είναι το Docker Compose και γιατί το χρειαζόμαστε
- Δομή αρχείου `docker-compose.yml`
- Εντολές: `docker compose up`, `docker compose down`
- Service discovery: πώς τα containers βρίσκουν το ένα το άλλο

## Αρχεία

- `docker-compose.yml` — ορίζει 2 services: web server (Nginx) + database (PostgreSQL)

## Βήματα

### 1. Εξέταση του docker-compose.yml

```yaml
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

Τι βλέπουμε:
- **2 services**: `web` και `db`
- **ports**: ο web server είναι προσβάσιμος στο `localhost:8080`
- **environment**: η βάση δεδομένων ρυθμίζεται με μεταβλητές περιβάλλοντος
- **volumes**: τα δεδομένα της βάσης αποθηκεύονται σε named volume
- **depends_on**: ο web ξεκινάει μετά τη βάση

### 2. Εκκίνηση

```bash
cd ~/cloud-uth/code/01_docker/06_compose-basics

docker compose up -d
```

### 3. Επιβεβαίωση

```bash
# Δες τα containers που τρέχουν
docker compose ps

# Δες τα logs
docker compose logs

# Logs μόνο ενός service
docker compose logs db
```

### 4. Σύνδεση στη βάση δεδομένων

```bash
# Εκτέλεση psql μέσα στο container της βάσης
docker compose exec db psql -U student -d mydb

# Μέσα στο psql:
\l
\q
```

### 5. Service discovery

Τα containers στο ίδιο compose network μπορούν να επικοινωνούν χρησιμοποιώντας το **όνομα του service** ως hostname:

```bash
# Από το web container, μπορούμε να "δούμε" τη βάση
docker compose exec web bash -c "apt-get update -qq && apt-get install -y -qq postgresql-client > /dev/null 2>&1 && pg_isready -h db -U student"
```

Το `db` είναι hostname — ο Docker το αντιστοιχεί αυτόματα στο σωστό container.

### 6. Τερματισμός

```bash
# Σταμάτησε τα containers
docker compose down

# Σταμάτησε και διάγραψε τα volumes (τα δεδομένα)
docker compose down -v
```
