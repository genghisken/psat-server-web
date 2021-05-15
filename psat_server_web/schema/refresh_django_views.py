from setup_database_utils import *

def main(argv = None):
   """main.

   Args:
       argv:
   """
   # This code will NOT use MySQLdb to connect to the database.  This is to preserve the
   # ability to run each SQL script individually.  However, we will need to capture the
   # output of each script.

   if argv is None:
      argv = sys.argv

   if len(argv) != 4:
      sys.exit("Usage: refresh_django_views.py <username> <password> <schema name>")

   user = argv[1]
   password = argv[2]
   databaseName = argv[3]

   if newSchemaAndViews(user, password, databaseName, createNewSchema = False) > 0:
      print("Something went wrong.  Terminating program.")
      return 1

   return 0


# ###########################################################################################
#                                         Main hook
# ###########################################################################################


if __name__=="__main__":
    main()

