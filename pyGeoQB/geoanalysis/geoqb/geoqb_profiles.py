import ssl
ssl._create_default_https_context = ssl._create_unverified_context
context = ssl.create_default_context()

import httpx
import os

from solid.solid_api import SolidAPI
from rdflib import Graph, Namespace, OWL, RDF
from rdflib import URIRef, Literal, BNode





class Auth2:

    def __init__(self):
        self.client = httpx.Client(verify=False)

    @property
    def is_login(self) -> bool:
        return self.client.cookies.get('nssidp.sid') is not None

    def login(self, idp, username, password):
        # NSS only
        if idp[-1] == '/':
            idp = idp[:-1]
        url = '/'.join((idp, 'login/password'))

        data = {
            'username': username,
            'password': password
        }

        r = self.client.post(url, data=data)
        r.raise_for_status()

        if not self.is_login:
            raise Exception('Cannot login.')

        print("* ", r)



#######################################################
#
# Some obvious categories are well known:
#
#######################################################

categories_standard = [
    'tourism',
    'public_transport',
    'accessibility',
    'amenity' ,
    'business',
    'education',
    'transport',
    'medical_services',
    'security',
    'services' ]

#
# Define Customer's Impact Profiles
#
pFAM  = ( "FAMILY" , [7.0, -6.0, 5.0, 8.0,  9.0, -10.0,  4.0,  4.0, 7.0,  3.0] )
pOLD  = ( "OLD"    , [-2.0, 8.0, 9.0, 5.0,  -6.0, 1.0,  1.0,  10.0, 4.0, 7.0] )
pYOUNG = ( "YOUNG"   , [10.0, 10.0,  2.0, 5.0, 3.0,  10.0, 6.0,  2.0, 1.0,  1.0] )

p1  = ( "Student"      , [ 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0] )
p2  = ( "Rentner"      , [ 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0] )
p3 = ( "Partytyp"      , [ 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0] )
p4  = ( "Sportler"     , [ 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0] )
p5 = ( "Naturfreund"   , [ 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0] )

def defineProfilesFor( profile_keys , custom_profile ):

    interactionTYPES = ["impact_lr", "impact_sr"]
    pWEIGHT          = [1,  1, 1,  1, 1,  1, 1,  1, 1,  1]
    pINTERACTION     = [1,  1, 1,  1, 1,  1, 1,  1, 1,  1] # index on interactionTYPES

    prof = {}
    prof[p1[0]] = p1
    prof[p2[0]] = p2
    prof[p3[0]] = p3
    prof[p4[0]] = p4
    prof[p5[0]] = p5

    temp = []
    for i in range(1,11):
        temp.append( custom_profile[ str(i) ] )

    cp = ( "my customprofile" , temp )
    prof[cp[0]] = cp

    pPROF23 = ( cp[0]          , 10, interactionTYPES, pWEIGHT, pINTERACTION, prof[cp[0]])
    pPROF22 = ( profile_keys[0], 10, interactionTYPES, pWEIGHT, pINTERACTION, prof[profile_keys[0]])
    pPROF21 = ( profile_keys[1], 10, interactionTYPES, pWEIGHT, pINTERACTION, prof[profile_keys[1]])

    return pPROF21, pPROF22, pPROF23



def getStandardCategories():
    return categories_standard;


def getCategoriesFromLayers( layers, source_system ):

    categories = []
    i = 0
    print( ">>> Extract categories from Layers ... " )
    for lKey in layers:

        if source_system == "KGC2022":
            lKey = lKey.split( "_Point" )[0]

        categories.append(lKey)
        print( str(i) + " - " + lKey )
        i = i + 1


    return categories

def getStandardProfiles():
    prof = {}
    prof['pFAM'] = pFAM
    prof['pOLD'] = pOLD
    prof['pYOUNG'] = pYOUNG
    return prof


def put_custom_profile_into_pod( profile_name, values):

    SOLID_USERNAME = os.environ.get('SOLID_USERNAME')
    SOLID_PASSWORD = os.environ.get('SOLID_PASSWORD')

    SOLID_IDP = os.environ.get('SOLID_IDP')
    SOLID_POD_ENDPOINT = os.environ.get('SOLID_POD_ENDPOINT')

    print(f">>>--------------------------------------------<<<")
    print(f">>> Linked-Open-Data Cloud - the cloud of PODs <<<")
    print(f">>>--------------------------------------------<<<")
    print(f">>>")
    print(f">>>")
    print(f">>> SOLID datapod [{SOLID_POD_ENDPOINT}] is used with IDP: [{SOLID_IDP}] for user: [{SOLID_USERNAME}]")
    print(f">>>")
    print(f">>>")
    print("* Login ...")
    auth = Auth2()
    #auth = Auth()
    api = SolidAPI(auth)
    auth.login(SOLID_IDP, SOLID_USERNAME, SOLID_PASSWORD)
    print( f"*       ... DONE")

    g = Graph()

    # general relations
    geolayer = Namespace('http://geoqb.com/layer/general#')
    g.bind('geoqb',geolayer)

    for v in values :
        print( v )
        rel = URIRef('http://geoqb.com/layer/general#weight_for_layer_' + v)
        g.add((rel, RDF.value, Literal( str( values[v] ) )))

    newData = g.serialize(format='n3')

    profile_url = f"{SOLID_POD_ENDPOINT}/public/ecolytiq-sustainability-profile/" + profile_name + ".ttl"
    resp = api.put_file(profile_url, newData, 'text/plain')

    print( resp )



def describeSolidDatapod():
    SOLID_IDP = os.environ.get('SOLID_IDP')
    SOLID_POD_ENDPOINT = os.environ.get('SOLID_POD_ENDPOINT')

    print("\n>>> SOLID Datapod is configured for public data profiles." )
    print( f" > solid.idp           : {SOLID_IDP} ")
    print( f" > solid.pod.endpoint  : {SOLID_POD_ENDPOINT} ")



def get_custom_profile_from_pod( profile_name ):

    SOLID_USERNAME = os.environ.get('SOLID_USERNAME')
    SOLID_PASSWORD = os.environ.get('SOLID_PASSWORD')

    SOLID_IDP = os.environ.get('SOLID_IDP')
    SOLID_POD_ENDPOINT = os.environ.get('SOLID_POD_ENDPOINT')

    print(f">>>--------------------------------------------<<<")
    print(f">>> Linked-Open-Data Cloud - the cloud of PODs <<<")
    print(f">>>--------------------------------------------<<<")
    print(f">>>")
    print(f">>>")
    print(f">>> SOLID datapod [{SOLID_POD_ENDPOINT}] is used with IDP: [{SOLID_IDP}] for user: [{SOLID_USERNAME}]")
    print(f">>>")
    print(f">>>")
    print("* Login ...")
    auth = Auth2()
    #auth = Auth()
    api = SolidAPI(auth)
    auth.login(SOLID_IDP, SOLID_USERNAME, SOLID_PASSWORD)
    print( f"*       ... DONE")

    profile_url = f"{SOLID_POD_ENDPOINT}/public/ecolytiq-sustainability-profile/" + profile_name + ".ttl"
    resp = api.get(profile_url)

    g = Graph()
    g.parse(data=resp.text, format="turtle")

    layer_weights = {}

    for s, p, o in g:

        #print(s, p, o)

        parts = s.split("weight_for_layer_")

        if parts[0] == "http://geoqb.com/layer/general#":
            layer_weights[parts[1]] = float(o.value)
            print( str(parts[1]) + " => " + str( layer_weights[parts[1]] ) )

    print( "Profile loading done." )

    return layer_weights




