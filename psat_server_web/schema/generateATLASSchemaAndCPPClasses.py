from gkutils.commonutils import readGenericDataFile, readATLASddetHeader
import sys, os

doubles = ['mjd', 'ra', 'dec']
strings = ['obs', 'obj','filt']
shorts = ['nx','ny','rad']

# All items are assumed to be float unless otherwise stated in this schema dictionary
schema = {'mjd': 'double',
          'ra': 'double',
          'dec': 'double',
          'obs': 'string',
          'obj': 'string',
          'filt': 'string',
          'nx': 'unsigned short',
          'ny': 'unsigned short',
          'rad': 'int', 
          'psc': 'short', 
          'pcr': 'short', 
          'pno': 'short', 
          'pbn': 'short', 
          'pmv': 'short', 
          'pvr': 'short', 
          'pxt': 'short', 
          'pkn': 'short', 
          'ptr': 'short',
          'det': 'char',
          'dup': 'char'} 

cToMysql = {'float': 'float',
            'int': 'int',
            'short': 'smallint',
            'unsigned short': 'smallint_unsigned',
            'char': 'tinyint',
            'double': 'double',
            'string': 'varchar'}

cToStringConvert = {'float': 'stof',
            'int': 'stoi',
            'short': 'stoi',
            'unsigned short': 'stoi',
            'char': 'stoi',
            'double': 'stod',
            'string': ''}


typeNulls = {'float': {'type':'NULL_FLOAT_DOUBLE', 'operator': '>='},
             'int': {'type':'NULL_INT', 'operator': '=='},
             'short': {'type':'NULL_SHORT', 'operator': '=='},
             'char': {'type':'NULL_CHAR', 'operator': '=='},
             'unsigned short': {'type':'NULL_UNSIGNED_SHORT', 'operator': '=='},
             'double': {'type':'NULL_FLOAT_DOUBLE', 'operator': '>='},
             'string': {'type':'EMPTY_STRING', 'operator': '=='}}

# How do we define each row?

# How do I define which attributes are part of the classification vector?

# The code needs to read a data file and define the following:

# * header database table
# * detections database table

# * header database insert class header
# * header database insert class
# * detections database insert class header
# * detections database insert class

# For the most part we assume all the attributes are floats.
# Exceptions are:
# * ra (double)
# * dec (double)
# * a few integer columns to be defined
# * members of the classification vector, which will be combined into a long int.

def createDBTable(tableName, suffix, keys, engine='MyISAM'):
    """createDBTable.

    Args:
        tableName:
        suffix:
        keys:
        engine:
    """
    print("cat > %s%s.sql <<EOF" % (tableName, suffix))
    print("CREATE TABLE \`%s%s\` (" % (tableName, suffix))
    print("\`id\` bigint unsigned not null auto_increment,     -- autoincrementing detection id")
    if 'metadata' in tableName:
        print("\`filename\` varchar(255),")
    else:
        print("\`atlas_metadata_id\` bigint(20) unsigned NOT NULL, -- a reference to the input file and other information (OBS data)")
        print("\`atlas_object_id\` bigint(20) unsigned NOT NULL,   -- a reference to the unique object which tags this object")
        print("\`det_id\` int unsigned not null,                   -- the internal id of the detection (unique per file)")
    for row in keys:
        try:
            type = schema[row]
        except KeyError as e:
            type = "float"

        print("\`%s\` %s, " % (row, cToMysql[type]))
    if 'metadata' in tableName:
        print("""\`input\` varchar(255),
\`reference\` varchar(255),""")
    else:
        print("""\`date_modified\` datetime,            -- when was the detection modified?
\`image_group_id\` bigint unsigned, -- a reference to the group of images that refers to this detection
\`quality_threshold_pass\` bool,    -- does this detection pass some specified cuts?
\`deprecated\` bool,                -- option to ignore this detection
\`realbogus_factor\` float,         -- machine learning real/bogus value""")
    print("""\`htm16ID\` bigint unsigned,
\`date_inserted\` datetime NOT NULL,   -- when was the detection inserted?
PRIMARY KEY \`key_id\` (\`id\`),""")
    if 'metadata' in tableName:
        print("""UNIQUE KEY \`key_filename_mjd\` (\`filename\`,\`mjd\`),
KEY \`idx_mjd\` (\`mjd\`),
UNIQUE KEY \`key_obs\` (\`obs\`),
KEY \`idx_texp\` (\`texp\`),
KEY \`idx_filename\` (\`filename\`),
KEY \`idx_input\` (\`input\`),
KEY \`idx_reference\` (\`reference\`),""")
    else:
        print("""KEY \`idx_atlas_object_id\` (\`atlas_object_id\`),
KEY \`idx_atlas_metadata_id\` (\`atlas_metadata_id\`),""")
    print("""KEY \`idx_htm16ID\` (\`htm16ID\`),
KEY \`idx_date_inserted\` (\`date_inserted\`),
KEY \`idx_ra_dec\` (\`ra\`,\`dec\`)
) ENGINE=%s;
EOF
""" % engine)


def createCPPClass(classname, suffix, keys):
    """createCPPClass.

    Args:
        classname:
        suffix:
        keys:
    """
    print("cat > %s%s.h <<EOF" % (classname, suffix))
    print("#ifndef %s%s_H_" % (classname.upper(), suffix.upper()))
    print("#define %s%s_H_" % (classname.upper(), suffix.upper()))
    print("struct %s%s" % (classname, suffix))
    print("{")
    if 'metadata' in classname:
        print("    std::string filename;")
        print("    std::string input;")
        print("    std::string reference;")
    else:
        print("    unsigned long long metadata_id;")
        print("    unsigned long long object_id;")
        print("    unsigned int det_id;")

    for row in keys:
        try:
            type = schema[row]
            if type == 'string':
                type = 'std::string'
        except KeyError as e:
            type = "float"

        print("    %s %s;" % (type, row))

    print("    unsigned long long htm16ID;")
    print("};")
    print("#endif /* %s%s_H_ */" % (classname.upper(), suffix.upper()))
    print("EOF")

def createCPPDBClassH(classname, suffix, keys):
    """createCPPDBClassH.

    Args:
        classname:
        suffix:
        keys:
    """
    print("cat > %s%sDB.h <<EOF" % (classname, suffix))
    print("#ifndef %s%sDB_H_" % (classname.upper(), suffix.upper()))
    print("#define %s%sDB_H_" % (classname.upper(), suffix.upper()))

    print("#include <mysql++.h>")
    print("#include \"DataRowDefinitions.h\"")
    print("#include \"%s%s.h\"" % (classname, suffix))
    print("#include \"CommonUtils.h\"")
    print("#include \"NullMagicNumbers.h\"")

    print("class %s%sDB {" % (classname, suffix))
    print("public:")
    print("    %s%sDB();" % (classname, suffix))

    if 'metadata' in classname:
        print("    unsigned long long insertRow(const %s%s& %s, mysqlpp::Query& query, std::string filename);" % (classname, suffix, classname))
    else:
        print("    unsigned long long insertRow(const %s%s& %s, mysqlpp::Query& query);" % (classname, suffix, classname))
    print("    virtual ~%s%sDB();" % (classname, suffix))
    print("private:")

    if 'metadata' in classname:
        print("    mysqlpp::Null<mysqlpp::sql_varchar> row_filename;")
        print("    mysqlpp::Null<mysqlpp::sql_varchar> row_input;")
        print("    mysqlpp::Null<mysqlpp::sql_varchar> row_reference;")
    else:
        print("    mysqlpp::Null<mysqlpp::sql_bigint_unsigned> row_metadata_id;")
        print("    mysqlpp::Null<mysqlpp::sql_bigint_unsigned> row_object_id;")
        print("    mysqlpp::Null<mysqlpp::sql_int_unsigned> row_det_id;")


    for row in keys:
        try:
            type = schema[row]
        except KeyError as e:
            type = "float"

        print("    mysqlpp::Null<mysqlpp::sql_%s> row_%s;" % (cToMysql[type], row))

    print("    mysqlpp::Null<mysqlpp::sql_bigint_unsigned> row_htm16ID;")

    print("};")
    print("#endif /* %s%sDB_H_ */" % (classname.upper(), suffix.upper()))
    print("EOF")

def createCPPDBClassCPP(classname, suffix, keys):
    """createCPPDBClassCPP.

    Args:
        classname:
        suffix:
        keys:
    """

    print("cat > %s%sDB.cpp <<EOF" % (classname, suffix))
    print("/*")
    print("* %s%sDB.cpp" % (classname, suffix))
    print("*")
    print("*  Created on: May 04, 2017")
    print("*      Author: kws")
    print("*")
    print("*/")
    print("#include \"%s%sDB.h\"" % (classname, suffix))

    print("%s%sDB::%s%sDB():" % (classname, suffix, classname, suffix))
    if 'metadata' in classname:
        print("row_filename(mysqlpp::null),")
        print("row_input(mysqlpp::null),")
        print("row_reference(mysqlpp::null),")
    else:
        print("row_metadata_id(mysqlpp::null),")
        print("row_object_id(mysqlpp::null),")
        print("row_det_id(mysqlpp::null),")

    for row in keys:
        print("row_%s(mysqlpp::null)," % row)

    print("""row_htm16ID(mysqlpp::null)
{
    // TODO Auto-generated constructor stub

}""")

    if 'metadata' in classname:
        print("unsigned long long %s%sDB::insertRow(const %s%s& %s, mysqlpp::Query& query, std::string filename)" % (classname, suffix, classname, suffix, classname.replace('s','')))
    else:
        print("unsigned long long %s%sDB::insertRow(const %s%s& %s, mysqlpp::Query& query)" % (classname, suffix, classname, suffix, classname.replace('s','')))

    print("""{

    // Declare a utils object.  Note that the methods in this class should probably be made static.
    // This would negate the need to constantly declare it.""")

    print("    if (NULL_UNSIGNED_LONG == %s.htm16ID) row_htm16ID = mysqlpp::null; else row_htm16ID = %s.htm16ID;" % (classname.replace('s',''), classname.replace('s','')))

    if 'metadata' in classname:
        print("    if (EMPTY_STRING == %s.filename) row_filename = mysqlpp::null; else row_filename = %s.filename;" % (classname.replace('s',''), classname.replace('s','')))
        print("    if (EMPTY_STRING == %s.input) row_input = mysqlpp::null; else row_input = %s.input;" % (classname.replace('s',''), classname.replace('s','')))
        print("    if (EMPTY_STRING == %s.reference) row_reference = mysqlpp::null; else row_reference = %s.reference;" % (classname.replace('s',''), classname.replace('s','')))
    else:
        print("    if (NULL_UNSIGNED_LONG == %s.metadata_id) row_metadata_id = mysqlpp::null; else row_metadata_id = %s.metadata_id;" % (classname.replace('s',''), classname.replace('s','')))
        print("    if (NULL_UNSIGNED_LONG == %s.object_id) row_object_id = mysqlpp::null; else row_object_id = %s.object_id;" % (classname.replace('s',''), classname.replace('s','')))
        print("    if (NULL_INT == %s.det_id) row_det_id = mysqlpp::null; else row_det_id = %s.det_id;" % (classname.replace('s',''), classname.replace('s','')))

    for row in keys:
        try:
            type = schema[row]
        except KeyError as e:
            type = "float"
        print("    if (%s %s %s.%s) row_%s = mysqlpp::null; else row_%s = %s.%s;" % (typeNulls[type]['type'], typeNulls[type]['operator'], classname.replace('s',''), row, row, row, classname.replace('s',''), row))

    print("    query << std::setprecision(20) << \"INSERT INTO atlas_%s%s\" <<" % (classname, suffix))
    print("                         \"(\" <<")
    if 'metadata' in classname:
        print("                         \"filename,\" <<")
        print("                         \"input,\" <<")
        print("                         \"reference,\" <<")
    else:
        print("                         \"atlas_metadata_id,\" <<")
        print("                         \"atlas_object_id,\" <<")
        print("                         \"det_id,\" <<")

    for row in keys:
        print("                         \"\`%s\`,\" <<" % row)

    print("                         \"htm16ID,\" <<")
    print("                         \"date_inserted\" <<")
    print("                         \")\" <<")
    print("                         \" VALUES (\" <<")

    if 'metadata' in classname:
        print("""                         mysqlpp::quote << row_filename << "," <<
                         mysqlpp::quote << row_input << "," <<
                         mysqlpp::quote << row_reference << "," << """)
    else:
        print("""                         row_metadata_id << "," <<
                         row_object_id << "," <<
                         row_det_id << "," << """)
    for row in keys:
        try:
            type = schema[row]
        except KeyError as e:
            type = "float"

        if type == 'string':
            print("                         mysqlpp::quote << row_%s << \",\" <<" % row)
        else:
            print("                         row_%s << \",\" <<" % row)
    print("""                         row_htm16ID << "," <<
                         "now()" <<
                         ");";
    unsigned long long id = 0;
    try
    {
        query.execute();
        // Grab the auto incrementing ID from the database
        id = query.insert_id();
        query.reset();
    }
    catch (const mysqlpp::Exception& er)
    {
        // Catch-all for MySQL++ exceptions
        std::cerr << "Error: " << er.what() << std::endl;
        query.reset();
    }

    return id;

}
""")

    print("%s%sDB::~%s%sDB() {" % (classname, suffix, classname, suffix))
    print("""
    // TODO Auto-generated destructor stub
}
""")
    print("EOF")

def createIngesterH(suffix, headerKeys, dataKeys):
    """createIngesterH.

    Args:
        suffix:
        headerKeys:
        dataKeys:
    """

    print("cat > DetectionCrossmatcher%s.h <<EOF" % (suffix))
    print("/*")
    print(" * DetectionCrossmatcher%s.h" % (suffix))
    print(" *")
    print(" *  Created on: May 4, 2017")
    print(" *      Author: kws")
    print(" */")
    print("")
    print("#ifndef DETECTIONCROSSMATCHER%s_H_" % (suffix.upper()))
    print("#define DETECTIONCROSSMATCHER%s_H_" % (suffix.upper()))
    print("")
    print("#include <cmath>")
    print("#include <mysql++.h>")
    print("//#include <fstream>")
    print("//#include <iostream>")
    print("")
    print("#include \"CommonUtils.h\"")
    print("#include \"ReadDDTFile.h\"")
    print("")
    print("#include \"Config.h\"")
    print("#include \"DataRowDefinitions.h\"")
    print("#include \"detections%s.h\"" % (suffix))
    print("#include \"metadata%s.h\"" % (suffix))
    print("#include \"DataRowDefinitions.h\"")
    print("#include \"NullMagicNumbers.h\"")
    print("#include \"ReadDDTFile.h\"")
    print("#include \"detections%sDB.h\"" % (suffix))
    print("#include \"metadata%sDB.h\"" % (suffix))
    print("#include \"TransientObjectTableDB.h\"")
    print("#include \"TransientMomentsDB.h\"")
    print("")
    print("// 2014-12-01 KWS Need to inspect the config values.")
    print("")
    print("")
    print("// Transient Classification Flag Designations - over-engineered for 32 exclusive categories")
    print("// and any combination therein.  This has been created to avoid the need to change table")
    print("// structures when a new category is introduced.")
    print("")
    print("")
    print("class DetectionCrossmatcher%s {" % (suffix))
    print("public:")
    print("    DetectionCrossmatcher%s();" % (suffix))
    print("    //int classifyTransients(string dbUser, string dbPass, string dbName, string dbHost, string filename);")
    print("    int crossmatcher(std::map<std::string, DatabaseMember> dbmap, struct FlagsAndRecurrenceRadius frr, std::string filename);")
    print("    virtual ~DetectionCrossmatcher%s();" % (suffix))
    print("")
    print("private:")
    print("    int writeDetectionRow(std::ofstream& outputFile, const metadata%s& metadata, const detections%s& detection);" % (suffix, suffix))
    print("    int createNewObject(ObjectRow& object, detections%s& detection, metadata%s& metadata, MomentsRow& moments, TransientObjectTableDB& objectDB, detections%sDB& detectionDB, TransientMomentsDB& momentsDB, CommonUtils& common, bool writeFile, bool ingestMoments, ofstream& outputFile, mysqlpp::Query& query);" % (suffix, suffix, suffix))
    print("    unsigned int transient_classification_flags;")
    print("    int checkStarProximity(detections%s& detection, mysqlpp::Query& query, mysqlpp::StoreQueryResult& resultSet, CommonUtils& common, struct FlagsAndRecurrenceRadius frr);" % (suffix))
    print("};")
    print("")
    print("#endif /* DETECTIONCROSSMATCHER%s_H_ */" % (suffix.upper()))
    print("EOF")

def createIngesterCPP(suffix, headerKeys, dataKeys):
    """createIngesterCPP.

    Args:
        suffix:
        headerKeys:
        dataKeys:
    """

    print("cat > DetectionCrossmatcher%s.cpp <<EOF" % (suffix))
    print("/*")
    print(" * DetectionCrossmatcher%s.cpp" % (suffix))
    print(" *")
    print(" *  Created on: May 04, 2017")
    print(" *      Author: kws")
    print(" *")
    print(" */")
    print("")
    print("#include \"DetectionCrossmatcher%s.h\"" % (suffix))
    print("")
    print("")
    print("using namespace std;")
    print("using namespace mysqlpp;")
    print("")
    print("DetectionCrossmatcher%s::DetectionCrossmatcher%s():" % (suffix, suffix))
    print("transient_classification_flags(0)")
    print("{")
    print("")
    print("    // TODO Auto-generated constructor stub")
    print("")
    print("}")
    print("")
    print("DetectionCrossmatcher%s::~DetectionCrossmatcher%s() {" % (suffix, suffix))
    print("    // TODO Auto-generated destructor stub")
    print("}")
    print("")
    print("int DetectionCrossmatcher%s::crossmatcher(map<string, DatabaseMember> dbmap, struct FlagsAndRecurrenceRadius frr, string filename)" % (suffix))
    print("{")
    print("    CommonUtils common;")
    print("    string strippedFilename = common.extractFilename(filename);")
    print("")
    print("    string dbUser = dbmap[\"local\"].username;")
    print("    string dbPass = dbmap[\"local\"].password;")
    print("    string dbName = dbmap[\"local\"].database;")
    print("    string dbHost = dbmap[\"local\"].hostname;")
    print("")
    print("    bool skipHTM = frr.skipHTM;")
    print("    bool writeFile = frr.writeFile;")
    print("    double localTransientSearchRadius = frr.recurrenceRadius;")
    print("    double vStarRadius = frr.vStarRadius;")
    print("    unsigned int maxDetections = frr.maxDetections;")
    print("    bool diffDetections = frr.diffDetections;")
    print("    bool ingestMoments = frr.ingestMoments;")
    print("")
    print("    cout << \"Recurrence Radius = \" << localTransientSearchRadius << endl;")
    print("    cout << \"Variable Star Radius = \" << vStarRadius << endl;")
    print("    cout << \"Max Number of Detections = \" << maxDetections << endl;")
    print("")
    print("    // -----------------------------------------------------------------")
    print("")
    print("    // Temporarily use a YAML setting to turn on or off the HTM code.")
    print("    // With HTM turned off, the database is doing a simple insert.")
    print("    if (skipHTM)")
    print("    {")
    print("        cerr << \"Skip HTM cone search - straight insert only\" << endl;")
    print("    }")
    print("    else")
    print("    {")
    print("        cerr << \"Enabled HTM cone search\" << endl;")
    print("    }")
    print("")
    print("")
    print("")
    print("    // Load the DDC Header file into a map and the data into a vector of maps")
    print("    bool ddet = true;")
    print("    string ddetfilenameheader;")



    print("    ReadDDTFile *%s;" % (suffix))
    print("    map<string,string>* %sHeader;" % (suffix))
    print("    vector<map<string,string>*> %sData;" % (suffix))
    print("    %s = new ReadDDTFile(filename);" % (suffix))
    print("")
    print("    // Classification vector")
    print("    // Pvr = \"variable\" means stationary and (very) long persistance: star, AGN, etc.")
    print("    // Ptr = \"transient\" means short persistence, possibly moving")
    print("    // Pmv = \"moving\" uses trailing or other information")
    print("    // Pkn = \"known asteroid\" from catalogs")
    print("    // Psc = \"scar\" means clutter from imperfect star subtration or bleeds")
    print("    // Pxt = \"xtalk\" : x,y sensitive to stars at (x+n*1320),y and (x+n*1320),(10560-y)")
    print("    // Pbn = \"burn\" is a persistence trail away from serial register")
    print("    // Pno = \"noise\" is generic noise")
    print("    // Pcr = \"cosmic\" is cosmic ray")
    print("")
    print("    // Should read the below from a config file!")
    print("    std::set<std::string> cvector;")
    print("    cvector.insert(\"pvr\");")
    print("    cvector.insert(\"ptr\");")
    print("    cvector.insert(\"psc\");")
    print("    cvector.insert(\"pxt\");")
    print("    cvector.insert(\"pbn\");")
    print("    cvector.insert(\"pno\");")
    print("    cvector.insert(\"pcr\");")
    print("")
    print("    // Add the classification vector contents. They should add up to <= 999")
    print("    int classification_vector = 0;")
    print("    unsigned long long htm16ID;")
    print("")
    print("    if (diffDetections)")
    print("    {")
    print("        %sHeader = %s->getHeader();" % (suffix, suffix))
    print("        if (%sHeader)" % (suffix))
    print("        {")
    print("            for (map<string,string>::iterator i = %sHeader->begin(); i != %sHeader->end(); ++i)" % (suffix, suffix))
    print("            {")
    print("                cout << i->first << \": \" << i->second << endl; ")
    print("            }")
    print("        }")
    print("    }")
    print("    %sData = %s->getData();" % (suffix, suffix))
    print("")
    print("    long nrows = %sData.size();" % (suffix))
    print("")
    print("    cout << \"Number of rows to ingest = \" << nrows << endl;")
    print("")
    print("    if (nrows == 0)")
    print("    {")
    print("        cerr << \"No rows to ingest!\" << endl;")
    print("        return -1;")
    print("    }")
    print("")
    print("    if (maxDetections && nrows > maxDetections)")
    print("    {")
    print("        cerr << \"Too many rows (\" << nrows << \") to ingest from \" << filename << \"!  Possible bad data.\" << endl;")
    print("        return -1;")
    print("    }")
    print("")
    print("")
    print("    // Set the \"header\" row.  The TSV contains this info on every row.")
    print("")
    print("    metadata%s metadata;" % (suffix))
    print("")
    print("    metadata.filename = filename;")
    print("")
    print("    metadata.input = \"\";")
    print("    metadata.reference = \"\";")
    print("")
    print("    if (diffDetections)")
    print("    {")
    print("        try")
    print("        {")
    for row in headerKeys:
        try:
            type = schema[row]
        except KeyError as e:
            type = "float"

        cToString = cToStringConvert[type]
        if cToString:
            openType = cToString + '('
            closeType = ')'
        else:
            openType = ''
            closeType = ''

        print("            metadata.%s = %s%sHeader->at(\"%s\")%s;" % (row, openType, suffix, row, closeType))
    print("            metadata.htm16ID = common.generate_htm_id(16,metadata.ra,metadata.dec);")
    print("        }")
    print("        catch (const std::out_of_range& oor)")
    print("        {")
    print("            cerr << \"Mandatory key not found error: \" << oor.what() << endl;")
    print("            cerr << \"Cannot continue...\" << endl;")
    print("            return -1;")
    print("        }")
    print("    }")
    print("")
    print("")
    print("    ofstream outputFile;")
    print("")
    print("    if (writeFile)")
    print("    {")
    print("        cerr << \"Write a detections file.\" << endl;")
    print("        outputFile.open((filename + \".out\").c_str());")
    print("        // Write the header")
    print("        outputFile <<")
    print("        \"metadata_id\" << \"\\t\" <<")
    print("        \"object_id\" << \"\\t\" <<")
    print("        \"det_id\" << \"\\t\" <<")

    for row in dataKeys:
        print("        \"%s\" << \"\\t\" <<" % row)

    print("        \"htm16ID\" <<")
    print("        endl;")
    print("    }")
    print("    else")
    print("    {")
    print("        cerr << \"Inserting detections into the database.\" << endl;")
    print("    }")
    print("")
    print("")
    print("    string catalogue_to_search = \"atlas_diff_objects\";")
    print("")
    print("    // Star catalogs")
    print("    string stars_ps1 = \"tcs_cat_ps1_ubercal_stars\";")
    print("    string stars_sdss_dr9 = \"tcs_cat_sdss_dr9_stars\";")
    print("    string stars_guide_star = \"tcs_guide_star_cat\";")
    print("    string stars_2mass = \"tcs_2mass_psc_cat\";")
    print("")
    print("    unsigned long long metadata_id; // The ID of the FITS header")
    print("")
    print("    try {")
    print("        mysqlpp::Connection conn(true);  // 2015-02-06 KWS I misunderstood the value of false and true: false = Don't throw exceptions, true = throw them.")
    print("")
    print("        if (!conn.connect(dbName.c_str(), dbHost.c_str(), dbUser.c_str(), dbPass.c_str()))")
    print("        {")
    print("            cerr << \"Failed to connect to database.  Exiting.\" << endl;")
    print("            cerr << \"NOTE: Enter \\\"\\\" to denote a blank db password.\" << endl;")
    print("            return -1;")
    print("        }")
    print("")
    print("        // Pass the Query manipulator around by reference.")
    print("        mysqlpp::Query query = conn.query();")
    print("")
    print("        // First we're going to insert the file metadata")
    print("        metadata%sDB header_row;" % (suffix))
    print("        TransientObjectTableDB objectDB;")
    print("        detections%sDB detectionDB;" % (suffix))
    print("        TransientMomentsDB momentsDB;")
    print("")
    print("        metadata_id = header_row.insertRow(metadata, query, strippedFilename);")
    print("")
    print("        if (metadata_id == 0)")
    print("        {")
    print("            // Something went wrong with the insert of the header.  Abort processing of this file!")
    print("            cerr << \"Failed to insert header.  Skipping file processing for \" << strippedFilename << \".\" << endl;")
    print("            return -1;")
    print("        }")
    print("")
    print("        // Column list for cone searching (commented out columns below are examples)")
    print("        std::list<string> columns;")
    print("        columns.push_back(\"*\");")
    print("")
    print("")
    print("        // Now iterate through the detections")
    print("")
    print("        detections%s detection;" % (suffix))
    print("        ObjectRow object;")
    print("        MomentsRow moments;")
    print("        mysqlpp::StoreQueryResult resultSet;")
    print("")
    print("        unsigned int counter = 0;")
    print("        for (vector< map<string,string>* >::iterator p = %sData.begin(); p != %sData.end(); ++p)" % (suffix, suffix))
    print("        {")
    print("            classification_vector = 0;")
    print("            // Is our key one of the classification vectors - if so, lets add them up")
    print("            for (map<string,string>::iterator i = (*p)->begin(); i != (*p)->end(); ++i)")
    print("            {")
    print("                if (cvector.find(i->first) != cvector.end())")
    print("                {")
    print("                    cout << i->first << \": \" << i->second << \" \";")
    print("                    classification_vector += stoi(i->second);")
    print("                }")
    print("            }")
    print("            cout << endl;")
    print("")
    print("            try")
    print("            {")
    for row in dataKeys:
        try:
            type = schema[row]
        except KeyError as e:
            type = "float"

        cToString = cToStringConvert[type]
        if cToString:
            openType = cToString + '('
            closeType = ')'
        else:
            openType = ''
            closeType = ''
        print("                detection.%s = %s(*p)->at(\"%s\")%s;" % (row, openType, row, closeType))
    print("            }")
    print("            catch (const std::out_of_range& oor)")
    print("            {")
    print("                cerr << \"Mandatory key not found error: \" << oor.what() << endl;")
    print("                cerr << \"Cannot continue...\" << endl;")
    print("                return -1;")
    print("            }")
    print("")
    print("            detection.htm16ID = common.generate_htm_id(16,detection.ra,detection.dec);")
    print("")
    print("            //int")
    print("            if (diffDetections)")
    print("                detection.det_id = counter;")
    print("            else")
    print("                detection.det_id = stoi((*p)->at(\"id\"));")
    print("")
    print("            // 2016-03-18 KWS Ingest the moments data.  These will be stored in a")
    print("            //                separate database table which will link to the parent")
    print("            //                detection")
    print("            if (ingestMoments)")
    print("            {")
    print("                try")
    print("                {")
    print("                    moments.x = stof((*p)->at(\"x\"));")
    print("                }")
    print("                catch (const std::out_of_range& oor)")
    print("                {")
    print("                    cerr << \"Optional key not found error: \" << oor.what() << endl;")
    print("                    moments.x = NULL_FLOAT_DOUBLE;")
    print("                }")
    print("                try")
    print("                {")
    print("                    moments.y = stof((*p)->at(\"y\"));")
    print("                }")
    print("                catch (const std::out_of_range& oor)")
    print("                {")
    print("                    cerr << \"Optional key not found error: \" << oor.what() << endl;")
    print("                    moments.y = NULL_FLOAT_DOUBLE;")
    print("                }")
    print("                try")
    print("                {")
    print("                    moments.cx = stof((*p)->at(\"cx\"));")
    print("                }")
    print("                catch (const std::out_of_range& oor)")
    print("                {")
    print("                    cerr << \"Optional key not found error: \" << oor.what() << endl;")
    print("                    moments.cx = NULL_FLOAT_DOUBLE;")
    print("                }")
    print("                try")
    print("                {")
    print("                    moments.cy = stof((*p)->at(\"cy\"));")
    print("                }")
    print("                catch (const std::out_of_range& oor)")
    print("                {")
    print("                    cerr << \"Optional key not found error: \" << oor.what() << endl;")
    print("                    moments.cy = NULL_FLOAT_DOUBLE;")
    print("                }")
    print("                try")
    print("                {")
    print("                    moments.xpk = stof((*p)->at(\"xpk\"));")
    print("                }")
    print("                catch (const std::out_of_range& oor)")
    print("                {")
    print("                    cerr << \"Optional key not found error: \" << oor.what() << endl;")
    print("                    moments.xpk = NULL_FLOAT_DOUBLE;")
    print("                }")
    print("                try")
    print("                {")
    print("                    moments.ypk = stof((*p)->at(\"ypk\"));")
    print("                }")
    print("                catch (const std::out_of_range& oor)")
    print("                {")
    print("                    cerr << \"Optional key not found error: \" << oor.what() << endl;")
    print("                    moments.ypk = NULL_FLOAT_DOUBLE;")
    print("                }")
    print("                try")
    print("                {")
    print("                    moments.rKron = stof((*p)->at(\"rKron\"));")
    print("                }")
    print("                catch (const std::out_of_range& oor)")
    print("                {")
    print("                    cerr << \"Optional key not found error: \" << oor.what() << endl;")
    print("                    moments.rKron = NULL_FLOAT_DOUBLE;")
    print("                }")
    print("                try")
    print("                {")
    print("                    moments.rVar = stof((*p)->at(\"rVar\"));")
    print("                }")
    print("                catch (const std::out_of_range& oor)")
    print("                {")
    print("                    cerr << \"Optional key not found error: \" << oor.what() << endl;")
    print("                    moments.rVar = NULL_FLOAT_DOUBLE;")
    print("                }")
    print("                try")
    print("                {")
    print("                    moments.flux = stof((*p)->at(\"flux\"));")
    print("                }")
    print("                catch (const std::out_of_range& oor)")
    print("                {")
    print("                    cerr << \"Optional key not found error: \" << oor.what() << endl;")
    print("                    moments.flux = NULL_FLOAT_DOUBLE;")
    print("                }")
    print("                try")
    print("                {")
    print("                    moments.Crad = stof((*p)->at(\"Crad\"));")
    print("                }")
    print("                catch (const std::out_of_range& oor)")
    print("                {")
    print("                    cerr << \"Optional key not found error: \" << oor.what() << endl;")
    print("                    moments.Crad = NULL_FLOAT_DOUBLE;")
    print("                }")
    print("                try")
    print("                {")
    print("                    moments.Qrad = stof((*p)->at(\"Qrad\"));")
    print("                }")
    print("                catch (const std::out_of_range& oor)")
    print("                {")
    print("                    cerr << \"Optional key not found error: \" << oor.what() << endl;")
    print("                    moments.Qrad = NULL_FLOAT_DOUBLE;")
    print("                }")
    print("                try")
    print("                {")
    print("                    moments.Trad = stof((*p)->at(\"Trad\"));")
    print("                }")
    print("                catch (const std::out_of_range& oor)")
    print("                {")
    print("                    cerr << \"Optional key not found error: \" << oor.what() << endl;")
    print("                    moments.Trad = NULL_FLOAT_DOUBLE;")
    print("                }")
    print("                try")
    print("                {")
    print("                    moments.Q2 = stof((*p)->at(\"Q2\"));")
    print("                }")
    print("                catch (const std::out_of_range& oor)")
    print("                {")
    print("                    cerr << \"Optional key not found error: \" << oor.what() << endl;")
    print("                    moments.Q2 = NULL_FLOAT_DOUBLE;")
    print("                }")
    print("                try")
    print("                {")
    print("                    moments.Q2cos = stof((*p)->at(\"Q2cos\"));")
    print("                }")
    print("                catch (const std::out_of_range& oor)")
    print("                {")
    print("                    cerr << \"Optional key not found error: \" << oor.what() << endl;")
    print("                    moments.Q2cos = NULL_FLOAT_DOUBLE;")
    print("                }")
    print("                try")
    print("                {")
    print("                    moments.Q2sin = stof((*p)->at(\"Q2sin\"));")
    print("                }")
    print("                catch (const std::out_of_range& oor)")
    print("                {")
    print("                    cerr << \"Optional key not found error: \" << oor.what() << endl;")
    print("                    moments.Q2sin = NULL_FLOAT_DOUBLE;")
    print("                }")
    print("                try")
    print("                {")
    print("                    moments.Q3cos = stof((*p)->at(\"Q3cos\"));")
    print("                }")
    print("                catch (const std::out_of_range& oor)")
    print("                {")
    print("                    cerr << \"Optional key not found error: \" << oor.what() << endl;")
    print("                    moments.Q3cos = NULL_FLOAT_DOUBLE;")
    print("                }")
    print("                try")
    print("                {")
    print("                    moments.Q3sin = stof((*p)->at(\"Q3sin\"));")
    print("                }")
    print("                catch (const std::out_of_range& oor)")
    print("                {")
    print("                    cerr << \"Optional key not found error: \" << oor.what() << endl;")
    print("                    moments.Q3sin = NULL_FLOAT_DOUBLE;")
    print("                }")
    print("                try")
    print("                {")
    print("                    moments.Q1cos = stof((*p)->at(\"Q1cos\"));")
    print("                }")
    print("                catch (const std::out_of_range& oor)")
    print("                {")
    print("                    cerr << \"Optional key not found error: \" << oor.what() << endl;")
    print("                    moments.Q1cos = NULL_FLOAT_DOUBLE;")
    print("                }")
    print("                try")
    print("                {")
    print("                    moments.Q1sin = stof((*p)->at(\"Q1sin\"));")
    print("                }")
    print("                catch (const std::out_of_range& oor)")
    print("                {")
    print("                    cerr << \"Optional key not found error: \" << oor.what() << endl;")
    print("                    moments.Q1sin = NULL_FLOAT_DOUBLE;")
    print("                }")
    print("            }")
    print("")
    print("")
    print("            // Insert the detection, but before doing so, we need to cone search.")
    print("")
    print("            detection.metadata_id = metadata_id;")
    print("            unsigned long long object_id = 0;")
    print("            unsigned long long detection_id = 0;")
    print("            unsigned long long moments_id = 0;")
    print("")
    print("            // Pick up John Tonry's Indexing ID. We'll use M = 200 (18 arcsec area grid size).")
    print("            // This value of M should also be < 2^31 (signed int).")
    print("            int M = 200;")
    print("")
    print("            // Do HTM cone search but using HTM only.  The results are NOT")
    print("            // refined, so we need to refine them ourselves.")
    print("            if (skipHTM)")
    print("            {")
    print("                createNewObject(object, detection, metadata, moments, objectDB, detectionDB, momentsDB, common, writeFile, ingestMoments, outputFile, query);")
    print("            }")
    print("            else")
    print("            {")
    print("                common.htmCircle(16, detection.ra, detection.dec, localTransientSearchRadius, catalogue_to_search, columns, query);")
    print("")
    print("                resultSet = query.store();")
    print("                query.reset();")
    print("")
    print("                if (resultSet.num_rows() == 0)")
    print("                {")
    print("                    // Find out if it's near a star")
    print("                    object.classification = NULL_INT;")
    print("                    if (frr.matchStars)")
    print("                        object.classification = checkStarProximity(detection, query, resultSet, common, frr);")
    print("                    createNewObject(object, detection, metadata, moments, objectDB, detectionDB, momentsDB, common, writeFile, ingestMoments, outputFile, query);")
    print("                    // Nope - no objects - therefore we need to create a new object.")
    print("                }")
    print("                else")
    print("                {")
    print("                    // We have some results but are they within the required radius?")
    print("                    bool foundObject = false;")
    print("                    for (size_t j = 0; j < resultSet.num_rows(); j++)")
    print("                    {")
    print("                        double separation = 0;")
    print("                        separation = common.calculate_separation(detection.ra, detection.dec, resultSet[j][\"ra\"],resultSet[j][\"dec\"]);")
    print("")
    print("                        if (separation < localTransientSearchRadius)")
    print("                        {")
    print("                            foundObject = true;")
    print("                            // Currently, in Pan-STARRS, we add a new detection row for")
    print("                            // every object within the search radius.  Do we want to do")
    print("                            // that here??")
    print("                            object_id = resultSet[j][\"id\"];")
    print("                            detection.object_id = object_id;")
    print("")
    print("                            if (writeFile)")
    print("                            {")
    print("                                int status = writeDetectionRow(outputFile, metadata, detection);")
    print("                            }")
    print("                            else")
    print("                            {")
    print("                                // Need to insert moment info here with detection_id")
    print("                                detection_id = detectionDB.insertRow(detection, query);")
    print("                                if (ingestMoments && detection_id > 0)")
    print("                                {")
    print("                                    moments.detection_id = detection_id;")
    print("                                    moments_id = momentsDB.insertRow(moments, query);")
    print("                                }")
    print("                            }")
    print("")
    print("                            //detection_id = detectionDB.insertRow(detection, query);")
    print("                            if (detection_id == 0 && !writeFile)")
    print("                            {")
    print("                                // Something went wrong - we want the detection insert to always succeed.")
    print("                                cerr << \"Failed to insert object.\" << endl;")
    print("                                //return -1;")
    print("                            }")
    print("                            if (ingestMoments)")
    print("                            {")
    print("                                if (moments_id == 0 && !writeFile)")
    print("                                {")
    print("                                    // Something went wrong - we want the detection insert to always succeed.")
    print("                                    cerr << \"Failed to insert moments information.\" << endl;")
    print("                                    //return -1;")
    print("                                }")
    print("                            }")
    print("                        }")
    print("                    }")
    print("                    if (!foundObject)")
    print("                    {")
    print("                        object.classification = NULL_INT;")
    print("                        if (frr.matchStars)")
    print("                            object.classification = checkStarProximity(detection, query, resultSet, common, frr);")
    print("                        createNewObject(object, detection, metadata, moments, objectDB, detectionDB, momentsDB, common, writeFile, ingestMoments, outputFile, query);")
    print("                        // Nope - no objects within search radius - therefore we need to create a new object.")
    print("                    }")
    print("")
    print("                }")
    print("")
    print("            }")
    print("")
    print("")
    print("            counter++;")
    print("        }")
    print("")
    print("")
    print("    } catch (mysqlpp::BadQuery er) { // handle any connection or")
    print("        // query errors that may come up")
    print("        std::cerr << \"Error: \" << er.what() << std::endl;")
    print("        return -1;")
    print("    } catch (const mysqlpp::BadConversion& er) {")
    print("        // Handle bad conversions")
    print("        std::cerr << \"Conversion error: \" << er.what() << std::endl")
    print("                << \"\\tretrieved data size: \" << er.retrieved")
    print("                << \", actual size: \" << er.actual_size << std::endl;")
    print("        return -1;")
    print("    } catch (const mysqlpp::Exception& er) {")
    print("        // Catch-all for any other MySQL++ exceptions")
    print("        std::cerr << \"Catch-all Error: \" << er.what() << std::endl;")
    print("        return -1;")
    print("    }")
    print("")
    print("    if (writeFile)")
    print("    {")
    print("        outputFile.close();")
    print("    }")
    print("")
    print("    // Happy with results.")
    print("    return 0;")
    print("")
    print("}")
    print("")
    print("// Write out the detection row into a previously opened file.")
    print("int DetectionCrossmatcher%s::writeDetectionRow(ofstream& outputFile, const metadata%s& metadata, const detections%s& detection)" % (suffix, suffix, suffix))
    print("{")
    print("    outputFile << setprecision(10) <<")
    print("    detection.metadata_id << \"\\t\" <<")
    print("    detection.object_id << \"\\t\" <<")
    print("    detection.det_id << \"\\t\" <<")

    for row in dataKeys:
        print("    detection.%s << \"\\t\" <<" % (row))

    print("    detection.htm16ID <<")
    print("    endl;")
    print("")
    print("    return 0;")
    print("}")
    print("")
    print("int DetectionCrossmatcher%s::createNewObject(ObjectRow& object, detections%s& detection, metadata%s& metadata, MomentsRow& moments, TransientObjectTableDB& objectDB, detections%sDB& detectionDB, TransientMomentsDB& momentsDB, CommonUtils& common, bool writeFile, bool ingestMoments, ofstream& outputFile, mysqlpp::Query& query)" % (suffix, suffix, suffix, suffix))
    print("{")
    print("    // Create a new object record")
    print("")
    print("    // set the object RA and Dec")
    print("    object.ra = detection.ra;")
    print("    object.dec = detection.dec;")
    print("    object.htm16ID = detection.htm16ID;")
    print("    // Need to get the detection ID before we insert the object.")
    print("    // But need the object ID before we insert the detection.")
    print("    // Thus we need to generate the ID HERE not in the objectDB code.")
    print("    object.object_id = common.generate_ra_dec_id00(object.ra,object.dec);")
    print("    // Insert the detection.")
    print("    detection.object_id = object.object_id;")
    print("")
    print("    long long detection_id = 0;")
    print("    long long moments_id = 0;")
    print("")
    print("    if (writeFile)")
    print("    {")
    print("        int status = writeDetectionRow(outputFile, metadata, detection);")
    print("    }")
    print("    else")
    print("    {")
    print("        detection_id = detectionDB.insertRow(detection, query);")
    print("        // Need to insert moment info here with detection_id")
    print("        if (ingestMoments && detection_id > 0)")
    print("        {")
    print("            moments.detection_id = detection_id;")
    print("            moments_id = momentsDB.insertRow(moments, query);")
    print("        }")
    print("    }")
    print("")
    print("    if (detection_id == 0 && !writeFile)")
    print("    {")
    print("        // Something went wrong - we want the detection insert to always succeed.")
    print("        cerr << \"Failed to insert detection.\" << endl;")
    print("        //return -1;")
    print("    }")
    print("")
    print("    if (ingestMoments)")
    print("    {")
    print("        if (moments_id == 0 && !writeFile)")
    print("        {")
    print("            // Something went wrong - we want the detection insert to always succeed.")
    print("            cerr << \"Failed to insert moments information.\" << endl;")
    print("            //return -1;")
    print("        }")
    print("    }")
    print("")
    print("    object.detection_id = detection_id;")
    print("")
    print("    long long object_id = objectDB.insertRow(object, query);")
    print("    if (object_id == 0 || object_id != object.object_id)")
    print("    {")
    print("        // Something went wrong with the insert of the object.")
    print("        cerr << \"Failed to insert object.\" << endl;")
    print("        // The object may have failed to insert because it already exists! That's fine.")
    print("        //return -1;")
    print("    }")
    print("")
    print("}")
    print("")
    print("int DetectionCrossmatcher%s::checkStarProximity(detections%s& detection, mysqlpp::Query& query, mysqlpp::StoreQueryResult& resultSet, CommonUtils& common, struct FlagsAndRecurrenceRadius frr)" % (suffix, suffix))
    print("{")
    print("    std::list<string> columns;")
    print("    columns.push_back(\"*\");")
    print("    int object_classification = NULL_INT;")
    print("    bool classified = false;")
    print("    //mysqlpp::StoreQueryResult resultSet;")
    print("    double separation;")
    print("    float mag;")
    print("")
    print("    // Near PS1 catalogued star?")
    print("    if (!classified)")
    print("    {")
    print("        cout << \"PS1 star check \" << detection.ra << \" \" << detection.dec << endl;")
    print("        common.htmCircle(16, detection.ra, detection.dec, frr.vStarRadius, \"tcs_cat_ps1_ubercal_stars\", columns, query);")
    print("        resultSet = query.store();")
    print("        query.reset();")
    print("        if (resultSet.num_rows() > 0)")
    print("        {")
    print("            for (size_t j = 0; j < resultSet.num_rows(); j++)")
    print("            {")
    print("                separation = common.calculate_separation(detection.ra, detection.dec, resultSet[j][\"RA\"],resultSet[j][\"Dec\"]);")
    print("                mag = resultSet[j][\"r\"];")
    print("                if (separation < frr.vStarRadius && mag < 17.0)")
    print("                {")
    print("                    classified = true;")
    print("                    object_classification = 2;")
    print("                    cout << \"PS1 match: object_classification = \" << object_classification << endl;")
    print("                    break;")
    print("                }")
    print("            }")
    print("        }")
    print("    }")
    print("")
    print("")
    print("    // Near Guide Star?")
    print("    if (!classified)")
    print("    {")
    print("        cout << \"Guide star check\" << endl;")
    print("        common.htmCircle(16, detection.ra, detection.dec, frr.vStarRadius, \"tcs_guide_star_cat\", columns, query);")
    print("        resultSet = query.store();")
    print("        query.reset();")
    print("        if (resultSet.num_rows() > 0)")
    print("        {")
    print("            for (size_t j = 0; j < resultSet.num_rows(); j++)")
    print("            {")
    print("                separation = common.calculate_separation(detection.ra, detection.dec, resultSet[j][\"RightAsc\"]*common.RAD_TO_DEG_FACTOR,resultSet[j][\"Declination\"]*common.RAD_TO_DEG_FACTOR);")
    print("                if (separation < frr.vStarRadius)")
    print("                {")
    print("                    classified = true;")
    print("                    object_classification = 2;")
    print("                    break;")
    print("                }")
    print("            }")
    print("        }")
    print("    }")
    print("")
    print("")
    print("    // Near 2MASS Star?")
    print("    if (!classified)")
    print("    {")
    print("        cout << \"2MASS star check\" << endl;")
    print("        common.htmCircle(16, detection.ra, detection.dec, frr.vStarRadius, \"tcs_2mass_psc_cat\", columns, query);")
    print("        resultSet = query.store();")
    print("        query.reset();")
    print("        if (resultSet.num_rows() > 0)")
    print("        {")
    print("            for (size_t j = 0; j < resultSet.num_rows(); j++)")
    print("            {")
    print("                separation = common.calculate_separation(detection.ra, detection.dec, resultSet[j][\"ra\"],resultSet[j][\"decl\"]);")
    print("                if (separation < frr.vStarRadius)")
    print("                {")
    print("                    classified = true;")
    print("                    object_classification = 2;")
    print("                    break;")
    print("                }")
    print("            }")
    print("        }")
    print("    }")
    print("")
    print("")
    print("    // Near SDSS DR9 Star?")
    print("    // Skip this check for the time being.")
    print("")
    print("    return object_classification;")
    print("}")
    print("EOF")

def createMain(suffix, headerKeys, dataKeys):
    """createMain.

    Args:
        suffix:
        headerKeys:
        dataKeys:
    """

    print("cat > IngesterMain%s.cpp <<EOF" % (suffix))
    print("//============================================================================")
    print("// Name        : IngesterMain%s.cpp" % (suffix))
    print("// Author      : Ken Smith")
    print("// Version     :")
    print("// Copyright   :")
    print("// Description : Runs a query against a table using the HTM circleRegion code.")
    print("//               Assumes column name is always htm<level>ID")
    print("//============================================================================")
    print("")
    print("#include <cmath>")
    print("#include <mysql++.h>")
    print("")
    print("#include \"DetectionCrossmatcher%s.h\"" % (suffix))
    print("#include \"CommonUtils.h\"")
    print("#include \"Config.h\"")
    print("")
    print("using namespace std;")
    print("")
    print("int main(int argc, char *argv[]) {")
    print("")
    print("    if (argc != 3)")
    print("    {")
    print("        cerr << \"Usage: \" << argv[0] << \" <config file> <%s filename>\" << endl;" % (suffix))
    print("        return -1;")
    print("    }")
    print("")
    print("    string configFile = argv[1];")
    print("    string filename = argv[2];")
    print("")
    print("    DetectionCrossmatcher%s crossmatcher;" % (suffix))
    print("    CommonUtils utils;")
    print("    Config config(configFile);")
    print("")
    print("    map<string, DatabaseMember> dbmap = config.getDatabases();")
    print("    struct FlagsAndRecurrenceRadius frr = config.getFlagsAndRecurrenceRadius();")
    print("")
    print("")
    print("    string fileextension = utils.extractFilenameExtension(filename);")
    print("    if (fileextension != \".%s\")" % (suffix))
    print("    {")
    print("        cerr << \"Please feed me a headed %s file!\" << endl;" % (suffix))
    print("        return -1;")
    print("    }")
    print("")
    print("    if (crossmatcher.crossmatcher(dbmap, frr, filename))")
    print("    {")
    print("        cerr << \"Something went wrong.\" << endl;")
    print("        return -1;")
    print("    }")
    print("")
    print("    return 0;")
    print("}")
    print("EOF")

def createMakefile(suffix):
    """createMakefile.

    Args:
        suffix:
    """
    print("cat > Makefile_%s <<EOF" % (suffix))
    print("HTM_INCLUDE = \$(CODEBASE)/htm/include")
    print("UTILS_INCLUDE = \$(CODEBASE)/ingesters/ps1_transients/cpp/include")
    print("TPHOT_INCLUDE = \$(CODEBASE)/ingesters/tphot/cpp/include")
    print("HTM_LIB = \$(CODEBASE)/htm")
    print("OBJDIR = ./objs")
    print("INCDIR = .")
    print("RM = rm -f")
    print("CC = g++")
    print("DEBUG = -g")
    print("CFLAGS = -Wall -c -fPIC  \$(DEBUG) -Wall -I\$(MYSQL_INCLUDE) -I\$(MYSQLPP_INCLUDE) -I\$(HTM_INCLUDE) -I\$(INCDIR) -I\$(TPHOT_INCLUDE) -Wno-deprecated \$(CLANG_FLAGS) -I\$(UTILS_INCLUDE) -std=c++0x")
    print("LFLAGS = -Wall \$(DEBUG) -L\$(MYSQL_LIB) -L\$(MYSQLPP_LIB) -L\$(HTM_LIB)")
    print("")
    print("LIBS = -lm -lmysqlclient -lmysqlpp -lhtm -lpcrecpp -lyaml-cpp")
    print("")
    print("OBJS = \$(OBJDIR)/IngesterMain%s.o \$(OBJDIR)/DetectionCrossmatcher%s.o \$(OBJDIR)/detections%sDB.o \$(OBJDIR)/metadata%sDB.o \$(OBJDIR)/ReadDDTFile.o \$(OBJDIR)/CommonUtils.o \$(OBJDIR)/Config.o \$(OBJDIR)/TransientMomentsDB.o \$(OBJDIR)/TransientObjectTableDB.o" % (suffix, suffix, suffix, suffix))
    print("")
    print("IngesterMain%s.o: \$(OBJS)" % (suffix))
    print("\t\$(CC)  -o IngesterMain%s \$(OBJS) \$(LFLAGS) \$(LIBS)" % (suffix))
    print("")
    print("\$(OBJDIR)/IngesterMain%s.o: ./IngesterMain%s.cpp" % (suffix, suffix))
    print("\t\$(CC) \$(CFLAGS) ./IngesterMain%s.cpp -o \$@" % (suffix))
    print("")
    print("\$(OBJDIR)/DetectionCrossmatcher%s.o: ./DetectionCrossmatcher%s.cpp" % (suffix, suffix))
    print("\t\$(CC) \$(CFLAGS) ./DetectionCrossmatcher%s.cpp -o \$@" % (suffix))
    print("")
    print("\$(OBJDIR)/detections%sDB.o: ./detections%sDB.cpp" % (suffix, suffix))
    print("\t\$(CC) \$(CFLAGS) ./detections%sDB.cpp -o \$@" % (suffix))
    print("")
    print("\$(OBJDIR)/metadata%sDB.o: ./metadata%sDB.cpp" % (suffix, suffix))
    print("\t\$(CC) \$(CFLAGS) ./metadata%sDB.cpp -o \$@" % (suffix))
    print("")
    print("\$(OBJDIR)/ReadDDTFile.o: \$(CODEBASE)/ingesters/tphot/cpp/src/ReadDDTFile.cpp")
    print("\t\$(CC) \$(CFLAGS) \$(CODEBASE)/ingesters/tphot/cpp/src/ReadDDTFile.cpp -o \$@")
    print("")
    print("\$(OBJDIR)/CommonUtils.o: \$(CODEBASE)/ingesters/ps1_transients/cpp/src/CommonUtils.cpp")
    print("\t\$(CC) \$(CFLAGS) \$(CODEBASE)/ingesters/ps1_transients/cpp/src/CommonUtils.cpp -o \$@")
    print("")
    print("\$(OBJDIR)/Config.o: \$(CODEBASE)/ingesters/tphot/cpp/src/Config.cpp")
    print("\t\$(CC) \$(CFLAGS) \$(CODEBASE)/ingesters/tphot/cpp/src/Config.cpp -o \$@")
    print("")
    print("\$(OBJDIR)/TransientMomentsDB.o: \$(CODEBASE)/ingesters/tphot/cpp/src/TransientMomentsDB.cpp")
    print("\t\$(CC) \$(CFLAGS) \$(CODEBASE)/ingesters/tphot/cpp/src/TransientMomentsDB.cpp -o \$@")
    print("")
    print("\$(OBJDIR)/TransientObjectTableDB.o: \$(CODEBASE)/ingesters/tphot/cpp/src/TransientObjectTableDB.cpp")
    print("\t\$(CC) \$(CFLAGS) \$(CODEBASE)/ingesters/tphot/cpp/src/TransientObjectTableDB.cpp -o \$@")
    print("")
    print("all: IngesterMain%s" % (suffix))
    print("")
    print("clean:")
    print("\t-\$(RM) \$(OBJS) IngesterMain%s" % (suffix))
    print("")
    print("EOF")

def main(argv = None):
    """main.

    Args:
        argv:
    """
    import optparse

    if argv is None:
        argv = sys.argv

    usage = "Usage: %s <inputFile>" % argv[0]
    if len(argv) < 2:
        sys.exit(usage)

    filename = argv[1]
    suffix = filename.split('.')[-1]
    
    hlines, header = readATLASddetHeader(filename, useOrderedDict = True)
    headerKeys = [x.lower() for x in list(header)]
    colData = readGenericDataFile(filename, skipLines=hlines, useOrderedDict = True)
    dataKeys = [x.lower().replace('-','').replace('/','') for x in list(colData[0])]

    # Create database table
    if headerKeys:
        createDBTable('atlas_metadata', suffix, headerKeys)
        print()
        createCPPClass('metadata', suffix, headerKeys)
        print()
        createCPPDBClassH('metadata', suffix, headerKeys)
        print()
        createCPPDBClassCPP('metadata', suffix, headerKeys)

    createDBTable('atlas_detections', suffix, dataKeys)
    print()
    createCPPClass('detections', suffix, dataKeys)
    print()
    createCPPDBClassH('detections', suffix, dataKeys)
    print()
    createCPPDBClassCPP('detections', suffix, dataKeys)

    #print
    createIngesterH(suffix, headerKeys, dataKeys)
    print()
    createIngesterCPP(suffix, headerKeys, dataKeys)

    print()
    createMain(suffix, headerKeys, dataKeys)

    print()
    createMakefile(suffix)



if __name__ == '__main__':
    main()
