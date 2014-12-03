pre_start_action() {

    echo "Checking for any new migrations in the DB"
    python $DATA_DIR/manage.py migrate cbv

}
