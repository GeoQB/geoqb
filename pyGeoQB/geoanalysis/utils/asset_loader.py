import requests
import pandas as pd
import re
import sys
sys.path.append('./')
import geoanalysis.geoqb.geoqb_workspace as gqws
import geoanalysis.geoqb.data4good.HighResolutionPopulationDensityMapsAndDemographicEstimates as asset1


def dlf( url, filename):
    #import requests
    #chunk_size = 4096
    #filename = "population_deu_2019-07-01.csv.zip"
    #document_url = "https://data.humdata.org/dataset/7d08e2b0-b43b-43fd-a6a6-a308f222cdb2/resource/77a44470-f80a-44be-9bb2-3e904dbbe9b1/download/population_deu_2019-07-01.csv.zip"
    #with requests.get(document_url, stream=True) as r:
    #    with open(filename, 'wb') as f:
    #        for chunk in r.iter_content(chunk_size):
    #            if chunk:
    #                f.write(chunk)
    print( "> Please use 'wget' ... ")
    cmd = f"wget -O {filename} {url}"
    print( "# " + cmd )

    dfCP=pd.DataFrame([cmd])
    dfCP.to_clipboard(index=False,header=False)
    print( "> CTRL-V + ENTER ... to copy and execute the download command ... ")


def DownloadFile(url, fileHandle):

    f = fileHandle

    r = requests.get(url)

    i = 0
    for chunk in r.iter_content(chunk_size=512 * 1024):
        print( i )
        i=i+1
        if chunk: # filter out keep-alive new chunks
            f.write(chunk)
            f.flush()
            print( "." )

    f.flush()
    f.close()

    return


if __name__ == '__main__':

    i = 0

    for k in asset1.DOWNLOAD_URLS:
        print(f"{i} {k}" )
        localFile = gqws.getFileHandle( asset1.DS_STAGE_PATH, k, 'wb' )
        myUrl = asset1.DOWNLOAD_URLS[k]
        print( myUrl )
        print(f"> Start loading a data asset into stage: {asset1.DS_STAGE_PATH}")
        #DownloadFile( myUrl, localFile )

    #asset1.clean()

    #asset1.init()



