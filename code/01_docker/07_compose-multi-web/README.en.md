# Docker Compose — Reverse Proxy & Load Balancing

Advanced example: Nginx reverse proxy in front of multiple web servers.

For consistent terminology across the course guides, consult [glossary.md](../../../glossary.md).

## What you will learn

- Reverse proxy pattern
- Load balancing between containers
- Custom Docker networks
- Multiple services in a single compose file

## Files

- `docker-compose.yml` — 3 services: nginx proxy + web1 + web2
- `nginx.conf` — reverse proxy configuration with upstream load balancing
- `web1/index.html` — Web1 page
- `web2/index.html` — Web2 page

## Architecture

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

## Steps

### 1. Examining nginx.conf

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

- `upstream backend` : defines a server group — uses the service names
- `proxy_pass` : forwards requests to the group
- Round-robin: each request goes alternately to web1 and web2

### 2. Start

```bash
cd ~/cloud-uth/code/01_docker/07_compose-multi-web

docker compose up -d
```

### 3. Test

Open your browser at [http://localhost:8080](http://localhost:8080).

Refresh multiple times — you should see "Welcome to Web1" and "Welcome to Web2" alternating!

Alternatively, from the terminal:

```bash
# Each call may go to a different server
curl http://localhost:8080
curl http://localhost:8080
curl http://localhost:8080
```

### 4. Inspect the network

```bash
# See the networks Docker created
docker network ls

# See which containers are in the network
docker network inspect 07_compose-multi-web_mynetwork
```

### 5. Shutdown

```bash
docker compose down
```
