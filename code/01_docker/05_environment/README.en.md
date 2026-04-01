# Environment Variables

Configuring containers through environment variables, without changing code.

## What you will learn

- How to define environment variables in a Dockerfile (`ENV`)
- How to pass them at `docker run` time (`-e`)
- How to change container behavior without rebuilding

## Files

- `Dockerfile` — defines default values for 3 variables
- `app.sh` — script that reads the variables and prints them

## Steps

### 1. Build

```bash
cd ~/cloud-uth/code/01_docker/05_environment

docker build -t env-app .
```

### 2. Run with default values

```bash
docker run --rm --name env-demo env-app
```

You will see the default values from the Dockerfile:
- `APP_NAME=my-app`
- `APP_ENV=development`
- `APP_PORT=8080`

Press `Ctrl+C` to stop.

### 3. Override variables

```bash
docker run --rm --name env-demo \
  -e APP_NAME=cloud-app \
  -e APP_ENV=production \
  -e APP_PORT=3000 \
  env-app
```

The values change without building a new image!

### 4. Inspect container variables

```bash
docker run -d --name env-inspect env-app
docker exec env-inspect env
docker stop env-inspect
docker rm env-inspect
```

### 5. Cleanup

```bash
docker rmi env-app
```
