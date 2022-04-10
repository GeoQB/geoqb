import tensorflow as tf
import numpy as np

import json
import base64

import json
from json import JSONEncoder
import numpy

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, numpy.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

def storeArray( a, fn ):
    print( "> Store array in file: " + fn )
    fOut = open( fn, "w")
    encodedNumpyData = json.dumps(a, cls=NumpyArrayEncoder )  # use dump() to write array into file
    fOut.write(encodedNumpyData)
    fOut.close()

def loadArray( fn ):
    print( "> Load array from file: " + fn )
    fIn = open( fn, 'r' )
    dataArray = json.load(fIn)
    return dataArray

def calculate_distance_map_parray( l1, l2 ):
    t1 = tf.constant(l1)
    t2 = tf.constant(l2)
    return calculate_distance_map(t1,t2)

def calculate_distance_map_np( l1, l2 ):
    data_tf1 = tf.convert_to_tensor(l1, np.float32)
    data_tf2 = tf.convert_to_tensor(l2, np.float32)
    return calculate_distance_map(data_tf1,data_tf2)

def calculate_distance_map( t1, t2 ):

    t2m = tf.multiply(t2, -1)
    tdiff = tf.add( t2m, t1 )
    tdiffabs = tf.abs( tdiff )
    tdiffabsscaled = tf.multiply( tdiffabs, 512 )

    return tdiffabsscaled.numpy(), tf.math.reduce_sum( tdiffabs ).numpy()





def calcDiffLayers( report_folder, fn1 = "myIMPACT1.json", fn2 = "myIMPACT2.json", fn3 = "myIMPACT3.json" ):

    m1 = loadArray( report_folder + "/" + fn1 )
    m2 = loadArray( report_folder + "/" + fn2 )
    m3 = loadArray( report_folder + "/" + fn3 )

    delta1 = calculate_distance_map_np( m1, m2 )
    delta2 = calculate_distance_map_np( m2, m3 )
    delta3 = calculate_distance_map_np( m3, m1 )

    deltaA = calculate_distance_map_np( m1, m1 )
    deltaB = calculate_distance_map_np( m2, m2 )
    deltaC = calculate_distance_map_np( m3, m3 )

#    print( delta1 )
#    print( delta2 )
#    print( delta3 )

#    print( deltaA )
#    print( deltaB )
#    print( deltaC )

    storeArray( delta1[0], report_folder + "/" + "d1.json" )
    storeArray( delta2[0], report_folder + "/" +"d2.json" )
    storeArray( delta3[0], report_folder + "/" +"d3.json" )

    from PIL import Image

    im = Image.fromarray(delta1[0])
    im = im.convert("L")
    im.save(report_folder + "/tiles/f1/" + "delta1.jpeg")

    im = Image.fromarray(delta2[0])
    im = im.convert("L")
    im.save(report_folder + "/tiles/f1/" + "delta2.jpeg")

    im = Image.fromarray(delta3[0])
    im = im.convert("L")
    im.save( report_folder + "/tiles/f1/" + "delta3.jpeg")

    return ( report_folder + "/tiles/f1/" + "delta1.jpeg",
             report_folder + "/tiles/f1/" + "delta2.jpeg",
             report_folder + "/tiles/f1/" + "delta3.jpeg")