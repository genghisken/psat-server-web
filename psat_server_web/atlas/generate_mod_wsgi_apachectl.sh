#!/bin/bash
# Create a setup script and immediately start the apache instance.  Our URL prefix
# is specified by the --mount-point setting.  We need to specify a PYTHONPATH before
# starting the apache instance. Run this script from THIS directory.

if [ -f .env ]; then chmod 600 .env; source .env; fi

export APACHEPATH="/tmp/atlas"

if [ $DJANGO_MYSQL_DBNAME ]
then
    export APACHEPATH=/tmp/$DJANGO_MYSQL_DBNAME
fi

export PORT=8086
if [ $WSGI_PORT ]
then
    export PORT=$WSGI_PORT
fi

if [ -f $APACHEPATH/apachectl ]; then
    echo "Stopping Apache if already running"
    $APACHEPATH/apachectl stop
    sleep 1
    # wait a second to make sure the port is released
else
    echo "Creating directory $APACHEPATH"
    mkdir -p APACHEPATH
fi

mod_wsgi-express setup-server --working-directory atlas --url-alias /static static --application-type module atlas.wsgi --server-root $APACHEPATH --port $PORT --mount-point /

export PYTHONPATH=$(pwd)
$APACHEPATH/apachectl start
