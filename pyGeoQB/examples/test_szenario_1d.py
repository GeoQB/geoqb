#####
#
# This GeoQB demo script reads the full graph model from TigerGraph.
#
# Furthermore, using selective layers, we do the data blending demo ...
#



##################################################
# GeoQB dependencies ...
#
import sys
sys.path.append('/')

import geoanalysis.geoqb.data4good.HighResolutionPopulationDensityMapsAndDemographicEstimates as d4g_population
import geoanalysis.geoqb.geoqb_tg as gqtg
import geoanalysis.geoqb.geoqb_workspace as gqws

import os
import pandas as pd
from datetime import datetime

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

#####################################################
#  Extracted data will be stored in this folder.
#  - it can be a mounted Google Drive folder, or a volume, or a local path.
#
#path_offset = "./workspace"
path_offset = gqws.prepareWorkspaceFolders()
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

#
# Just load the full graph ...
#
gqtg.getFullGraph2( conn, graph_name, WORKPATH=WORKPATH, overwrite=True )


#
# Iterate over individual layers ...
#
locs = [ "Wismar", "Rostock", "Lübeck", "Stralsund", "Frankleben", "Stollberg", "Chemnitz", "Berlin", "Kiel", "Hamburg" ]
#locs = [ "Halle", "Zwickau", "Leipzig" ]
#locs = [ "Frankleben" ]
locs = [ "Erfurt" ]

allNodes = None

for loc in locs:
    dfSPOS, dfedgesNEG = gqtg.getLayer( conn, graph_name, WORKPATH=WORKPATH, overwrite=True,  s1=loc, s2="POS" )
    dfSNEG, dfedgesNEG = gqtg.getLayer( conn, graph_name, WORKPATH=WORKPATH, overwrite=True,  s1=loc, s2="NEG" )

    nodesPOS = dfSPOS.dropna(subset=['lat', 'lon'])
    nodesNEG = dfSNEG.dropna(subset=['lat', 'lon'])

    allNodesTemp = pd.concat([nodesPOS, nodesNEG], axis=0)

    if allNodes is None:
        allNodes = allNodesTemp
    else:
        allNodes = pd.concat([allNodes, allNodesTemp], axis=0)

###################################################################################
# Using our managed Data4good data asset we can enrich our existing graph layers
#

#
# ... enrich all the preloaded data!
#
d4g_population.enrich( conn, allNodes )