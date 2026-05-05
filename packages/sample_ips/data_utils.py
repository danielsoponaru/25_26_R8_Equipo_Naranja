import os
import pandas as pd
import IP2Location

def procesar_network_flows(ruta_entrada, ruta_salida, ruta_db_ip, num_casos=100000, random_state=42):
    """
    Lee el dataset masivo de tráfico de red, extrae una muestra aleatoria representativa
    y enriquece las direcciones IP de origen y destino con información geográfica detallada 
    (Región, Latitud y Longitud) utilizando la base de datos IP2Location LITE.
    
    Rutas de datasets esperadas:
    - Entrada: Datos/Originales/Network_flows.csv
    - DB IP2Location: Datos/Originales/IP2LOCATION-LITE-DB5.BIN (o DB3/DB11)
    - Salida: Datos/Transformados/Networkflows_100k.csv
    """
    if not os.path.exists(ruta_db_ip):
        print(f"Error critico: No se encuentra el archivo de base de datos en: {ruta_db_ip}")
        print("Por favor, asegurate de haber descargado y descomprimido el archivo .BIN en la ruta indicada.")
        return None

    print(f"Cargando dataset original desde: {ruta_entrada}...")
    try:
        df = pd.read_csv(ruta_entrada)
        print(f"Dataset cargado con exito. Filas totales: {len(df):,}")
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
        return None
    
    print(f"Extrayendo una muestra aleatoria de {num_casos:,} registros...")
    df_reducido = df.sample(n=num_casos, random_state=random_state).copy()
    
    print("Conectando con la base de datos IP2Location...")
    db_geo = IP2Location.IP2Location(ruta_db_ip)
    
    def obtener_geolocalizacion(ip):
        try:
            record = db_geo.get_all(ip)
            region = record.region if record.region else "Unknown"
            latitude = record.latitude if record.latitude else 0.0
            longitude = record.longitude if record.longitude else 0.0
            return region, latitude, longitude
        except Exception:
            return "Unknown", 0.0, 0.0

    col_src = 'Source.IP'
    col_dst = 'Destination.IP'
    
    if col_src in df_reducido.columns and col_dst in df_reducido.columns:
        print("Enriqueciendo IPs de Origen...")
        geo_origen = df_reducido[col_src].apply(obtener_geolocalizacion)
        df_reducido['Source_Region'] = [x[0] for x in geo_origen]
        df_reducido['Source_Latitude'] = [x[1] for x in geo_origen]
        df_reducido['Source_Longitude'] = [x[2] for x in geo_origen]
        
        print("Enriqueciendo IPs de Destino...")
        geo_destino = df_reducido[col_dst].apply(obtener_geolocalizacion)
        df_reducido['Destination_Region'] = [x[0] for x in geo_destino]
        df_reducido['Destination_Latitude'] = [x[1] for x in geo_destino]
        df_reducido['Destination_Longitude'] = [x[2] for x in geo_destino]
        
        print("Enriquecimiento geografico completado.")
    else:
        print(f"Error: No se encontraron las columnas de IP '{col_src}' o '{col_dst}' en el CSV.")
        print(f"Columnas disponibles: {list(df_reducido.columns)}")
        return df_reducido

    print(f"Guardando el dataset resultante en: {ruta_salida}...")
    try:
        df_reducido.to_csv(ruta_salida, index=False)
        print("Proceso finalizado con exito. El archivo esta listo para ser enviado a la VM.")
    except Exception as e:
        print(f"Error al guardar el archivo de salida: {e}")
        
    return df_reducido