import logging

import paho.mqtt.client as mqtt

from functions import Handler


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


BROKER = "localhost"

TOPIC_DATA = "topic_data"

TOPIC_QUERIES = "topic_queries"


handler = Handler()


client_3 = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION1,
    "client_3"
)

# CALLBACK
client_3.on_message = handler.on_message


# CONEXIÓN
client_3.connect(BROKER)


# SUBSCRIPCIONES
client_3.subscribe(TOPIC_DATA)

client_3.subscribe(TOPIC_QUERIES)


logging.info("Suscrito a topic_data y topic_queries")


# LOOP INFINITO
client_3.loop_forever()