# Docker container usage examples

## 1. Introduction

This guide will help you learn the basics of **Docker** and run both **simple** and **more advanced** examples.

## 2. Running basic Docker commands

**Testing Docker**

```bash
docker run hello-world
```

This downloads and runs the `hello-world` container.

**Run an Ubuntu container in interactive mode**

```bash
docker run -it ubuntu bash
```

- `-it`: Enables interactive mode, giving the user a terminal shell inside the container that was started.
- You can run commands such as `ls`, `pwd`, and `exit`.

**List running containers**

```bash
docker ps
```

For all containers, including stopped ones:

```bash
docker ps -a
```

**Delete a container**

```bash
docker rm <container_id>
```

**Delete a Docker image**

```bash
docker rmi <image_id>
```

## 3. Running a simple web server with Docker

**Start an Nginx container**

```bash
docker run -d -p 8080:80 nginx
```

- `-d`: Runs the container in the background.
- `-p 8080:80`: Maps port **8080** of the **host** to **port 80 of the container**.

**Test it in the browser**  
Open:

http://localhost:8080

You will see the default Nginx page.

## 4. Example 1: Creating a new Docker container with additional files

In this example, we will build a **custom container** based on Ubuntu that includes a simple **Bash script** and runs it when the container starts.

### 4.1 Create a working directory

First, create a new folder for the project:

```bash
mkdir ~/docker-custom-container
cd ~/docker-custom-container
```

### 4.2 Create the `script.sh` file

This script prints a message every 5 seconds.

```bash
nano script.sh
```

Add the following content:

```bash
#!/bin/bash
while true; do
    echo "The Docker container is running! $(date)"
    sleep 5
done
```

Save it (`CTRL` + `X`, then `Y`, then `Enter`).

**Make the script executable**

```bash
chmod +x script.sh
```

### 4.3 Create the `Dockerfile`

Now we will create the **Dockerfile**, which describes our container.

```bash
nano Dockerfile
```

Paste the following:

```dockerfile
# Use the Ubuntu image
FROM ubuntu:latest

# Set the maintainer
LABEL maintainer="example@example.com"

# Update the system and install bash
RUN apt-get update && apt-get install -y bash

# Copy the script into the container
COPY script.sh /script.sh

# Set execution permissions for the script
RUN chmod +x /script.sh

# Run the script when the container starts
CMD ["/script.sh"]
```

Save the file (`CTRL` + `X`, then `Y`, then `Enter`).

### 4.4 Build the Docker image

Now build the Docker image:

```bash
docker build -t my-custom-container .
```

### 4.5 Run the container

Run the container in the background:

```bash
docker run -d --name my-container my-custom-container
```

To view the container logs in real time:

```bash
docker logs -f my-container
```

You will see messages such as:

```
The Docker container is running! Tue Mar 5 12:00:00 UTC 2025
The Docker container is running! Tue Mar 5 12:00:05 UTC 2025
...
```

### 4.6 Management and cleanup

**Stop the container**

```bash
docker stop my-container
```

**Delete the container**

```bash
docker rm my-container
```

**Delete the image**

```bash
docker rmi my-custom-container
```

## 5. Example 2: Running a more advanced setup with Nginx and multiple web servers

We will create a **Docker Compose setup** with:

- **Nginx** as a **reverse proxy**
- **Two web servers** with simple HTML pages

### 5.1 Create a working directory

```bash
mkdir ~/docker-nginx-multi
cd ~/docker-nginx-multi
```

### 5.2 Create `docker-compose.yml`

Run:

```bash
nano docker-compose.yml
```

Paste the following content:

```yaml
version: "3.8"

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

### 5.3 Create folders for the HTML files

```bash
mkdir web1 web2
```

### 5.4 Create HTML pages

For the **Web1 server**:

```bash
echo "<h1>Welcome to Web1</h1>" > web1/index.html
```

For the **Web2 server**:

```bash
echo "<h1>Welcome to Web2</h1>" > web2/index.html
```

### 5.5 Create the `nginx.conf` file (reverse proxy)

Run:

```bash
nano nginx.conf
```

Paste the following:

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

**Start the containers**

```bash
docker compose up -d
```

**Test in the browser**

Open:

http://localhost:8080

Nginx will alternate requests between **Web1** and **Web2**.

## 6. Docker Volumes: Difference between ephemeral and persistent volumes

In Docker, there are **two types of data storage**:

- **Ephemeral storage** – Data is lost when the container is deleted.
- **Persistent storage** – Data is preserved independently of the container.

Let us look at the difference using practical examples.

### 6.1 Ephemeral storage (data is lost)

The data is stored inside the container filesystem and **does not survive** when the container is deleted.

**Step 1: Start a container and create a file**

```bash
docker run -it --name temp-container ubuntu bash
```

Inside the container, create a file:

```bash
echo "Temporary data" > /tmp/tempfile.txt
cat /tmp/tempfile.txt
```

You will see:

```
Temporary data
```

**Step 2: Delete the container and check the data**

Delete the container:

```bash
docker rm temp-container
```

Start a **new container** and check whether the file exists:

```bash
docker run -it ubuntu bash
ls /tmp
```

The file **does not exist** because the container filesystem was ephemeral.

### 6.2 Persistent storage (data is preserved)

The data is stored **outside the container**, in a Docker **Volume**, and remains available even after the container is deleted.

**Step 1: Create a volume**

```bash
docker volume create mydata
```

Confirm that the volume was created:

```bash
docker volume ls
```

**Step 2: Start a container with the volume**

```bash
docker run -it --name persistent-container -v mydata:/data ubuntu bash
```

Inside the container, create a file:

```bash
echo "Persistent data" > /data/persistentfile.txt
cat /data/persistentfile.txt
```

You will see:

```
Persistent data
```

Exit the container:

```bash
exit
```

**Step 3: Delete the container and verify the data**

Delete the container:

```bash
docker rm persistent-container
```

Now start a new container and check whether the data still exists:

```bash
docker run -it --rm -v mydata:/data ubuntu bash
ls /data
cat /data/persistentfile.txt
```

You will see that the file **still exists**:

```
persistentfile.txt
Persistent data
```
