#####
#
# This GeoQB demo script uses the OSM data loader module to create the raw OSM data layers.
# This data will be pushed into the staging area in TigerGraph.
#
# - bulkload into staging area


##################################################
# GeoQB dependencies ...
#

import sys
sys.path.append('./')

import geoanalysis.geoqb.geoqb_workspace as gqws

import geoanalysis.geoqb.geoqb_plots as gqplots

import geoanalysis.geoqb.geoqb_h3 as gqh3

#import geoanalysis.geoqb.geoqb_kafka as gqk

import geoanalysis.geoqb.geoqb_osm_pandas as gqosm

import geoanalysis.geoqb.geoqb_tg as gqtg

import geoanalysis.geoqb.geoqb_layers as gql

import geoanalysis.geoqb.sample_data.sample_layers as sl

#
# Python dependencies ...
#
import pandas as pd
from datetime import datetime
import time
import copy
import json
import os

#
# The timestamp is used in all asset names so that we can implicitely find out what belongs to a single study.
# It can also be changed to a logical version number.
#
timestamp = datetime.now()

user="mirko"

# We persist metadata in Kafka topics in Confluent Cloud
topic = "OSM_nodes_stage"
topicQMD = "QMD_OSM_nodes_stage"

#zoom = 12
zoom = 9
#zoom = 6

ts = "latest"
lengths = [ 30 ]

locs = [ "Wismar", "Rostock", "Lübeck", "Stralsund", "Frankleben", "Stollberg", "Chemnitz", "Berlin", "Kiel", "Hamburg" ]
#locs = [ "Wismar", "Frankleben" ]

layers = {}

def loadDataFromWeb(locs, lengths, load_layer_tags = True, load_full_set_of_tags = False ):

        dryRun = False

        layers = {}

        for location_name in locs:

            for l in lengths :

                if load_full_set_of_tags:
                    temp_layer = sl.getKGC2022_FullDataset( location_name = location_name, l = l, zoom=zoom, path_offset=path_offset, dryRun=dryRun )
                    for lay in temp_layer:
                        layers[lay] = temp_layer[lay]

                if load_layer_tags:
                    temp_layers = sl.getKGC2022_DemoDataStack( location_name = location_name, l = l, zoom=zoom, path_offset=path_offset, dryRun=dryRun )
                    for lay in temp_layers:
                        layers[lay] = temp_layers[lay]


        #
        # We collect all layer definition queries in a single file ...
        #
        print( "### Save query dumps: " + path_offset + "/dumps/q.dump" )
        file1 = open( path_offset + "/dumps/q.dump" , "w")

        for layer in layers:
          print( "*** Layer: " + layer)
          multiLayer = layers[layer]
          if multiLayer is not None:
            print( "*** Layer data loaded: {}")
            multiLayer.printQueryStack( file1 );
          else:
            print( "!!! Warning !!! - Layer data not loaded.")
        file1.close()

        #
        # We collect all layer metadate in a single file ...
        #
        file2 = open( path_offset + "/dumps/md.dump" , "w")

        jsonLayers = []
        for layer in layers:
            multiLayer = layers[layer]
            jsonLayers.append( multiLayer.toJSON() )

        json.dump(jsonLayers, file2, indent = 6)

        file2.close()





        #
        # Process initialized layers
        #
        z = len( layers )
        i = 0
        print( f"### Iterate over set of {z} MultiLayers :")
        for layer in layers:

            i = i + 1
            multiLayer = layers[layer]

            print( f"#  Process layer {i} : {multiLayer.qn}")

            multiLayer.plotMultiLayerData( path_offset = path_offset )

            multiLayer.persistDataFrames( path_offset )

            multiLayer.stageLayerDataInTigerGraph( path_offset, conn )

            # layer.stageLayerDataInKafkaTopic( path_offset = path_offset, topic_name = topic )

            #### DEPENDENCY ON Gecko-Driver must be managed or removed ...
            # multiLayer.showHexagonMap( path_offset )



#####################################################
#  Some variables ...
#
TG_SECRET = os.environ.get('TG_SECRET')
TG_SECRET_ALIAS = os.environ.get('TG_SECRET_ALIAS')
TG_USERNAME = os.environ.get('TG_USERNAME')
TG_PASSWORD = os.environ.get('TG_PASSWORD')
TG_URL = os.environ.get('TG_URL')

#####################################################
#  Extracted data will be stored in this folder.
#  - it can be a mounted Google Drive folder, or a volume, or a local path.
#
#path_offset = "./workspace"
path_offset = gqws.prepareWorkspaceFolders()

#######################################################
# Connection to TigerGraph
#
graph_name = "OSMLayers_Demo6a"
conn, token = gqtg.initTG( graph_name=graph_name,
                           username=TG_USERNAME,
                           password=TG_PASSWORD,
                           hostname=TG_URL,
                           secretalias=TG_SECRET_ALIAS,
                           secret=TG_SECRET )
print( conn )

####################################################################
#  Load some data ... plot overview, and ingest into tigergraph.
#
loadDataFromWeb( locs=locs , lengths=lengths,
                 load_layer_tags = True,
                 load_full_set_of_tags = False )

gqtg.showStats( conn, graph_name )




