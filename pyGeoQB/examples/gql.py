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

import geoanalysis.geoqb.geoqb_workspace as gqws

import geoanalysis.geoqb.geoqb_tg as gqtg


#####################################################
#  Extracted data will be stored in this folder.
#  - it can be a mounted Google Drive folder, or a volume, or a local path.
#
#path_offset = "./workspace"
path_offset = gqws.prepareWorkspaceFolders( verbose=False )

import glob
import plac
from pathlib import Path
import json

from datetime import datetime

#####################################################
#  Some variables ...
#
TG_SECRET = os.environ.get('TG_SECRET')
TG_SECRET_ALIAS = os.environ.get('TG_SECRET_ALIAS')
TG_USERNAME = os.environ.get('TG_USERNAME')
TG_PASSWORD = os.environ.get('TG_PASSWORD')
TG_URL = os.environ.get('TG_URL')

import geoanalysis.geoqb.sample_data.sample_layers as sl



def topolgy_inspection():

    path_offset = gqws.prepareWorkspaceFolders()
    WORKPATH = f"{path_offset}/sample_clusters/"

    ######################################################
    #  Make sure that we have workspace folder ...
    #
    from pathlib import Path
    Path(WORKPATH).mkdir(parents=True, exist_ok=True)

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

    import geoanalysis.geoqb.graph_analyser as ga
    ga.analyseClusters( graph_name, conn, WORKPATH )




def calc_impact_score_for_layer_stack( location_name ):

    path_offset = gqws.prepareWorkspaceFolders()
    WORKPATH = f"{path_offset}/sample_score/"

    ######################################################
    #  Make sure that we have workspace folder ...
    #
    from pathlib import Path
    Path(WORKPATH).mkdir(parents=True, exist_ok=True)

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

    import geoanalysis.geoqb.calc_impact_score as scorer
    scorer.calc_score( location_name, conn, WORKPATH, 10, graph_name )



def export_layer_stack(location_name, type="sophox", graph_name="OSMLayers_Demo6a", zoom=9, dryRun=False):

    path_offset = gqws.prepareWorkspaceFolders()
    WORKPATH = f"{path_offset}/sample_extract/"

    ######################################################
    #  Make sure that we have workspace folder ...
    #
    from pathlib import Path
    Path(WORKPATH).mkdir(parents=True, exist_ok=True)

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

    dfSPOS, dfedgesNEG = gqtg.getLayer( conn, graph_name, WORKPATH=WORKPATH, overwrite=True,  s1=location_name, s2="POS" )
    dfSNEG, dfedgesNEG = gqtg.getLayer( conn, graph_name, WORKPATH=WORKPATH, overwrite=True,  s1=location_name, s2="NEG" )

def export_all_layer_stack(location_name, type="sophox", graph_name="OSMLayers_Demo6a", zoom=9, dryRun=False):

    path_offset = gqws.prepareWorkspaceFolders()
    WORKPATH = f"{path_offset}/sample_extract/"

    ######################################################
    #  Make sure that we have workspace folder ...
    #
    from pathlib import Path
    Path(WORKPATH).mkdir(parents=True, exist_ok=True)

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

    dfSPOS, dfedgesNEG = gqtg.getFullGraph2( conn, graph_name, WORKPATH=WORKPATH, overwrite=True )

    print( f"> exported data is stored in {WORKPATH}.")


def ingest_layer_stack(location_name, type="sophox", zoom=9, dryRun=False):

    temp_layers = sl.getKGC2022_DemoDataStack( location_name = location_name, l = 30, zoom=zoom, path_offset=path_offset, dryRun=dryRun )

    i = 0
    for key in temp_layers:
        i = i + 1
        multiLayer = temp_layers[key]
        print( f"#  Process layer {i} : {multiLayer.qn}")
        multiLayer.plotMultiLayerData( path_offset = path_offset )
        multiLayer.persistDataFrames( path_offset )

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

        multiLayer.stageLayerDataInTigerGraph( path_offset, conn )



def create_layer_stack(location_name, type="sophox", zoom=9, dryRun=False):

    temp_layers = sl.getKGC2022_DemoDataStack( location_name = location_name, l = 30, zoom=zoom, path_offset=path_offset, dryRun=dryRun )

    i = 0
    for key in temp_layers:
        i = i + 1
        multiLayer = temp_layers[key]
        print( f"#  Process layer {i} : {multiLayer.qn}")
        multiLayer.plotMultiLayerData( path_offset = path_offset )
        multiLayer.persistDataFrames( path_offset )


def main(graph, cmd='ls', name='default', verbose=False):
    print( f"ENV GEOQB_WORKSPACE: {path_offset}")
    if cmd=="ls":
        print( f"CMD: {cmd} <verbos:{verbose}>")
        globs = glob.glob(f"{path_offset}/md/{name}*")
        locs = {}
        for g in globs:
            if verbose:
                print( g )
            p = g[len(path_offset)+4:].split("_")[0]
            locs[p]=g
        print( f"\n> {len(globs)} individual layers in multi-layer-graph workspace." )
        print( f"> {len(locs)} locations." )
        print( f"> {locs.keys()}" )
    if cmd=="create":
        location = input("> new location: " )
        print( f"[{location}]" )
        type = input("> layer type: (Sophox) " )
        if len(type) == 0:
            type = "sophox"
        print(f"[{type}]")
        create_layer_stack( location_name=location, type=type )

    if cmd=="ingest":
        location = input("> new location: " )
        print( f"[{location}]" )
        #type = input("> layer type: (Sophox) " )
        #if len(type) == 0:
        type = "sophox"
        #print(f"[{type}]")

        ingest_layer_stack( location_name=location, type=type )

    if cmd=="extract":
        location = input("> location: " )
        print( f"[{location}]" )
        #type = input("> layer type: (Sophox) " )
        #if len(type) == 0:
        type = "sophox"
        #print(f"[{type}]")

        export_layer_stack( location_name=location, type=type )

    if cmd=="extract-all":
        location = input("> location: " )
        print( f"[{location}]" )
        #type = input("> layer type: (Sophox) " )
        #if len(type) == 0:
        type = "sophox"
        #print(f"[{type}]")

        export_all_layer_stack( location_name=location, type=type )

    if cmd=="calc-impact-score":
        location = input("> location: " )
        print( f"[{location}]" )
        #type = input("> layer type: (Sophox) " )
        #if len(type) == 0:
        type = "sophox"
        #print(f"[{type}]")

        calc_impact_score_for_layer_stack( location_name=location )

    if cmd=="ca":

        go = input("> Analyse the full graph ... (node2vec + k-means + word-clouds) " )

        topolgy_inspection()


    else:
        print( f"CMD {cmd} <verbos:{verbose}> not yet implemented.")

if __name__ == '__main__':
    plac.call(main)