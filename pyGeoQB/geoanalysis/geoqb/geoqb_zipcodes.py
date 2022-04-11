import pandas as pd

dfZip = None

def getGermanZipCodes( verbose = False ):

    global dfZip

    path_to_zipcode_list = "./data/raw/German-Zip-Codes.csv"

    if dfZip is None:
        dfZip = pd.read_csv( path_to_zipcode_list, header=1, sep=";", dtype=str,
                         names= ['Ort','Zusatz','Plz','Vorwahl','Bundesland'] )

    if verbose:
        print( f"*** Load ZIP code data from FILE: <{path_to_zipcode_list}>.")
        print( dfZip )

    return dfZip

def enrichLoactionName( location_name, region_code = "DE", verbose=False ):
    print(">>> ZIP Code enrichment: {location_name} IN Region: {region_code}" )
    if region_code=="DE" :
        dfZip = getGermanZipCodes( verbose = verbose );
    else:
        raise ValueError( f"Model {region_code} is not yet supported" )

    row = dfZip.loc[dfZip['Ort'] == location_name]
    return row.to_dict