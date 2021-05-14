"""Move ATLAS objects in specified list to another database.
   This code MUST be run from the webserver - psweb or psweb2.
   Check that the webserver has access to the /psdbN directory!

Usage:
  %s <username> <password> <schemaname> <dbhost> <rootconfig> [--atlas]
  %s (-h | --help)
  %s --version

Options:
  -h --help              Show this screen.
  --version              Show version.
  --atlas                Assume the ATLAS schema (no separate _django schema).

"""
import sys
__doc__ = __doc__ % (sys.argv[0], sys.argv[0], sys.argv[0])
from docopt import docopt
from gkutils.commonutils import Struct, cleanOptions

from setup_database_utils import *

def main(argv = None):
   """main.

   Args:
       argv:
   """
   # This code will NOT use MySQLdb to connect to the database.  This is to preserve the
   # ability to run each SQL script individually.  However, we will need to capture the
   # output of each script.
   opts = docopt(__doc__, version='0.1')
   opts = cleanOptions(opts)

   # Use utils.Struct to convert the dict into an object for compatibility with old optparse code.
   options = Struct(**opts)

   user = options.username
   password = options.password
   databaseName = options.schemaname
   dbhost = options.dbhost
   configFile = options.rootconfig

   # 2017-11-30 KWS Added local laptop hostnames for experimental installations.
   if os.uname()[1].split('.')[0] not in ['psweb', 'psweb2', 'rocket', 'montoya', 'mp148918']:
      sys.exit("This script must be run from the webserver (psweb or psweb2).")
      
   import yaml
   with open(configFile) as yaml_file:
      config = yaml.load(yaml_file)

   rootUsername = config['databases']['root']['username']
   rootPassword = config['databases']['root']['password']
   webRootDir = config['filesystem']['web']['rootdir']
   imageRootDir = config['filesystem']['images']['rootdir']

   if newDatabase(databaseName, dbhost, rootDBUser = rootUsername, rootDBPassword = rootPassword) > 0:
      print("Cannot create Database.  Terminating program.")
      #return 1

   if not options.atlas:
      if newDjangoDatabase(databaseName, dbhost, rootDBUser = rootUsername, rootDBPassword = rootPassword) > 0:
         print("Cannot create Django Database.  Terminating program.")
         return 1

   if newUserAndGrants(user, password, databaseName, dbhost, dropUser = False, rootDBUser = rootUsername, rootDBPassword = rootPassword) > 0:
      print("Cannot create user.  Terminating program.")
      return 1

   if newSchemaAndViews(user, password, databaseName, dbhost, atlas = options.atlas, webRootDir = webRootDir) > 0:
      print("Something went wrong.  Terminating program.")
      return 1

   if djangoDirectoryStructure(user, password, databaseName, dbhost, reUseDevelopmentTemplates = False, atlas = options.atlas, imageRootDir = imageRootDir, webRootDir = webRootDir) > 0:
      print("Something went wrong.  Terminating program.")
      return 1

   if createWebConfigFile(databaseName, atlas = options.atlas, webRootDir = webRootDir) > 0:
      print("Something went wrong.  Terminating program.")
      return 1

   print("Database Created.  The following steps are now required as the ROOT user on the webserver:")
   print("1) cp -p (or mv) the python.<new database>.conf file to /etc/httpd/conf.d (CHECK that there's")
   print("   not a file there with the same name FIRST.")
   print("2) Restart the webserver and CHECK that other services are still running OK. Use apachectl stop and apachectl start.")
   print("   Do NOT use apachectl restart. (This causes the lightcurve code to misbehave.)")
   print("3) Try the new URL, which by default is 'http://star.pst.qub.ac.uk/sne/<new database>/psdb/")
   print("4) (OPTIONAL) EDIT the new database URLs if necessary in the new config file python.<new database>.conf")
   print("   and restart the webserver.")

   print("")

   print("To undo the above you need to:")
   print(" 1) Recursively remove (rm -r) the %s directory from the svnrelease area" % (databaseName))
   print(" 2) Recursively remove (rm -r) the %s directory" % ('/psdb3/images/' + databaseName))
   print(" 3) Drop the %s and %s databases in mysql (need to be mysql root user)" % (databaseName, databaseName + "_django"))
   print(" 4) POSSIBLY drop the %s user in mysql (need to be mysql root user) ASSUMING this is not a SHARED USER" % user)
   print("    WARNING!! DO NOT DROP SHARED USERS!!  This will cause the other databases to stop working.")
   print("    Probably best NOT to share users across different databases.")

   return 0


# ###########################################################################################
#                                         Main hook
# ###########################################################################################


if __name__=="__main__":
    main()

