# -*- coding: utf-8 -*-

import os
import sys
sys.path.append('./')

import warnings
warnings.filterwarnings('ignore')

from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd

import geoanalysis.geoqb.geoqb_workspace as gqws
import geoanalysis.utils.clip_board_tool as cbt




def create_word_clouds_from_vIds_per_cluster( WORKPATH=None, CLUSTER_FILE=None,
                                              names=['v_id', 'cluster'],
                                              skipPatterns = [ "https", "ffff" ],
                                              zClusters=8, hideNote=False):

    path_offset = gqws.prepareWorkspaceFolders()

    #
    # a working path within the workspace ...
    #
    if WORKPATH is None:
        WORKPATH = path_offset + "/ga_2_node2vec_kmeans/"

    if CLUSTER_FILE is None:
        CLUSTER_FILE = f"{WORKPATH}/nodeLabels.tsv"

    results = pd.read_csv( CLUSTER_FILE, sep ='\t', names=['v_id', 'cluster'])

    #('v_id','cluster')
    columns = ( names[0], names[1] )

    dfr = pd.DataFrame(results, columns=columns)

    print( dfr )

    dfrFiltered = None

    for pattern in skipPatterns:

        if dfrFiltered is not None:
            dfr = dfrFiltered

        dfr['USE'] = dfr['v_id'].str.contains(pattern)

        dfrFiltered = dfr[dfr['USE'] == False]

    if dfrFiltered is None:
        dfrFiltered = dfr


    print( dfrFiltered )
    gr = dfrFiltered.groupby("cluster")

    gb_groups = gr.groups
    print(gb_groups)
    print( gb_groups.keys() )
    clusterIds = gb_groups.keys()

    for i in clusterIds:
        print( gb_groups[i] )
        group2 = gr.get_group(i)
        print(group2)

        text2 = "\n ".join(v_id for v_id in group2.v_id)
        fn = f"{WORKPATH}/cluster_{i}.txt"
        f = open( fn, "w")
        f.write( text2 )
        f.close()

        # Creating word_cloud with text as argument in .generate() method

        word_cloud2 = WordCloud(collocations = True, background_color = 'white').generate(text2)

        # Display the generated Word Cloud

        plt.imshow(word_cloud2, interpolation='bilinear')
        fn = f"{WORKPATH}/cluster_{i}.png"
        plt.axis("on")
        plt.savefig(fn)
        plt.clf()
        #plt.show()

    print( f"> Word-cloud from cluster ids using COLUMNS {names} and SKIP_PATTERNS {skipPatterns} has been created in {WORKPATH}.")

    if not hideNote:
        cbt.add_to_clipboard(WORKPATH)

if __name__ == '__main__':

    skipPatterns = [ 'ffff', 'https:' ]
    create_word_clouds_from_vIds_per_cluster( skipPatterns=skipPatterns, hideNote = True )
