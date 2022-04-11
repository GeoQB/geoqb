###############################
#
# Metadata Enrichment Examples
#  - ZIP Code by "Location Name". : If the location_name is a city, we can lookup the ZIP Code for Germany.
#  - Data4Good : Population data is linked to h3index cells
#
import sys
sys.path.append('../../../')

import os
import pandas as pd
import numpy as np
from os.path import exists

import geoanalysis.geoqb as gq
import geoanalysis.geoqb.geoqb_workspace as gqws
import geoanalysis.geoqb.geoqb_zipcodes as gqzip
import geoanalysis.geoqb.geoqb_h3 as gqh3
import geoanalysis.geoqb.geoqb_tg as gqtg



#################################################################################
# (1) ZIP Codes
#


#
# We have a full list of ZIP codes for Germany from:
#   https://gist.github.com/jbspeakr/4565964
#
dfZip = gqzip.getGermanZipCodes()
print( dfZip )

#
# Now, we can get some ZIP codes for a German location.
#
print( gqzip.enrichLoactionName( "Wismar" ) )
print( gqzip.enrichLoactionName( "Frankleben" ) )





#
# (2) h3 neighborhoods and hirarchie for geo-index based operations.
#     https://uber.github.io/h3-py/api_reference.html
#
print( "##### 2 #####")
location_name = "Frankleben"
data = gqh3.getLocationCoordinatesAndH3Index( location_name , 9 )
print( data )

print( "##### 2.1 #####")
print( gqzip.enrichLoactionName(location_name, verbose=True) )

print( "##### 2.2 #####")
index, res = gqh3.getIndexAndZoomFrom_h3IndexString( data[2], verbose = True )

listOfIndexes = gqh3.get_listOfIndexes_zoom_in_N( index, 2 )
print( listOfIndexes )

print( "##### 2.3 #####")
print( gqh3.lat_lon_from_h3Index2("891f02a0507ffff"))



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

########
#
# We are ready to enrich the raw data ...
#

import geoanalysis.geoqb.data4good.HighResolutionPopulationDensityMapsAndDemographicEstimates as d4g_population
data = np.array( [[ "Irgendwo", "891f02a0507ffff" ]] )
dataset = pd.DataFrame({'city': data[:, 0], 'h3index': data[:, 1]})

fn = d4g_population.getDumpFileName()
print(f">>> Blending the data ... {fn}")

if not exists(fn ):
  df = d4g_population.getDataFrame_linked_by_h3Index( dataset )
else:
  df = pd.read_csv( fn, sep="\t" )

df=df.drop_duplicates(subset='h3index', keep="last")
print( df )
d4g_population.blendIntoMultilayerGraph( conn, df )

