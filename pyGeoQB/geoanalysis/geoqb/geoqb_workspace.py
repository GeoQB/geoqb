import os

######################################################
#  Make sure that we have workspace folder ...
#
from pathlib import Path
from os.path import exists



def getFileHandle( path="", fn="f1.dat" ):

    WORKPATH = os.environ.get('GEOQB_WORKSPACE')
    file = open( WORKPATH + path + fn, "w")

    return file


def prepareWorkspaceFolders( verbose=True):

    WORKPATH = os.environ.get('GEOQB_WORKSPACE')

    required_dirs = ["single_layer_images", "multi_layer_images", "graph_layers", "graph_layers/vertexes", "graph_layers/edges", "graph_layers/grid", "raw", "md", "dumps", "stage"]

    if verbose:
        print( f">>> Verify GeoQB-Workspace folder structure: {WORKPATH}")

    for d in required_dirs:
        fn = WORKPATH+d
        Path(fn).mkdir(parents=True, exist_ok=True)
        file_exists = exists(fn)
        if verbose:
            print( f">   {fn} --> (file_exists= {file_exists})")

    if verbose:
        print( f">>> DONE.")

    return WORKPATH
