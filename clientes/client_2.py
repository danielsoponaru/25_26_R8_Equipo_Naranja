import time

import paho.mqtt.client as mqtt


BROKER = "localhost"

TOPIC = "topic_queries"


client_2 = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION1,
    "client_2"
)

client_2.connect(BROKER)
client_2.loop_start()


consultas = [

    "mostrar_datos",

    "media_temperatura",

    "max_presion",

    "potencia_media",

    "comparacion_potencias",

    "estadisticas",

    "temperatura_maxima",

    "temperatura_minima",

    "frecuencia_media",

    "alerta_potencia"
]


print("\nEnviando consultas automáticas...\n")


while True:

    for consulta in consultas:

        client_2.publish(
            TOPIC,
            consulta,
            qos=1
        )

        print(
            f"Consulta enviada: {consulta}"
        )

        # Espera entre consultas
        time.sleep(1)
