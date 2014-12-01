
pre_start_action() {
    echo "installing requirements.txt"
    pip install -r $DATA_DIR/requirements.txt


    if [ -z $DB_PORT ];then
        echo "DB_PORT env var not configured, link a Postgresql DB container with alias: db on port 5432"
        exit 1
    fi

    echo "Waiting for DB to be ready"
    while ! exec 6<>/dev/tcp/${DB_PORT_5432_TCP_ADDR}/${DB_PORT_5432_TCP_PORT}; do
        echo "$(date) - still trying to connect to DB at ${DB_PORT}"
        sleep 1
    done

    echo "settings DATABASE_URL env var"
    export DATABASE_URL=$DB_PORT

    echo "Syncing DB"
    python $DATA_DIR/manage.py syncdb --noinput

    echo "Migrating DB"
    python $DATA_DIR/manage.py migrate cbv

    echo "Loading fixtures"

    python $DATA_DIR/manage.py loaddata $DATA_DIR/cbv/fixtures/project.json

    python $DATA_DIR/manage.py loaddata $DATA_DIR/cbv/fixtures/1.3.json
    python $DATA_DIR/manage.py loaddata $DATA_DIR/cbv/fixtures/1.4.json
    python $DATA_DIR/manage.py loaddata $DATA_DIR/cbv/fixtures/1.5.json
    python $DATA_DIR/manage.py loaddata $DATA_DIR/cbv/fixtures/1.6.json
    python $DATA_DIR/manage.py loaddata $DATA_DIR/cbv/fixtures/1.7.json

    echo "Creating Superuser. User: $USER / Email: $USER_EMAIL / Pass: $USER_PASS"
    echo "from django.contrib.auth.models import User; User.objects.create_superuser('$USER', '$USER_EMAIL', '$USER_PASS')" | \
    python manage.py shell

    touch $DATA_DIR/firstrun
}

