# Docker Volumes

Understanding the difference between ephemeral and persistent storage.

## What you will learn

- Why data inside a container is lost when the container is removed
- Bind mounts: linking a host directory to a container directory
- Named volumes: persistent storage managed by Docker

## Steps

### 1. Ephemeral storage — data is lost

```bash
# Create a file inside a container
docker run --name temp-nginx -d nginx
docker exec temp-nginx bash -c "echo 'My custom page' > /usr/share/nginx/html/test.html"

# Verify it exists
docker exec temp-nginx cat /usr/share/nginx/html/test.html

# Stop and remove the container
docker stop temp-nginx
docker rm temp-nginx

# Start a new container — the file is gone
docker run --name temp-nginx2 -d nginx
docker exec temp-nginx2 cat /usr/share/nginx/html/test.html
# You will see the default index.html, not "My custom page"
docker stop temp-nginx2
docker rm temp-nginx2
```

### 2. Bind mount — linking a file from the host

```bash
# Run nginx and bind-mount our index.html
docker run -d -p 8080:80 --name web-volumes \
  -v ./index.html:/usr/share/nginx/html/index.html:ro \
  nginx
```

Open [http://localhost:8080](http://localhost:8080) — you should see our custom page.

Now **edit** the `index.html` file in your editor, change the text, and refresh the browser. The change appears immediately!

Flag `:ro` = read-only: the container can only read, not write.

```bash
docker stop web-volumes
docker rm web-volumes
```

### 3. Named volume — persistent storage

```bash
# Create a named volume
docker volume create my-data

# Run a container with this volume
docker run -d --name vol-demo -v my-data:/data alpine sh -c "echo 'Hello from volume' > /data/message.txt && sleep 3600"

# Read the file
docker exec vol-demo cat /data/message.txt

# Stop and remove the container
docker stop vol-demo
docker rm vol-demo

# Start a NEW container — the data is still there!
docker run --rm -v my-data:/data alpine cat /data/message.txt
```

### 4. Cleanup

```bash
docker volume rm my-data
```
