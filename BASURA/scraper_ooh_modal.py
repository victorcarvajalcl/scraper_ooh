import requests
import pandas as pd
import time
from bs4 import BeautifulSoup

# ==========================
# CONFIG
# ==========================
INPUT_CSV = "soportes_vista_actual.csv"
OUTPUT_CSV = "soportes_vista_actual_detallado.csv"

# ⚠️ Usa los mismos que tu script anterior
CSRF_TOKEN = "7msYFYPi7utugGLMHLFmcD9jDUQWzu0ZtYzb52Arb66zrO2rJRLPob5WDP8JabUssnTvvoT0sLrtSyY5o4XhJw"

COOKIE = "_oohpublicidad_session=ThJddlIrYrBSkb6ZS0SIyWZB%2B1Fw3TMMUeXeDrsQQq%2ByClvFc8ihlbH9sv1UBuTits9rVEuzsqdOviUD6AaZRRCYXtnwpGFa7srr5Dz4u4bvi%2FcAKX9LgjRkobS5UgzUyAwrSi1TEt73DquqKwbAoS5KegrTdp29dw82%2FTpnwUHd2enyqmjXboP6qqaKcY2wr7TEQjeE1nXZEB7qB4%2FbXVQflh6JvIvuKEZaKtzPPOgtC66BkEhK4eUvp6qMA%2FztyZFN0uZBNrYTGu559gBwxyZxbsduogdhdNJGR6Xd--MKfQysNzRfkbPorn--DHPpowApyl9ZAx8K5E8w4w%3D%3D"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html",
    "Referer": "https://maps.oohpublicidad.cl",
    "x-csrf-token": CSRF_TOKEN,
    "cookie": COOKIE
}

# ==========================
# CLASIFICADOR MEJORADO
# ==========================
def clasificar_soporte(texto):
    texto = (texto or "").lower()

    tipo = "Desconocido"
    modelo = "Desconocido"

    if "shelter" in texto or "refugio" in texto:
        tipo = "Refugio / Paradero"
        modelo = "Shelter"

    elif "muro" in texto:
        tipo = "Muro"
        modelo = "Muro Publicitario"

    elif "video wall" in texto:
        tipo = "Pantalla"
        modelo = "Video Wall"

    elif "led" in texto:
        tipo = "Pantalla"
        modelo = "LED"

    elif "pantalla" in texto:
        tipo = "Pantalla"
        modelo = "Digital"

    elif "paleta" in texto or "billboard" in texto:
        tipo = "Paleta / Billboard"
        modelo = "Billboard"

    return tipo, modelo


# ==========================
# EXTRAER INFO DEL MODAL
# ==========================
def obtener_detalle(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)

        if r.status_code != 200:
            return None, None

        soup = BeautifulSoup(r.text, "html.parser")

        # Texto completo del modal
        texto = soup.get_text(separator=" ", strip=True)

        # Intentar detectar dirección simple
        direccion = None

        return texto, direccion

    except Exception as e:
        print("Error modal:", e)
        return None, None


# ==========================
# MAIN
# ==========================
df = pd.read_csv(INPUT_CSV)

# ⚡ PRUEBA RÁPIDA: descomenta esta línea para probar con 20 registros primero
# df = df.head(20)

resultados = []

for i, row in df.iterrows():
    url = row["url"]

    print(f"🔍 {i+1}/{len(df)} - {row.get('name', 'Sin nombre')}")

    texto_modal, direccion = obtener_detalle(url)

    # Clasificación mejorada
    tipo, modelo = clasificar_soporte(
        str(row.get("name", "")) + " " + str(texto_modal or "")
    )

    resultados.append({
        **row.to_dict(),
        "tipo_soporte_detalle": tipo,
        "modelo_soporte_detalle": modelo,
        "direccion_detectada": direccion,
        "texto_modal": texto_modal
    })

    # ⚠️ importante: evitar bloqueo
    time.sleep(0.3)

    # Guardado parcial cada 100 filas por seguridad
    if (i + 1) % 100 == 0:
        pd.DataFrame(resultados).to_csv(
            OUTPUT_CSV,
            index=False,
            encoding="utf-8-sig"
        )
        print(f"💾 Guardado parcial en fila {i+1}")

df_final = pd.DataFrame(resultados)
df_final.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

print("\n✅ NUEVO ARCHIVO GENERADO")
print(f"📁 {OUTPUT_CSV}")
print(f"📊 Total: {len(df_final)}")