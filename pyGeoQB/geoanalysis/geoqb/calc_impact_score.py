import sys

from geopy import distance

import math
import os
import pandas as pd
import geoanalysis.geoqb.geoqb_tg as gqtg
import geoanalysis.geoqb.geoqb_workspace as gqws

def calcAverageDistanceForAllPoints1d( p1 ):
    return 1,1,1
#
# p1, p2 : pairs of (lat,lon)
#
#  The default is the WGS-84 ellipsoid,
#  https://geopy.readthedocs.io/en/stable/#module-geopy.distance
def calcDistanceInMeters( p1, p2 ):
    ##
    # #  Some dummy points can disturb our calculations
    ##
    if ( p1[0] < 1 and p1[1] < 1):
        return 0;

    if ( p2[0] < 1 and p2[1] < 1):
        return 0;

    return distance.distance(p1, p2).km

def calcAverageDistanceForAllPoints1( df ):
    df1 = df[['lat','lon']]
    df2 = df[['lat','lon']]
    return calcAverageDistanceForAllPoints2( df1, df2 )

def calcAverageDistanceForAllPoints2( df1, df2 ):
    df1['key'] = 0
    df2['key'] = 0

    #dfX = df1.sort_values(by=['lat'])
    #print( dfX )

    # to obtain the cross join we will merge on
    # the key and drop it.
    joinResult = pd.merge(df1, df2, on ='key').drop("key", 1).apply(lambda x:  calcDistanceInMeters( (x['lon_x'],x['lat_x']),(x['lon_y'],x['lat_y'])) , axis=1).reset_index(name='dist')

    mean = joinResult['dist'].mean()
    count = joinResult['dist'].count()
    max = joinResult['dist'].max()

    return mean, count, max







def calc_score( location_name, conn, WORKPATH, run, graph_name ):

    fn1 = f"impact-score-0{run}.tsv"

    file = gqws.getFileHandle( path="sample_score/", fn=fn1, mode="a" ) ### MAKE an automatic counter for placehoder x

    try:
        size = os.path.getsize( file.name )
        print( f"> FILE SIZE: {size}")
        if size < 1:
            file.write("DURATION\tLOC\tzPOS\tzNEG\tzALl\tposM\tposM/allMAX\tmath.sqrt(posZ)\tposMAX\tallM\tallM/allMAX\tmath.sqrt(allZ)\tallMAX\tnegM\tnegM/allMAX\tmath.sqrt(negZ)\tnegMAX\n")
            print( f"> Define table header ... <{file.name}>" )
        else:
            print( f"> Table is ready for appending data ... <{file.name}>" )
    except:
        pass

    from datetime import datetime

    t1 = datetime.now()

    print( f"************** Customized Impact Score for area around {location_name} **************")
    dfNodesPOS, dfEdgesPOS = gqtg.getLayer( conn, graph_name, WORKPATH=WORKPATH, overwrite=False,  s1=location_name, s2="POS" )
    dfNodesNEG, dfEdgesNEG = gqtg.getLayer( conn, graph_name, WORKPATH=WORKPATH, overwrite=False,  s1=location_name, s2="NEG" )
    #dfNodesALL, dfEdgesALL = gqtg.getLayer( conn, graph_name, WORKPATH=WORKPATH, overwrite=False,  s1=loc, s2="AllTags" )

    dfNodesALL = pd.concat([dfNodesPOS,dfNodesNEG])

    dfNodesPOS = dfNodesPOS[['lat','lon']].dropna(subset=['lat', 'lon'])
    dfNodesALL = dfNodesALL[['lat','lon']].dropna(subset=['lat', 'lon'])
    dfNodesNEG = dfNodesNEG[['lat','lon']].dropna(subset=['lat', 'lon'])

    print ( "POS", len(dfNodesPOS) )
    print ( "NEG", len(dfNodesNEG) )
    print ( "ALL", len(dfNodesALL) )

    z = len(dfNodesALL)
    tEstimate = 0.0003 * z*z + 0.0404 * z - 25.793

    print()
    print( f"Expected processing time: {tEstimate} s")


    posM, posZ, posMAX = calcAverageDistanceForAllPoints1( dfNodesPOS )

    negM, negZ, negMAX = calcAverageDistanceForAllPoints1( dfNodesNEG )

    allM, allZ, allMAX = calcAverageDistanceForAllPoints1( dfNodesALL )

    print(  "POS", posM, posM/allMAX, math.sqrt(posZ), posMAX )
    print(  "ALL", allM, allM/allMAX, math.sqrt(allZ), allMAX )
    print(  "NEG", negM, negM/allMAX, math.sqrt(negZ), negMAX )

    t2 = datetime.now()

    duration = t2-t1

    file.write(  f"{duration}\t{location_name}\t{len(dfNodesPOS)}\t{len(dfNodesNEG)}\t{len(dfNodesALL)}\t{posM}\t{posM/allMAX}\t{math.sqrt(posZ)}\t{posMAX}\t{allM}\t{allM/allMAX}\t{math.sqrt(allZ)}\t{allMAX}\t{negM}\t{negM/allMAX}\t{math.sqrt(negZ)}\t{negMAX}\n"  )
    file.flush()

    file.close()

    print( f"> PROCESSING TIME: {duration} ")
    print( f"> ESTIMATED TIME : {tEstimate} s")

    return file.name






