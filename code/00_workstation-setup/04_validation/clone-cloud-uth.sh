#!/usr/bin/env bash
set -euo pipefail

cd ~

if [ ! -d cloud-uth/.git ]; then
  git clone https://github.com/ikons/cloud-uth.git
fi

cd cloud-uth
