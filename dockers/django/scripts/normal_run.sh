pre_start_action() {
    echo "trying to update if needed requirements.txt"
    pip install -r $DATA_DIR/requirements.txt

    if [ -z $DB ];then
        echo "DB env var not configured, link a Postgresql DB container with alias: db on port 5432"
        exit 1
    fi

    echo "Waiting for DB to be ready"
    while ! exec 6<>/dev/tcp/${DB_PORT_5432_TCP_ADDR}/${DB_PORT_5432_TCP_PORT}; do
        echo "$(date) - still trying to connect to DB at ${DB_PORT}"
        sleep 1
    done

    echo "settings DATABASE_URL env var"
    export DATABASE_URL=$DB_PORT

    echo "Checking for any new migrations in the DB"
    python $DATA_DIR/manage.py migrate cbv

}
