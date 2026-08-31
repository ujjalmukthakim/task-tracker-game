#!/usr/bin/env zsh
# Starts the Django API and React client together for local development.
set -e

cd "${0:A:h}"
python3 manage.py migrate
python3 manage.py runserver 127.0.0.1:8000 --noreload &
api_pid=$!
trap 'kill $api_pid 2>/dev/null' EXIT INT TERM

cd frontend
npm run dev -- --host 127.0.0.1
