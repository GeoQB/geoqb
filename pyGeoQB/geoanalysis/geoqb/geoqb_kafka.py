from confluent_kafka import Producer, Consumer, KafkaException
import json
import os
import pandas as pd
import sys
import flat_table


import argparse

from confluent_kafka import avro, KafkaError
from confluent_kafka.admin import AdminClient, NewTopic

# Kafka
bootstrap_servers=os.environ.get('bootstrap_servers')
security_protocol=os.environ.get('security_protocol')
sasl_mechanisms=os.environ.get('sasl_mechanisms')
sasl_username=os.environ.get('sasl_username')
sasl_password=os.environ.get('sasl_password')

# Confluent Cloud Schema Registry
schema_registry_url=os.environ.get('schema_registry_url')
basic_auth_credentials_source=os.environ.get('basic_auth_credentials_source')
basic_auth_user_info=os.environ.get('basic_auth_user_info')

# Create Producer instance
producer = Producer({
        'bootstrap.servers': bootstrap_servers,
        'sasl.mechanisms': sasl_mechanisms,
        'security.protocol': security_protocol,
        'sasl.username': sasl_username,
        'sasl.password': sasl_password
})

# Create Producer instance
consumer = None


#
# This function exports the OSM nodes data into a Kafka topic.
#
def publishToTopic(row, topic):
  json_vdata = json.dumps( row.to_dict() )
  print( json_vdata )
  producer.produce(topic, key=str(row['id']), value=json_vdata )
  producer.flush()



def getTopicsForPrefix( prefix ):

    """
     Create a topic if needed
     Examples of additional admin API functionality:
     https://github.com/confluentinc/confluent-kafka-python/blob/master/examples/adminapi.py
     """

    a = AdminClient({
        'bootstrap.servers': bootstrap_servers,
        'sasl.mechanisms': 'PLAIN',
        'security.protocol': 'SASL_SSL',
        'sasl.username': sasl_username,
        'sasl.password': sasl_password
    })

    t=[]

    clusterMD = a.list_topics()
    #print( len(clusterMD.topics))
    for topic in clusterMD.topics:
        try:
            #print("{}".format(topic))
            if topic.startswith( prefix ):
                t.append( topic )

        except Exception as e:
            # Continue if error code TOPIC_ALREADY_EXISTS, which may be true
            # Otherwise fail fast
            if e.args[0].code() != KafkaError.TOPIC_ALREADY_EXISTS:
                print("Failed to list topic {}: {}".format(topic, e))

    return t




def readAndPrint_N_messages_from_topic( topic, N ):

    topics = [ topic ]

    consumer = Consumer( {
        'bootstrap.servers': bootstrap_servers,
        'sasl.mechanisms': sasl_mechanisms,
        'security.protocol': security_protocol,
        'sasl.username': sasl_username,
        'sasl.password': sasl_password,
        'client.id':'geoqb_blender_tool',
        'group.id':'geoqb_blender_tool_cg_01',
        'enable.auto.commit': False,
        'auto.offset.reset': 'earliest'
    })

    consumer.subscribe( topics )

    data = []

    i = 0
    running = True
    while running:

        msg = consumer.poll(timeout=1.0)

        if msg is None: continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                # End of partition event
                sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                 (msg.topic(), msg.partition(), msg.offset()))
            elif msg.error():
                raise KafkaException(msg.error())
        else:
            data.append(msg)
            i=i+1
            if i == 3:
                running = False

    consumer.close()

    print(f"> {len(data)} messages loaded from topic {topic}." )

    msg_key = data[0].key()
    msg_str = data[0].value()
    msg_h = data[0].headers()

    jsonDataK = msg_key.decode('UTF-8')
    jsonDataV = msg_str.decode('UTF-8')

    if msg_h is None:
        jsonDataH = "<no headers>"
    else:
        jsonDataH = msg_h

    print( "* KEY     : " + jsonDataK )
    print( "* HEADERS : " + jsonDataH )
    print( "* VALUE   : " + jsonDataV )
    print()


    rec = []

    for m in data:
        msg_key = m.key().decode('UTF-8')
        msg_val = m.value().decode('UTF-8')
        msg_h = m.headers()
        jsonDataH = None

        if msg_h is None:
            jsonDataH = "<no headers>"
        else:
            jsonDataH = msg_h

        m = ( msg_key, jsonDataH, msg_val )
        rec.append( m )
        # print( m )

    df1 = pd.DataFrame(rec, columns=['key', 'header', 'records'])

    df2 = flat_table.normalize(df1, expand_dicts=True, expand_lists=True)

    # print( df2 )

    return df2






def showTopics_FilteredAndSelectOne( prefix ):

    topics = getTopicsForPrefix( prefix )

    i=1
    selected = None
    for t in topics:
        print( f"[{i}]    {t}" )
        i=i+1
        if selected is None:
            selected = t
    if selected is None:
        selected = ""
    print( f"\n> {len(topics)} enrichment data topic(s) with prefix <{prefix}> in linked streaming data workspace." )
    inp = input(f"\n* Please select a topic: ({selected}): " )
    if not inp=="":
        selected = inp
    print( f"* your selection: [{selected}]" )
    if selected=="":
        print( f"\n> No topic selected.")
        exit()
    else:
        print( f"\n> Ready to blend data from topic {selected} to the knowledge graph." )
        return selected
