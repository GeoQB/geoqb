######################################################################
#
# The pyGeoQB CLI wraps around the demo scripts and core functions.
#
######################################################################
# GeoQB dependencies ...
#
import click
import sys
sys.path.append('./')

import glob
import geoanalysis.geoqb.geoqb_workspace as gqws
import geoanalysis.geoqb.geoqb_kafka as gqkafka
import geoanalysis.geoqb.geoqb_profiles as gqprofile
import plac

import geoanalysis.geoqb.data4good.HighResolutionPopulationDensityMapsAndDemographicEstimates as asset1

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



def main( cmd: ('(ls|init|describe|clear|delete)'), folder: ('(md|raw|stage)','option',"f" ), verbose=False, ):

    print( f"ENV GEOQB_WORKSPACE: {path_offset}")

    if folder is None:
        folder = "md"

    if cmd=="ls":

        if folder=="md":

            print( f"CMD: {cmd} <verbose:{verbose}>")
            globs = glob.glob(f"{path_offset}/{folder}/*")
            locs = {}
            for g in globs:
                if verbose:
                    print( g )
                p = g[len(path_offset)+4:].split("_")[0]
                locs[p]=g
            print("\n-----------------------------")
            print("  LAYERS in GeoQB workspace")
            print("-----------------------------")
            print( f"> {len(globs)} individual layers in multi-layer-graph workspace." )
            print( f"> {len(locs)} locations." )
            s_in_bytes = gqws.get_size(path_offset)
            print( f"> Total capacity: {s_in_bytes/1024/1024/1024:.2f} GB.")

            i = 0
            sep = ""
            layerNames = ""
            for dk in locs.keys():
                layerNames = layerNames + sep + dk
                i = i + 1
                if i > 0 :
                    sep = ", "

            if ( i > 0 ):
                print( f"\n* [{layerNames}]" )
            print()


            print("\n---------------------------------")
            print("  DataAssets in GeoQB workspace")
            print("---------------------------------")
            asset1.describe()

    elif cmd=="init":
        print( f"CMD: {cmd} <verbose:{verbose}>")
        gqws.prepareWorkspaceFolders( verbose=True )

        answer = input(f"> Reload data assets? [PLEASE CONFIRM] with Yes!  : " )
        if not answer=="Yes!":
            print( f"> Your data is still available in {fn}.")
            exit()
        else:
            asset1.init()
            asset1.describe()
        print()

    elif cmd=="describe":
        gqws.describeWorkspace( verbose=True )
        gqkafka.describeCluster()
        gqprofile.describeSolidDatapod()
        print()

    elif cmd=="delete":
        fn = gqws.getWorkspaceFolder()
        answer = input(f"> DELETE WORKSPACE {fn} : [PLEASE CONFIRM] with Yes!  : " )
        if not answer=="Yes!":
            print( f"> Your data is still available in {fn}.")
            exit()
        else:
            s_in_bytes = gqws.get_size(fn)
            print( f"> Ready to delete ... {s_in_bytes/1024/1024} MB.")
            gqws.soft_delete()

        fn = gqws.getWorkspaceFolder()
        gqws.prepareWorkspaceFolders( verbose=False )
        print()


    elif cmd=="clear":
        fn = gqws.getWorkspaceFolder()
        answer = input(f"> CLEAR WORKSPACE {fn} : [PLEASE CONFIRM] with Yes!  : " )
        if not answer=="Yes!":
            print( f"> Your data can be reloaded with 'init' command.")
            exit()
        else:
            s_in_bytes = asset1.get_size( asset1.FULL_DS_STAGE_PATH )
            print( f"> Ready to delete ... {s_in_bytes/1024/1024} MB.")
            asset1.clean()
            print( f"> Your data can be reloaded with 'init' command.")

        fn = gqws.getWorkspaceFolder()
        gqws.prepareWorkspaceFolders( verbose=False )
        print()

    else:
        print( f"CMD {cmd} <verbos:{verbose}> not yet implemented.")

if __name__ == '__main__':
    plac.call(main)