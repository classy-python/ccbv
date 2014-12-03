#!/bin/bash
# Starts django server

# Stop on error
set -e

DATA_DIR=/data

# SET DATABASE_URL env var
export DATABASE_URL="postgres://$DB_ENV_USER:$DB_ENV_PASS@db:$DB_PORT_5432_TCP_PORT/$DB_ENV_DB"

echo "trying to update if needed requirements.txt"
pip install -r $DATA_DIR/requirements.txt

if [ -z $DB_PORT ];then
    echo "DB env var not configured, link a Postgresql DB container with alias: db on port 5432"
    exit 1
fi

echo "Waiting for DB to be ready"
while ! exec 6<>/dev/tcp/${DB_PORT_5432_TCP_ADDR}/${DB_PORT_5432_TCP_PORT}; do
    echo "$(date) - still trying to connect to DB at ${DB_PORT}"
    sleep 1
done

if [[ -e /steps/firstrun ]]; then
  source /scripts/normal_run.sh
else
  source /scripts/first_run.sh
fi


pre_start_action

echo "collecting statics"
python $DATA_DIR/manage.py collectstatic --noinput

# Django
echo "Starting Django..."
python $DATA_DIR/manage.py runserver 0.0.0.0:8000
