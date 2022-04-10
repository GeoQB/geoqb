import tensorflow as tf
import numpy as np

import matplotlib.pyplot as plt

import json
import base64

import json
from json import JSONEncoder
import numpy

import potential_layer_calculations


def compute_euclidean_distance(x, y):

    y=tf.cast(y, dtype=tf.float32)
    x=tf.cast(x, dtype=tf.float32)

    size_x = x.shape.dims[0]
    size_y = y.shape.dims[0]
    for i in range(size_x):

        tile_one = tf.reshape(tf.tile(x[i], [size_y]), [size_y, -1])
        tile_one = tf.cast(tile_one, dtype=tf.float32)
        #print( tile_one )
        eu_one = tf.expand_dims(tf.sqrt(tf.reduce_sum(tf.pow(tf.subtract(tile_one, y), 2), axis=1)), axis=0)
        if i == 0:
            d = eu_one
        else:
            d = tf.concat([d, eu_one], axis=0)
    return d

def squared_dist(A, B):

    assert A.shape.as_list() == B.shape.as_list()

    row_norms_A = tf.reduce_sum(tf.square(A), axis=1)
    row_norms_A = tf.reshape(row_norms_A, [-1, 1])  # Column vector.

    row_norms_B = tf.reduce_sum(tf.square(B), axis=1)
    row_norms_B = tf.reshape(row_norms_B, [1, -1])  # Row vector.

    return row_norms_A - 2 * tf.matmul(A, tf.transpose(B)) + row_norms_B

def test_something3(self):

    A = tf.constant( shape=(100, 100), dtype=tf.float32 )

    B = tf.constant([[-1, 0],
                     [0, -4]])

    print( squared_dist( A,B ) )

    print( compute_euclidean_distance( A,B ) )

    return True

def test_something2(self):

    x = []
    y = []
    P = []

    for i in range( 0, 100 ):
        x.append( i )
        for j in range( 0, 100 ):
            if x == 0:
                y.append( j )
            p= [i,j]
            P.append( p )

    #print()
    #print( P )
    #print( len(P) )
    #print( type(P) )

    # two particles
    A1 = tf.constant([[10, 10],
                     [90, 90]])

    A2 = tf.convert_to_tensor(P)

    print( A1.shape )
    print( A2.shape )

    z = tf.matmul(A2, A1)

    print( z.shape )

    #h = plt.contourf(x, y, z)
    #plt.axis('scaled')
    #plt.colorbar()
    #plt.show()

    return True

def test_something(self):

    # This will be an int32 tensor by default; see "dtypes" below.
    rank_0_tensor = tf.constant(4)
    print(rank_0_tensor)


    # Let's make this a float tensor.
    rank_1_tensor = tf.constant([2.0, 3.0, 4.0])
    print(rank_1_tensor)

    a = tf.constant([[1, 2],
                     [3, 4]])

    b = tf.constant([[1, 1],
                     [1, 1]]) # Could have also said `tf.ones([2,2])`

    print(tf.add(a, b), "\n")
    print(tf.multiply(a, b), "\n")
    print(tf.matmul(a, b), "\n")



    a1 = [[1, 2],[3, 4]]

    a2 = [[-1, 0],[-9, 5]]

    # 2, 2, 12, -1
    print ( a1 )

    numpyArrayOne = numpy.array([[11, 22, 33], [44, 55, 66], [77, 88, 99]])

    # Serialization
    numpyData = {"array": numpyArrayOne}
    encodedNumpyData = json.dumps(numpyData, cls=potential_layer_calculations.NumpyArrayEncoder)  # use dump() to write array into file
    print("Printing JSON serialized NumPy array")
    print(encodedNumpyData)

    # Deserialization
    print("Decode JSON serialized NumPy array")
    decodedArrays = json.loads(encodedNumpyData)

    finalNumpyArray = numpy.asarray(decodedArrays["array"])
    print("NumPy Array")
    print(finalNumpyArray)

    potential_layer_calculations.storeArray( finalNumpyArray , "t2.json")

    return True