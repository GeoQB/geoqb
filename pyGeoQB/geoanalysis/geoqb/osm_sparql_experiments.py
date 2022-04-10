# -*- coding: utf-8 -*-

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


import wikirepo

from wikirepo.data import wd_utils
from datetime import date

ents_dict = wd_utils.EntitiesDict()
# Strings must match their Wikidata English page names
countries = ["Germany", "United States of America", "People's Republic of China"]
# countries = ["Q183", "Q30", "Q148"] # we could also pass QIDs
# data.incl_lctn_lbls(lctn_lvls='country') # or all countries`
depth = 0
timespan = (date(2009, 1, 1), date(2010, 1, 1))
interval = "yearly"

df = wikirepo.data.query(
    ents_dict=ents_dict,
    locations=countries,
    depth=depth,
    timespan=timespan,
    interval=interval,
    climate_props=None,
    demographic_props=["population", "life_expectancy"],
    economic_props="median_income",
    electoral_poll_props=None,
    electoral_result_props=None,
    geographic_props=None,
    institutional_props="human_dev_idx",
    political_props="executive",
    misc_props=None,
    verbose=True,
)

col_order = [
    "location",
    "qid",
    "year",
    "executive",
    "population",
    "life_exp",
    "human_dev_idx",
    "median_income",
]
df = df[col_order]

df.head(6)



from qwikidata.entity import WikidataItem, WikidataLexeme, WikidataProperty
from qwikidata.linked_data_interface import get_entity_dict_from_api

# create an item representing "Douglas Adams"
Q_DOUGLAS_ADAMS = "Q42"
q42_dict = get_entity_dict_from_api(Q_DOUGLAS_ADAMS)
q42 = WikidataItem(q42_dict)

# create a property representing "subclass of"
P_SUBCLASS_OF = "P279"
p279_dict = get_entity_dict_from_api(P_SUBCLASS_OF)
p279 = WikidataProperty(p279_dict)

# create a lexeme representing "bank"
L_BANK = "L3354"
l3354_dict = get_entity_dict_from_api(L_BANK)
l3354 = WikidataLexeme(l3354_dict)

from qwikidata.sparql import (get_subclasses_of_item,
                              return_sparql_query_results)

# send any sparql query to the wikidata query service and get full result back
# here we use an example that counts the number of humans
sparql_query = """
SELECT (COUNT(?item) AS ?count)
WHERE {
        ?item wdt:P31/wdt:P279* wd:Q5 .
}
"""

res1 = return_sparql_query_results( q1 )

print( res1 )


import sparql 

endpoint = 'http://sophox.org/sparql'

s = sparql.Service(endpoint, "utf-8", "GET")

q = ( 'SELECT DISTINCT ?station, ?orbits WHERE { '
       '?station a <http://dbpedia.org/ontology/SpaceStation> . '
       '?station <http://dbpedia.org/property/orbits> ?orbits . '
       'FILTER(?orbits > 50000) } ORDER BY DESC(?orbits)')
result = sparql.query('http://dbpedia.org/sparql', q)
print(result)

result = sparql.query('http://sophox.org/sparql', q3)

print( result.variables )

data = []

for row in result.fetchall():
  r2 = sparql.unpack_row(row, convert=None, convert_type={})
  data.append(r2) 
  # print( str(r2) + "\n")

import pandas as pd

# create DataFrame using data
df = pd.DataFrame(data, columns = result.variables)
print(df)