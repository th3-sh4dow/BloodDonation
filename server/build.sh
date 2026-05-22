#!/usr/bin/env bash
# Render build script — single service (Django serves frontend + API)

set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
