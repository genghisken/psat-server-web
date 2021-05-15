from django.contrib.auth.models import User
from django.db import IntegrityError
import csv

# To run this code, change directory to the YSE area, setup the environment variables and
# activate the Anaconda python environment:
# E.g. use the aliases below
# cdps1ysegitweb
# cd web/ps1
#
# activatepswebpstc
# 
# python manage.py shell
# 
# from createUsers import createUsersFromList
#
# createUsersFromList(filename = 'userlist.csv')
#
# The filename (which can be any name) contains the following info:
#
# username,password
# john.doe,whateverthepasswordis
# joe.bloggs,whateverthepasswordis
# ... etc
#
# The aliases are defined as:
# alias cdps1ysegitweb='export CODEBASE=/files/django_websites/gitrelease/ps1yse/code; export PYTHONPATH=$CODEBASE/web/ps1/psdb:$CODEBASE/database/reports/python:$CODEBASE/machine_learning:$CODEBASE/utils/python:$CODEBASE/experimental/pstamp/python:$CODEBASE/nameserver/ps1sc_code/python; cd $CODEBASE'
# alias activatepswebpstc='unalias activate; unalias deactivate; export LD_LIBRARY_PATH=/usr/local/swtools/lib:/usr/local/swtools/python/lib;source /usr/local/swtools/python_virtualenv/users/pstc/django/bin/activate' 


def createUsers(userList):
    """createUsers.

    Args:
        userList:
    """
    for row in userList:
        try:
            user=User.objects.create_user(row['username'], password=row['password'])
            user.is_superuser=False
            user.is_staff=False
            user.save()
        except IntegrityError as e:
            print("User already exists")

def createUsersFromList(filename = 'userlist.csv'):
    """createUsersFromList.

    Args:
        filename:
    """
    # Open a file with the user IDs in it.
    data = csv.DictReader(open(filename), delimiter=',')
    userList = []
    for row in data:
        userList.append(row)

    createUsers(userList)



if __name__ == '__main__':
    main()