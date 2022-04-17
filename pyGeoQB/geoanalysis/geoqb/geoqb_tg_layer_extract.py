from string import Template
import pandas as pd

import flat_table

import geoanalysis.geoqb.geoqb_h3 as gqh3

import matplotlib.pyplot as plt

from os.path import exists

import networkx as nx

import pylab as plt #import Matplotlib plotting interface

import json

persistentQuery2b='''

USE GRAPH $graph_name

CREATE QUERY loadLayer(String lID1,String lID2) FOR GRAPH OSMLayers_Demo6a { 

    SetAccum<EDGE> @@edgeset;
    
    start = ANY;
  
    nodes1 = SELECT t FROM start:s -(:e)-> :t
    WHERE instr ( e.layer_id, lID1 ) >= 0 AND instr ( e.layer_id, lID2 ) >= 0
    accum
    @@edgeset += e;

    #nodes2 = SELECT s FROM start:s -(:e)-> :t;
  
    PRINT nodes1;
    #PRINT nodes2;
    PRINT @@edgeset;
  
}

CREATE QUERY loadAll(/* Parameters here */) FOR GRAPH  { 

    SetAccum<EDGE> @@edgeset;
    
    start = ANY;
  
    nodes2 = SELECT t FROM start:s -(:e)-> :t
    accum
    @@edgeset += e;

    nodes1 = SELECT s FROM start:s -(:e)-> :t;
  
    PRINT nodes1 as sources;
    PRINT nodes2 as targets;
    PRINT @@edgeset as edges;

}
'''



def getTagLayerForParaForOSMGraph( conn, graph_name, res = 9 , WORKPATH="./temp/", overwrite=False, verbose=True, s1 = " ", s2 = " " ):

    path_to_buffer_file = WORKPATH + graph_name +"_"+str(res) + "_OSM_tag_layer_" + s1 + "_" + s2 + "_data.json"
    path_to_edgelist_file = WORKPATH + graph_name +"_"+str(res) + "_OSM_tag_layer_" + s1 + "_" + s2 + "_edge_list.csv"
    path_to_nodelist_file = WORKPATH + graph_name +"_"+str(res) + "_OSM_tag_layer_" + s1 + "_" + s2 + "_node_list.csv"
    t = ""

    file_exists = exists(path_to_buffer_file)
    if not file_exists or overwrite:

        valueStructure = {
            'graph_name' : graph_name,
            'res' : str(res),
            'lID1' : s1,
            'lID2' : s2
        }

        params = valueStructure

        preInstalledResult = conn.runInstalledQuery("loadLayer", params, sizeLimit=120*1024*1024)
        print( type(preInstalledResult) )
        print( len(preInstalledResult) )

        f = open( path_to_buffer_file, "w")
        f.write( json.dumps( preInstalledResult ) )
        f.flush()
        f.close()

    #print( t )

#    print( "*******")

    f2 = open( path_to_buffer_file, "r")
    data = json.load(f2)

#    print( "###############")
    dfS = pd.DataFrame(data[0]["nodes1"])
    dfS = flat_table.normalize(dfS)
    expected_type = "h3place"
    dfS ['lat'] = dfS.apply( lambda x : gqh3.lat_lon_from_h3Index( x["v_id"], x["v_type"], expected_type )[0], axis = 1 )
    dfS ['lon'] = dfS.apply( lambda x : gqh3.lat_lon_from_h3Index( x["v_id"], x["v_type"], expected_type )[1], axis = 1 )
    dfS = dfS.rename(columns={
        'v_id':'Id',
        'attributes.lat':'Lat',
        'attributes.lon':'Lon',
    })

    dfS.to_csv(path_to_nodelist_file, index=False, sep ='\t')

    #print( dfnetwork )
 #   print( "### NETWORK ###")
  #  print( "###############")


   # print( "\n###############")

    dfedges = pd.DataFrame(data[1]["@@edgeset"])

    dfedges = dfedges.rename(columns={
        'from_id':'Source',
        'to_id':'Target'
    })

    dfedges = flat_table.normalize(dfedges)
    dfedges.to_csv(path_to_edgelist_file, index=False, sep ='\t')
    #print( "###  EDGES  ###")
    #print( "###############")

    return dfS, dfedges




def getTagLayerForResolutionForOSMGraph( conn, graph_name, WORKPATH="./temp/", res = 9 , overwrite=False, verbose=True ):

    path_to_buffer_file = WORKPATH + graph_name +"_"+str(res) + "_OSM_tag_layer_data.json"
    path_to_edgelist_file = WORKPATH + graph_name +"_"+str(res) + "_OSM_tag_layer_edge_list.csv"
    path_to_nodelist_file = WORKPATH + graph_name +"_"+str(res) + "_OSM_tag_layer_node_list.csv"

    t = ""

    file_exists = exists(path_to_buffer_file)

    data = None

    if not file_exists or overwrite:

        preInstalledQResult = conn.runInstalledQuery("loadAll", None, sizeLimit=120*1024*1024)
        data = preInstalledQResult

        f = open( path_to_buffer_file, "w")
        f.write( json.dumps( preInstalledQResult ) )
        f.flush()
        f.close()

    else:
        f = open( path_to_buffer_file, "r")
        data = json.load(f)
        f.close

    print( "**********************************************")
    print( f"* Nr of item sets in graph export query: {len(data)}" )
    print( "**********************************************")

    dfS = pd.DataFrame(data[0]["nodes1"])
    dfS = flat_table.normalize(dfS)
    expected_type = "h3place"
    dfS ['lat'] = dfS.apply( lambda x : gqh3.lat_lon_from_h3Index( x["v_id"], x["v_type"], expected_type )[0], axis = 1 )
    dfS ['lon'] = dfS.apply( lambda x : gqh3.lat_lon_from_h3Index( x["v_id"], x["v_type"], expected_type )[1], axis = 1 )
    dfS = dfS.rename(columns={
        'v_id':'Id',
        'attributes.lat':'Lat',
        'attributes.lon':'Lon',
    })

    dfS.to_csv(path_to_nodelist_file, index=False, sep ='\t')
    print( ">   item set 'nodes1' ... DONE.")

    dfedges = pd.DataFrame(data[1]["@@edgeset"])

    dfedges = dfedges.rename(columns={
        'from_id':'Source',
        'to_id':'Target'
    })

    dfedges = flat_table.normalize(dfedges)
    dfedges.to_csv(path_to_edgelist_file, index=False, sep ='\t')
    print( ">   item set '@@edgeset' ... DONE.")

    return dfS, dfedges

