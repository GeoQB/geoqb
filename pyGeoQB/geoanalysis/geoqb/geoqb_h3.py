from h3 import h3

import overpass
import os

overPass_URL1=os.environ.get('overpass_endpoint')

# "https://overpass-api.de/api/interpreter"
api = overpass.API(endpoint=overPass_URL1)


#
# Calculate the H3 Index for a pair of coordinates (lat,lon)
# at a default resolution of 10
#
def h3Index(location,resolution=10):
  lat, lon = location.lat, location.lon
  return h3Index_lat_lon_level( lat, lon, res )



#
# Calculate the H3 Index for a pair of coordinates (lat,lon)
# at a resolution defined by argument
#
def h3Index_lat_lon_level( lat, lon, resolution ):
  #print( type(resolution) )
  #print( resolution )
  h3index = h3.geo_to_h3(lat, lon, resolution)
  return "h3("+str(resolution)+")_"+h3index

def getIndexAndZoomFrom_h3IndexString( indexString, verbose = False ):
    h3index = indexString.split("_")[1]
    res = indexString.split("_")[0].split("(")[1].split(")")[0]
    if verbose:
        print( h3index )
        print( res )
    return h3index, res

def lat_lon_from_h3Index2( h ):
    geo = h3.h3_to_geo( h )
    return geo

def lat_lon_from_h3Index( h, type, expected_type ):
    if type == expected_type:
        geo = h3.h3_to_geo( h )
    else:
        geo = ( None, None )
    return geo

def h3Index_lat_lon_level_NO_LABEL( lat, lon, resolution ):
  h3index = h3.geo_to_h3(lat, lon, resolution)
  return h3index


def get_listOfIndexes_zoom_in_N_neighbors( index, N, verbose=False):

    res = h3.h3_get_resolution(index)
    if verbose:
        print( res )

    listOfIndexes=[]
    listOfIndexes.append( index )

    return h3.k_ring(index, k=1)


def get_listOfIndexes_zoom_in_N( index, N, verbose=False):
    res = h3.h3_get_resolution(index)
    if verbose:
        print( res )

    listOfIndexes=[]
    listOfIndexes.append( index )

    return h3.uncompact( listOfIndexes, res+N )


def getLocationCoordinatesAndH3IndexFromPoint( location, resolution ):

    s = location[6 : len(location)-1 ]

    parts = s.split(", ")

    lat = float(parts[0])
    lon = float(parts[1])

    print( "lat: ", lat, " lon:", lon)

    myBBCenter_h3index = h3Index_lat_lon_level( lat, lon, resolution )

    return lat, lon, myBBCenter_h3index, "No location query needed.", location

#
# Request coordinates for a location from Overpass API and
# calculate H3 index.
#
# Return all elements for the particular location
#
def getLocationCoordinatesAndH3Index( location, resolution, verbose = False ):

  location_nodeQuery = 'node["name"="' + location + '"];'

  print( ">>> Location-Name to Coordinates Query via OverPass : " + location_nodeQuery )

  response = api.get( location_nodeQuery )

  #
  # What format is this?
  #   class 'geojson.feature.FeatureCollection' from GeoJSON it is.
  #
  # We get a set of features of multiple types, e.g., point, feature, ...
  #
  print( response )
  #print( type(response) )
  print( f">>> Response length: {len( response)}" )

  lat = response["features"][0]["geometry"]["coordinates"][1]
  lon = response["features"][0]["geometry"]["coordinates"][0]


  if verbose:
      print( response["features"][0]["geometry"]["coordinates"] )
      print( "lat: ", lat, " lon:", lon)

  myBBCenter_h3index = h3Index_lat_lon_level( lat, lon, resolution )

  return lat, lon, myBBCenter_h3index, location_nodeQuery, response



def getHexHistograms( data, resolution ):
  X = data
  z = len(X)

  counts = {}
  i = 0
  for loc in X:
    i = i + 1
    #print( (str(i * 100.0 / z) + " % - ", loc ) )
    index = h3Index_lat_lon_level( loc[1], loc[0], resolution )
    INDEX = index.split("_")[1]
    v = 1
    if INDEX in counts.keys():
      v = counts[INDEX]
      v = v + 1
    counts[INDEX] = v

  print( resolution, len( counts ) )
  return counts



def getLinks_and_Counters( coords_WithTags, resolution=6, verbose = False ):

  links = {}
  z = len(coords_WithTags)
  #print( z )
  #print( type(coords_WithTags) )

  if verbose:
    print(coords_WithTags)
    #print( type( coords_WithTags ) )

  counts = {}
  i = 0

  # XX = coords_WithTags.tolist()
  XX = coords_WithTags

  for loc in XX:
      #print( "---" + str( loc ) + "---" )
      #print( "***" + str(type( loc )) + "***" )
      #print( "---" + str( loc ) + "---" )
      i = i + 1

      #print( (str(i * 100.0 / z) + " % - ", loc ) )
      index = h3Index_lat_lon_level( loc[1], loc[0], resolution )
      INDEX = index.split("_")[1]

      v = 1
      if INDEX in counts.keys():
        v = counts[INDEX]
        v = v + 1
        # print( "INDEX: " + INDEX)

      counts[INDEX] = v

      #print( loc[2] )
      #print( type(loc[2]) )

      for tagKV in loc[2]:

        tag = tagKV
        # tag = tagKV+":"+loc[2][tagKV]   # works with OSM query data only ...

        k = (INDEX,tag)
        z = 1
        if k in links.keys():
          z = links[k]
          z = z + 1
        links[k] = z

  print( resolution, len( counts ) )

  return links, counts


def output_h3_id_attributes(h3_id):
    return {
        "co_ordinates  :" : h3.h3_to_geo(h3_id),
        "geo_boundary  :" : Polygon(h3.h3_to_geo_boundary(h3_id, geo_json=True)).wkt,
        "parent        :" : h3.h3_to_parent(h3_id),
        "children      :" : h3.h3_to_children(h3_id)
    }
