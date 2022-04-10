from confluent_kafka import Producer, KafkaError
import json
import os

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

#
# This function exports the OSM nodes data into a Kafka topic.
#
def publishToTopic(row, topic):
  json_vdata = json.dumps( row.to_dict() )
  print( json_vdata )
  producer.produce(topic, key=str(row['id']), value=json_vdata )
  producer.flush()

