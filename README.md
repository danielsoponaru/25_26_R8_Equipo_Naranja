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
│   ├── Originales/                     # Datos de partida (ver sección Datos)
│   │   └── IP2LOCATION-LITE-DB11.BIN  # Base de datos de geolocalización IP (incluida en el repo)
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

La mayoría de los datos originales **no están en el repositorio** por tamaño y confidencialidad. Antes de ejecutar los notebooks es necesario añadir manualmente los siguientes archivos:

| Archivo | Descripción | Usado en | En el repo |
|---|---|---|---|
| `IP2LOCATION-LITE-DB11.BIN` | Base de datos binaria de geolocalización IP (IP2Location LITE) | `05`, `06` | ✅ Sí |
| `firewall_logs.csv` | Logs de firewall (65.532 registros) | `03`, `04` | ❌ No |
| `network_flows.csv` | Flujos de red CICFlowMeter (3,5 M filas, ~1,6 GB) | `00`, `01`, `05`, `06` | ❌ No |
| `CompA.csv` | Series temporales compresor A | `02`, `07` | ❌ No |
| `CompB.csv` | Series temporales compresor B | `02`, `07` | ❌ No |
| `CompC.csv` | Series temporales compresor C | `02`, `07` | ❌ No |
| `CompD.csv` | Series temporales compresor D | `02`, `07` | ❌ No |

> **Por qué `IP2LOCATION-LITE-DB11.BIN` sí está en el repositorio:**
> Este archivo se distribuye gratuitamente bajo la licencia IP2Location LITE y es de acceso público
> ([ip2location.com](https://www.ip2location.com)). A diferencia de los CSVs del proyecto —que
> contienen datos industriales confidenciales o superan el umbral de tamaño de Git—, la base de
> datos LITE DB11 (~50 MB) es redistribuible y necesaria para reproducir el enriquecimiento de IPs
> con coordenadas geográficas (país, ciudad, latitud/longitud) que habilita la visualización
> geoespacial en Kibana y las features de contextualización del pipeline de detección de anomalías
> (`05-Network_Flows_Limpieza.ipynb`, `06-Deteccion_Anomalias.ipynb`). Incluirla garantiza que
> cualquier miembro del equipo pueda reproducir el entorno completo sin pasos de descarga adicionales.

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
     03 → 04 → 05 → 06  ⚠️
          ↓
          07
```

Los notebooks `02` y `07` (EDA y optimización de compresores) son independientes del bloque de seguridad de red y pueden ejecutarse en paralelo a partir del paso `01`.

---

## ⚠️ Advertencia — `06-Deteccion_Anomalias.ipynb`

**No ejecutar este notebook** a menos que se cumplan las dos condiciones siguientes:

1. **Datos completos disponibles**: requiere el fichero `network_flows.csv` original (~1,6 GB, 3,5 millones de filas) en `Datos/Originales/`. Sin él el notebook falla en las primeras celdas.

2. **Entorno correctamente configurado**: utiliza dos librerías con instalación específica:
   - **`hdbscan`** — requiere compilador C++ en Windows (Visual C++ Build Tools). Si no está instalado correctamente lanza errores de compilación al importar.
   - **`PyTorch`** — requiere elegir entre la versión CPU o GPU según el hardware disponible. Ver instrucciones detalladas en `indicaciones_entorno_virtual_conda.txt`.

El tiempo de ejecución completo del notebook puede **superar 1 hora** en CPU estándar. Los resultados ya generados están disponibles en `Datos/Transformados/anomalias_clasificadas.csv`.

---

## Entorno

Consultar `indicaciones_entorno_virtual_conda.txt` para crear el entorno Conda con todas las dependencias necesarias.

**Requisitos principales:** Python 3.10+, pandas, scikit-learn, tensorflow, plotly, dash, pymongo, paho-mqtt.
