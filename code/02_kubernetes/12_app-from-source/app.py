"""Minimal Flask service that reads names from the PostgreSQL backend of example 11."""

import os
import socket

import psycopg2
from flask import Flask, jsonify

APP_VERSION = os.environ.get("APP_VERSION", "0.1.0")

app = Flask(__name__)


def db_connect():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        connect_timeout=3,
    )


@app.get("/healthz")
def healthz():
    # Liveness probe: process is alive and Flask responds. No DB access here.
    return jsonify(status="ok"), 200


@app.get("/readyz")
def readyz():
    # Readiness probe: the app should only receive traffic when the DB is reachable.
    try:
        with db_connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
        return jsonify(status="ready"), 200
    except Exception as exc:
        return jsonify(status="not-ready", reason=str(exc)[:200]), 503


@app.get("/version")
def version():
    return jsonify(version=APP_VERSION)


@app.get("/")
def index():
    served_by = socket.gethostname()
    try:
        with db_connect() as conn, conn.cursor() as cur:
            cur.execute("SELECT name FROM my_table ORDER BY id;")
            names = [row[0] for row in cur.fetchall()]
        return jsonify(
            message="Hello from Python on Kubernetes!",
            version=APP_VERSION,
            served_by=served_by,
            names=names,
        )
    except Exception as exc:
        return jsonify(error=str(exc)[:200], served_by=served_by), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
