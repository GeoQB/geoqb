
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

import glob
import geoanalysis.geoqb.geoqb_workspace as gqws
import plac

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



def main( cmd: ('(ls|init|clear|blend)'), verbose=False, ):
    print( f"GeoQB blend - is a tool for data blending using your graph database.\n" )
    print( f"ENV GEOQB_WORKSPACE: {path_offset}")


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

        print( f"\n> {len(globs)} enrichment data assets in multi-layer-graph workspace." )
        s_in_bytes = gqws.get_size(path)

        print( f"> Data asset path : {path}")
        print( f"> Total capacity  : {s_in_bytes/1024/1024:.2f} MB.")

    elif cmd=="init":
        print( f"CMD: {cmd} <verbose:{verbose}>")
        print( "Initialize a new data asset. (Feature comming soon!)")

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
        dassetExist = os.path.exists(path)
        if dassetExist:
            print( f"<{answer}> is your selection\n > ... ready to remove the dataset." )
        else:
            print( f"*** WARNING *** The data asset <{answer}> does not exist." )
            exit()

    else:
        print( f"CMD {cmd} <verbos:{verbose}> not yet implemented.")

if __name__ == '__main__':
    plac.call(main)