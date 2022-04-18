#####
#
# .Module to access public demographic data from Data4Good project
#

import sys
sys.path.append('./')
import os
import pandas as pd
import geoanalysis.utils.asset_loader as asl
import geoanalysis.geoqb.geoqb_workspace as gqws
import geoanalysis.geoqb.geoqb_h3 as gqh3

#########################
#
# Dataset Metadata ...
#
INFO_URL="https://data.humdata.org/dataset/germany-high-resolution-population-density-maps-demographic-estimates"

DOWNLOAD_URLS={
    "population_deu_2019-07-01.csv.zip" : "https://data.humdata.org/dataset/7d08e2b0-b43b-43fd-a6a6-a308f222cdb2/resource/77a44470-f80a-44be-9bb2-3e904dbbe9b1/download/population_deu_2019-07-01.csv.zip",
}

FILE_NAMES=["population_deu_2019-07-01.csv.zip"]
#
#########################



#######################################
#
# Local context ....
#
WORKPATH=gqws.prepareWorkspaceFolders()
DS_STAGE_PATH="/stage/data4good/"
FULL_DS_STAGE_PATH=WORKPATH+DS_STAGE_PATH


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
    enrichmentData = pd.read_csv( FN, sep=",", compression="zip" )
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


def clean():
    i = 0

    for k in DOWNLOAD_URLS:
        print(f"{i} {k}" )
        localFile = gqws.getFileHandle( DS_STAGE_PATH, k, 'wb' )
        os.remove( localFile.name )
        print(f"> Deleted the staged file {localFile.name}")


def get_size():
    start_path = FULL_DS_STAGE_PATH
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



def init():

    i = 1

    for k in DOWNLOAD_URLS:
        print(f"({i}) => {k}" )
        localFile = gqws.getFileHandle( path=DS_STAGE_PATH, fn=k, mode='wb' )
        fn = localFile.name
        localFile.close()

        myUrl = DOWNLOAD_URLS[k]
        print( myUrl )
        print(f"> Start loading a data asset into stage: {DS_STAGE_PATH}")
        #asl.DownloadFile( myUrl, localFile )
        #asl.download_v2( myUrl, fn )
        asl.dlf( myUrl, fn )
        i = i + 1
        print( F"> After the DOWNLOAD is finished, your data is stored in <{localFile.name}>")


def getTargetSize():
    return 250 # MB

def describe():
    i = 1
    s = get_size( FULL_DS_STAGE_PATH ) / (1024*1024)
    ts = getTargetSize();
    for k in DOWNLOAD_URLS:

        print(f"({i}) => {k} :: [estimated size: {ts} MB]" )
        localFile = gqws.getFileHandle( DS_STAGE_PATH, k, 'wb' )
        myUrl = DOWNLOAD_URLS[k]
        print(f"> Data asset can be (re)loaded\n  from : [{myUrl}]\n  into : <{DS_STAGE_PATH}>  ({s} MB)")
        print( f"")
