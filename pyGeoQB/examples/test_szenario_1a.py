#####
#
# This GeoQB demo script uses the OSM data loader module to read the raw OSM data layers from disc.
# This data will be pushed into the staging area in TigerGraph.
#
# - bulkload into staging area
#

##################################################
# GeoQB dependencies ...
#

import sys
sys.path.append('./')

import os

import geoanalysis.geoqb.geoqb_plots as gqplots

import geoanalysis.geoqb.geoqb_h3 as gqh3

import geoanalysis.geoqb.geoqb_kafka as gqk

import geoanalysis.geoqb.geoqb_osm_pandas as gqosm

import geoanalysis.geoqb.geoqb_tg as gqtg

import geoanalysis.geoqb.geoqb_layers as gql

import geoanalysis.geoqb.sample_data.sample_layers as sl

import networkx as nx



#
# Python dependencies ...
#
import pandas as pd
from datetime import datetime
import time
import copy
import json
import glob


#
# The timestamp is used in all asset names so that we can implicitely find out what belongs to a single study.
# It can also be changed to a logical version number.
#
timestamp = datetime.now()

print("timestamp =", timestamp)
print("type(timestamp) =", type(timestamp))

user="mirko"

# We persist metadata in Kafka topics in Confluent Cloud
topic = "OSM_nodes_stage"
topicQMD = "QMD_OSM_nodes_stage"

# Extracted data will be stored in this mounted Google Drive folder:
path_offset = "./workspace"

#zoom = 12
zoom = 9
#zoom = 6

ts = "latest"

layers = {}

def readDataFromDrive():

    #
    # Process metadata files which describe layers ...
    #
    print( "Path: " + path_offset )

    file_list = glob.glob(path_offset + "/graphs/Wi*_MD.json") # Include slash or it will search in the wrong directory!!
    print('file_list {}'.format(file_list))
    print()

    #####################################################################
    # Read OSM layers from MD files and export inot TigerGraph
    #
    for fn in file_list:

        print( fn )

        layer = gql.SophoxLayer( fileName=fn )

        layer.plotLayerData( path_offset )

        layer.persistDataFrames( path_offset )

        layer.stageLayerDataInTigerGraph( path_offset, conn )

        #print( layer.toJSON() )

        #layer.stageLayerDataInKafkaTopic( path_offset = path_offset, topic_name = topic )





#####################################################
#  Some variables ...
#
TG_SECRET = os.environ.get('TG_SECRET')
TG_SECRET_ALIAS = os.environ.get('TG_SECRET_ALIAS')
TG_USERNAME = os.environ.get('TG_USERNAME')
TG_PASSWORD = os.environ.get('TG_PASSWORD')
TG_URL = os.environ.get('TG_URL')

#######################################################
#  Connection to TigerGraph
#
graph_name = "OSMLayers_Demo6a"
conn, token = gqtg.initTG( graph_name=graph_name, username=TG_USERNAME, password=TG_PASSWORD, hostname=TG_URL, secretalias=TG_SECRET_ALIAS, secret=TG_SECRET )
print( conn )

#######################################################
#  Ingest some data ...
#
readDataFromDrive()
