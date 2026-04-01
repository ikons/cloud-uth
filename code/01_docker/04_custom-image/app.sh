#!/bin/sh
echo "=== Custom Docker Image ==="
echo "Hostname: $(hostname)"
echo "Date: $(date)"
echo ""
echo "Container is running..."

count=1
while true; do
    echo "[${count}] Still running at $(date '+%H:%M:%S')"
    count=$((count + 1))
    sleep 5
done
