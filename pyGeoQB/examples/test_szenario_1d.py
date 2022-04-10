#####
#
# This GeoQB demo script reads the full graph model from TigerGraph.
#



##################################################
# GeoQB dependencies ...
#

import sys
sys.path.append('./')

import os
from os.path import exists

import geoanalysis.geoqb.data4good.HighResolutionPopulationDensityMapsAndDemographicEstimates as d4g_population

import geoanalysis.geoqb.geoqb_plots as gqplots

import geoanalysis.geoqb.geoqb_h3 as gqh3

import geoanalysis.geoqb.geoqb_kafka as gqk

import geoanalysis.geoqb.geoqb_osm_pandas as gqosm

import geoanalysis.geoqb.geoqb_tg as gqtg

import geoanalysis.geoqb.geoqb_layers as gql

import networkx as nx



#
# Python dependencies ...
#
import pandas as pd
from datetime import datetime
import time
import copy
import json

#
# The timestamp is used in all asset names so that we can implicitely find out what belongs to a single study.
# It can also be changed to a logical version number.
#
timestamp = datetime.now()

#####################################################
#  Some variables ...
#
TG_SECRET = os.environ.get('TG_SECRET')
TG_SECRET_ALIAS = os.environ.get('TG_SECRET_ALIAS')
TG_USERNAME = os.environ.get('TG_USERNAME')
TG_PASSWORD = os.environ.get('TG_PASSWORD')
TG_URL = os.environ.get('TG_URL')

WORKPATH = "workspace/sample1d/"

######################################################
#  Make sure that we have workspace folder ...
#
from pathlib import Path
Path(WORKPATH).mkdir(parents=True, exist_ok=True)

#######################################################
#  Connection to TigerGraph
#
graph_name = "OSMLayers_Demo6a"
conn, token = gqtg.initTG( graph_name=graph_name, username=TG_USERNAME, password=TG_PASSWORD, hostname=TG_URL, secretalias=TG_SECRET_ALIAS, secret=TG_SECRET )
print( conn )

gqtg.getFullGraph2( conn, graph_name, WORKPATH=WORKPATH, overwrite=True )

locs = [ "Wismar", "Rostock", "Lübeck", "Stralsund", "Frankleben", "Stollberg", "Chemnitz", "Berlin", "Kiel", "Hamburg" ]
#locs = [ "Halle", "Zwickau", "Leipzig" ]
#locs = [ "Frankleben" ]

allNodes = None

for loc in locs:
    dfSPOS, dfedgesNEG = gqtg.getLayer( conn, graph_name, WORKPATH=WORKPATH, overwrite=True,  s1=loc, s2="POS" )
    dfSNEG, dfedgesNEG = gqtg.getLayer( conn, graph_name, WORKPATH=WORKPATH, overwrite=True,  s1=loc, s2="NEG" )

    #######
    #
    #  Data Blending Demo ...
    #
    nodesPOS = dfSPOS.dropna(subset=['lat', 'lon'])
    nodesNEG = dfSNEG.dropna(subset=['lat', 'lon'])

    allNodesTemp = pd.concat([nodesPOS, nodesNEG], axis=0)

    if allNodes is None:
        allNodes = allNodesTemp
    else:
        allNodes = pd.concat([allNodes, allNodesTemp], axis=0)

#
# Enrich all the preloaded data ...
#
fn = d4g_population.getDumpFileName()
print(f">>> Local join in data file ... {fn}")
df = d4g_population.getDataFrame_linked_by_h3Index( allNodes )
print(f">>> Blending the data in the graph with data from ... {fn}")
d4g_population.blendIntoMultilayerGraph( conn, df )
