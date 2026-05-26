import json
import time
import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
import paho.mqtt.client as mqtt

#Configuración
BROKER = "localhost"

TOPIC = "topic_data"

DATA_FOLDER = (
    Path(__file__).resolve().parent.parent / "Datos" / "Originales"
)

PAUSE_SECONDS = 0.5

#logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


#cliente mqqtt
client_1 = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION1,
    "client_1"
)

client_1.connect(BROKER)

#csv
csv_files = [

    "CompA.csv",
    "CompB.csv",
    "CompC.csv",
    "CompD.csv"
]


print("\nEnviando datos continuamente...\n")

while True:

    for file_name in csv_files:

        file_path = DATA_FOLDER / file_name

        print(f"\nLeyendo {file_name}...\n")

        df = pd.read_csv(file_path)

        for _, row in df.iterrows():

            data = row.to_dict()

            # timestamp
            data["timestamp"] = (
                datetime.now().isoformat()
            )

            # archivo origen
            data["source_file"] = file_name

            payload = json.dumps(data)

            client_1.publish(
                TOPIC,
                payload,
                qos=1
            )

            logging.info(
                f"Publicado en {TOPIC}: {payload}"
            )

            time.sleep(PAUSE_SECONDS)
