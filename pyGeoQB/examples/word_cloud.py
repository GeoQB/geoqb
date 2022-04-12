# -*- coding: utf-8 -*-

import sys
sys.path.append('./')

import warnings
warnings.filterwarnings('ignore')

import os

from sklearn.cluster import KMeans
import numpy as np

from os.path import exists
from sklearn.manifold import TSNE
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from node2vec import Node2Vec
import pandas as pd
from gensim.models import KeyedVectors
from gensim.models import Word2Vec


from urllib.request import urlopen
import json
import flat_table
import plotly.express as px
from string import Template

import geoanalysis.geoqb.geoqb_workspace as gqws

import geoanalysis.geoqb.geoqb_tg as gqtg



path_offset = gqws.prepareWorkspaceFolders()




#
# a working path within the workspace ...
#
WORKPATH = path_offset + "/ga_2_node2vec_kmeans/"
results = pd.read_csv( f"{WORKPATH}/nodeLabels.tsv", sep ='\t', names=['v_id', 'cluster'])

print( results )



dfr = pd.DataFrame(results, columns=('v_id','cluster'))

pattern="https"

dfr['USE'] = dfr['v_id'].str.contains(pattern)



dfr1 = dfr[dfr['USE'] == False]

pattern="ffff"

dfr1['USE'] = dfr1['v_id'].str.contains(pattern)
DFR2 = dfr1[dfr1['USE'] == False]

print( DFR2 )



gr = DFR2.groupby("cluster")


print( gr )
print( type(gr) )


gb_groups = gr.groups
print(gb_groups)
print( gb_groups.keys() )

from wordcloud import WordCloud

for i in range(0,8):
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
