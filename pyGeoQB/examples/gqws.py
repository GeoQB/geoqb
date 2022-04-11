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

import glob
import plac
from pathlib import Path
import json

from datetime import datetime



def main(ws, cmd='ls', verbose=False, folder='md'):
    print( f"ENV GEOQB_WORKSPACE: {path_offset}")
    if cmd=="ls":
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
    else:
        print( f"CMD {cmd} <verbos:{verbose}> not yet implemented.")

if __name__ == '__main__':
    plac.call(main)