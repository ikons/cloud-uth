# Web Server with Docker

Run a web server (Nginx) in a container and view it in the browser.

For consistent terminology across the course guides, consult [glossary.md](../../../glossary.md).

## What you will learn

- Port mapping (`-p`)
- Running in background (`-d`)
- Logs and exec

## Steps

### 1. Start Nginx

```bash
docker run -d -p 8080:80 --name my-nginx nginx
```

Flags:
- `-d` : detached mode (runs in the background)
- `-p 8080:80` : maps port 8080 on our machine to port 80 inside the container
- `--name my-nginx` : gives the container a name

Open your browser at [http://localhost:8080](http://localhost:8080). You should see the default Nginx page.

### 2. Logs

```bash
# View container logs
docker logs my-nginx

# Follow logs in real time
docker logs -f my-nginx
```

Press `Ctrl+C` to stop following.

### 3. Executing commands inside the container

```bash
# Open a shell inside the running container
docker exec -it my-nginx bash

# Inside the container:
cat /usr/share/nginx/html/index.html
exit
```

This is the HTML file displayed in the browser.

### 4. Restart and stop

```bash
# Stop the container
docker stop my-nginx

# Start it again
docker start my-nginx

# Stop and remove it
docker stop my-nginx
docker rm my-nginx
```
