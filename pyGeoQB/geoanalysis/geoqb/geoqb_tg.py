import pyTigerGraph as tg

import geoanalysis.geoqb.geoqb_tg_layer_tag_histogram as gqtaghisto
import geoanalysis.geoqb.geoqb_tg_layer_extract as gqtaglayerextract
import geoanalysis.geoqb.geoqb_osm_pandas as gqosm
import geoanalysis.geoqb.geoqb_h3 as gqh3

import pandas as pd

from string import Template

#
# Create a TigerGraph Application
#
# Create the graph: OSMTest
# Manage the API-Key and secret
# Provide the configuration details for the connection
#
def initTG( graph_name="OSMLayers_Demo",
            secretalias = "???",
            secret = "???",
            hostname="https://geoqb.i.tgcloud.io/",
            username="???",
            password="???"
          ):

  #
  # After some time of inactivity, the TigerGraph application is stopped. We have to restart it.
  #  https://tgcloud.io/app/solutions
  #  https://osmtg.i.tgcloud.io/#/graph-explorer
  #

  api_token = tg.TigerGraphConnection(host=hostname, graphname=graph_name, username=username, password=password).getToken( secret, "3600" )[0]

  conn = tg.TigerGraphConnection(host=hostname, graphname=graph_name, password=password, apiToken=api_token)

  print( "---------------------------------------------" )
  print( "API-Token  : ", api_token )
  print( "Version    : ", tg.__version__ )
  print( "Connection : ", conn )
  print( "---------------------------------------------" )

  return conn,api_token


def storeLayerInGraphDB( namedQueryLabel, path_offset, conn ):

    fnLinks = namedQueryLabel + "_tagLinks.csv"
    fnPlaces = namedQueryLabel + "_places.csv"

    places = pd.read_csv( path_offset + fnPlaces)
    conn.upsertVertexDataFrame( df=places, vertexType='h3place', v_id='h3index', attributes={'resolution':'res'})

    tagLinks = pd.read_csv(path_offset+fnLinks)
    conn.upsertEdgeDataFrame(
      df=tagLinks,
      sourceVertexType='osmtag',
      edgeType='hasOSMTag',
      targetVertexType='h3place',
      from_id='osmtag',
      to_id='h3index',
      attributes={'tagCount':'z'} )



def ls( conn, options=[] ):

    print(">---------------------------------------<")
    print("> What's going on in the graph engine?  ")
    print(">---------------------------------------<")
    print(conn.gsql('ls', options=options))
    print(">")
    print(">---------------------------------------<")


def executeGSQL( conn, cmd, variables = None, options=[]):

    '''
    valueStructure = {
        'graph_name' : name
    }
    '''

    gsqlTemplate = Template( cmd )

    if variables is not None:
        gsqlScript = gsqlTemplate.substitute(variables)
    else:
        gsqlScript = cmd

    print( gsqlScript )

    result = conn.gsql(gsqlScript, options)
    return result


def showFullGraph( conn, name ):
    print( getFullGraph2( conn, name, verbose=False ) )

def showStats( conn, name ):
    print( statsForOSMGraph( conn, name, verbose=False ) )

def getStats( conn, name ):
    return statsForOSMGraph( conn, name, verbose=False )


def getLayer( conn, name, verbose=True, res = 9, WORKPATH="./temp/", overwrite=False, s1=" ", s2=" " ):
    return gqtaglayerextract.getTagLayerForParaForOSMGraph( conn, name, WORKPATH=WORKPATH, res=res, overwrite=overwrite, s1=s1, s2=s2 )

def getFullGraph2( conn, name, verbose=True, WORKPATH="./temp/", res = 9, overwrite=False ):
    return gqtaglayerextract.getTagLayerForResolutionForOSMGraph( conn, name, res=res, overwrite=overwrite, WORKPATH=WORKPATH )

def statsForOSMGraph( conn, name, verbose=True ):

    valueStructure = {
      'graph_name' : name
    }

    gsqlStatement ='''

USE GRAPH $graph_name

INTERPRET QUERY () SYNTAX v2 {

  SumAccum<int> @@placeCnt6= 0;
  SumAccum<int> @@placeCnt9= 0;
  SumAccum<int> @@placeCnt12= 0;

  Result_all = SELECT s
            FROM h3place:s
            ACCUM CASE WHEN s.resolution == 9 THEN
                            @@placeCnt9 += 1
                       WHEN s.resolution == 6 THEN
                            @@placeCnt6 += 1
                       WHEN s.resolution == 12 THEN
                            @@placeCnt12 += 1
                     END;

  PRINT @@placeCnt6;
  PRINT @@placeCnt9;
  PRINT @@placeCnt12; 
  
}

'''

    gsqlTemplate = Template(gsqlStatement)
    gsqlScript = gsqlTemplate.substitute(valueStructure)

    if verbose:
        print( gsqlScript )

    result = conn.gsql(gsqlScript, options=[])
    return result


def showTagHistogramForOSMGraph( conn, graph_name, verbose=True ):
    return gqtaghisto.getTagHistogramForOSMGraph(  conn, graph_name, verbose )



def setupOSMGlobalTypes( conn ):

    gsqlStatement ='''
Use global
CREATE VERTEX osmtag(PRIMARY_ID tagname STRING, tagname STRING, tagvalue STRING, osmid STRING) WITH STATS="OUTDEGREE_BY_EDGETYPE"
CREATE VERTEX h3place(PRIMARY_ID h3index STRING, h3index STRING, resolution INT DEFAULT "6", lat DOUBLE, lon DOUBLE) WITH STATS="OUTDEGREE_BY_EDGETYPE"
CREATE VERTEX osmplace(PRIMARY_ID osmid STRING, lat DOUBLE, lon DOUBLE) WITH STATS="OUTDEGREE_BY_EDGETYPE", PRIMARY_ID_AS_ATTRIBUTE="false"

CREATE UNDIRECTED EDGE hasOSMTag(FROM osmtag, TO h3place, tagCount UINT DEFAULT "1", layer_id STRING)
CREATE UNDIRECTED EDGE h3_grid_link(FROM h3place, TO h3place, layer_id STRING DEFAULT "all")
CREATE UNDIRECTED EDGE located_on_h3_cell(FROM osmplace, TO h3place, layer_id STRING, res INT DEFAULT "6")
'''

    print(conn.gsql(gsqlStatement, options=[]))



def dropOSMGlobalTypes( conn ):

    gsqlStatement ='''
Use global
DROP EDGE hasOSMTag
DROP EDGE h3_grid_link
DROP EDGE located_on_h3_cell
DROP VERTEX osmtag
DROP VERTEX h3place
DROP VERTEX osmplace
'''
    print(conn.gsql(gsqlStatement, options=[]))



def dropOSMGraph( conn, name ):

    valueStructure = {
      'graph_name' : name
    }

    gsqlStatement ='''
Use global
DROP GRAPH $graph_name'''

    gsqlTemplate = Template(gsqlStatement)
    gsqlScript = gsqlTemplate.substitute(valueStructure)
    print(conn.gsql(gsqlScript, options=[]))




def setupOSMGraph( conn, name ):

    valueStructure = {
      'graph_name' : name
    }

    gsqlStatement ='''
Use global
CREATE GRAPH $graph_name (osmtag, osmplace, h3place, hasOSMTag, h3_grid_link, located_on_h3_cell)'''

    gsqlTemplate = Template(gsqlStatement)
    gsqlScript = gsqlTemplate.substitute(valueStructure)
    print(conn.gsql(gsqlScript, options=[]))


def installQueries( conn ):
    print( "> W.I.P. ")

def runInstalledQuery( conn, qKey ):
    print( "> W.I.P. ")

def cleanData( conn, name ):
    print( "> W.I.P. : clean data ...")