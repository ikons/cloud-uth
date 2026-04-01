# Docker Compose — Basics

Running multiple containers together with Docker Compose.

## What you will learn

- What Docker Compose is and why we need it
- Structure of a `docker-compose.yml` file
- Commands: `docker compose up`, `docker compose down`
- Service discovery: how containers find each other

## Files

- `docker-compose.yml` — defines 2 services: web server (Nginx) + database (PostgreSQL)

## Steps

### 1. Examining the docker-compose.yml

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

What we see:
- **2 services**: `web` and `db`
- **ports**: the web server is accessible at `localhost:8080`
- **environment**: the database is configured with environment variables
- **volumes**: database data is stored in a named volume
- **depends_on**: web starts after the database

### 2. Start

```bash
cd ~/cloud-uth/code/01_docker/06_compose-basics

docker compose up -d
```

### 3. Verify

```bash
# See running containers
docker compose ps

# View logs
docker compose logs

# Logs for a single service
docker compose logs db
```

### 4. Connect to the database

```bash
# Run psql inside the database container
docker compose exec db psql -U student -d mydb

# Inside psql:
\l
\q
```

### 5. Service discovery

Containers in the same compose network can communicate using the **service name** as hostname:

```bash
# From the web container, we can reach the database
docker compose exec web bash -c "apt-get update -qq && apt-get install -y -qq postgresql-client > /dev/null 2>&1 && pg_isready -h db -U student"
```

`db` is a hostname — Docker automatically resolves it to the correct container.

### 6. Shutdown

```bash
# Stop containers
docker compose down

# Stop and remove volumes (data)
docker compose down -v
```
