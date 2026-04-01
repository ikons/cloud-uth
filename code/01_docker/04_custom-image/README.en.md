# Custom Docker Image

Building our first Docker image with a Dockerfile.

## What you will learn

- What a Dockerfile is
- Instructions: `FROM`, `COPY`, `RUN`, `CMD`
- `docker build` and `docker run`
- The concept of layers

## Files

- `Dockerfile` — instructions for building the image
- `app.sh` — a simple bash script that runs inside the container

## Steps

### 1. Examining the Dockerfile

```dockerfile
FROM alpine:latest
COPY app.sh /app.sh
RUN chmod +x /app.sh
CMD ["/app.sh"]
```

- `FROM` : base image we build upon
- `COPY` : copies files from the host into the image
- `RUN` : executes a command during build
- `CMD` : command that runs when the container starts

### 2. Build

```bash
cd ~/cloud-uth/code/01_docker/04_custom-image

docker build -t my-app .
```

- `-t my-app` : names the image `my-app`
- `.` : the current directory is the build context

### 3. Run

```bash
docker run --name my-app-container my-app
```

You will see output every 5 seconds. Press `Ctrl+C` to stop.

### 4. Run in background

```bash
docker run -d --name my-app-bg my-app
docker logs -f my-app-bg
```

### 5. Verify the image

```bash
# List images
docker images | grep my-app

# See the image layers
docker history my-app
```

### 6. Cleanup

```bash
docker stop my-app-bg
docker rm my-app-container my-app-bg
docker rmi my-app
```
