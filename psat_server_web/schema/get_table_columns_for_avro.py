"""Get table columns to convert into Avro format.

Usage:
  %s <database> <hostname> <tables>...
  %s (-h | --help)
  %s --version

Options:
  -h --help              Show this screen.
  --version              Show version.
  --flagdate=<flagdate>  Flag date threshold beyond which we will select objects [default: 20170920].
  --ddc                  Assume the DDC schema.
  --truncate             Truncate the database tables. Default is NOT to truncate.

"""
import sys
__doc__ = __doc__ % (sys.argv[0], sys.argv[0], sys.argv[0])
from docopt import docopt
from gkutils.commonutils import cleanOptions, Struct, dbConnect

sqlToAvro = {
    "bigint": "long",
    "int": "int",
    "double": "double",
    "float": "float",
    "tinyint": "int",
    "smallint": "int",
    "datetime": "something",
    "varchar": "string"}


def getTableInfo(conn, schema, table):
    """
    Get the ATLAS table we want to convert into avro format

    :param conn: database connection
    :param table: table name

    """
    import MySQLdb

    try:
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute ("""
            select column_name,
                     data_type, 
                   is_nullable
              from information_schema.columns
             where table_schema = %s COLLATE utf8_general_ci
               and table_name = %s COLLATE utf8_general_ci ;
        """, (schema, table))

        resultSet = cursor.fetchall ()
        cursor.close ()

    except MySQLdb.Error as e:
        sys.stderr.write("Error %d: %s\n" % (e.args[0], e.args[1]))
        sys.exit (1)

    return resultSet



def main(argv = None):
    opts = docopt(__doc__, version='0.1')
    opts = cleanOptions(opts)

    # Use utils.Struct to convert the dict into an object for compatibility with old optparse code.
    options = Struct(**opts)

    conn = dbConnect(options.hostname, 'kws', '', options.database)

    if options.tables:
        for row in options.tables:
            data = getTableInfo(conn, options.database, row)
            for column in data:
                if column['is_nullable'] == 'YES':
                    print('{"name": "%s", "type": ["%s", "null"], "default": "null", "doc": ""},' % (column['column_name'], sqlToAvro[column['data_type']]))
                else:
                    print('{"name": "%s", "type": "%s", "doc": ""},' % (column['column_name'], sqlToAvro[column['data_type']]))

    conn.close()



if __name__ == '__main__':
    main()
