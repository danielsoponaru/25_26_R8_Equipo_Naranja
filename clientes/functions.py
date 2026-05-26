import json
import logging
import pandas as pd
import csv
from datetime import datetime
from pathlib import Path


OUTPUT_FILE = (
    Path(__file__).resolve().parent.parent
    / "Datos"
    / "Transformados"
    / "resultados_consultas.csv"
)


class Handler:

    def __init__(self):

        self.data = []

        #mensaje mqtt
    def on_message(self, client, userdata, message):

        topic = message.topic

        payload = message.payload.decode("utf-8")

        logging.info(f"Mensaje recibido en {topic}")

        #Datos
        if topic == "topic_data":

            record = json.loads(payload)

            self.data.append(record)

            logging.info(f"Datos almacenados: {record}")

        #Consultas
        elif topic == "topic_queries":

            consultas(payload, self.data)


#Guardar csv
def guardar_resultados(resultado):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    file_exists = OUTPUT_FILE.is_file()

    with open(
        OUTPUT_FILE,
        mode="a",
        newline=""
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=resultado.keys()
        )

        # Crear cabecera solo la primera vez
        if not file_exists:

            writer.writeheader()

        writer.writerow(resultado)


#consultas
def consultas(query, data):

    if len(data) == 0:

        print("\nNo hay datos disponibles.")
        return

    df = pd.DataFrame(data)

    numeric_columns = [
        "Presion",
        "Temperatura",
        "Frecuencia",
        "Potencia_Medida",
        "Potencia_Estimada"
    ]

    for col in numeric_columns:

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    resultado = {

        "timestamp": datetime.now().isoformat(),

        "total_registros":
            len(df),

        "media_temperatura":
            round(df["Temperatura"].mean(), 2),

        "max_presion":
            round(df["Presion"].max(), 4),

        "potencia_media":
            round(df["Potencia_Medida"].mean(), 2),

        "comparacion_potencias":
            round(
                (
                    df["Potencia_Medida"] -
                    df["Potencia_Estimada"]
                ).mean(),
                2
            ),

        "temperatura_maxima":
            round(df["Temperatura"].max(), 2),

        "temperatura_minima":
            round(df["Temperatura"].min(), 2),

        "frecuencia_media":
            round(df["Frecuencia"].mean(), 2),

        "potencia_maxima":
            round(df["Potencia_Medida"].max(), 2),

        "alertas_potencia":
            int(
                (
                    df["Potencia_Medida"] > 120
                ).sum()
            )
    }

    #resultados

    for key, value in resultado.items():

        print(f"{key}: {value}")

    # csv
    guardar_resultados(resultado)

    print(
        "\nResultados guardados en:"
    )

    print(OUTPUT_FILE)
