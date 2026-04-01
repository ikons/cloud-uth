#!/bin/sh
echo "=== Application Configuration ==="
echo "APP_NAME: ${APP_NAME:-not set}"
echo "APP_ENV:  ${APP_ENV:-not set}"
echo "APP_PORT: ${APP_PORT:-not set}"
echo "================================="
echo ""
echo "Application is running..."

while true; do
    echo "[${APP_NAME:-app}] Running in ${APP_ENV:-unknown} mode on port ${APP_PORT:-?}"
    sleep 5
done
