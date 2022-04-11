#####
#
# This GeoQB demo script uses the OSM data loader module to create the raw data layers.
# The data profiling will be applied to the raw data in the staging area.
#
# - bulkload into staging area

import sys
sys.path.append('../../../')

#
# GeoQB dependencies ...
#
import geoanalysis.geoqb.geoqb_plots as gqplots

import geoanalysis.geoqb.geoqb_h3 as gqh3

import geoanalysis.geoqb.geoqb_kafka as gqk

import geoanalysis.geoqb.geoqb_osm_pandas as gqosm

import geoanalysis.geoqb.geoqb_tg as gqtg

import geoanalysis.geoqb.geoqb_layers as gql

#
# Python dependencies ...
#
import pandas as pd

from datetime import datetime
import time

import copy






#WS_PATH = "/content/drive/My Drive/GeoQB/Geo-QB-CORE/data/pois/"
REPORT_PATH = "./reports"

TOOL_VERSION = "1.0.1"

# We persist metadata in Kafka topics in Confluent Cloud
topic = "OSM_nodes_stage"
topicQMD = "QMD_OSM_nodes_stage"

# Extracted data will be stored in this mounted Google Drive folder:
path_offset = "./workspace/"

zoom = 9





########################################################################################################################
# Example 1:
#

#
# We load our layers for the whole region of Germany, specified by the ISO code.
#
area = 'area["ISO3166-1"="DE"][admin_level=2];'
locName = "Germany"

layers = {}
H3 = ""

#
# This is the initial version, using OSM data via OverPass API.
#
try:

  layer = gql.LayerSpecification( location_name=locName, area=area )
  H3 = layer.myBBCenter_h3index

  #layers['all'] = layer

  layer1 = copy.deepcopy( layer )
  layer1.setSelectionFilter( '"amenity"~"biergarten"', "Biergärten" )
  layers['Biergärten'] = layer1

  layer2 = copy.deepcopy( layer )
  layer2.setSelectionFilter( '"amenity"~"waste_basket"', "Abfallbehälter" )
  layers['Abfallbehälter'] = layer2

  layer3 = copy.deepcopy( layer )
  layer3.setSelectionFilter( '"amenity"~"atm"', "ATM" )
  layers['ATM'] = layer3

  layer4 = copy.deepcopy( layer )
  layer4.setSelectionFilter( '"amenity"~"toilets"', "WC" )
  layers['WC'] = layer4

  layer5 = copy.deepcopy( layer )
  layer5.setSelectionFilter( '"amenity"~"post_box"', "Briefkasten" )
  layers['Briefkasten'] = layer5

  layer6 = copy.deepcopy( layer )
  layer6.setSelectionFilter( '"amenity"~"bench"', "Rastplatz" )
  layers['Rastplatz'] = layer6

  layer7 = copy.deepcopy( layer )
  layer7.setSelectionFilter( '"amenity"~"kindergarten"', "Kindergarten" )
  layers['Kindergarten'] = layer7

  layer8 = copy.deepcopy( layer )
  layer8.setSelectionFilter( '"amenity"~"hunting_stand"', "Jägerstand" )
  layers['Jägerstand'] = layer8

  layer9 = copy.deepcopy( layer )
  layer9.setSelectionFilter( '"amenity"~"bicycle_parking"', "Fahrradparkplatz" )
  layers['Fahrradparkplatz'] = layer9

  layer10 = copy.deepcopy( layer )
  layer10.setSelectionFilter( '"amenity"~"community_centre"', "Gemeindezentrum" )
  layers['Gemeindezentrum'] = layer10

except ValueError as err:
  print("**** ERROR ****")
  print(err.args)


#
# TODO: make path :by_area_code_0.3_all_MD.json: flexible ...
#

for lKey in layers:
  print( f"\n*** Inspect layer: {lKey}" )
  l = layers[lKey]
  l.dumpLayerMD( path_offset, verbose=True )

  l.getJSONData( path_offset );
  l.plotLayerData( path_offset )

  #l.persistDataFrames( path_offset )
  #l.showHexagonMap()
  #l.stageLayerDataInTigerGraph( path_offset, conn )
