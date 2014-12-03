
pre_start_action() {
    echo "Ensure DB is clear"
    python $DATA_DIR/manage.py reset_db --router=default --noinput

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
    python $DATA_DIR/manage.py shell

    touch /steps/firstrun
}

