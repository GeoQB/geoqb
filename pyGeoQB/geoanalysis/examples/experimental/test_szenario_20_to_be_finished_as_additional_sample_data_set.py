#####
#
# This GeoQB demo script uses the Overpass API to read geo facts from OpenStreetmap servers.
# This data will be pushed into the Kafka based dataplane where it is forwareded to the staging area in TigerGraph.
#
# - incremental load into staging area
#

import sys
sys.path.append('../../../')

import os

import geoanalysis.geoqb.geoqb_plots as gqplots

import geoanalysis.geoqb.geoqb_h3 as gqh3

import geoanalysis.geoqb.geoqb_kafka as gqk

import geoanalysis.geoqb.geoqb_osm_pandas as gqosm

import geoanalysis.geoqb.geoqb_tg as gqtg







from datetime import datetime

#
# The timestamp is used in all asset names so that we can implicitely find out what belongs to a single study.
# It can also be changed to a logical version number.
#
timestamp = datetime.now()

print("timestamp =", timestamp)
print("type(timestamp) =", type(timestamp))

user="mirko"

# for individual experiments we need a single location name.
location_name="Stollberg"

# We persist metadata in Kafka topics in Confluent Cloud
topic = "OSM_nodes_stage"
topicQMD = "QMD_OSM_nodes_stage"

# Extracted data will be stored in this mounted Google Drive folder:
path_offset = "./workspace/"

zoom = 6

#
# The run_id becomes part of the filenames of all BLOBS created in an analysis
#
def getRunId( user, location_name, time, bbl='default', h3="h3:undefined"):
  run_id=user + "___" + location_name+ "___" + bbl + "___" + h3 + "___" + time
  return run_id

# this is the run_id for the ad-hoc activities in this workbook
run_id = getRunId( user, location_name, str(timestamp))
print( run_id )

import pandas as pd

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.ndimage.filters import gaussian_filter

import requests
import json

overpass_url = "http://overpass-api.de/api/interpreter"

#
# A set of named queries
#
nq = {}
title = {}

overpass_query_1 = """
[out:json];
area["ISO3166-1"="DE"][admin_level=2];
(node["amenity"="biergarten"](area);
 way["amenity"="biergarten"](area);
 rel["amenity"="biergarten"](area);
);
out center;
"""

overpass_query_2 = """
[out:json];
area["ISO3166-1"="DE"][admin_level=2];
(node["historic"](area);
 way["historic"](area);
 rel["historic"](area);
);
out center;
"""

overpass_query_3 = """
[out:json];
area["ISO3166-1"="DE"][admin_level=2];
(node["water"](area);
 way["water"](area);
 rel["water"](area);
);
out center;
"""

overpass_query_4 = """
[out:json];
area["ISO3166-1"="DE"][admin_level=2];
(node["amenity"="atm"](area);
 way["amenity"="atm"](area);
 rel["amenity"="atm"](area);
);
out center;
"""

nq['q1'] = overpass_query_1
title['q1'] = 'Biergarten in Germany'

nq['q2'] = overpass_query_2
title['q2'] = 'Historische Orte in Germany'

nq['q3'] = overpass_query_3
title['q3'] = 'Wasser in Germany'

nq['q4'] = overpass_query_4
title['q4'] = 'ATMs in Germany'


#
# Short version ....
#
#nq2 = {}
#nq2['q4'] = overpass_query_4
#title['q4'] = 'ATM in Bahamas'

data = 0





X = 1 # this is only for counting the hexagons

#####################################################
#  Some variables ...
#
TG_SECRET = os.environ.get('TG_SECRET')
TG_SECRET_ALIAS = os.environ.get('TG_SECRET_ALIAS')
TG_USERNAME = os.environ.get('TG_USERNAME')
TG_PASSWORD = os.environ.get('TG_PASSWORD')
TG_URL = os.environ.get('TG_URL')

#######################################################
# Connection to TigerGraph
#
graph_name = "OSMLayers_Demo6a"
conn, token = gqtg.initTG( graph_name=graph_name, username=TG_USERNAME, password=TG_PASSWORD, hostname=TG_URL, secretalias=TG_SECRET_ALIAS, secret=TG_SECRET )
print( conn )





for namedQuery in nq:

    X = gqplots.plotNamedQuery( nq[namedQuery], namedQuery, title[namedQuery] , path_offset=path_offset)

    links, selected_counts = gqh3.getLinks_and_Counters( X, zoom=6 )

    #m = gqplots.visualize_hexagons(selected_counts, zoom)
    #display(m)

    fnLinks = namedQuery + "_tagLinks.csv"
    fnPlaces = namedQuery + "_places.csv"

    gqosm.nodes_to_DF( X , fnPlaces )
    places = pd.read_csv(path_offset+fnPlaces)
    places.describe()
    places.info()
    print( places.columns )
    print( places )
    conn.upsertVertexDataFrame( df=places, vertexType='h3place', v_id='h3index', attributes={'resolution':'res'})

    gqosm.links_to_DF( links, fnLinks )
    tagLinks = pd.read_csv(path_offset+fnLinks)
    tagLinks.describe()
    tagLinks.info()
    print( tagLinks )
    conn.upsertEdgeDataFrame(
      df=tagLinks,
      sourceVertexType='osmtag',
      edgeType='hasOSMTag',
      targetVertexType='h3place',
      from_id='osmtag',
      to_id='h3index',
      attributes={'tagCount':'z'} )
