import copy

import geoanalysis.geoqb.geoqb_h3 as gqh3

import geoanalysis.geoqb.geoqb_sophox as gqsophox

import geoanalysis.geoqb.geoqb_plots as gqplots

import geoanalysis.geoqb.geoqb_osm_pandas as gqosm

import json

import pandas as pd


#
# The run_id becomes part of the filenames of all BLOBS created in an analysis
#
def getRunId( user, location_name, time, bbl='default', h3="h3:undefined"):
  run_id = user + "___" + location_name + "___" + bbl + "___" + str(h3) + "___" + str(time)
  return run_id

def calculateBoundingBox( center, l ):

  w=l
  h=l

  TL1 = center[0] - ( w / 2.0 )
  TL2 = center[1] - ( h / 2.0 )

  BR1 = center[0] + ( w / 2.0 )
  BR2 = center[1] + ( h / 2.0 )

  tl = str(TL1) + ", " + str(TL2)
  br = str(BR1) + ", " + str(BR2)

  #
  # bb shpould be a query and not bounding box
  #
  bb  = '(' + tl + ', ' + br + ');'

  print( "center_lat=" + str(center[0]) )
  print( "center_lon=" + str(center[1]) )
  print( "bb_w=" + str(w) )
  print( "bb_h=" + str(h) )
  print( "bounding box: " + bb  )

  return bb



#
# All data ... Sophox
#
def __getAmenityTagsQuery( center, location_name, l, amtags, query_label, r ):
    r = l * 0.5
    lon_lat = str(center[1])+" "+str(center[0])
    q1='''
SELECT ?osmid ?distance ?loc ?amenity WHERE {
  VALUES ?amenity { ___amtags___ }
  ?osmid osmt:amenity ?amenity . 
  SERVICE wikibase:around { 
      ?osmid osmm:loc ?loc . 
      bd:serviceParam wikibase:center "Point(___lon_lat___)"^^geo:wktLiteral . 
      bd:serviceParam wikibase:radius "___r___" . 
      bd:serviceParam wikibase:distance ?distance .
  } 
  FILTER(?distance < ___r___)
} 
    '''
    query = q1.replace("___lon_lat___", lon_lat)
    query = query.replace("___amtags___", amtags)
    query = query.replace("___r___", r)

    title = 'all nodes around ('+location_name+') radius='+str(r)
    qn = location_name + "_r" + str(r) + "_" + query_label
    return query, title, qn


#
# All data ... Sophox
#
def getAllTagsQuery( center, location_name, l, query_label ):
    r = l * 0.5
    lon_lat = str(center[1])+" "+str(center[0])
    q1='''
SELECT ?osmid ?distance ?loc ?tag ?osmt WHERE {
  ?osmid ?osmt ?tag . 
  SERVICE wikibase:around { 
      ?osmid osmm:loc ?loc . 
      bd:serviceParam wikibase:center "Point(___lon_lat___)"^^geo:wktLiteral . 
      bd:serviceParam wikibase:radius "15" . 
      bd:serviceParam wikibase:distance ?distance .
  } 
  FILTER(?distance < 15)
}
    '''

    query = q1.replace("___lon_lat___", lon_lat)

    title = query_label + ' around ('+location_name+') radius='+str(r)

    qn = location_name + "_r" + str(r) + "_" + query_label

    return query, title, qn


#
# All data by tags... Sophox
#
def getGenericTagsQuery( center, location_name, l, tag_cat, tags, query_label ):
    r = l * 0.5
    lon_lat = str(center[1])+" "+str(center[0])
    q1='''
SELECT ?osmid ?distance ?loc ?tag WHERE {
  ___VALUES___
  ?osmid osmt:___tag_cat___ ?tag . 
  SERVICE wikibase:around { 
      ?osmid osmm:loc ?loc . 
      bd:serviceParam wikibase:center "Point(___lon_lat___)"^^geo:wktLiteral . 
      bd:serviceParam wikibase:radius "15" . 
      bd:serviceParam wikibase:distance ?distance .
  } 
  FILTER(?distance < 15)
} 
    '''

    if tags is None:
        tagsLine = ""
    else:
        tagsLine = "VALUES ?tag { ___tags___ }".replace("___tag_cat___",tag_cat).replace("___tags___" , tags)

    query = q1.replace("___lon_lat___", lon_lat)
    query = query.replace("___VALUES___", tagsLine)
    query = query.replace("___tag_cat___", tag_cat)

    title = query_label + ' around ('+location_name+') radius='+str(r)

    qn = location_name + "_r" + str(r) + "_" + query_label

    return query, title, qn


#
# All data ... Overpass
#
def _getAllTagsQuery( bb, location_name, l, area=None ):
    if area is None:
        area = ""
    title = 'all nodes around ('+location_name+') l='+str(l)
    query = '[out:json];'+area+'(node[~"."~"."]' + bb +");"+area+'(way[~"."~"."]' + bb +");"+area+'(relation[~"."~"."]' + bb +");out body;"
    qn = location_name + "_" + str(l) + "_all"
    return query, title, qn

def _getFilteredTagsQuery( bb, location_name, l, area=None, filterString='~"."~"."', filterTag="all" ):
    if area is None:
        area = ""
    title = 'nodes around ('+location_name+')[l='+str(l)+', filter='+filterTag+']'
    query = '[out:json];'+area+'(node['+ filterString +']' + bb +");"+area+'(way['+ filterString +']' + bb +");"+area+'(relation['+ filterString +']' + bb +");out body;"
    #query = '[out:json];'+area+'(node['+ filterString +']' + bb +");out body;"
    qn = location_name + "_" + str(l) + "_" + filterTag
    return query, title, qn

#
# Ways and relations are ignored in this case ...
#
def getAllNodesQuery( bb, location_name, l, area=None ):
    if area is None:
        area = ""
    else:
        bb = "(area)"
    title = 'all nodes around ('+location_name+') l='+str(l)
    query = '[out:json];'+area+'(node[~"."~"."]' + bb +";);out body;"
    qn = location_name + "_" + str(l) + "_all"
    return query, title, qn

def getFilteredNodesQuery( bb, location_name, l, area=None, filterString='~"."~"."', filterTag="all" ):
    if area is None:
        area = ""
    else:
        bb = "(area)"
    title = 'nodes around ('+location_name+')[l='+str(l)+', filter='+filterTag+']'
    query = '[out:json];'+area+'(node['+ filterString +']' + bb +";);out body;"
    qn = location_name + "_" + str(l) + "_" + filterTag
    return query, title, qn

#def getTaggedNodesQuery( bb, location_name, l, tag ):
#    title = 'nodes with TAG['+tag+'] around <'+location_name+'> l='+str(l)
#    return '[out:json]; node[' + tag + ']' + bb,title


#class LayerSpecification(zoom=9, center=(54.613253,13.354836), l=0.3, location_name="Breege"):

class LayerSpecification:

    def getState(self):

        layerState = {}

        layerState['location_name'] = self.location_name
        layerState['run_id'] = self.run_id
        layerState['center'] = self.center
        layerState['centerURI'] = self.center_uri
        layerState['myBBCenter_h3index'] = self.myBBCenter_h3index
        layerState['bb'] = self.bb
        layerState['area'] = self.area
        layerState['l'] = self.l
        layerState['zoom'] = self.zoom
        layerState['title'] = self.title
        layerState['qn'] = self.qn
        layerState['query'] = self.query
        layerState['fnLinks'] = self.fnLinks
        layerState['fnPlaces'] = self.fnPlaces
        layerState['fnGrid'] = self.fnGrid
        layerState['fnRawOSMResponse'] = self.fnRawOSMResponse
        layerState['fnRawSophoxResponse'] = self.fnRawSophoxResponse
        layerState['fnMD'] = self.fnMD
        layerState['weight'] = self.layerWeight
        layerState['label'] = self.layerLabel

        return layerState

    def toJSON(self):
        layerState = self.getState()
        return json.dumps(layerState, default=lambda o: o.__dict__, sort_keys=False, indent=4)


    def __init__(self, location_name="Breege", zoom=9, l=0.3, fileName=None, center=None, URI=None, area=None, fromLayer = False  ):

        # given ...

        self.zoom = zoom
        self.area = area
        self.l = l
        self.center = None
        self.location_name = location_name
        self.filename = fileName
        self.center_uri = URI
        self.fnRawSophoxResponse = None
        self.layerWeight = None
        self.layerLabel = None
        self.data_workspace = "graph_layers/"

        if fromLayer:
            self.location_name = location_name
            return
        elif fileName==None and URI==None and center==None and area==None:
            self.location_name = location_name
            self.initFromOverpassAPI()
            return
        elif fileName is not None:
            self.initFromMDFile( fileName )
            return

        if (area is not None):
            self.area = area
            self.location_name = "by_area_code"
            self.bb="(area);"

            self.center = (0,0)
            self.center_uri = "NO CENTER COORDINATES KNOWN"
            self.initFromOverpassAPI()
            return

        if (area is None) and (URI is not None) and (center is not None):
            locName = URI
            self.location_name = locName.replace('/',"_").replace(':',"_")
            self.center = center
            self.center_uri = URI
            self.initFromOverpassAPI()
            return
        else:
            raise ValueError('Without an area code we need the URI AND the center coordinates to create the Layer')

        self.setFolderNames()

    #
    #try:
    #  some_code_that_may_raise_our_value_error()
    #except ValueError as err:
    #  print(err.args)
    #


    def initFromMDFile(self, mdFileName):
        f = open( mdFileName, "r")
        dataRaw = json.load(f)
        f.close()

        #
        #
        #
        try:
            data = dataRaw[0]
            print(  )
            print( ">>> Multi-Layer processing is under construction ... works from generator, not yet from loader.")
            print( f">   Used only the first available layer in {mdFileName}! ")
            print( f">   Ignored {len(dataRaw)-1} layers in {mdFileName}")
        except:
            data = dataRaw

        self.location_name = data['location_name']
        self.zoom = data['zoom']
        self.l = data['l']

        self.center = data['center']
        self.center_uri = data['centerURI']
        self.bb = data['bb']
        self.run_id = data['run_id']
        self.area = data['area']

        self.myBBCenter_h3index = data['myBBCenter_h3index']

        self.query = data['query']
        self.title = data['title']
        self.qn = data['title']

        self.fnLinks = data['fnLinks']
        self.fnPlaces = data['fnPlaces']

        try:
          self.fnGrid = data['fnGrid']
        except KeyError:
            self.fnGrid = self.data_workspace + self.qn + "_grid"

        self.fnRawOSMResponse = data['fnRawOSMResponse']
        self.fnRawSophoxResponse = data['fnRawSophoxResponse']

        self.fnMD = data['fnMD']

        self.layerLabel = data['label']
        self.layerWeight = data['weight']

        self.jsonData = {}
        self.X = None

    def initFromLayer(self, data):

        self.location_name = data['location_name']
        self.zoom = data['zoom']
        self.l = data['l']

        self.center = data['center']
        self.center_uri = data['centerURI']
        self.bb = data['bb']
        self.run_id = data['run_id']
        self.area = data['area']

        self.myBBCenter_h3index = data['myBBCenter_h3index']

        self.query = data['query']
        self.title = data['title']
        self.qn = data['title']

        self.fnLinks = data['fnLinks']
        self.fnPlaces = data['fnPlaces']
        self.fnGrid = data['fnGrid']

        self.fnRawOSMResponse = data['fnRawOSMResponse']
        self.fnRawSophoxResponse = data['fnRawSophoxResponse']

        self.fnMD = data['fnMD']

        self.layerLabel = data['label']
        self.layerWeight = data['weight']

        self.jsonData = {}
        self.X = None



    def initFromOverpassAPI(self):

        print( "*** Initialize layer via OverPass API or from center point ...")
        self.myBBCenter_h3index=0

        if self.center==None and self.area==None:

            lat = None
            lon = None
            self.myBBCenter_h3index  = None
            q  = None
            r = None

            print(self.location_name)

            if  self.location_name.startswith("Point(") :
                print("##**##**##**")
                lat, lon, self.myBBCenter_h3index, q, r = gqh3.getLocationCoordinatesAndH3IndexFromPoint( self.location_name, self.zoom )
            else:
                print("##**____##**")
                lat, lon, self.myBBCenter_h3index, q, r = gqh3.getLocationCoordinatesAndH3Index( self.location_name, self.zoom )

            self.center = (lat,lon)
            print( self.center )
            self.myBBCenter_h3index = gqh3.h3Index_lat_lon_level_NO_LABEL( lat, lon, self.zoom )
            self.bb = calculateBoundingBox(self.center, self.l)

        if self.area is not None and self.area!="":
            self.bb = "(area);"

        if self.center is not None:
            lat = self.center[0]
            lon = self.center[1]
            self.myBBCenter_h3index = gqh3.h3Index_lat_lon_level_NO_LABEL( lat, lon, self.zoom )
            self.bb = calculateBoundingBox(self.center, self.l)

        self.run_id = getRunId( "du", self. location_name, "latest", bbl=str(self.l), h3=self.myBBCenter_h3index)

        #self.query, self.title, self.qn = getAllTagsQuery( self.bb, self.location_name, self.l, self.area )
        self.query, self.title, self.qn = getAllNodesQuery( self.bb, self.location_name, self.l, self.area )

        self.fnLinks = self.data_workspace + self.qn + "_tag_links.csv"
        self.fnPlaces = self.data_workspace + self.qn + "_places_nodes.csv"
        self.fnGrid = self.data_workspace + self.qn + "_grid"

        self.fnRawOSMResponse = self.data_workspace + self.qn + "_raw_osm.json"
        self.fnRawOSMResponse = self.data_workspace + self.qn + "_raw_osm.json"

        self.fnMD = self.data_workspace + "md" + self.qn + ".json"

        self.jsonData = {}
        self.X = None

    def setSelectionFilter(self, filterString='~"."~"."', filterTag="all" ):
        self.query, self.title, self.qn = getFilteredNodesQuery( self.bb, self.location_name, self.l, self.area, filterString, filterTag )
        #self.query, self.title, self.qn = getFilteredTagsQuery( self.bb, self.location_name, self.l, self.area, filterString, filterTag )

    def getQuery(self):
        return self.query, self.title, self.qn

    def getJSONDataFromWeb(self, path_offset):
        return gqplots.reloadOrDumpNamedQueryAsJSON( self.query, self.qn, self.title, path_offset, self.fnRawOSMResponse, forceReload=True )

    def getJSONData(self, path_offset, forceReload=True):
        return gqplots.reloadOrDumpNamedQueryAsJSON( self.query, self.qn, self.title, path_offset, self.fnRawOSMResponse, forceReload=True )

    def plotLayerData(self, path_offset):
        self.jsonData = self.getJSONData(path_offset)
        self.coords = gqplots.plotNamedQuery( self.jsonData, self.qn, self.title, path_offset=path_offset )
        return self.coords

    def persistDataFrames(self, path_offset):

        print( "*#-> 0")
        self.links, self.tag_counts = gqh3.getLinks_and_Counters( coords_WithTags = self.coords, resolution=self.zoom )
        #print(self.links )
        #print(self.tag_counts )

        print( "*#-> 1 - START")
        print( path_offset )
        h3places_nodes = gqosm.nodes_to_DF( self.coords , self.fnPlaces, path_offset, resolution=self.zoom )
        print( "*#-> 1 - END")


        #
        # expand the H3 area to lower level resolution ...
        #
        #zoom_in_levels = 2
        #h3places_nodes["h3index_grid_places"] = h3places_nodes.apply( lambda x : gqh3.get_listOfIndexes_zoom_in_N( x["h3index"], zoom_in_levels ), axis = 1 )
        #h3places_nodes["h3index_grid_res"] = self.zoom + zoom_in_levels
        #h3places_nodes["layer_id"] = self.qn

        #print( h3places_nodes )

        #h3places_nodes = h3places_nodes.explode('h3index_grid_places').reset_index(drop=True)
        #h3places_nodes["h3index_grid_neighbors"] = h3places_nodes.apply( lambda x : gqh3.get_listOfIndexes_zoom_in_N_neighbors( x["h3index"], zoom_in_levels ), axis = 1 )
        #h3places_nodes = h3places_nodes.explode('h3index_grid_neighbors').reset_index(drop=True)

        #firstLevelNodes = h3places_nodes["h3index"].drop_duplicates()
        #secondLevelNodes = h3places_nodes["h3index_grid_places"].drop_duplicates()
        #thirdLevelNodes = h3places_nodes["h3index_grid_neighbors"].drop_duplicates()

        #firstLevelNodes  = firstLevelNodes.rename( index=str, column={ 'from_id':'h3index'},inplace=True)
        #secondLevelNodes = secondLevelNodes.rename( index=str, column={ 'h3index_grid_places':'h3index'},inplace=True)
        #thirdLevelNodes  = thirdLevelNodes.rename( index=str, column={ 'h3index_grid_neighbors':'h3index'},inplace=True)

        #firstLevelNodes.to_csv( path_offset + self.fnGrid + "_1_NODES.csv", index=False)
        #secondLevelNodes.to_csv( path_offset + self.fnGrid + "_2_NODES.csv", index=False)
        #thirdLevelNodes.to_csv( path_offset + self.fnGrid + "_3_NODES.csv", index=False)


        print( "*#-> 2 - START")

        gqosm.links_to_DF( self.links, self.fnLinks, path_offset, layer_id=self.qn )

        print( "*#-> 2 - END")

        #print( "*#-> 3")

        #df1 = pd.DataFrame(data=firstLevelNodes, columns=['h3index'])
        #df2 = pd.DataFrame(data=secondLevelNodes, columns=['h3index'])
        #df3 = pd.DataFrame(data=thirdLevelNodes, columns=['h3index'])

        #frames = [ df1, df2 ]
        #allGridNodes = pd.concat(frames)

        #allGridNodes = allGridNodes.drop_duplicates()

        #df1 = pd.DataFrame(data=allGridNodes, columns=['h3index'])
        #print(type(allGridNodes))

        #df1.to_csv( path_offset + self.fnGrid + "_NODES.csv", index=False)

        #h3places_nodes.to_csv( path_offset + self.fnGrid + "_GRID_NODES.csv", index=False)

        #print( "*#-> 4")



#
# Here is a dependency to SELENIUM WebDriver ... we try to avoid this for now. (1.3.2022)
#
    '''
    def showHexagonMap(self, path_offset):

        m = gqplots.visualize_hexagons(self.tag_counts, self.zoom)

        img_data = m._to_png(5)
        img = Image.open(io.BytesIO(img_data))
        img.save( path_offset + '/heximage.png')
    '''

    ''''''
    def dumpLayerMD( self, path_offset, verbose=False ):
        MDFN = path_offset + "/" + self.fnMD
        f = open( MDFN, "w")
        f.write( self.toJSON() )
        if verbose:
            print( F">>> MD Filename: {MDFN}")
            print( self.toJSON() )
        f.close()

    def dumpLayerMD2( self, path_offset, verbose=False ):
        MDFN = path_offset + "/" + self.fnMD
        f = open( MDFN, "a")
        f.write( self.toJSON() )
        if verbose:
            print( F">>> MD Filename: {MDFN}")
            print( self.toJSON() )
        f.close()

    def stageLayerDataInTigerGraph(self, path_offset, conn):

        print(">>> Places: "+path_offset + self.fnPlaces)
        places = pd.read_csv(path_offset + self.fnPlaces)
        expected_type = "h3place"
        places ['latCell'] = places.apply( lambda x : gqh3.lat_lon_from_h3Index2( x["h3index"] )[0], axis = 1 )
        places ['lonCell'] = places.apply( lambda x : gqh3.lat_lon_from_h3Index2( x["h3index"] )[1], axis = 1 )


#
        #  only h3Places are loaded ... OSM-tags are added to the h3Place!!!
        #
        zN1 = conn.upsertVertexDataFrame(
            df=places, vertexType='h3place', v_id='h3index',
            attributes={'resolution':'res','lat':'latCell','lon':'lonCell' })

        zN2 = conn.upsertVertexDataFrame(
            df=places, vertexType='osmplace', v_id='osmid',
            attributes={ 'lat':'lat','lon':'lon'})

        print(">>> Links : "+path_offset + self.fnLinks)
        tagLinks = pd.read_csv( path_offset + self.fnLinks )


        #
        #  only edges are loaded...
        #
        zE1 = conn.upsertEdgeDataFrame(
          df=tagLinks,
          sourceVertexType='osmtag',
          edgeType='hasOSMTag',
          targetVertexType='h3place',
          from_id='osmtag',
          to_id='h3index',
          attributes={'tagCount':'z', 'layer_id':'layer_id'} )

        places['layer_id'] = self.qn

        zE2 = conn.upsertEdgeDataFrame(
            df=places,
            sourceVertexType='osmplace',
            edgeType='located_on_h3_cell',
            targetVertexType='h3place',
            from_id='osmid',
            to_id='h3index',
            attributes={ 'layer_id':'layer_id' } )


        print( "UPLOAD STATS: " + str( zN1 ) + " - " + str( zN2 ) + " nodes, " + str(zE1) + " - " + str( zE2 ) + " edges. " )

        gqosm.verifyNodeAndLinks( places , tagLinks, True )




    def stageLayerDataInKafkaTopic(self, path_offset = ".", topic_name = "OSM_nodes_stage" ):

        data = self.getJSONData( path_offset );

        kdata = {}
        kdata['location_name'] = self.location_name
        kdata['query'] = self.query
        kdata['run_id'] = self.run_id

        json_kdata = json.dumps(kdata)

        vdata = {}
        vdata['location_name'] = self.location_name
        vdata['query'] = self.query
        vdata['z'] = len(data)
        vdata['json_data'] = data
        vdata['md'] = self.toJSON()

        json_vdata = json.dumps(vdata)

        print( self )
        print( ">>> Uploaded to Kafka topic ... " + topic_name )

        # gqk.producer.produce( topic_name, key=json_kdata, value=json_vdata )
        # gqk.producer.flush()

    def setLayerWeight(self, weight ):
        self.layerWeight = weight

    def setLayerLabel(self, label ):
        self.layerLabel = label

    def setFolderNames( self ):

        self.fnMD = "md/" + self.qn + "_MD.json"
        self.fnRawOSMResponse = "raw/" + self.qn + "_raw_osm.json"
        self.fnRawSophoxResponse = None

        self.fnLinks = self.data_workspace + "edges/" + self.qn + "_tag_links.csv"
        self.fnPlaces = self.data_workspace + "vertexes/" + self.qn + "_places_nodes.csv"
        self.fnGrid = self.data_workspace+ "grid/" + self.qn + "_grid.csv"

        print( ">>> Will use the following folders: ")
        print( f">>> {self.fnLinks} ")
        print( f">>> {self.fnPlaces} ")
        print( f">>> {self.fnGrid} ")
        print( f">>> {self.fnRawOSMResponse} ")
        print( f">>> {self.fnRawSophoxResponse} ")





class SophoxLayer(LayerSpecification):


    def setFolderNames( self ):

        self.fnMD = "md/" + self.qn + "_MD.json"
        self.fnRawOSMResponse = None
        self.fnRawSophoxResponse = "raw/" + self.qn + "_raw_sophox.json"

        self.fnLinks = self.data_workspace + "edges/" + self.qn + "_tag_links.csv"
        self.fnPlaces = self.data_workspace + "vertexes/" + self.qn + "_places_nodes.csv"
        self.fnGrid = self.data_workspace+ "grid/" + self.qn + "_grid.csv"

        print( ">>> Will use the following folders: ")
        print( f">>> {self.fnLinks} ")
        print( f">>> {self.fnPlaces} ")
        print( f">>> {self.fnGrid} ")
        print( f">>> {self.fnRawOSMResponse} ")
        print( f">>> {self.fnRawSophoxResponse} ")



    def setAllTagQuery(self, query_label = "AllTags"):
        self.query, self.title, self.qn = getAllTagsQuery( self.center, self.location_name, self.l, query_label )
        self.setFolderNames()


    def setSelectionFilter(self, query_label = "LABEL", tag_cat = "amenity", tags='"kindergarten"' ):
        #self.query, self.title, self.qn = getAmenityTagsQuery( self.center, self.location_name, self.l, amenity_tags, query_label )
        self.query, self.title, self.qn = getGenericTagsQuery( self.center, self.location_name, self.l, tag_cat, tags, query_label )
        self.setFolderNames()

    def getJSONData(self, path_offset, forceReload=True, dryRun = False ):
        print("#*#*#")
        return gqsophox.reloadOrDumpNamedQueryAsJSON( self.query, self.qn, self.title, path_offset, self.fnRawSophoxResponse, forceReload, dryRun = dryRun)

    def plotLayerData(self, path_offset, dryRun = False ):

        self.jsonData, fn = self.getJSONData(path_offset, forceReload=False, dryRun = False )

        print( "*** " + fn )

        coords = self.getTagCoordsFromJSON( fn, dryRun = False, verbose = False )
        z = len( coords )

        print( f"*** Ready to plot {z} coordintates in a layer. " )

        image_path_offset = path_offset + "/single_layer_images"
        self.coords, self.X = gqplots.plotCoordinatesForNamedQuery( coords, self.qn, self.title, image_path_offset )

        return self.coords

    def getCoordinates_X(self):
        return self.X

    def getTagCoordsFromJSON( self, fn, dryRun = False, verbose = False ):

        coords = []

        if dryRun:
            print( "*** DRYRUN-MODE: SKIP Loading JSON data from FILENAME: " + fn )
            return coords

        print( "*** Load JSON data from FILENAME: " + fn )

        f = open( fn )
        data = json.load( f )

        print( ">>> DATA: <<<"  )
        print( len(data) )
        print( "###***^^^")

        if verbose:
            print( data )
            print( len(data) )

        for record in data:
            #print( record )
            #print( len(record) )
            #print( type(record) )
            p = record['loc']
            if p is not None:
                z=len(p)
                #print( type(p) )
                point = p[6:z-1]
                co = point.split(" ")
                tag = record['tag']
                osmid = record['osmid']
                # amenity = record['amenity']
                lon = co[0]
                lat = co[1]
                tags = []
                tags.append( tag )
                coords.append( ( float(lon), float(lat), tags, osmid) )

        #print( coords )
        return coords

    def printQueryStack(self, file ):
        file.write( "#\n# " + self.qn + "\n#\n")
        file.write( "#defaultView:Map" )
        file.write( self.query )
        file.write( "\n\n" )
        file.flush()



class MultiSophoxLayer(SophoxLayer):

    def addQueryToStack( self, key, query ):
        self.queriesAll[key] = query

    def initFromSophosLayer(self, sophosLayer, path_offset, dryRun = True ):
        l1 = copy.deepcopy(sophosLayer)
        super().initFromLayer( l1.getState() )

        self.coordsAll = []
        self.queriesAll = {}

        data, fn = self.getJSONData( path_offset, dryRun )

        self.addTagCoords( sophosLayer.getTagCoordsFromJSON( fn ) )
        self.addQueryToStack( sophosLayer.qn, sophosLayer.query )

    def addSheet( self, sheet, path_offset ):
        temp = copy.deepcopy(sheet)
        data, fn = temp.getJSONData( path_offset, forceReload=False )
        self.addTagCoords( sheet.getTagCoordsFromJSON( fn ) )
        self.addQueryToStack( sheet.qn, sheet.query )

    def addTagCoords( self , coords ):
        for co in coords:
            self.coordsAll.append( co )

    def getTagCoordsFromJSON( self ):
        return self.coordsAll

    def plotMultiLayerData(self, path_offset):
        print( "Nr of coordinates to plot:" , str(len( self.coordsAll )) )
        image_path_offset = path_offset + "/multi_layer_images"
        self.coords, self.X = gqplots.plotCoordinatesForNamedQuery( self.coordsAll, self.qn, self.title, path_offset=image_path_offset )
        return self.coords

    def printQueryStack(self, file ):
        for q in self.queriesAll:
            qq = self.queriesAll[q]
            print( "# " + q + "\n#")
            print( "#defaultView:Map\n#" )
            print( qq )
            file.write( "#\n# " + q + "\n#\n")
            file.write( "#defaultView:Map" )
            file.write( qq )
            file.write( "\n\n" )
        file.flush()


