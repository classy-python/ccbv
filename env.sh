# gets directory path, required to set up sqlite db file
DIR_PATH=$(cd -P -- "$(dirname -- "$0")" && pwd -P)

export DEBUG='True'
export DATABASE_URL='sqlite:///'$DIR_PATH'/db.sqlite'
export STATIC_URL='/static_media/'
