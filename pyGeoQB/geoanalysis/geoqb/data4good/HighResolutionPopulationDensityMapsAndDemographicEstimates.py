#####
#
# .Module to access public demographic data from Data4Good project
#

import sys
sys.path.append('./')

import pandas as pd

import geoanalysis.geoqb.geoqb_workspace as gqws
import geoanalysis.geoqb.geoqb_h3 as gqh3

#########################
#
# Dataset Metadata ...
#
INFO_URL="https://data.humdata.org/dataset/germany-high-resolution-population-density-maps-demographic-estimates"

DOWNLOAD_URLS={
    "population_deu.csv.zip" : "https://data.humdata.org/dataset/7d08e2b0-b43b-43fd-a6a6-a308f222cdb2/resource/77a44470-f80a-44be-9bb2-3e904dbbe9b1/download/population_deu_2019-07-01.csv.zip",
}

FILE_NAMES=["population_deu_2019-07-01.csv"]
#
#########################



#######################################
#
# Local context ....
#
WORKPATH=gqws.prepareWorkspaceFolders()
DS_STAGE_PATH=WORKPATH+"/stage/data4good/"


def getDumpFileName( SUFFIX="" ):
    return DS_STAGE_PATH + f"/dump_temp_enrichment{SUFFIX}.csv.zip"

#
# The staged data file is used to blend the input data.
# Small datasets can be handled easily with Pandas, and larger data will be processed via PySpqrk.
#
def getDataFrame_linked_by_h3Index( dfIndexesToEnrich, indexColumn="h3index", res=9, dumpFile=True, SUFFIX="-snip" ):

    print( dfIndexesToEnrich )
    FN = DS_STAGE_PATH + FILE_NAMES[0]
    print( f">>> Read data file: {FN}")
    enrichmentData = pd.read_csv( FN, sep="," )
    print( enrichmentData )

    print( f">>> Calc h3index ...")
    enrichmentData["h3index"] = enrichmentData.apply( lambda x : gqh3.h3Index_lat_lon_level_NO_LABEL( x["Lat"], x["Lon"], res ), axis = 1 )
    print( enrichmentData )

    joined = pd.merge( dfIndexesToEnrich, enrichmentData, left_on='Id', right_on='h3index' )

    print( f">>> Add Metadata ...")
    enrichmentData = joined.drop_duplicates(subset='h3index', keep="last")
    enrichmentData["res"] = res
    enrichmentData["source"] = "data4good.population"
    enrichmentData["t"] = "2019"
    enrichmentData["factID"] = "demographics.population"

    print( enrichmentData )

    if dumpFile :
        fn = getDumpFileName( SUFFIX=SUFFIX )
        enrichmentData.to_csv( fn , index=True, sep ='\t')

    return enrichmentData


def blendIntoMultilayerGraph( conn, df ):

    df = df.drop_duplicates(subset='h3index', keep="last")
    df["t"] = df["t"].astype(str)

    print( "> Nodes ... ")
    zN = conn.upsertVertexDataFrame(
        df=df, vertexType='fact', v_id='factID',
        attributes={'source':'source' } )

    print( "> Edges ... ")
    zE = conn.upsertEdgeDataFrame(
        df=df,
        sourceVertexType='h3place',
        edgeType='observed_at',
        targetVertexType='fact',
        from_id='h3index',
        to_id='factID',
        attributes={ 'value':'Population', 'time':'t' } )

    print( f"UPLOAD STATS: {zN} nodes {zE} edges added to the graph." )



def enrich( conn, df ):
    fn = getDumpFileName()
    print(f">>> Local join in data file ... {fn}")
    df = getDataFrame_linked_by_h3Index( df )
    print(f">>> Blending the data in the graph with data from ... {fn}")
    blendIntoMultilayerGraph( conn, df )


