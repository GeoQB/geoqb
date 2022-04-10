
import sparql
import os
import json


def reloadOrDumpNamedQueryAsJSON( query, nq, title, path_offset, fnRawOSMResponse, forceReload=True, dryRun = True ):

    data = ""

    fileName = path_offset + "/" + fnRawOSMResponse

    if dryRun:
        return data, fileName

    if not forceReload:

        try:
            f = open( fileName )
            f.close()

            print("***### Load data from Sophox-Dump-File: " + fileName + ".")

            # Do something with the filecontent ...
            with open(fileName) as json_file:
                data = "---DATA---" #json.load(json_file)

            print( data )
            return data, fileName


        except IOError:

            print("File: " + fileName + " not accessible. Load data from Sophox API.")
            print( ">>> Start reloading : ")
            print( "*** Loading .... ")

    sophox_endpoint = os.environ.get('sophox_endpoint')

    s = sparql.Service(sophox_endpoint, "utf-8", "GET")

    result = sparql.query(sophox_endpoint, query)

    print( f">>> Columns in result set: {result.variables}" )

    print( f">>> {query}" )
    print( f">>> {nq}" )
    print( f">>> {title}" )

    data = []

    for row in result.fetchall():
        r2 = sparql.unpack_row(row, convert=None, convert_type={})
        data.append(r2)

    import pandas as pd

    # create DataFrame using data
    df = pd.DataFrame(data, columns = result.variables)

    data = df.to_json(orient = 'records')

    f2 = open( fileName, 'w' )
    f2.write( data )
    f2.close()

    return data, fileName
