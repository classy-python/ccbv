#!/bin/bash
# Starts django server

# Stop on error
set -e

DATA_DIR=/data

if [[ -e $DATA_DIR/firstrun ]]; then
  source /scripts/normal_run.sh
else
  source /scripts/first_run.sh
fi


pre_start_action

# Django
echo "Starting Django..."
python $DATA_DIR/manage.py runserver
