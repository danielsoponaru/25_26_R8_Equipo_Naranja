import pandas as pd
import IP2Location
import os

def procesar_network_flows(ruta_entrada, ruta_salida, ruta_db_ip, num_casos=100000, random_state=42):
    """
    Lee el dataset masivo, extrae una muestra y añade la región de las IPs.
    """
    print(f"⏳ Cargando datos desde: {ruta_entrada}...")
    df = pd.read_csv(ruta_entrada)
    
    print(f"🎲 Extrayendo {num_casos} casos aleatorios...")
    df_reducido = df.sample(n=num_casos, random_state=random_state).copy()    
    
    if not os.path.exists(ruta_db_ip):
        print(f"❌ Error: No se encuentra el archivo .BIN en {ruta_db_ip}")
        return df_reducido

    # Inicializamos la base de datos de IP2Location
    database = IP2Location.IP2Location(ruta_db_ip)
    
    def buscar_region(ip):
        try:
            return database.get_region(ip)
        except:
            return "Unknown"

    print("🌍 Enriqueciendo IPs con localización regional...")
    if 'Source.IP' in df_reducido.columns and 'Destination.IP' in df_reducido.columns:
        df_reducido['Region_Origen'] = df_reducido['Source.IP'].apply(buscar_region)
        df_reducido['Region_Destino'] = df_reducido['Destination.IP'].apply(buscar_region)
    else:
        print("⚠️ Revisa el nombre de las columnas de IP en tu CSV.")

    df_reducido.to_csv(ruta_salida, index=False)
    print(f"✅ Archivo listo guardado en: {ruta_salida}")
    
    return df_reducido