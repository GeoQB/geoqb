from string import Template
import pandas as pd

import flat_table

import matplotlib.pyplot as plt

from os.path import exists

persistentQuery3a='''

USE GRAPH $graph_name

INTERPRET QUERY () SYNTAX v2 {

    SumAccum<int> @osmtagCnt=0;

    histogram = SELECT t
           FROM :t -(hasOSMTag:e)- :s
           WHERE s.resolution == $res
           ACCUM t.@osmtagCnt += 1;

    PRINT histogram;
    PRINT $res as resolution;

}'''


persistentQuery3b='''
CREATE QUERY osm_tag_histogram(INT res) FOR GRAPH $graph_name {

    SumAccum<int> @osmtagCnt=0;

    Result_tags = SELECT t
           FROM :t -(hasOSMTag:e)- :s
           WHERE s.resolution == res
           ACCUM t.@osmtagCnt += 1;

    PRINT histogram;
    PRINT res as resolution;

}'''


def getTagHistogramForOSMGraph( conn, graph_name, overwrite=False, verbose=True ):
    path_to_buffer_file = "tag_histogram_layers_data_"+ graph_name +".json"
    file_exists = exists(path_to_buffer_file)
    if not file_exists or overwrite:

        valueStructure = {
            'graph_name' : graph_name,
            'res' : 9
        }

        gsqlStatement = persistentQuery3a

        gsqlTemplate = Template(gsqlStatement)
        gsqlScript = gsqlTemplate.substitute(valueStructure)

        if verbose:
            print( gsqlScript )

        result = conn.gsql(gsqlScript, options=[])

        f = open( path_to_buffer_file, "w")
        f.write( result )
        f.flush()
        f.close()

    rows = None
    with open(path_to_buffer_file, "r") as f:
        rows = f.readlines()[1:]

    t = ""
    for r in rows:
        t=t+r

    import json
    data = json.loads(t)

    dfF = pd.DataFrame(data["results"][0]["histogram"])
    df1 = flat_table.normalize(dfF)
    #print(df1)

    df2 = df1.rename(columns={
        'attributes.@osmtagCnt':'osmtagCnt',
        'attributes.tagvalue':'tagvalue',
        'attributes.tagname':'tagname'
    })

    df2 = df2.astype({"osmtagCnt": int})
    df2 = df2.sort_values(by=['osmtagCnt'], ascending=False )
    df2.describe()
    print(df2)

    dfPlot = df2['osmtagCnt']

    dfPlot.plot.hist('osmtagCnt', bins=100, alpha=0.5, log=True )
    # plt.show()
    plt.savefig("tag_histogram_layers_chart_"+ graph_name + ".png")

    return df2