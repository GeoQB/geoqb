import osmium as osm
import pandas as pd
import geoanalysis.geoqb.geoqb_h3 as gqh3
import time
import json
import overpass
import os

# import geoanalysis.geoqb.geoqb_kafka as gqk

overPass_URL1=os.environ.get('overpass_endpoint')

class OSMHandler(osm.SimpleHandler):

    def __init__(self):
        osm.SimpleHandler.__init__(self)
        self.osm_data = []

    def tag_inventory(self, elem, elem_type):
        for tag in elem.tags:
            self.osm_data.append([elem_type,
                                   elem.id,
                                   elem.version,
                                   elem.visible,
                                   pd.Timestamp(elem.timestamp),
                                   elem.uid,
                                   elem.user,
                                   elem.changeset,
                                   len(elem.tags),
                                   tag.k,
                                   tag.v,
                                   elem.location])

    def node(self, n):
        self.tag_inventory(n, "node")

    def way(self, w):
        self.tag_inventory_way(w, "way")

    def relation(self, r):
        self.tag_inventory(r, "relation")



#
# Relations DF
#
class OSMHandlerRelation2(osm.SimpleHandler):

    def __init__(self):
        osm.SimpleHandler.__init__(self)
        self.osm_data = []

    def tag_inventory(self, elem, elem_type):
        nodes = [node.ref for node in elem.members]
        for tag in elem.tags:
            self.osm_data.append([elem_type,
                                   elem.id,
                                   elem.version,
                                   elem.visible,
                                   pd.Timestamp(elem.timestamp),
                                   elem.uid,
                                   elem.user,
                                   elem.changeset,
                                   len(elem.tags),
                                   tag.k,
                                   tag.v,
                                   len(elem.members),
                                   nodes
                                  ])

    def node(self, n):
        self.tag_inventory(n, "node")

    def way(self, w):
        self.tag_inventory(w, "way")

    def relation(self, r):
        self.tag_inventory(r, "relation")



#
# Nodes DF : from persisted XML file
#
def keep_osm_data_n( fn_n ):
  osmhandler = OSMHandler()
  # scan the input file and fills the handler list accordingly
  osmhandler.apply_file( fn_n )

  # transform the list into a pandas DataFrame
  data_colnames = ['type', 'id', 'version', 'visible', 'ts', 'uid',
                  'user', 'chgset', 'ntags', 'tagkey', 'tagvalue', 'location']

  df_osm = pd.DataFrame(osmhandler.osm_data, columns=data_colnames)
  df_osm = df_osm.sort_values(by=['type', 'id', 'ts'])
  df_osm['lat'] = df_osm['location'].apply( lambda x: x.lat )
  df_osm['lon'] = df_osm['location'].apply( lambda x: x.lon )
  df_osm['h3'] = df_osm['location'].apply( gqh3.h3Index)
  #print( df_osm )
  #print( df_osm.iloc[0])
  return df_osm

#
# Relations DF : from persisted XML file
#
def keep_osm_data_r( fn_r ):

  osmhandler = OSMHandlerRelation2()
  # scan the input file and fills the handler list accordingly
  osmhandler.apply_file( fn_r )
  # transform the list into a pandas DataFrame
  data_colnames = ['type', 'id', 'version', 'visible', 'ts', 'uid',
                  'user', 'chgset', 'ntags', 'tagkey', 'tagvalue', 'nmembers','members']

  df_osm = pd.DataFrame(osmhandler.osm_data, columns=data_colnames)
  df_osm = df_osm.sort_values(by=['type', 'nmembers', 'id', 'ts'],ascending=False)

  #print( df_osm )
  #print( df_osm.iloc[0])
  return df_osm



class OSMHandlerRel(osm.SimpleHandler):

    def __init__(self):
        osm.SimpleHandler.__init__(self)
        self.osm_data = []

    def tag_inventory(self, elem, elem_type):
        nodes = [node.ref for node in elem.members]
        for tag in elem.tags:
            #print( elem )
            self.osm_data.append([elem_type,
                                   elem.id,
                                   elem.version,
                                   elem.visible,
                                   pd.Timestamp(elem.timestamp),
                                   elem.uid,
                                   elem.user,
                                   elem.changeset,
                                   len(elem.tags),
                                   tag.k,
                                   tag.v,
                                   len(elem.members),
                                   nodes
                                  ])

    def node(self, n):
        self.tag_inventory(n, "node")

    def way(self, w):
        self.tag_inventory(w, "way")

    def relation(self, r):
        self.tag_inventory(r, "relation")

def keep_osm_data_r( fn_r ):

  osmhandler = OSMHandlerRel()
  # scan the input file and fills the handler list accordingly
  osmhandler.apply_file( fn_r )

  # transform the list into a pandas DataFrame
  data_colnames = ['type', 'id', 'version', 'visible', 'ts', 'uid',
                  'user', 'chgset', 'ntags', 'tagkey', 'tagvalue','nmembers','allmembers']

  df_osm = pd.DataFrame(osmhandler.osm_data, columns=data_colnames)
  df_osm = df_osm.sort_values(by=['type', 'id', 'ts'])
  #print( df_osm )
  #print( df_osm.iloc[0])
  return df_osm


class OSMHandlerWay(osm.SimpleHandler):

    def __init__(self):
        osm.SimpleHandler.__init__(self)
        self.osm_data = []

    def tag_inventory(self, elem, elem_type):
        nodes = [node.ref for node in elem.nodes]
        for tag in elem.tags:
            self.osm_data.append([elem_type,
                                   elem.id,
                                   elem.version,
                                   elem.visible,
                                   pd.Timestamp(elem.timestamp),
                                   elem.uid,
                                   elem.user,
                                   elem.changeset,
                                   len(elem.tags),
                                   tag.k,
                                   tag.v,
                                   len(elem.nodes),
                                   nodes
                                  ])

    def node(self, n):
        self.tag_inventory(n, "node")

    def way(self, w):
        self.tag_inventory(w, "way")

    def relation(self, r):
        self.tag_inventory(r, "relation")

def keep_osm_data_w( fn_w ):
  osmhandler = OSMHandlerWay()
  # scan the input file and fills the handler list accordingly
  osmhandler.apply_file( fn_w )

  # transform the list into a pandas DataFrame
  data_colnames = ['type', 'id', 'version', 'visible', 'ts', 'uid',
                  'user', 'chgset', 'ntags', 'tagkey', 'tagvalue', 'nnodes', 'allnodes' ]

  df_osm = pd.DataFrame(osmhandler.osm_data, columns=data_colnames)
  df_osm = df_osm.sort_values(by=['type', 'nnodes', 'id', 'ts'])
  #print( df_osm )
  #print( df_osm.iloc[0])
  return df_osm


def dumpPOIsIntoXMLandKafka(location_name, l, ts, run_id, zoom, topicQMD, path_offset):

  lat, lon, myBBCenter_h3index, q, r = gqh3.getLocationCoordinatesAndH3Index( location_name, zoom)
  center = (lat,lon)

  print("=================================================================" )
  print( run_id )
  print("-----------------------------------------------------------------" )
  print()

  time.sleep(3)

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
  bb  = '[~"."~"."](' + tl + ', ' + br + ');'
  bbs = '(' + tl + ', ' + br + ');'
  print( "bounding box: " + bb  )
  print( "bb={" + bb + "}" )
  print( "c_lat=" + str(center[0]) )
  print( "c_lon=" + str(center[1]) )
  print( "bb_w=" + str(w) )
  print( "bb_h=" + str(h) )

  kdata = {}
  kdata['runId'] = run_id
  kdata['query'] = bb
  json_kdata = json.dumps(kdata)

  vdata = {}
  vdata['runId'] = run_id

  # https://wiki.openstreetmap.org/wiki/Overpass_API

  #
  # Alternative way to access the OverPass API
  # https://janakiev.com/blog/openstreetmap-with-python-and-overpass-api/
  #
  api1 = overpass.API(endpoint=os.environ.get('overpass_endpoint'))
  query = 'node' + bb
  node_data = api1.get( query, responseformat="xml")
  vdata['query'] = query
  vdata['z'] = len(node_data)
  json_vdata = json.dumps(vdata)
  gqk.producer.produce(topicQMD, key=json_kdata, value=json_vdata )
  print( len(node_data) )
  #
  # files go into folder /content ...
  #
  fn_n = path_offset + run_id + "_node_data.xml"
  file = open( fn_n,'w' )
  file.write( node_data )
  file.close()

  #keep_osm_data_n( fn_n )

  time.sleep(2)

  api2 = overpass.API(endpoint=os.environ.get('overpass_endpoint'))
  query = 'way' + bb
  way_data = api2.get( query, responseformat="xml")
  vdata['query'] = query
  vdata['z'] = len(way_data)
  json_vdata = json.dumps(vdata)
  gqk.producer.produce(topicQMD, key=json_kdata, value=json_vdata )
  print( len(way_data) )
  #
  # files go into folder /content ...
  #
  fn_w = path_offset + run_id + "_way_data.xml"
  file = open(fn_w,'w')
  file.write( way_data )
  file.close()

  #keep_osm_data_w( fn_w )

  time.sleep(2)


  api3 = overpass.API(endpoint=os.environ.get('overpass_endpoint'))
  query = 'relation' + bb
  relation_data = api3.get( query, responseformat="xml")
  vdata['query'] = query
  vdata['z'] = len(relation_data)
  json_vdata = json.dumps(vdata)
  gqk.producer.produce(topicQMD, key=json_kdata, value=json_vdata )
  print( len(relation_data) )
  #
  # files go into folder /content ...
  #
  fn_r = path_offset + run_id + "_relation_data.xml"
  file = open( fn_r ,'w')
  file.write( relation_data )
  file.close()

  #keep_osm_data_r( fn_r )

  time.sleep(2)




def links_to_DF( links, fn, path_offset, layer_id ):

  print( type(links) )
  print( len(links))

  links2=[]

  for l in links:
    #print( l, links[l] )
    links2.append( (l[0],l[1],links[l],layer_id) )

  linksDF = pd.DataFrame.from_records(links2, columns=['h3index', 'osmtag', 'z', 'layer_id'])

  linksDF.to_csv( path_offset + fn, index=False)


import pandas as pd

def nodes_to_DF( X, fn, path_offset, resolution ):

  #print( type(X) )
  #print( len(X) )
  #print( X )

  df = pd.DataFrame(X, columns = ["lon","lat","tags","osmid"])

  df["h3index"] = df.apply( lambda x : gqh3.h3Index_lat_lon_level_NO_LABEL( x["lat"], x["lon"], resolution ), axis = 1 )
  df["res"] = resolution

  print(df)
  #print(type(df))
  #print(df.columns)

  df = df[["h3index","res","lat","lon","osmid" ]]
  df.to_csv( path_offset + fn, index=False)
  return df





def verifyNodeAndLinks( dfNodes, dfTagLinks, verbose=False ):

  dfNodes = dfNodes.drop_duplicates(subset=['h3index'])
  index = dfNodes.index
  number_of_rows = len(index)

  index1 = dfTagLinks.index
  number_of_rows1 = len(index1)


  dfDS = pd.merge(dfNodes,dfTagLinks,left_on='h3index',right_on='h3index')
  #dfDS = dfNodes.join(dfTagLinks.set_index('h3index'), on='h3index', lsuffix='_nodes_h3_index', rsuffix='_tags_h3_index')
  dfDS.dropna(subset = ["osmtag"], inplace=True)

  if verbose:
    print("**** JOINED ****")
    dfDS.describe()
    dfDS.info()
    print( dfDS )
    print()

    print("**** NODES ****")
    dfNodes.describe()
    dfNodes.info()
    print( dfNodes )
    print()

    print("**** TAGS ****")
    dfTagLinks.describe()
    dfTagLinks.info()
    print( dfTagLinks )
    print()

  index2 = dfDS.index
  number_of_rows2 = len(index2)

  print( "Nodes   :" + str( number_of_rows ) )
  print( "OSMTags :" + str( number_of_rows1 ) )
  print( "MERGED  :" + str( number_of_rows2 ) )
