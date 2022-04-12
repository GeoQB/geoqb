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

import geoanalysis.geoqb.geoqb_workspace as gqws

#####################################################
#  Extracted data will be stored in this folder.
#  - it can be a mounted Google Drive folder, or a volume, or a local path.
#
#path_offset = "./workspace"
path_offset = gqws.prepareWorkspaceFolders( verbose=False )
WORKPATH = f"{path_offset}/sample_clusters/" # needed by individual tools ...

import glob
import plac
from pathlib import Path
import json

from datetime import datetime



def main( cmd: ('(ls|init|clear)'), folder: ('(md|raw|stage)' ), verbose=False, ):

    print( f"ENV GEOQB_WORKSPACE: {path_offset}")
    if cmd=="ls":
        if folder=="md":
            print( f"CMD: {cmd} <verbos:{verbose}>")
            globs = glob.glob(f"{path_offset}/{folder}/*")
            locs = {}
            for g in globs:
                if verbose:
                    print( g )
                p = g[len(path_offset)+4:].split("_")[0]
                locs[p]=g
        print( f"\n> {len(globs)} individual layers in multi-layer-graph workspace." )
        print( f"> {len(locs)} locations." )
        print( f"> {locs.keys()}" )
        s_in_bytes = gqws.get_size()
        print( f"> Total capacity: {s_in_bytes/1024/1024/1024:.2f} GB.")


    elif cmd=="init":
        print( f"CMD: {cmd} <verbos:{verbose}>")
        gqws.prepareWorkspaceFolders( verbose=True )

    elif cmd=="clear":
        fn = gqws.getWorkspaceFolder()
        answer = input(f"> CLEAR WORKSPACE {fn} : [PLEASE CONFIRM] with Yes!  : " )
        if not answer=="Yes!":
            print( f"> Your data is still available in {fn}.")
            exit()
        else:
            s_in_bytes = gqws.get_size()
            print( f"> Ready to delete ... {s_in_bytes/1024/1024} MB.")
            gqws.soft_delete()

        fn = gqws.getWorkspaceFolder()
        gqws.prepareWorkspaceFolders( verbose=False )

    else:
        print( f"CMD {cmd} <verbos:{verbose}> not yet implemented.")

if __name__ == '__main__':
    plac.call(main)