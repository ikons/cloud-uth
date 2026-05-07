# Custom Docker Image

Φτιάχνουμε το πρώτο μας Docker image με Dockerfile.

Για συνεπή ελληνική ορολογία στους οδηγούς του μαθήματος, ανατρέξτε στο [glossary.md](../../../glossary.md).

## Τι θα μάθουμε

- Τι είναι ένα Dockerfile
- Εντολές: `FROM`, `COPY`, `RUN`, `CMD`
- `docker build` και `docker run`
- Η έννοια των layers

## Αρχεία

- `Dockerfile` — οδηγίες για το χτίσιμο του image
- `app.sh` — ένα απλό bash script που τρέχει μέσα στο container

## Βήματα

### 1. Εξέταση του Dockerfile

```dockerfile
FROM alpine:latest
COPY app.sh /app.sh
RUN chmod +x /app.sh
CMD ["/app.sh"]
```

- `FROM` : βασικό image πάνω στο οποίο χτίζουμε
- `COPY` : αντιγράφει αρχεία από τον host στο image
- `RUN` : εκτελεί εντολή κατά το build
- `CMD` : εντολή που τρέχει όταν ξεκινάει το container

### 2. Build

```bash
cd ~/cloud-uth/code/01_docker/04_custom-image

docker build -t my-app .
```

- `-t my-app` : ονομάζουμε το image `my-app`
- `.` : ο τρέχων φάκελος είναι το build context

### 3. Run

```bash
docker run --name my-app-container my-app
```

Θα δείτε output κάθε 5 δευτερόλεπτα. Πατήστε `Ctrl+C` για να σταματήσετε.

### 4. Run σε background

```bash
docker run -d --name my-app-bg my-app
docker logs -f my-app-bg
```

### 5. Επιβεβαίωση image

```bash
# Δες τα images
docker images | grep my-app

# Δες τα layers του image
docker history my-app
```

### 6. Καθαρισμός

```bash
docker stop my-app-bg
docker rm my-app-container my-app-bg
docker rmi my-app
```
