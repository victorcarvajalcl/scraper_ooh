import os
import zipfile
import requests
import geopandas as gpd

# =========================
# CONFIG
# =========================
ZIP_URL = "https://www.bcn.cl/siit/obtienearchivo?id=repositorio/10221/10396/1/division_comunal.zip"
ZIP_NAME = "division_comunal.zip"
EXTRACT_FOLDER = "tmp_comunas"
OUTPUT_FILE = "data/comunas.geojson"

# =========================
# PASO 1: Descargar ZIP
# =========================
print("⬇️ Descargando división comunal de Chile...")

response = requests.get(ZIP_URL, stream=True)
response.raise_for_status()

with open(ZIP_NAME, "wb") as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)

print(f"✅ Descargado: {ZIP_NAME}")

# =========================
# PASO 2: Descomprimir
# =========================
print("📦 Descomprimiendo archivos...")

os.makedirs(EXTRACT_FOLDER, exist_ok=True)

with zipfile.ZipFile(ZIP_NAME, "r") as zip_ref:
    zip_ref.extractall(EXTRACT_FOLDER)

print(f"✅ Extraído en: {EXTRACT_FOLDER}")

# =========================
# PASO 3: Buscar SHP
# =========================
shp_file = None
for root, dirs, files in os.walk(EXTRACT_FOLDER):
    for file in files:
        if file.endswith(".shp"):
            shp_file = os.path.join(root, file)
            break
    if shp_file:
        break

if not shp_file:
    raise FileNotFoundError("❌ No se encontró archivo .shp dentro del ZIP")

print(f"🗺 SHP encontrado: {shp_file}")

# =========================
# PASO 4: Leer shapefile
# =========================
print("📖 Leyendo geometrías...")

gdf = gpd.read_file(shp_file)

print("Columnas encontradas:")
print(gdf.columns.tolist())

# =========================
# PASO 5: Filtrar Región Metropolitana
# =========================
possible_region_cols = ["NOM_REG", "nom_reg", "REGION", "region", "Region"]
region_col = None

for col in possible_region_cols:
    if col in gdf.columns:
        region_col = col
        break

if not region_col:
    raise ValueError("❌ No se encontró columna de región")

rm_keywords = [
    "Región Metropolitana de Santiago",
    "Region Metropolitana de Santiago",
    "Metropolitana"
]

gdf_rm = gdf[gdf[region_col].astype(str).str.contains("|".join(rm_keywords), case=False, na=False)].copy()

if gdf_rm.empty:
    print("⚠️ No encontró solo RM, se exportarán todas las comunas de Chile.")
    gdf_export = gdf.copy()
else:
    print(f"✅ Comunas encontradas en RM: {len(gdf_rm)}")
    gdf_export = gdf_rm

# =========================
# PASO 6: Renombrar campo comuna si existe
# =========================
possible_comuna_cols = ["NOM_COMUNA", "nom_comuna", "COMUNA", "comuna", "Comuna"]
comuna_col = None

for col in possible_comuna_cols:
    if col in gdf_export.columns:
        comuna_col = col
        break

if comuna_col and comuna_col != "comuna":
    gdf_export["comuna"] = gdf_export[comuna_col]

# =========================
# PASO 7: Reproyectar a WGS84
# =========================
if gdf_export.crs is not None and gdf_export.crs.to_string() != "EPSG:4326":
    print(f"🌍 Reproyectando desde {gdf_export.crs} a EPSG:4326...")
    gdf_export = gdf_export.to_crs(epsg=4326)

# =========================
# PASO 8: Guardar GeoJSON
# =========================
os.makedirs("data", exist_ok=True)
gdf_export.to_file(OUTPUT_FILE, driver="GeoJSON")

print(f"🎉 GeoJSON generado correctamente: {OUTPUT_FILE}")
print(f"📍 Total comunas exportadas: {len(gdf_export)}")