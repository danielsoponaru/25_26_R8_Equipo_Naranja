"""
Nombre del script: mongodb_firewall.py
Dataset de entrada: Firewall_logs.csv
Ruta del dataset en el repositorio: ./Datos\Originales\Firewall_logs.csv

Descripción:
Cargar los logs del firewall en MongoDB y ejecutar las consultas analíticas
para la sección "Almacenamiento y consulta con MongoDB" del informe del Reto 8.
"""

import os
import pandas as pd
from pymongo import MongoClient, ASCENDING
from pymongo.errors import BulkWriteError, ConnectionFailure

#CONFIGURACIÓN Y RUTAS RELATIVAS
#Definimos la ruta relativa tomando como base la carpeta donde está este script
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
RUTA_CSV = r"C:\25_26_R8_Equipo_Naranja\Datos\Originales\Firewall_logs.csv"
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "reto8"
COL_NAME = "firewall_logs"
BATCH_SIZE = 2000

#Mapeo columnas CSV, campos MongoDB
COLUMNAS = {
    "Source Port":          "src_port",
    "Destination Port":     "dst_port",
    "NAT Source Port":      "nat_src_port",
    "NAT Destination Port": "nat_dst_port",
    "Action":               "action",
    "Bytes":                "bytes",
    "Bytes Sent":           "bytes_sent",
    "Bytes Received":       "bytes_recv",
    "Packets":              "packets",
    "Elapsed Time (sec)":   "elapsed_sec",
    "pkts_sent":            "pkts_sent",
    "pkts_received":        "pkts_recv",
}

CAMPOS_INT = {"src_port", "dst_port", "nat_src_port", "nat_dst_port",
              "packets", "pkts_sent", "pkts_recv"}
CAMPOS_FLOAT = {"bytes", "bytes_sent", "bytes_recv", "elapsed_sec"}


#FUNCIONES DE PREPROCESAMIENTO Y CARGA 
def limpiar_registro(fila: dict) -> dict:
    """Convierte una fila del CSV en un documento MongoDB con tipos correctos."""
    doc = {}
    for col_csv, col_mongo in COLUMNAS.items():
        val = fila.get(col_csv)
        if pd.isna(val):
            continue
        if col_mongo == "action":
            doc[col_mongo] = str(val).strip().lower()
        elif col_mongo in CAMPOS_INT:
            doc[col_mongo] = int(val)
        else:
            doc[col_mongo] = float(val)
    return doc


def insertar_por_lotes(df: pd.DataFrame, coleccion, batch_size: int = BATCH_SIZE) -> int:
    """Inserta el DataFrame en bloques para optimizar la memoria y evitar timeouts."""
    total_insertados = 0
    for inicio in range(0, len(df), batch_size):
        bloque = df.iloc[inicio : inicio + batch_size]
        documentos = [limpiar_registro(f) for f in bloque.to_dict("records")]
        try:
            res = coleccion.insert_many(documentos, ordered=False)
            total_insertados += len(res.inserted_ids)
        except BulkWriteError as err:
            total_insertados += err.details.get("nInserted", 0)
    return total_insertados


#PIPELINES DE AGREGACIÓN
def consulta_distribucion_acciones(col):
    """Calcula el porcentaje y total de registros por tipo de acción del firewall."""
    total = col.count_documents({})
    if total == 0:
        print("La colección está vacía.")
        return

    pipeline = [
        {"$group": {
            "_id":   "$action",
            "total": {"$sum": 1}
        }},
        {"$sort": {"total": -1}},
        {"$project": {
            "_id":   0,
            "accion": "$_id",
            "total":  1,
            "pct":    {"$round": [
                          {"$multiply": [{"$divide": ["$total", total]}, 100]},
                          2
                      ]}
        }}
    ]
    
    print(f"\n{'='*45}\nDISTRIBUCIÓN DE ACCIONES DEL FIREWALL\n{'='*45}")
    print(f"{'Acción':<14} {'Registros':>10} {'%':>8}\n" + "-"*36)
    for doc in col.aggregate(pipeline):
        print(f"{doc['accion']:<14} {doc['total']:>10,} {doc['pct']:>7.2f}%")
    print(f"{'TOTAL':<14} {total:>10,} {100.00:>7.2f}%")


def consulta_top_puertos_bloqueados(col, top_n: int = 10):
    """Identifica los puertos de destino con más intentos de conexión denegados/bloqueados."""
    pipeline = [
        {"$match": {"action": {"$in": ["deny", "drop"]}}},
        {"$group": {
            "_id":      "$dst_port",
            "intentos": {"$sum": 1}
        }},
        {"$sort":  {"intentos": -1}},
        {"$limit": top_n},
        {"$project": {"_id": 0, "puerto": "$_id", "intentos": 1}}
    ]
    
    print(f"\n{'='*45}\nTOP {top_n} PUERTOS CON MÁS CONEXIONES BLOQUEADAS\n{'='*45}")
    print(f"{'Puerto':>8}  {'Intentos bloqueados':>20}\n" + "-"*32)
    for doc in col.aggregate(pipeline):
        print(f"{doc['puerto']:>8}  {doc['intentos']:>20,}")


def consulta_trafico_por_accion(col):
    """Analiza los bytes totales, medios y tiempos de sesión agrupados por acción."""
    pipeline = [
        {"$group": {
            "_id":           "$action",
            "n_conexiones":  {"$sum":  1},
            "bytes_total":   {"$sum":  "$bytes"},
            "bytes_medio":   {"$avg":  "$bytes"},
            "pkts_medio":    {"$avg":  "$packets"},
            "elapsed_medio": {"$avg":  "$elapsed_sec"}
        }},
        {"$sort": {"bytes_total": -1}},
        {"$project": {
            "_id":           0,
            "accion":        "$_id",
            "n_conexiones":  1,
            "total_MB":      {"$round": [{"$divide": ["$bytes_total", 1048576]}, 3]},
            "media_bytes":   {"$round": ["$bytes_medio",   2]},
            "media_pkts":    {"$round": ["$pkts_medio",    2]},
            "media_elapsed": {"$round": ["$elapsed_medio", 2]}
        }}
    ]
    
    print(f"\n{'='*75}\nESTADÍSTICAS DE TRÁFICO POR ACCIÓN\n{'='*75}")
    print(f"{'Acción':<12} {'Conexiones':>11} {'Total MB':>10} {'Media B/conn':>14} {'Media s/conn':>14}\n" + "-"*75)
    for doc in col.aggregate(pipeline):
        print(f"{doc['accion']:<12} {doc['n_conexiones']:>11,} {doc['total_MB']:>10.3f} {doc['media_bytes']:>14.1f} {doc['media_elapsed']:>14.2f}")


def consulta_sesiones_largas(col, min_horas: float = 1.0, min_bytes: int = 1_048_576):
    """Encuentra sesiones permitidas ('allow') persistentes en el tiempo con alto volumen de datos."""
    filtro = {
        "action":      "allow",
        "elapsed_sec": {"$gt": min_horas * 3600},
        "bytes":       {"$gt": min_bytes}
    }
    proyeccion = {
        "_id": 0, "src_port": 1, "dst_port": 1, "bytes": 1, "elapsed_sec": 1, "pkts_sent": 1, "pkts_recv": 1
    }
    sesiones = list(col.find(filtro, proyeccion).sort("bytes", -1).limit(20))
    
    print(f"\n{'='*65}\nSESIONES ALLOW CON MÁS DE {min_horas:.0f}h Y MÁS DE {min_bytes/1e6:.0f} MB\n{'='*65}")
    print(f"Encontradas: {len(sesiones)} sesiones")
    if sesiones:
        print(f"\n{'Dst':>6}  {'Bytes (MB)':>10}  {'Horas':>7}  {'Pkts_sent':>10}  {'Pkts_recv':>10}\n" + "-"*52)
        for s in sesiones[:10]:
            print(f"{s['dst_port']:>6}  {s['bytes']/1e6:>10.3f}  {s['elapsed_sec']/3600:>7.2f}  {s.get('pkts_sent',0):>10}  {s.get('pkts_recv',0):>10}")


def consulta_tasa_bloqueo_por_puerto(col, min_registros: int = 50, top_n: int = 15):
    """Calcula la tasa porcentual de bloqueo (deny + drop) para los puertos más activos."""
    pipeline = [
        {"$group": {
            "_id":        "$dst_port",
            "total":      {"$sum": 1},
            "bloqueadas": {"$sum": {
                "$cond": {
                    "if":   {"$in": ["$action", ["deny", "drop"]]},
                    "then": 1,
                    "else": 0
                }
            }}
        }},
        {"$match": {"total": {"$gte": min_registros}}},
        {"$addFields": {
            "tasa_pct": {
                "$round": [
                    {"$multiply": [{"$divide": ["$bloqueadas", "$total"]}, 100]},
                    1
                ]
            }
        }},
        {"$sort":  {"tasa_pct": -1}},
        {"$limit": top_n},
        {"$project": {
            "_id": 0, "puerto": "$_id", "total": 1, "bloqueadas": 1, "tasa_pct": 1
        }}
    ]
    
    print(f"\n{'='*65}\nTOP {top_n} PUERTOS POR TASA DE BLOQUEO (min. {min_registros} registros)\n{'='*65}")
    print(f"{'Puerto':>8}  {'Total':>8}  {'Bloq.':>8}  {'Tasa %':>8}\n" + "-"*40)
    for doc in col.aggregate(pipeline):
        print(f"{doc['puerto']:>8}  {doc['total']:>8,}  {doc['bloqueadas']:>8,}  {doc['tasa_pct']:>7.1f}%")


#EJECUCIÓN PRINCIPAL
if __name__ == "__main__":
    client = None
    try:
        #1. Validación de existencia de datos antes de arrancar
        if not os.path.exists(RUTA_CSV):
            raise FileNotFoundError(f"No se encontró el archivo de datos en: {RUTA_CSV}. "
                                    f"Asegúrate de colocar 'Firewall_logs.csv' en la subcarpeta 'datos_origen'.")

        #2. Conexión segura con control de errores
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        client.server_info() # Lanza ConnectionFailure si Mongo está apagado
        
        db = client[DB_NAME]
        col_fw = db[COL_NAME]

        #3. Lectura y carga eficiente
        print("Leyendo CSV original...")
        df_fw = pd.read_csv(RUTA_CSV)
        print(f" -> {len(df_fw):,} filas leídas con éxito.")

        print("Reiniciando colección en MongoDB e insertando nuevos documentos...")
        col_fw.drop()
        n = insertar_por_lotes(df_fw, col_fw)
        print(f" -> {n:,} documentos indexados en '{DB_NAME}.{COL_NAME}'.")

        #4. Generación de Índices para optimizar rendimiento (Criterio Big Data)
        print("Configurando índices de rendimiento...")
        col_fw.create_index([("action", ASCENDING)], name="idx_action")
        col_fw.create_index([("dst_port", ASCENDING)], name="idx_dst_port")
        col_fw.create_index([("action", ASCENDING), ("dst_port", ASCENDING)], name="idx_action_dst")
        print(f" -> Índices activos: {list(col_fw.index_information().keys())}")

        #5. Ejecución del bloque analítico
        consulta_distribucion_acciones(col_fw)
        consulta_top_puertos_bloqueados(col_fw)
        consulta_trafico_por_accion(col_fw)
        consulta_sesiones_largas(col_fw)
        consulta_tasa_bloqueo_por_puerto(col_fw)

    except ConnectionFailure:
        print("\n[ERROR CRÍTICO]: No se pudo conectar a MongoDB. ¿Está el servicio activo en el puerto 27017?")
    except FileNotFoundError as fnf_err:
        print(f"\n[ERROR DE RUTA]: {fnf_err}")
    except Exception as e:
        print(f"\n[ERROR INESPERADO]: {e}")
    finally:
        if client:
            client.close()
            print("\nConexión con MongoDB cerrada de forma segura. Proceso finalizado.")