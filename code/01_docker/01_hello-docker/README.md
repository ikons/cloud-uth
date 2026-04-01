# Hello Docker

Πρώτη επαφή με το Docker — τρέχουμε τα πρώτα μας containers.

## Τι θα μάθουμε

- Τι είναι ένα Docker image και τι ένα container
- Βασικές εντολές: `docker run`, `docker ps`, `docker rm`, `docker rmi`

## Βήματα

### 1. Το πρώτο container

```bash
docker run hello-world
```

Τι συμβαίνει:
1. Ο Docker ψάχνει τοπικά το image `hello-world`.
2. Αν δεν το βρει, το κατεβάζει από το Docker Hub (pull).
3. Δημιουργεί ένα container από αυτό το image.
4. Τρέχει το container, που τυπώνει ένα μήνυμα και τερματίζει.

### 2. Εκτέλεση εντολής μέσα σε container

```bash
docker run alpine echo "Hello from Alpine Linux!"
```

Το `alpine` είναι ένα πολύ μικρό Linux image (~5MB). Τρέχουμε μια εντολή `echo` μέσα σε αυτό.

### 3. Διαδραστικό container

```bash
docker run -it alpine sh
```

Ανοίγει ένα shell μέσα στο container. Δοκιμάστε:

```bash
hostname
cat /etc/os-release
ls /
exit
```

Flags:
- `-i` : interactive (κρατάει ανοιχτό το stdin)
- `-t` : allocate pseudo-TTY (terminal)

### 4. Εξέταση containers

```bash
# Δες τα containers που τρέχουν τώρα
docker ps

# Δες ΟΛΕΣ τα containers (και τα σταματημένα)
docker ps -a
```

### 5. Καθαρισμός

```bash
# Διαγραφή ενός σταματημένου container (αντικατάστησε το <container_id>)
docker rm <container_id>

# Διαγραφή ΟΛΩΝ των σταματημένων containers
docker container prune

# Δες τα images που έχεις τοπικά
docker images

# Διαγραφή ενός image
docker rmi hello-world
```
