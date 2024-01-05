import random

def getPairsWithSum_X_silent( list, x):

    candidates = {}

    result = []

    for z in list:

        match = None
        y = -(z-x)

        try:
            match = candidates[y]
            if match is not None:
                result.append( (y,match) )
                candidates.pop( y )
            else:
                candidates[z] = y
        except KeyError:
            candidates[z] = y

    return result

def getPairsWithSum_X( list, x):

    candidates = {}
    result = []

    for z in list:

        match = None
        y = -(z-x)

        print( f"c: {candidates}" )
        print( f"r: {result}" )
        print( f"z: {z}" )
        print( f"y: {y}" )

        try:
            match = candidates[y]
            print( f" # {match}" )

            print( match )
            if match is not None:
                result.append( (y,match) )
                candidates.pop( y )
            else:
                candidates[z] = y
        except KeyError:
            print( f" * {match}" )
            candidates[z] = y

    return result






list1 = [ 1,1,1,4,4,4,1,4,2,3,8]
list2 = [random.randrange(1, 50, 1) for i in range(25)]

print( getPairsWithSum_X_silent( list1, 5 ) )

print( getPairsWithSum_X_silent( list1, 15) )
