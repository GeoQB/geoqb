import os

######################################################
#  Make sure that we have workspace folder and some maintenance functions ...
#

from pathlib import Path
from os.path import exists
import os
import shutil
from pathlib import Path


def getFileHandle( path="", fn="f1.dat", mode="w" ):
    WORKPATH = os.environ.get('GEOQB_WORKSPACE')
    # print("***>>> " + WORKPATH )
    #print("***--- " + path )

    file = open( WORKPATH + "/" + path + fn, mode)
    return file

def getWorkspaceFolderTRASH():
    path_tc = os.environ.get('GEOQB_WORKSPACE_TC')
    tcp = Path(path_tc)
    return tcp

def getWorkspaceFolder():
    path_offset = os.environ.get('GEOQB_WORKSPACE')
    return path_offset




def soft_delete():
    source = getWorkspaceFolder()
    destination = getWorkspaceFolderTRASH()
    # TODO: Stop if destination exists already.
    dest = shutil.move(source, destination)
    print("> Destination path:", dest)

def get_size():
    start_path = getWorkspaceFolder()
    return get_size( start_path )

def get_size(start_path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)

    return total_size # in bytes

def prepareWorkspaceFolders( verbose=True):

    path_offset = os.environ.get('GEOQB_WORKSPACE')

    required_dirs = ["single_layer_images", "multi_layer_images", "graph_layers", "graph_layers/vertexes", "graph_layers/edges", "graph_layers/grid", "raw", "md", "dumps", "stage"]

    if verbose:
        print( f"ENV GEOQB_WORKSPACE: {path_offset}")
        print( f">>> Verify GeoQB-Workspace folder structure: {path_offset}")

        for d in required_dirs:
            fn = path_offset+d
            Path(fn).mkdir(parents=True, exist_ok=True)
            file_exists = exists(fn)
            if verbose:
                print( f"         (exists:={file_exists}) : {fn} ")
        print( f">   Workspace inspection done.")

    return path_offset


def describeWorkspace( verbose=True ):

    path_offset = os.environ.get('GEOQB_WORKSPACE')

    required_dirs = ["single_layer_images", "multi_layer_images", "graph_layers", "graph_layers/vertexes", "graph_layers/edges", "graph_layers/grid", "raw", "md", "dumps", "stage"]
    print( f"\n>>> GeoQB-Workspace folder structure: {path_offset}")

    status = True

    for d in required_dirs:
        fn = path_offset+d
        Path(fn).mkdir(parents=True, exist_ok=True)
        file_exists = exists(fn)
        status = status and file_exists
        if verbose:
            print( f" > (exists:={file_exists}) : {fn} ")
    print( f" > Workspace status: READ TO USE := {status}.")




