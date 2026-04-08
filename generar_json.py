import csv, json, re

# -----------------------------
# 1) Arreglar coordenadas malas
# -----------------------------
def fix_coord(val):
    s = str(val).strip()
    if s.lower() == "nan" or s == "":
        return None

    sign = '-' if s.startswith('-') else ''
    digits = re.sub(r'\D', '', s)

    if not digits:
        return None

    # Latitudes Chile ~ -33.xxxxxx / Longitudes ~ -70.xxxxxx
    if len(digits) >= 3:
        return float(f"{sign}{digits[:2]}.{digits[2:]}")
    return float(sign + digits)

# -----------------------------------
# 2) Detectar comuna por nombre (base)
# -----------------------------------
def comuna_from_name(name):
    name = (name or "").lower()

    comunas = [
        "recoleta", "las condes", "providencia", "santiago", "maipu", "ñuñoa", "nunoa",
        "la reina", "penalolen", "peñalolen", "independencia", "renca", "vitacura",
        "estacion central", "san miguel", "la florida", "quilicura", "pudahuel",
        "cerrillos", "lo barnechea", "conchali", "conchalí", "macul", "la cisterna",
        "san joaquin", "san joaquín", "la granja", "el bosque", "pedro aguirre cerda",
        "parque arauco", "mall sport", "costanera center", "vivo los trapenses"
    ]

    for c in comunas:
        if c in name:
            return (
                c.title()
                .replace("Nunoa", "Ñuñoa")
                .replace("Penalolen", "Peñalolén")
                .replace("Conchali", "Conchalí")
                .replace("San Joaquin", "San Joaquín")
                .replace("Parque Arauco", "Las Condes")
                .replace("Mall Sport", "Las Condes")
                .replace("Costanera Center", "Providencia")
                .replace("Vivo Los Trapenses", "Lo Barnechea")
            )

    return "Sin comuna"

# -----------------------------------
# 3) Detectar categoría según ícono
# -----------------------------------
def categoria_from_icon(icon_url):
    icon = (icon_url or "").lower()

    if "marker-billboard" in icon:
        return "Letrero Publicitario"
    elif "marker-digital" in icon:
        return "Pantallas Digitales"
    elif "marker-street" in icon or "marker-urban" in icon:
        return "Mobiliario Urbano"
    elif "marker-bus" in icon:
        return "Bus"
    elif "marker-colectivo" in icon:
        return "Colectivo"
    elif "marker-metro" in icon:
        return "Metro"
    elif "marker-mall" in icon or "marker-shopping" in icon:
        return "Centro Comercial"
    elif "marker-airport" in icon:
        return "Aeropuerto"
    elif "marker-supermarket" in icon:
        return "Supermercado"
    elif "marker-terminal" in icon:
        return "Terminal de Buses"
    elif "marker-cinema" in icon:
        return "Cine"
    elif "marker-indoor" in icon:
        return "Indoor"
    elif "marker-misc" in icon:
        return "No tradicional"
    else:
        return "Otros"

# -----------------------------------
# 4) H3 (si está instalado)
# -----------------------------------
try:
    import h3
    H3_OK = True
except:
    H3_OK = False

rows = []

# ⚠️ ESTE es el archivo correcto que vimos en tu carpeta
csv_file = "1 soportes_vista_actual.csv"

with open(csv_file, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f, delimiter=';')

    for r in reader:
        lat = fix_coord(r.get("lat"))
        lng = fix_coord(r.get("lng"))

        if lat is None or lng is None:
            continue

        item = {
            "id": r.get("id"),
            "name": r.get("name"),
            "lat": lat,
            "lng": lng,
            "slug": r.get("slug"),
            "url": r.get("url"),
            "icon": r.get("icon"),
            "comuna": comuna_from_name(r.get("name")),
            "categoria": categoria_from_icon(r.get("icon"))
        }

        if H3_OK:
            item["h6"] = h3.latlng_to_cell(lat, lng, 6)
            item["h8"] = h3.latlng_to_cell(lat, lng, 8)

        rows.append(item)

with open("data/soportes_h3.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)

print(f"JSON creado con {len(rows)} soportes en data/soportes_h3.json")