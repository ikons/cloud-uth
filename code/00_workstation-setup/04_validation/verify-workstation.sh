#!/usr/bin/env bash
set -euo pipefail

cd ~/cloud-uth
git rev-parse --show-toplevel
docker version
docker compose version
docker run --rm hello-world
