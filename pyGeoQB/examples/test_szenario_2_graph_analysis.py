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

sns.set_style('whitegrid')

#####################################################
#  Some variables ...
#
SECRET = os.environ.get('TG_SECRET')
path_offset = gqws.prepareWorkspaceFolders()

#
# a working path within the workspace ...
#
WORKPATH = path_offset + "/ga_2_node2vec_kmeans/"


######################################################
#  Make sure that we have workspace folder ...
#
from pathlib import Path
Path(WORKPATH).mkdir(parents=True, exist_ok=True)

#######################################################
# Connection to TigerGraph
#
graph_name = "OSMLayers_Demo6a"
conn, token = gqtg.initTG( graph_name = graph_name, secretalias="demo6a", secret=SECRET )
print( conn )


#######################################################
# Query the graph data from stage ...
#
print(">>> Start graph extraction ...")
dfNodes, dfEdges = gqtg.getFullGraph2( conn, graph_name, WORKPATH=WORKPATH )
print(">   Graph data loaded ...")

#print(dfNodes)
#print(dfEdges)

# Create a graph using networkx library ...
graph = nx.from_pandas_edgelist(dfEdges, 'Source', 'Target')

print(">>> Networkx-graph constructed ...")

#
# NODE2VEC Algorithmus ... (from: https://github.com/eliorc/node2vec/blob/master/README.md)
#
#EDGES_EMBEDDING_FILENAME=WORKPATH+"/edges_embedding_f1.txt"
EMBEDDING_FILENAME=WORKPATH+"/node_embedding_f2.txt"
EMBEDDING_MODEL_FILENAME=WORKPATH+"/embedding_model.txt"

file1_exists = exists(EMBEDDING_MODEL_FILENAME)
file2_exists = exists(EMBEDDING_FILENAME)

if file1_exists and file2_exists:

  # Load model after Node2Vec.save
  model = Word2Vec.load(EMBEDDING_MODEL_FILENAME)

  # Load model after Node2Vec.wv.save_word2vec_format
  #model = KeyedVectors.load_word2vec_format(EMBEDDING_FILENAME)

  print( ">>> Node2Vec model loaded. " )

else:

  # Precompute probabilities and generate walks - **ON WINDOWS ONLY WORKS WITH workers=1**
  node2vec = Node2Vec(graph, dimensions=64, walk_length=10, num_walks=25, workers=4)  # Use temp_folder for big graphs

  # Embed nodes
  model = node2vec.fit(window=10, min_count=1, batch_words=4)  # Any keywords acceptable by gensim.Word2Vec can be passed, `dimensions` and `workers` are automatically passed (from the Node2Vec constructor)

  # Save embeddings for later use
  model.wv.save_word2vec_format(EMBEDDING_FILENAME)

  # Save model for later use
  model.save(EMBEDDING_MODEL_FILENAME)

  print( ">>> Node2Vec model created and stored. " )


#############################################################
#
# We have the model data saved and can reuse it later.
#
#############################################################








print( ">>> Embed edges using Hadamard method.")
from node2vec.edges import HadamardEmbedder

edges_embs = HadamardEmbedder(keyed_vectors=model.wv)

embeddings = np.array([model.wv[x] for x in model.wv.index_to_key])

tsne = TSNE(n_components=2, random_state=7, perplexity=15)

embeddings_2d = tsne.fit_transform(embeddings)

figure = plt.figure(figsize=(11, 9))

ax = figure.add_subplot(111)

ax.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1])
fn=WORKPATH + "/embeddings_2d.png"
plt.savefig(fn)
plt.clf()
print( f">  2D embeddings are plotted in {fn}.")
print( ">>> Done.")


print(" >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
print(" > Examples: compare some nodes:")

try:
  print (model.wv.similarity('861f18807ffffff', '861f18807ffffff'))
  print (model.wv.similarity('861f18807ffffff', '861f1895fffffff'))
  print (model.wv.most_similar(positive=['861f18807ffffff'], negative=[], topn=5))
except:
  print( "    Test nodes not available .... but this is not a problem. Let's continue. ")

print(" >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import numpy as np

#Load Data
X=model.wv.vectors
nodeNames = model.wv.index_to_key

#Transform the data
pca = PCA(5)
df = pca.fit_transform(X)
#df.shape

#X = np.loadtxt(EMBEDDING_FILENAME, skiprows=1,) # load the embedding of the nodes of the graph
#print(X)
# sort the embedding based on node index in the first column in X
#X=X[X[:,0].argsort()]; 
#print(X)

Z=X[0:X.shape[0],1:X.shape[1]]; # remove the node index from X and save in Z

kmeans = KMeans(n_clusters=8, random_state=0).fit(Z) # apply kmeans on Z
labels=kmeans.labels_  # get the cluster labels of the nodes.

dfkmeans = KMeans(n_clusters=8, random_state=0).fit_predict(Z) # apply kmeans on Z

print( type(dfkmeans) )

print( dfkmeans[0] )

#predict the labels of clusters.
dfLabel = kmeans.fit_predict(Z)
print(dfLabel)

results = np.array(list(zip(nodeNames,dfLabel)))

dfr = pd.DataFrame(results, columns=('v_id','cluster'))
print( dfr )



gr = dfr.groupby("cluster") #.count()
print( gr )

from wordcloud import WordCloud

for i in range(0,8):
  group = gr.get_group(str(i))

  text2 = "\n ".join(v_id for v_id in group.v_id)
  fn = f"{WORKPATH}/cluster_{i}.json"
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

#predict the labels of clusters.
label = kmeans.fit_predict(Z)

#Getting unique labels
u_labels = np.unique(label)

#Getting the Centroids
centroids = kmeans.cluster_centers_



for x in range( 0,5 ):
  for y in range( 0,5 ):
    if x < y:
      plt.clf()
      #plotting the results:
      for i in u_labels:
        plt.scatter(df[label == i , x] , df[label == i , y] , label = i)
      plt.scatter(centroids[:,x] , centroids[:,y] , s = 50, color = 'blue')
      plt.title( str(x) + " - " + str(y) )
      plt.legend()
      plt.savefig( f"{WORKPATH}/kmeans-clustering-of-node-vectors-{x}-{y}.png")

exit()

print(">>> PCA and K-Means culstering analysis done ...")
print(f">   Results are stored in {WORKPATH} ...")




