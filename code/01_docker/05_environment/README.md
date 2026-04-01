# Environment Variables

Παραμετροποιούμε containers μέσω environment variables, χωρίς να αλλάζουμε κώδικα.

## Τι θα μάθουμε

- Πώς ορίζουμε environment variables σε Dockerfile (`ENV`)
- Πώς τις περνάμε κατά το `docker run` (`-e`)
- Πώς αλλάζουμε τη συμπεριφορά ενός container χωρίς rebuild

## Αρχεία

- `Dockerfile` — ορίζει default τιμές για 3 μεταβλητές
- `app.sh` — script που διαβάζει τις μεταβλητές και τις εμφανίζει

## Βήματα

### 1. Build

```bash
cd ~/cloud-uth/code/01_docker/05_environment

docker build -t env-app .
```

### 2. Run με default τιμές

```bash
docker run --rm --name env-demo env-app
```

Θα δείτε τις default τιμές από το Dockerfile:
- `APP_NAME=my-app`
- `APP_ENV=development`
- `APP_PORT=8080`

Πατήστε `Ctrl+C` για να σταματήσετε.

### 3. Override μεταβλητών

```bash
docker run --rm --name env-demo \
  -e APP_NAME=cloud-app \
  -e APP_ENV=production \
  -e APP_PORT=3000 \
  env-app
```

Οι τιμές αλλάζουν χωρίς να χτίσουμε νέο image!

### 4. Εξέταση μεταβλητών ενός container

```bash
docker run -d --name env-inspect env-app
docker exec env-inspect env
docker stop env-inspect
docker rm env-inspect
```

### 5. Καθαρισμός

```bash
docker rmi env-app
```
