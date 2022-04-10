import copy

import geoanalysis.geoqb.geoqb_layers as gql

def getSampleLayerStack9( layer, path_offset ):
    #
    # Layer #5 - services (attracting)
    #----------------------------------
    attr = [
        ("Services_POS" , "amenity",  '"kindergarten" "library" "music_school" "school" "clinic" "dentist" "doctors" "pharmacy" "theatre" "childcare" "marketplace"'),
        ("Services_POS" , "emergency" , None )
    ]
    attr_weight = 1
    return ( "Services_POS", defineSampleLayerStack( layer, attr, attr_weight, path_offset ) )

def getSampleLayerStack10( layer, path_offset ):
    #
    # Layer #5 - services (detracting)
    #----------------------------------
    detr = [
        ("Services_NEG" , "amenity",  '"brothel" "casino" "conference_centre" "events_venue" "gambling" "love_hotel" "nightclub" "stripclub" "swingerclub" "prison"' )
    ]
    detr_weight = -1
    return ( "Services_NEG", defineSampleLayerStack( layer, detr, detr_weight, path_offset ) )

def getSampleLayerStack7( layer, path_offset ):
    #
    # Layer #4 - leisure (attracting)
    #----------------------------------
    attr = [
        ("Leisure_POS" , "amenity",  '"place_of_worship" "public_bath"'),
        ("Leisure_POS" , "historic" , None ),
        ("Leisure_POS" , "leisure" , None ),
        ("Leisure_POS" , "sport" , None )
    ]
    attr_weight = 1
    return ( "Leisure_POS", defineSampleLayerStack( layer, attr, attr_weight, path_offset ) )

def getSampleLayerStack8( layer, path_offset ):
    #
    # Layer #4 - leisure (detracting)
    #----------------------------------
    detr = [
        ("Leisure_NEG" , "leisure",  '"adult_gambling_centre" ' )
    ]
    detr_weight = -1
    return ( "Leisure_NEG", defineSampleLayerStack( layer, detr, detr_weight, path_offset ) )







def getSampleLayerStack5( layer, path_offset ):
    #
    # Layer #3 - lifestyle (attracting)
    #----------------------------------
    attr = [
        ("Environment_POS" , "amenity",  ' "fountain" "tourism"')
    ]
    attr_weight = 1
    return ( "Environment_POS", defineSampleLayerStack( layer, attr, attr_weight, path_offset ) )


def getSampleLayerStack6( layer, path_offset ):
    #
    # Layer #3 - lifestyle (detracting)
    #----------------------------------
    detr = [
        ("Environment_NEG" , "geological",  '"volcanic_caldera" "volcanic_vent" "volcanic_lava_field" ' ),
        ("Environment_NEG" , "landuse" , '"industrial" "depot" "military" "quarry"' )
    ]
    detr_weight = -1
    return ( "Environment_NEG", defineSampleLayerStack( layer, detr, detr_weight, path_offset ) )





def getSampleLayerStack3( layer, path_offset ):
    #
    # Layer #2 - lifestyle (attracting)
    #----------------------------------
    attr = [
        ("Lifestyle_POS" , "amenity",  ' "bar" "biergarten" "cafe" "ice_cream" "restaurant" "pub"'),
        ("Lifestyle_POS" , "craft",  None )
    ]
    attr_weight = 1
    return ( "Lifestyle_POS", defineSampleLayerStack( layer, attr, attr_weight, path_offset ) )

def getSampleLayerStack4( layer, path_offset ):
    #
    # Layer #2 - lifestyle (detracting)
    #----------------------------------
    detr = [
        ("Lifestyle_NEG" , "shop",  '"shop"  "department_store" "wholesale" "erotic"' ),
        ("Lifestyle_NEG" , "amenity" , '"fast_food" "food_court"' ),
        ("Lifestyle_NEG" , "craft" , '"car_painter" "agricultural_engines"' )
    ]
    detr_weight = -1
    return ( "Lifestyle_NEG", defineSampleLayerStack( layer, detr, detr_weight, path_offset ) )


def getSampleLayerStack1( layer, path_offset ):
    #
    # Layer #1 - Transport (attracting)
    #----------------------------------
    attr = [
        ("Transport_POS" , "amenity",  '"bicycle_parking" "bicycle_repair_station" "bicycle_rental" "bus_station" "car_sharing" "charging_station"'),
        ("Transport_POS" , "public_transport",  None )
    ]
    attr_weight = 1
    return ( "Transport_POS", defineSampleLayerStack( layer, attr, attr_weight, path_offset ) )

def getSampleLayerAllTags ( layer, path_offset ):
    weight = 1
    label = "AllTags"
    return ( label, defineSampleLayerAllTags( layer, label, weight, path_offset ) )


def getSampleLayerStack2( layer, path_offset ):
    #
    # Layer #1 - Transport (detracting)
    #----------------------------------
    detr = [
        ("Transport_NEG" , "aeroway",  None ),
        ("Transport_NEG" , "highway" , '"primary" "trunk" "highway"' )
    ]
    detr_weight = -1
    return ( "Transport_NEG", defineSampleLayerStack( layer, detr, detr_weight, path_offset ) )




def defineSampleLayerAllTags( layer, layerWeight, label, path_offset ):

    stackOfLayers = []

    lTemp = copy.deepcopy( layer )

    lTemp.setLayerWeight( layerWeight )
    lTemp.setLayerLabel( label )

    lTemp.setAllTagQuery()

    stackOfLayers.append( lTemp )

    return stackOfLayers



def defineSampleLayerStack( layer, queryParts, layerWeight, path_offset ):

    stackOfLayers = []

    for tuple in queryParts:

        lTemp = copy.deepcopy( layer )

        lTemp.setLayerWeight( layerWeight )
        lTemp.setLayerLabel( tuple[0] )

        lTemp.setSelectionFilter( query_label = tuple[0] + "_" + tuple[1], tag_cat=tuple[1], tags=tuple[2])

        stackOfLayers.append( lTemp )

    return stackOfLayers

#
# Generate named queries for OSM layers
#
def combineSheets(sheets, path_offset , dryRun = False ):

    LEN = len(sheets)
    print( "***************************************" )
    print( f"*** process {LEN} sheets (dryRun:{dryRun})" )
    print( sheets )
    print( "***************************************" )

    sheetOne = sheets[0]

    sheetOne.getJSONData(path_offset, forceReload=False, dryRun = False )
    sheetOne.plotLayerData( path_offset )

    cl = gql.MultiSophoxLayer( location_name=sheetOne.location_name, zoom=sheetOne.zoom, l=sheetOne.l, fromLayer = True )
    cl.initFromSophosLayer( sophosLayer=sheetOne, path_offset=path_offset, dryRun = dryRun )

    print( "---------------------------------" )
    cl.dumpLayerMD( path_offset, verbose=True )
    print( "---------------------------------" )

    i = 1
    while i < len(sheets):

        print( sheets[i].toJSON() )
        sheets[i].getJSONData(path_offset, forceReload=False, dryRun = False )

        # we append the metadata ...
        sheets[i].dumpLayerMD2( path_offset, verbose=True ) # append mode

        sheets[i].plotLayerData( path_offset )

        cl.addSheet( sheets[i], path_offset=path_offset )
        #print( sheet.getJSONData( path_offset, forceReload=True ) )
        i = i + 1

    print( "###" )

    return cl


def getKGC2022_FullDataset( location_name, l, zoom, path_offset, dryRun ):

    layers = {}

    layer = gql.SophoxLayer( location_name=location_name, zoom=zoom, l=l )

    layers1 = getSampleLayerAllTags( layer, path_offset )

    layers[ layers1[0]+"_"+location_name ] = combineSheets( layers1[1], path_offset, dryRun = dryRun )

    return layers


def getKGC2022_DemoDataStack( location_name, l, zoom, path_offset, dryRun ):

    layers = {}

    layer = gql.SophoxLayer( location_name=location_name, zoom=zoom, l=l )

    layers1 = getSampleLayerStack1( layer, path_offset )
    layers[ layers1[0]+"_"+location_name ] = combineSheets( layers1[1], path_offset, dryRun = dryRun )

    layers2 = getSampleLayerStack2( layer, path_offset )
    layers[ layers2[0]+"_"+location_name ] = combineSheets( layers2[1], path_offset, dryRun = dryRun )

    layers3 = getSampleLayerStack3( layer, path_offset )
    layers[ layers3[0]+"_"+location_name ] = combineSheets( layers3[1], path_offset, dryRun = dryRun )

    layers4 = getSampleLayerStack4( layer, path_offset )
    layers[ layers4[0]+"_"+location_name ] = combineSheets( layers4[1], path_offset, dryRun = dryRun )

    layers5 = getSampleLayerStack5( layer, path_offset )
    layers[ layers5[0]+"_"+location_name ] = combineSheets( layers5[1], path_offset, dryRun = dryRun )

    layers6 = getSampleLayerStack6( layer, path_offset )
    layers[ layers6[0]+"_"+location_name ] = combineSheets( layers6[1], path_offset, dryRun = dryRun )

    layers7 = getSampleLayerStack7( layer, path_offset )
    layers[ layers7[0]+"_"+location_name ] = combineSheets( layers7[1], path_offset, dryRun = dryRun )

    layers8 = getSampleLayerStack8( layer, path_offset )
    layers[ layers8[0]+"_"+location_name ] = combineSheets( layers8[1], path_offset, dryRun = dryRun )

    layers9 = getSampleLayerStack9( layer, path_offset )
    layers[ layers9[0]+"_"+location_name ] = combineSheets( layers9[1], path_offset, dryRun = dryRun )

    layers10 = getSampleLayerStack10( layer, path_offset )
    layers[ layers10[0]+"_"+location_name ] = combineSheets( layers10[1], path_offset, dryRun = dryRun )

    return layers