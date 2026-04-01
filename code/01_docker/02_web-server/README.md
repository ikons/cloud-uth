# Web Server με Docker

Τρέχουμε έναν web server (Nginx) σε container και τον βλέπουμε στον browser.

## Τι θα μάθουμε

- Port mapping (`-p`)
- Εκτέλεση σε background (`-d`)
- Logs και exec

## Βήματα

### 1. Εκκίνηση Nginx

```bash
docker run -d -p 8080:80 --name my-nginx nginx
```

Flags:
- `-d` : detached mode (τρέχει στο background)
- `-p 8080:80` : συνδέει τη θύρα 8080 του μηχανήματός μας με τη θύρα 80 του container
- `--name my-nginx` : δίνουμε όνομα στο container

Ανοίξτε τον browser στο [http://localhost:8080](http://localhost:8080). Θα δείτε τη default σελίδα του Nginx.

### 2. Logs

```bash
# Δες τα logs του container
docker logs my-nginx

# Παρακολούθηση logs σε πραγματικό χρόνο
docker logs -f my-nginx
```

Πατήστε `Ctrl+C` για να σταματήσετε την παρακολούθηση.

### 3. Εκτέλεση εντολής μέσα στο container

```bash
# Άνοιξε ένα shell μέσα στο container που τρέχει
docker exec -it my-nginx bash

# Μέσα στο container:
cat /usr/share/nginx/html/index.html
exit
```

Βλέπουμε το HTML αρχείο που εμφανίζεται στον browser.

### 4. Επανεκκίνηση και στάση

```bash
# Σταμάτησε το container
docker stop my-nginx

# Ξεκίνησέ το πάλι
docker start my-nginx

# Σταμάτησέ το και διάγραψέ το
docker stop my-nginx
docker rm my-nginx
```
