#!/bin/bash
# Create a setup script and immediately start the apache instance.  Our URL prefix
# is specified by the --mount-point setting.  We need to specify a PYTHONPATH before
# starting the apache instance. Run this script from THIS directory.
# 
# REQUIREMENTS:
# Write a file in ~/.config/django/django_env_$CONDA_DEFAULT_ENV (e.g. panstarrs)
# The contents of this file should be as follows:
# export DJANGO_SECRET_KEY=''
# 
# export DJANGO_MYSQL_DBUSER=''
# export DJANGO_MYSQL_DBPASS=''
# export DJANGO_MYSQL_DBNAME=''
# export DJANGO_MYSQL_DBHOST=''
# export DJANGO_MYSQL_DBPORT=''
# 
# export DJANGO_TNS_DAEMON_PORT=''
# export DJANGO_TNS_DAEMON_SERVER=''
# export DJANGO_MPC_DAEMON_PORT=''
# export DJANGO_MPC_DAEMON_SERVER=''
# export DJANGO_NAME_DAEMON_PORT=''
# export DJANGO_NAME_DAEMON_SERVER=''
# 
# export WSGI_PORT=''
# export WSGI_PREFIX=''
#
# export DJANGO_SURVEY_FIELD='3P'
# 
# export DJANGO_LASAIR_TOKEN=''
# export DJANGO_DISPLAY_AGNS=''
# export DJANGO_DUSTMAP_LOCATION=''
#
# export DJANGO_NAMESERVER_API_URL=''
# export DJANGO_NAMESERVER_TOKEN=''
# export DJANGO_NAMESERVER_MULTIPLIER=10000000


if [ -f ~/.config/django/django_env_$CONDA_DEFAULT_ENV ]; then chmod 600 ~/.config/django/django_env_$CONDA_DEFAULT_ENV; source ~/.config/django/django_env_$CONDA_DEFAULT_ENV; fi

export APACHEPATH="/tmp/panstarrs"

if [ $DJANGO_MYSQL_DBNAME ]
then
    export APACHEPATH=/tmp/$DJANGO_MYSQL_DBNAME
fi

export PORT=8084
if [ $WSGI_PORT ]
then
    export PORT=$WSGI_PORT
fi

export PREFIX=/panstarrstransients
if [ $WSGI_PREFIX ]
then
    export PREFIX=$WSGI_PREFIX
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

mod_wsgi-express setup-server --working-directory psdb --url-alias $PREFIX/static static --url-alias $PREFIX/media media --application-type module psdb.wsgi --server-root $APACHEPATH --port $PORT --mount-point $PREFIX


export PYTHONPATH=$(pwd)
$APACHEPATH/apachectl start
