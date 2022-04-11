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
import geoanalysis.geoqb

import geoanalysis.geoqb.geoqb_workspace as gqws

#####################################################
#  Extracted data will be stored in this folder.
#  - it can be a mounted Google Drive folder, or a volume, or a local path.
#
#path_offset = "./workspace"
path_offset = gqws.prepareWorkspaceFolders( verbose=False )

import click
import json


def main():
    print("\n .... W.I.P!")

if __name__ == '__main__':
    main()