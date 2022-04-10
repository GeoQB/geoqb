from h3 import h3
import folium

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import requests
import json


def visualize_hexagons(hexagons, zoom=6 , color="red", folium_map=None):

    # This is  the colormap I'd like to use.

    cm = plt.cm.get_cmap('RdYlBu_r')

    """
    hexagons is a list of hexcluster. Each hexcluster is a list of hexagons.
    eg. [[hex1, hex2], [hex3, hex4]]
    """
    polylines = []
    lat = []
    lng = []

    X_min = 0
    X_max = 0

    for hexT in hexagons.keys():
        hex = hexT
        VALUE = hexagons[hex]
        if VALUE < X_min:
          X_min = VALUE
        if VALUE > X_max:
          X_max = VALUE

    X_Span = X_max - X_min

    print( X_Span , X_min, X_max )

    cstack = []

    for hexT in hexagons.keys():
        hex = hexT
        VALUE = hexagons[hex]
        #print( hex, VALUE)

        polygons = h3.h3_set_to_multi_polygon([hex], geo_json=False)
        # flatten polygons into loops.
        outlines = [loop for polygon in polygons for loop in polygon]
        polyline = [outline + [outline[0]] for outline in outlines][0]
        lat.extend(map(lambda v:v[0],polyline))
        lng.extend(map(lambda v:v[1],polyline))
        polylines.append(polyline)

        c = "white"
        if VALUE/X_max > 0.1:
          c = "yellow"
        if VALUE/X_max > 0.3:
          c = "green"
        if VALUE/X_max > 0.5:
          c = "blue"

        if VALUE == 0.0:
          c = "red"

        #c = cm(((VALUE-X_min)/X_Span))

        cstack.append(c)

    if folium_map is None:

        m = folium.Map(location=[ 50.7119248,12.7565797], zoom_start=zoom, tiles='cartodbpositron')
        #m = folium.Map(location=[sum(lat)/len(lat), sum(lng)/len(lng)], zoom_start=zoom, tiles='cartodbpositron')
    else:
        m = folium_map

    for polyline in polylines:
        c = cstack.pop(0)
        #print( c )

        my_PolyLine=folium.PolyLine(locations=polyline,weight=1,color=color, fill_color=c,)
        m.add_child(my_PolyLine)

    return m


import operator
from collections import OrderedDict

def storeTagHistogram( runId, osm_type, data, path_offset):
  sorted_store2 = sorted(data.items(), key=operator.itemgetter(1), reverse=True)
  dct = OrderedDict( sorted_store2 )

  f = open( path_offset + run_id + "_GeoQB_tag_histogram_"+ osm_type +".tsv", "w")

  for key, value in dct.items():
      f.write(str(key) + "\t" + str(value) + "\n")

  f.close()

  """
  ====================
  Horizontal bar chart
  ====================
  """
  import matplotlib.pyplot as plt
  plt.rcdefaults()
  import numpy as np
  import matplotlib.pyplot as plt

  plt.rcParams['figure.figsize'] = [24.0, 5.0]
  plt.rcParams['figure.dpi'] = 200
  plt.rcParams['savefig.dpi'] = 200

  plt.rcParams['font.size'] = 6
  plt.rcParams['legend.fontsize'] = 'small'
  plt.rcParams['figure.titlesize'] = 'small'

  fig, ax = plt.subplots()

  people = data.keys()

  y_pos = np.arange(len(people))

  performance = dct.values()

  ax.bar(y_pos, performance, align='center', color='green', ecolor='black')

  plt.xticks(np.arange(len(people)), people)

  plt.xticks(rotation=90)
  plt.yticks(rotation=90)

  ax.set_xlabel('TAGs in ' + osm_type + " :: " + path_offset + runId)

  ax.set_ylabel('COUNT')

  plt.savefig( path_offset + run_id + "_GeoQB_tag_histogram_" + osm_type + ".png" )

  #plt.show()

  plt.close(fig )

  print( "PERFORMANCE DATA STRUCTURE:" , performance )

  print( type( performance ) )

  return


def createTagHistogramPlot( run_id, data, path_offset, osm_type="nodes" ):
    storeTagHistogram( run_id, osm_type, data, path_offset )


#
#def visualize_polygon(polyline, color):
#    polyline.append(polyline[0])
#    lat = [p[0] for p in polyline]
#    lng = [p[1] for p in polyline]
#    m = folium.Map(location=[sum(lat)/len(lat), sum(lng)/len(lng)], zoom_start=8, tiles='cartodbpositron')
#    my_PolyLine=folium.PolyLine(locations=polyline,weight=8,color=color)
#    m.add_child(my_PolyLine)
#    return m



import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
from scipy.ndimage.filters import gaussian_filter

def myplot(x, y, s, bins=1000):
    heatmap, xedges, yedges = np.histogram2d(x, y, bins=bins)
    heatmap = gaussian_filter(heatmap, sigma=s)

    extent = [ xedges[0], xedges[-1], yedges[0], yedges[-1]]

    return heatmap.T, extent

def getCoordsAsList(df):
  df['coords'] = df['location'].apply( lambda x: (x.lat,x.lon) )
  coords = []
  for r in df['coords']:
    coords.append((r[0], r[1]))
  return coords

from mpl_toolkits.axes_grid1 import make_axes_locatable

def plotBoundingBoxPOIs( path_offset, run_id, coords, title, bins ):
  print( ">>> FUNCTION:  plotBoundingBoxPOIs( path_offset, runId, coords, title, bins ):" )
  if len(coords) < 1:
    print( "   * nr of item: " + str(len(coords)) + " .... NOTHING TO DO .... RETURN." )
    return
  else:
    print( "   * nr of item: " + str(len(coords)) + " .... LET'S PLOT." )


  # Convert coordinates into numpy array
  X = np.array(coords)
  ## Map collected data ...
  x = X[:, 1]
  y = X[:, 0]

  print( min( x ) , max( x ) )
  print( min( y ) , max( y ) )

  fig, axs = plt.subplots(2, 2)
  fig.set_size_inches(18.5, 10.5)

  sigmas = [0, 16, 32, 64]

  for ax, s in zip(axs.flatten(), sigmas):
      if s == 0:
          ax.plot(x, y, 'k.', markersize=5)
          ax.set_title(title)
      else:

          img, extent = myplot(x, y, s, bins)

          ax.imshow(img, extent=extent, origin='lower', cmap=cm.jet, )
          ax.set_title("Smoothing with  $\sigma$ = %d" % s)

  #plt.show()
  fig.savefig( path_offset + run_id + "_" + title + "_POI_distribution.png", dpi=100)
  plt.close( fig )


def reloadOrDumpNamedQueryAsJSON( query, nq, title, path_offset, fnRawOSMResponse, forceReload=True ):

    data = ""

    fileName = path_offset + fnRawOSMResponse

    if not forceReload:

        try:
            f = open( fileName )
            f.close()

            print("Load data from File: " + fileName + ".")

            # Do something with the filecontent ...
            with open(fileName) as json_file:
                data = json.load(json_file)

            # print( data )
            return data


        except IOError:

            print("File: " + fileName + " not accessible. Load data from OverPass API.")
            print( ">>> force reload .... ")

    #overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_url = "https://overpass.kumi.systems/api/interpreter"

    print( query )
    print( nq )
    print( title )

    response = requests.get(overpass_url,
                            params={'data': query})
    print( response )

    data = response.json()

    print( data )

    f2 = open( fileName, 'w' )
    json.dump(data, f2)
    f2.close()

    return data


def plotNamedQuery( data, nq, title, path_offset ):

  # Collect coords into list
  coords = []
  for element in data['elements']:
    if element['type'] == 'node':
      lon = element['lon']
      lat = element['lat']
      tags = element['tags']
      coords.append((lon, lat,tags))
    elif 'center' in element:
      lon = element['center']['lon']
      lat = element['center']['lat']
      tags = element['tags']
      coords.append( (lon, lat, tags) )

  if len(coords) < 1:
    print( "nr of item:" + str( len(coords) ) )
    return
  else:
    print( "nr of item:" + str( len(coords) ) )

  plotCoordinatesForNamedQuery( coords, nq, title, path_offset=path_offset )

def plotCoordinatesForNamedQuery( coords, nq, title, path_offset ):

  # Convert coordinates into numpy array

  #print( type(coords) )
  #print( len(coords) )

  # maybe a layer is empty ...
  if len(coords) == 0:
      #coords = [(0,0, {"dummy-osm-tag1","dummy-osm-tag2"} )]
      coords = [(0,0,[1],"-")]

  #print( type(coords[0]) )
  #print( coords[0] )

  coords2 = []
  for c in coords:
      coords2.append( ( float(c[0]), float(c[1]), 1.0 ) )

  X = np.array(coords2)

  plt.plot(X[:, 0], X[:, 1], 'x')
  plt.title( title )
  plt.xlabel('Longitude')
  plt.ylabel('Latitude')
  plt.axis('equal')
  #plt.show()

  fig, axs = plt.subplots(2, 2)
  fig.set_size_inches(18.5, 10.5)

  ## Map collected data ...
  X = np.array(coords)
  x = X[:, 0].astype(np.float)
  y = X[:, 1].astype(np.float)

  #print( type(x) )
  #print( type(y) )

  #z = X[:, 2]

  sigmas = [0, 12, 24, 48]

  for ax, s in zip(axs.flatten(), sigmas):
      if s == 0:
          ax.plot(x, y, 'k.', markersize=5)
          ax.set_title(title)
      else:
          img, extent = myplot(x, y, s)
          ax.imshow(img, extent=extent, origin='lower', cmap=cm.jet)
          ax.set_title("Smoothing with  $\sigma$ = %d" % s)

  #plt.show()
  fig.savefig( path_offset + "/" + nq + "-" + title +'.png', dpi=100)

  plt.close( fig )
  return coords, X
