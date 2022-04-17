######################################################################
#
# The pyGeoQB CLI wraps around the demo scripts and core functions.
#
######################################################################
# GeoQB dependencies ...
#
import click
import sys
import os
sys.path.append('./')
import pandas as pd
import flat_table


import glob
import geoanalysis.geoqb.geoqb_workspace as gqws
import geoanalysis.geoqb.data4good.HighResolutionPopulationDensityMapsAndDemographicEstimates as d4g_population
import geoanalysis.geoqb.geoqb_tg as gqtg
import geoanalysis.geoqb.geoqb_kafka as gqkafka
import geoanalysis.geoqb.geoqb_layers as gql
import geoanalysis.geoqb.cli.cli_helper as cli
import plac

#####################################################
#  Some variables ...
#
TG_SECRET = os.environ.get('TG_SECRET')
TG_SECRET_ALIAS = os.environ.get('TG_SECRET_ALIAS')
TG_USERNAME = os.environ.get('TG_USERNAME')
TG_PASSWORD = os.environ.get('TG_PASSWORD')
TG_URL = os.environ.get('TG_URL')
GEOQB_TG_GRAPHNAME = os.environ.get('GEOQB_TG_GRAPHNAME')

import geoanalysis.geoqb.sample_data.sample_layers as sl

def getConnection():
    #######################################################
    # Connection to TigerGraph
    #
    graph_name = GEOQB_TG_GRAPHNAME
    conn, token = gqtg.initTG( graph_name=graph_name,
                               username=TG_USERNAME,
                               password=TG_PASSWORD,
                               hostname=TG_URL,
                               secretalias=TG_SECRET_ALIAS,
                               secret=TG_SECRET )
    return conn, graph_name

#####################################################
#  Extracted data will be stored in this folder.
#  - it can be a mounted Google Drive folder, or a volume, or a local path.
#
#path_offset = "./workspace"
path_offset = gqws.prepareWorkspaceFolders( verbose=False )
WORKPATH = f"{path_offset}/sample_clusters/" # needed by individual tools ...

from pathlib import Path
from datetime import datetime
import json

def validateStructure4GraphMapping( df ):
    print("!!! WARNING !!! - Validation is not implemented yet. Feature comming soon.")
    return True


def blendDataFromTopicToLayer( layerName, dataDF ):

    print( "#.")

    conn, graph_name = getConnection()

    dfSPOS, dfedgesNEG = gqtg.getLayer( conn, graph_name, WORKPATH=WORKPATH, overwrite=True,  s1=layerName, s2="POS" )
    dfSNEG, dfedgesNEG = gqtg.getLayer( conn, graph_name, WORKPATH=WORKPATH, overwrite=True,  s1=layerName, s2="NEG" )

    nodesPOS = dfSPOS.dropna(subset=['lat', 'lon'])
    nodesNEG = dfSNEG.dropna(subset=['lat', 'lon'])

    allNodesTemp = pd.concat([nodesPOS, nodesNEG], axis=0)

    #
    # This is the mapping of a particular measurement to an h3place in the graph
    #
    v_cnShort = [ "temp" , "p", "dp" ]
    v_cnLong = [ "TEMPERATURE" , "PRESURE", "delta_PRESURE" ]
    observation_source = [ "myTempSensor", "myPSensor", "calc" ]
    observation_typ = [ "environment.temperature.absolute", "environment.air-presure.absolute", "environment.air-presure.change" ]

    mappings = []
    i=0
    while i < len(v_cnShort):
        mapping1 = ( v_cnShort[i], v_cnLong[i], observation_source[i], observation_typ[i] )
        mappings.append( mapping1 )
        i = i + 1

    print( f"> # of nodes in layer: {len(allNodesTemp)}" )

    gqtg.blendDataToLayerDataInTigerGraph( allNodesTemp, dataDF, mappings, path_offset, conn )



def start_blending_data_to_layer( asset="data4good", filters=["_", "POS"] ):

    #print( f"WS : {path_offset}md/*")

    globs = glob.glob(f"{path_offset}md/*")
    locs = {}
    for g in globs:
        p = g[len(path_offset)+3:].split("_")[0]
        locs[p]=g
    print( f"> For {len(locs)} location(s) we can do the data blending." )
    print( f"* {locs.keys()}" )

    selected = ""
    location = input(f"> select a location ({selected}): " )
    print( f"* your input: [{location}]" )
    if location=="":
        location = selected
    if location in locs:
        print( f"> Continue data blending with data asset: {asset}.")

        conn, graph_name = getConnection()

        dfSPOS, dfedgesNEG = gqtg.getLayer( conn, graph_name, WORKPATH=WORKPATH, overwrite=True,  s1=location, s2="POS" )
        dfSNEG, dfedgesNEG = gqtg.getLayer( conn, graph_name, WORKPATH=WORKPATH, overwrite=True,  s1=location, s2="NEG" )

        nodesPOS = dfSPOS.dropna(subset=['lat', 'lon'])
        nodesNEG = dfSNEG.dropna(subset=['lat', 'lon'])

        allNodesTemp = pd.concat([nodesPOS, nodesNEG], axis=0)
        print("> Layer data loaded from graph.")

        if asset=="data4good":
            print( "> Work with asset <data4good>.")
            ###################################################################################
            # Using our managed Data4good data asset we can enrich our existing graph layers
            #

            #
            # ... enrich all the preloaded data!
            #
            d4g_population.enrich( conn, allNodesTemp )

    else:
        print( f"* The selection {location} is not available in the list of LAYER STACKS: {locs.keys()}")
        exit()

    pass









def main( cmd: ('(ls|asset|topic|init|clear)'), verbose=False, ):

    print( f"\nGeoQB blend - is a tool for data blending for data from local data assets, streaming pods, and public linked data pods.\n" )

    if cmd=="ls":
        path = f"{path_offset}stage/*"
        print( f"CMD: {cmd} <verbose:{verbose}>\n")
        globs = glob.glob( path )
        locs = {}
        i=1
        for g in globs:
            p = g[len(path_offset)+6:].split("_")[0]
            locs[p]=g
            print( f"[{i}]    {p} - {g}" )
            i = i + 1

        print( f"\n> {len(globs)} enrichment data assets in multi-layer-graph workspace." )
        s_in_bytes = gqws.get_size(path)

        print( f"> Data asset path : {path}")
        print( f"> Total capacity  : {s_in_bytes/1024/1024:.2f} MB.")

    elif cmd=="topic":
        print( f"CMD: {cmd} <verbose:{verbose}>\n")

        prefix="GQ"

        topic =gqkafka.showTopics_FilteredAndSelectOne( prefix )

        df = gqkafka.readAndPrint_N_messages_from_topic(topic, 1)

        layerName = cli.selectLayer()

        '''
        
        GQ_temperature_stream
        
        "891e34d61d3ffff"
        
        {
            "temp": 22.9,
            "t": 1650014969,
            "p": 1010.0,
            "dp" : -10.5
        }

        '''

        structureValid = validateStructure4GraphMapping( df )

        if structureValid:
            print(f"> Start blending data from topic <{topic}> to layer <{layerName}> ...")
            blendDataFromTopicToLayer( layerName, df )
        else:
            print(f"> Data from topic {topic} can't be blended." )

    elif cmd=="init":
        print( f"CMD: {cmd} <verbose:{verbose}>")
        print( "Initialize a new data asset. ( This feature is comming soon!)")

    elif cmd=="clear":
        fn = gqws.getWorkspaceFolder()
        print( "To clear the workspace, please use 'gqws clear'"  )

        path1 = f"{path_offset}stage/*"
        print( f"CMD: {cmd} <verbose:{verbose}>\n")
        globs = glob.glob( path1 )
        locs = {}
        i=1
        for g in globs:
            p = g[len(path_offset)+6:].split("_")[0]
            locs[p]=g
            print( f"[{i}]    {p} - {g}" )

        answer = input(f"\n> Which data asset should be removed: : [PLEASE PROVIDE foldername]  : " )
        path = f"{path_offset}stage/{answer}"
        dassetExist = os.path.exists(path) and len(answer) > 1
        if dassetExist:
            print( f"<{answer}> is your selection\n > ... ready to remove the dataset." )
        else:
            print( f"*** WARNING *** The data asset <{answer}> does not exist." )
            exit()

    elif cmd=="asset":
        asset = cli.selectAsset(cmd=cmd,verbose=verbose)
        start_blending_data_to_layer(asset=asset)

    else:
        print( f"CMD {cmd} <verbos:{verbose}> not yet implemented.")

if __name__ == '__main__':
    plac.call(main)