# Docker Volumes

Κατανοούμε τη διαφορά μεταξύ ephemeral (εφήμερης) και persistent (μόνιμης) αποθήκευσης.

## Τι θα μάθουμε

- Γιατί τα δεδομένα μέσα σε ένα container χάνονται
- Bind mounts: σύνδεση φακέλου του host με φάκελο του container
- Named volumes: μόνιμη αποθήκευση που διαχειρίζεται ο Docker

## Βήματα

### 1. Ephemeral storage — τα δεδομένα χάνονται

```bash
# Δημιουργούμε ένα αρχείο μέσα στο container
docker run --name temp-nginx -d nginx
docker exec temp-nginx bash -c "echo 'My custom page' > /usr/share/nginx/html/test.html"

# Επιβεβαιώνουμε ότι υπάρχει
docker exec temp-nginx cat /usr/share/nginx/html/test.html

# Σταματάμε και αφαιρούμε το container
docker stop temp-nginx
docker rm temp-nginx

# Ξεκινάμε νέο container — το αρχείο δεν υπάρχει πια
docker run --name temp-nginx2 -d nginx
docker exec temp-nginx2 cat /usr/share/nginx/html/test.html
# Θα δείτε το default index.html, όχι το "My custom page"
docker stop temp-nginx2
docker rm temp-nginx2
```

### 2. Bind mount — σύνδεση αρχείου από τον host

```bash
# Τρέχουμε nginx και συνδέουμε το index.html από τον τρέχοντα φάκελο
docker run -d -p 8080:80 --name web-volumes \
  -v ./index.html:/usr/share/nginx/html/index.html:ro \
  nginx
```

Ανοίξτε [http://localhost:8080](http://localhost:8080) — θα δείτε τη δική μας σελίδα.

Τώρα **επεξεργαστείτε** το αρχείο `index.html` στον editor σας, αλλάξτε το κείμενο, και κάντε refresh τον browser. Η αλλαγή εμφανίζεται αμέσως!

Flag `:ro` = read-only: το container μπορεί μόνο να διαβάσει, όχι να γράψει.

```bash
docker stop web-volumes
docker rm web-volumes
```

### 3. Named volume — μόνιμη αποθήκευση

```bash
# Δημιουργούμε ένα named volume
docker volume create my-data

# Τρέχουμε container με αυτό το volume
docker run -d --name vol-demo -v my-data:/data alpine sh -c "echo 'Hello from volume' > /data/message.txt && sleep 3600"

# Διαβάζουμε το αρχείο
docker exec vol-demo cat /data/message.txt

# Σταματάμε και αφαιρούμε το container
docker stop vol-demo
docker rm vol-demo

# Ξεκινάμε ΝΕΕΣ container — τα δεδομένα είναι ακόμα εκεί!
docker run --rm -v my-data:/data alpine cat /data/message.txt
```

### 4. Καθαρισμός

```bash
docker volume rm my-data
```
