import pandas as pd
import json
import h3
import os

print("🚀 Iniciando generación de hexágonos...")

# ============================
# CONFIGURACIÓN
# ============================
ARCHIVO_H6 = "data/resumen_h6.csv"
ARCHIVO_H8 = "data/resumen_h8.csv"

SALIDA_H6 = "data/h6.geojson"
SALIDA_H8 = "data/h8.geojson"


def detectar_columna_hex(df):
    posibles = ["h6", "h8", "h3_index", "hex", "hex_id", "index"]
    for col in posibles:
        if col in df.columns:
            return col
    raise ValueError(f"❌ No se encontró columna hex válida. Columnas disponibles: {list(df.columns)}")


def fila_a_feature(row, columna_hex):
    hex_id = str(row[columna_hex]).strip()

    # Convertir hexágono H3 a coordenadas
    boundary = h3.cell_to_boundary(hex_id)

    # GeoJSON usa [lng, lat]
    coords = [[lng, lat] for lat, lng in boundary]
    coords.append(coords[0])  # cerrar polígono

    props = row.to_dict()
    props["hex"] = hex_id

    return {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [coords]
        },
        "properties": props
    }


def csv_a_geojson(archivo_csv, archivo_salida):
    print(f"\n📂 Procesando: {archivo_csv}")

    if not os.path.exists(archivo_csv):
        print(f"❌ No existe el archivo: {archivo_csv}")
        return

    df = pd.read_csv(archivo_csv)

    print(f"🧾 Columnas encontradas: {list(df.columns)}")
    print(f"📊 Filas encontradas: {len(df)}")

    if len(df) == 0:
        print(f"⚠️ El archivo {archivo_csv} está vacío")
        return

    columna_hex = detectar_columna_hex(df)
    print(f"🔎 Columna hex detectada: {columna_hex}")

    features = []

    for _, row in df.iterrows():
        try:
            feature = fila_a_feature(row, columna_hex)
            features.append(feature)
        except Exception as e:
            print(f"⚠️ Error con fila {row.to_dict()} -> {e}")

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(archivo_salida, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False)

    print(f"✅ Generado: {archivo_salida} ({len(features)} hexágonos)")


if __name__ == "__main__":
    csv_a_geojson(ARCHIVO_H6, SALIDA_H6)
    csv_a_geojson(ARCHIVO_H8, SALIDA_H8)
    print("\n🎯 Listo. GeoJSON H6 y H8 creados.")