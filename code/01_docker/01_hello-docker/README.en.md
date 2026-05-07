# Hello Docker

First contact with Docker — running our first containers.

For consistent terminology across the course guides, consult [glossary.md](../../../glossary.md).

## What you will learn

- What a Docker image is and what a container is
- Basic commands: `docker run`, `docker ps`, `docker rm`, `docker rmi`

## Steps

### 1. Your first container

```bash
docker run hello-world
```

What happens:
1. Docker looks for the `hello-world` image locally.
2. If not found, it pulls it from Docker Hub.
3. It creates a container from that image.
4. It runs the container, which prints a message and exits.

### 2. Running a command inside a container

```bash
docker run alpine echo "Hello from Alpine Linux!"
```

`alpine` is a very small Linux image (~5MB). We run an `echo` command inside it.

### 3. Interactive container

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
- `-i` : interactive (keeps stdin open)
- `-t` : allocate pseudo-TTY (terminal)

### 4. Inspecting containers

```bash
# See currently running containers
docker ps

# See ALL containers (including stopped)
docker ps -a
```

### 5. Cleanup

```bash
# Remove a stopped container (replace <container_id>)
docker rm <container_id>

# Remove ALL stopped containers
docker container prune

# See locally downloaded images
docker images

# Remove an image
docker rmi hello-world
```
