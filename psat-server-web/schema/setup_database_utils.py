import sys, os, time, socket

#DEV_TEMPLATE_LOCATION = 'home/kws/svnworkspace/ps1/code'
#DEV_TEMPLATE_LOCATION = 'Users/kws/Documents/code/svnworkspace/panstarrs/ps1/code'

TEMP_DIRECTORY = '/tmp/schema/'
TEMP_TARFILE = 'tempTarfile.tar'

webRootLocation = os.getcwd().replace('/code/database/schema','')
DEV_TEMPLATE_LOCATION = webRootLocation + '/code'


# Python script to create a new database instance, new user, new Django instance
def newDatabase(databaseName, dbhost, recreateDatbase = False, rootDBUser = None, rootDBPassword = None):
   """newDatabase.

   Args:
       databaseName:
       dbhost:
       recreateDatbase:
       rootDBUser:
       rootDBPassword:
   """

   # Create the core database schema and views
   # CHECK that they don't already exist and ABORT if they do

   cmd = 'mysql -u %s --password=%s --skip-column-names -h %s -Be "show databases like \'%s\';"' % (rootDBUser, rootDBPassword, dbhost, databaseName)
   database = os.popen(cmd).readline().rstrip()

   if database == databaseName:
      print("WARNING!! This database already exists.")
      return 1

   cmd = 'mysql -u %s --password=%s -h %s -Be "create database %s;" ' % (rootDBUser, rootDBPassword, dbhost, databaseName)
   output = os.popen(cmd).readlines()

   if output:
      print(output)
      return 1

   return 0

def newDjangoDatabase(databaseName, dbhost, rootDBUser = None, rootDBPassword = None):
   """newDjangoDatabase.

   Args:
       databaseName:
       dbhost:
       rootDBUser:
       rootDBPassword:
   """
   # Create the database specific Django scripts
   # Setup the Django database instance
   # CHECK that it doesn't already exist and ABORT if it does

   return newDatabase('%s_django' % databaseName, dbhost, rootDBUser = rootDBUser, rootDBPassword = rootDBPassword)


# Create the user & grant permissions
def newUserAndGrants(user, password, databaseName, dbhost, dropUser = False, rootDBUser = None, rootDBPassword = None):
   """newUserAndGrants.

   Args:
       user:
       password:
       databaseName:
       dbhost:
       dropUser:
       rootDBUser:
       rootDBPassword:
   """
   # Create the core database schema and views
   # CHECK that they don't already exist and ABORT if they do

   cmd = 'mysql -u %s --password=%s --skip-column-names -h %s -Be "select User from mysql.user where user = \'%s\';"' % (rootDBUser, rootDBPassword, dbhost, user)
   existingUser = os.popen(cmd).readline().rstrip()


   if existingUser == user:
      # Need to decide what to do in relation to existing users - or a situation where one user
      # is shared across multiple schemas.
      print("This user already exists...  Continuing anyway...")

   grants = open('./create_user_grants_generic.sql', 'r')

   if not os.path.exists(TEMP_DIRECTORY):
      os.makedirs(TEMP_DIRECTORY)
      os.chmod(TEMP_DIRECTORY, 0o775)

   tempFilename = TEMP_DIRECTORY + 'create_user_grants_%s.sql' % os.getpid()

   tempGrants = open(tempFilename, 'w')

   newFileLines = []

   for line in grants:
      if not dropUser and 'drop' in line:
         line = line.replace('drop','-- drop')
      if 'USER' in line:
         line = line.replace('USER', user)
      if 'PASSWORD' in line:
         line = line.replace('PASSWORD', password)
      if 'DATABASE' in line:
         line = line.replace('DATABASE', databaseName)

      newFileLines.append(line)

   tempGrants.writelines(newFileLines)
   tempGrants.close()
   grants.close()

   cmd = 'mysql -u %s --password=%s -h %s -Be "source %s;" ' % (rootDBUser, rootDBPassword, dbhost, tempFilename)
   print(cmd)

   output = os.popen(cmd).readlines()

   if output:
      print(output)
      return 1

   os.remove(tempFilename)

   return 0


def newSchemaAndViews(user, password, databaseName, dbhost, createNewSchema = True, fgss = False, atlas = False, webRootDir = '../../'):
   """newSchemaAndViews.

   Args:
       user:
       password:
       databaseName:
       dbhost:
       createNewSchema:
       fgss:
       atlas:
   """

   # If createNewSchema is False, only (re-)create the Django database views.  This is required
   # when alterations are made to the existing schema.
   if createNewSchema:
      cmd = 'mysql -u %s --password=%s %s -h %s -Be "source ./create_schema.sql;" ' % (user, password, databaseName, dbhost)
      output = os.popen(cmd).readlines()

      if output:
         print(output)
         return 1

   if atlas:
      webroot = webRootDir + 'atlas'
      # We don't have a separate _django schema for ATLAS.
      cmd = 'mysql -u %s --password=%s %s -h %s -Be "source %s/sql/create_web_views.sql;" ' % (user, password, databaseName, dbhost, webroot)
      output = os.popen(cmd).readlines()

      if output:
         print(output)
         return 1

      # No need to go any further.
      return 0
   else:
      webroot = webRootDir + 'ps1'


   webViews = open(webroot + '/sql/create_web_views.sql', 'r')

   if not os.path.exists(TEMP_DIRECTORY):
      os.makedirs(TEMP_DIRECTORY)
      os.chmod(TEMP_DIRECTORY, 0o775)

   tempFilename = TEMP_DIRECTORY + 'create_web_views_%s.sql' % os.getpid()

   tempSQL = open(tempFilename, 'w')

   newFileLines = []

   for line in webViews:
      if 'DATABASE' in line:
         line = line.replace('DATABASE', databaseName)

      newFileLines.append(line)


   tempSQL.writelines(newFileLines)
   tempSQL.close()
   webViews.close()


   cmd = 'mysql -u %s --password=%s %s -h %s -Be "source %s;" ' % (user, password, databaseName + '_django', dbhost, tempFilename)
   output = os.popen(cmd).readlines()

   os.remove(tempFilename)

   if output:
      print(output)
      return 1


   catViews = open('../../web/ps1/sql/create_web_cat_views.sql', 'r')

   if not os.path.exists(TEMP_DIRECTORY):
      os.makedirs(TEMP_DIRECTORY)
      os.chmod(TEMP_DIRECTORY, 0o775)

   tempFilename = TEMP_DIRECTORY + 'create_web_cat_views_%s.sql' % os.getpid()

   tempSQL = open(tempFilename, 'w')

   newFileLines = []

   for line in catViews:
      if 'DATABASE' in line:
         line = line.replace('DATABASE', databaseName)

      newFileLines.append(line)


   tempSQL.writelines(newFileLines)
   tempSQL.close()
   catViews.close()


   cmd = 'mysql -u %s --password=%s %s -h %s -Be "source %s;" ' % (user, password, databaseName + '_django', dbhost, tempFilename)
   output = os.popen(cmd).readlines()

   os.remove(tempFilename)

   # If we want an FGSS database then need to run some replacement views.

   if fgss:
      #cmd = 'mysql -u %s --password=%s %s -h %s -Be "source ../../web/ps1/sql/create_web_views_fgss.sql;" ' % (user, password, databaseName + '_django', dbhost)
      #output = os.popen(cmd).readlines()
      # No need to do this anymore.  Logic for FGSS now included in generate stats code.
      pass

   if output:
      print(output)
      return 1

   return 0



# Copy the Django directories to a separate location for each instance
# 2013-04-12 KWS Deprecated most of this.  We now want the target directory to be
#                checked out of SVN.
def djangoDirectoryStructure(user, password, databaseName, dbhost, reUseDevelopmentTemplates = False, atlas = False, imageRootDir = '/', webRootDir = '../../web'):
   """djangoDirectoryStructure.

   Args:
       user:
       password:
       databaseName:
       dbhost:
       reUseDevelopmentTemplates:
       atlas:
       rootDir:
   """
   IMAGE_ROOT = imageRootDir + dbhost + '/images/'
   # Create necessary image directories and symbolic links
   # CHECK that they don't already exist.

   # TAR up the current web directory structure

   #tarFile = TEMP_TARFILE
   #cmd = 'tar cf %s%s --exclude .svn ../../web' % (TEMP_DIRECTORY, tarFile)
   #output = os.popen(cmd).readlines()
   #print output

   if atlas:
       webroot = webRootDir + 'atlas'
       webpath = webroot + '/atlas'
   else:
       webroot = webRootDir + 'ps1'
       webpath = webroot + '/psdb'

   # Rewrite the settings.py file
   settingsTemplate = open(webpath + '/settings.py.template', 'r')

   if not os.path.exists(TEMP_DIRECTORY):
      os.makedirs(TEMP_DIRECTORY)
      os.chmod(TEMP_DIRECTORY, 0o775)

   tempFilename = TEMP_DIRECTORY + 'settings.py.%s' % databaseName

   tempGrants = open(tempFilename, 'w')

   newFileLines = []

   for line in settingsTemplate:
      if 'GENERIC_USER' in line:
         line = line.replace('GENERIC_USER', user)
      if 'GENERIC_PASSWORD' in line:
         line = line.replace('GENERIC_PASSWORD', password)
      if 'GENERIC_HOST' in line:
         line = line.replace('GENERIC_HOST', dbhost)
      if 'GENERIC_FILESYSTEM' in line:
         if not reUseDevelopmentTemplates:
            line = line.replace('GENERIC_FILESYSTEM', webRootLocation)
         else:
            line = line.replace('GENERIC_FILESYSTEM', DEV_TEMPLATE_LOCATION)

      if 'GENERIC_DATABASE' in line:
         if atlas:
            line = line.replace('GENERIC_DATABASE', databaseName)
         else:
            line = line.replace('GENERIC_DATABASE', databaseName + '_django')

      newFileLines.append(line)

   tempGrants.writelines(newFileLines)
   tempGrants.close()
   settingsTemplate.close()

   # Replace the settings.py file with the altered settings.py.generic
   cmd = 'cp -p  %s %s' % (tempFilename, webpath + '/settings.py')
   output = os.popen(cmd).readlines()
   print(output)

   # Create the /psdb/images directories

   if not os.path.exists(IMAGE_ROOT + databaseName) and os.access(IMAGE_ROOT, os.W_OK):
      os.makedirs(IMAGE_ROOT + databaseName)
      os.chmod(IMAGE_ROOT + databaseName, 0o775)
      os.makedirs(IMAGE_ROOT + databaseName + '/lightcurves')
      os.chmod(IMAGE_ROOT + databaseName + '/lightcurves', 0o777) # Altered to 777 so apache can write here.
      os.makedirs(IMAGE_ROOT + databaseName + '/reports')
      os.chmod(IMAGE_ROOT + databaseName + '/reports', 0o775)
   else:
      print("Cannot create directory structure.  No permission or directory already exists.")




   # Now delete and recreate the symbolic links
   #cmd = 'rm %s %s %s %s' % ('/' + webRootLocation + '/' + databaseName + '/web/ps1/site_media/images/lightcurves',
   #                          '/' + webRootLocation + '/' + databaseName + '/web/ps1/site_media/images/location_maps',
   #                          '/' + webRootLocation + '/' + databaseName + '/web/ps1/site_media/images/recurrence_plots', 
   #                          '/' + webRootLocation + '/' + databaseName + '/web/ps1/site_media/images/reports') 
   #output = os.popen(cmd).readlines()
   #print output

   cmd = 'ln -s %s %s' % (IMAGE_ROOT + databaseName + '/lightcurves', webroot + '/site_media/images/lightcurves')
   output = os.popen(cmd).readlines()
   print(output)
   cmd = 'ln -s %s %s' % (IMAGE_ROOT + databaseName + '/reports', webroot + '/site_media/images/reports')
   output = os.popen(cmd).readlines()
   print(output)
   cmd = 'ln -s %s %s' % (IMAGE_ROOT, webroot + '/site_media/images/data')
   output = os.popen(cmd).readlines()
   print(output)


   ## 2011-12-01 KWS Need to replace the lightcurve generator symlink in the devel directory with the actual file

   #cmd = 'rm %s' % (webRootLocation + '/' + databaseName + '/web/ps1/psdb/plotLightCurve.py')
   #output = os.popen(cmd).readlines()
   #print output

   #cmd = 'cp -p ../../experimental/pstamp/python/plotLightCurve.py %s' % (webRootLocation + '/' + databaseName + '/web/ps1/psdb/plotLightCurve.py')
   #output = os.popen(cmd).readlines()
   #print output


   os.remove(tempFilename)


   return 0


def createWebConfigFile(databaseName, eggCacheLocation = '/files/django_websites/generic_egg_cache', virtualEnvRoot = '/files/django_websites/python_virtualenv', atlas = False, webRootDir = '../../../'):
   """createWebConfigFile.

   Args:
       databaseName:
       eggCacheLocation:
       virtualEnvRoot:
       atlas:
       webRootDir:
   """
   # Create the python.conf file for appending to the existing config file
   # Do NOT attach automatically - this should be done manually.
   # GENERIC_URL = Web application URL
   # DATABASE = database name
   # WEB_ROOT = Directory root of web application


   wsgiTemplate = open(webRootDir + 'config/wsgi.conf.template', 'r')

   if not os.path.exists(TEMP_DIRECTORY):
      os.makedirs(TEMP_DIRECTORY)
      os.chmod(TEMP_DIRECTORY, 0o775)

   wsgiTempFilename = TEMP_DIRECTORY + 'wsgi.%s.conf' % databaseName

   tempWSGIGrants = open(wsgiTempFilename, 'w')

   newWSGIFileLines = []

   for line in wsgiTemplate:
      if 'GENERIC_FILESYSTEM' in line:
         line = line.replace('GENERIC_FILESYSTEM', webRootLocation)
      if 'WEB_ROOT' in line:
         line = line.replace('WEB_ROOT', webRootLocation)
      if 'VIRTUALENV_ROOT' in line:
         line = line.replace('VIRTUALENV_ROOT', virtualEnvRoot)

      newWSGIFileLines.append(line)

   tempWSGIGrants.writelines(newWSGIFileLines)

   tempWSGIGrants.close()
   wsgiTemplate.close()

   if atlas:
       webpath = webRootDir + 'atlas/atlas'
   else:
       webpath = webRootDir + 'ps1/psdb'


   cmd = 'cp -p  %s %s' % (wsgiTempFilename, webpath)
   print(cmd)
   output = os.popen(cmd).readlines()
   print(output)


   os.remove(wsgiTempFilename)

   return 0
