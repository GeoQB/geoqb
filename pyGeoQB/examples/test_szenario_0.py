#####################################################################################################
#
# This GeoQB demo script uses the TigerGraph module to create a data staging area in TigerGraph.
#
# - preparation of the GeoQB graph workspace
#

###########################
# GeoQB dependencies ...
#
import sys
sys.path.append('/')

import geoanalysis.geoqb.geoqb_tg as gqtg
import os

import warnings
warnings.filterwarnings('ignore')

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

gqtg.ls( conn )

#gqtg.setupOSMGlobalTypes( conn )
#gqtg.setupOSMGraph( conn, graph_name )

#gqtg.dropOSMGraph( conn, graph_name )
#gqtg.dropOSMGlobalTypes( conn )
#gqtg.cleanData( conn, graph_name  )

gqtg.showStats( conn, graph_name )





