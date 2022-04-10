# -*- coding: utf-8 -*-

import pandas as pd
import sparql

q5 = """
SELECT ?osmid ?distance ?loc ?natural WHERE {
  ?osmid osmt:natural ?natural . 
  SERVICE wikibase:around { 
      ?osmid osmm:loc ?loc . 
      bd:serviceParam wikibase:center "Point(11.927373 51.313281)"^^geo:wktLiteral . 
      bd:serviceParam wikibase:radius "20" . 
      bd:serviceParam wikibase:distance ?distance .
  } 
  FILTER(?distance < 15)
} 
"""

q4 = """
SELECT ?osmid ?distance ?loc ?office WHERE {
  ?osmid osmt:office ?office . 
  SERVICE wikibase:around { 
      ?osmid osmm:loc ?loc . 
      bd:serviceParam wikibase:center "Point(11.927373 51.313281)"^^geo:wktLiteral . 
      bd:serviceParam wikibase:radius "20" . 
      bd:serviceParam wikibase:distance ?distance .
  } 
  FILTER(?distance < 15)
} 
"""

q3 = """
SELECT ?osmid ?distance ?loc ?craft WHERE {
  ?osmid osmt:craft ?craft . 
  SERVICE wikibase:around { 
      ?osmid osmm:loc ?loc . 
      bd:serviceParam wikibase:center "Point(11.927373 51.313281)"^^geo:wktLiteral . 
      bd:serviceParam wikibase:radius "20" . 
      bd:serviceParam wikibase:distance ?distance .
  } 
  FILTER(?distance < 15)
} 
"""

q2 = """
SELECT ?osmid ?distance ?loc ?amenity WHERE {
  VALUES ?amenity { "kindergarten" "school" "university" "college" }
  ?osmid osmt:amenity ?amenity . 
  SERVICE wikibase:around { 
      ?osmid osmm:loc ?loc . 
      bd:serviceParam wikibase:center "Point(11.927373 51.313281)"^^geo:wktLiteral . 
      bd:serviceParam wikibase:radius "20" . 
      bd:serviceParam wikibase:distance ?distance .
  } 
  FILTER(?distance < 15)
} 
"""

q1 = """
SELECT ?place ?location ?distance ?placeLabel WHERE {
    SERVICE wikibase:around { 
      ?place wdt:P625 ?location . 
      bd:serviceParam wikibase:center "Point(11.926951 51.312740)"^^geo:wktLiteral . 
      bd:serviceParam wikibase:radius "5" . 
      bd:serviceParam wikibase:distance ?distance .
    } 
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
} ORDER BY ?distance LIMIT 100
"""

qs = [q1, q2, q3, q4, q5 ]

for q in qs:

    result = sparql.query('http://sophox.org/sparql', q)

    print( result.variables )

    data = []

    for row in result.fetchall():
      r2 = sparql.unpack_row(row, convert=None, convert_type={})
      data.append(r2)
      # print( str(r2) + "\n")

    # create DataFrame using data
    df = pd.DataFrame(data, columns = result.variables)
    print(df)