
import geoanalysis.geoqb.geoqb_workspace as gqws
import geoanalysis.geoqb.data4good.HighResolutionPopulationDensityMapsAndDemographicEstimates as d4g_population
import geoanalysis.geoqb.geoqb_tg as gqtg
import geoanalysis.geoqb.geoqb_kafka as gqkafka
import geoanalysis.geoqb.geoqb_layers as gql

import glob
import os
path_offset = gqws.prepareWorkspaceFolders( verbose=False )
WORKPATH = f"{path_offset}/sample_clusters/" # needed by individual tools ...

def selectLayer():
    return "Aue"

def selectAsset( cmd, verbose ):
    path1 = f"{path_offset}stage/*"
    print( f"CMD: {cmd} <verbose:{verbose}>\n")
    globs = glob.glob( path1 )
    locs = {}
    i=1
    selected = ""
    for g in globs:
        p = g[len(path_offset)+6:].split("_")[0]
        locs[p]=g
        print( f"[{i}]    {p} - {g}" )
        selected = p
        i = i + 1

    answer = input(f"\n> Which data asset should be blended into a layer ? [{selected}] : " )
    if answer=="":
        answer = selected
    path = f"{path_offset}stage/{answer}"
    dassetExist = os.path.exists(path) and len(path) > 1
    if dassetExist:
        print( f"<{answer}> is your selection\n > ... ready to start blending process." )
        return answer
    else:
        print( f"*** WARNING *** The data asset <{answer}> does not exist." )
        exit()