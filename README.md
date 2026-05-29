# Reto 8 — Seguridad de Redes y Optimización Industrial con Big Data
**Equipo NARANJA · Grado Business Data Analytics · Mondragon Unibertsitatea · 2025-2026**

---

## Estructura del proyecto

```
25_26_R8_Equipo_Naranja/
│
├── 00-Sampleado_ELK.ipynb              # Muestreo de 100k flujos del dataset original para ELK
├── 01-Comparacion_Datasets.ipynb       # Análisis comparativo de las fuentes disponibles
├── 02-EDA_Dashboard.ipynb              # EDA + dashboard interactivo (compresores y telemetría)
├── 03-Consultas_MongoDB.py             # Consultas analíticas sobre los logs de firewall en MongoDB
├── 04-Analisis_Firewall.ipynb          # Detección de hallazgos y amenazas en los logs de firewall
├── 05-Network_Flows_Limpieza.ipynb     # Limpieza y feature engineering de los flujos de red
├── 06-Deteccion_Anomalias.ipynb        # Pipeline completo de detección de anomalías (IF + KMeans + HDBSCAN + Autoencoder)
├── 07-Optimizacion_Compresores.ipynb   # Algoritmo genético para optimización energética de compresores
│
├── Datos/
│   ├── Originales/                     # ⚠️ VACÍO — añadir aquí los datos originales (ver sección Datos)
│   └── Transformados/                  # Archivos generados automáticamente por los notebooks
│       └── resultados_consultas.csv
│
├── Logstash/
│   └── logstash_pipeline.conf          # Configuración del pipeline de ingesta en Elasticsearch
│
├── MQTT/
│   ├── client_1.py                     # Cliente productor (publica datos de sensores)
│   ├── client_2.py                     # Cliente consumidor (recibe y analiza datos)
│   ├── client_3.py                     # Cliente coordinador (gestiona topics y distribución)
│   └── functions.py                    # Funciones auxiliares compartidas
│
├── packages/
│   └── sample_ips/                     # Base de datos de geolocalización IP2Location
│
├── indicaciones_entorno_virtual_conda.txt   # Instrucciones para crear el entorno Conda
└── README.md
```

---

## Datos

### Datos originales (`Datos/Originales/`)

Esta carpeta está **vacía en el repositorio**. Antes de ejecutar los notebooks es necesario añadir manualmente los siguientes archivos:

| Archivo | Descripción | Usado en |
|---|---|---|
| `firewall_logs.csv` | Logs de firewall (65.532 registros) | `03`, `04` |
| `network_flows.csv` | Flujos de red CICFlowMeter (3,5 M filas, ~1,6 GB) | `00`, `01`, `05`, `06` |
| `CompA.csv` | Series temporales compresor A | `02`, `07` |
| `CompB.csv` | Series temporales compresor B | `02`, `07` |
| `CompC.csv` | Series temporales compresor C | `02`, `07` |
| `CompD.csv` | Series temporales compresor D | `02`, `07` |

> Los datos originales no se incluyen en el repositorio por razones de tamaño y confidencialidad.

### Datos transformados (`Datos/Transformados/`)

Estos archivos son **generados automáticamente** al ejecutar los notebooks. No es necesario crearlos manualmente:

| Archivo | Generado por | Descripción |
|---|---|---|
| `resultados_consultas.csv` | `03-Consultas_MongoDB.py` | Resultados de las consultas analíticas sobre MongoDB |
| `network_flows_sample.csv` | `00-Sampleado_ELK.ipynb` | Muestra de 100k flujos para ELK |
| `network_flows_limpio.csv` | `05-Network_Flows_Limpieza.ipynb` | Dataset limpio con features derivadas |
| `anomalias_clasificadas.csv` | `06-Deteccion_Anomalias.ipynb` | Flujos etiquetados con nivel de severidad |

---

## Orden de ejecución

```
00 → 01 → 02
          ↓
     03 → 04 → 05 → 06
          ↓
          07
```

Los notebooks `02` y `07` (EDA y optimización de compresores) son independientes del bloque de seguridad de red y pueden ejecutarse en paralelo a partir del paso `01`.

---

## Entorno

Consultar `indicaciones_entorno_virtual_conda.txt` para crear el entorno Conda con todas las dependencias necesarias.

**Requisitos principales:** Python 3.10+, pandas, scikit-learn, tensorflow, plotly, dash, pymongo, paho-mqtt.
