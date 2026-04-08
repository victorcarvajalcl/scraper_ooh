import requests
import pandas as pd
import time

API_URL = "https://maps.oohpublicidad.cl/espacios-publicitarios/mapa"

# ==========================
# DATOS REALES DE TU VISTA ACTUAL
# ==========================
BOUNDS = "[[ -33.32379318416692, -70.29950241970978 ], [ -33.51635866584017, -70.7677946560379 ]]"

FORMAT_IDS = (
    "67281296-bfcd-4cc8-9e15-a53e91522c88,"
    "93152d56-066a-4e5e-91c5-9bdff7bad610,"
    "c66d3c5a-a929-4b8b-bc53-d2ffddfc2748,"
    "c802b67f-0f85-487e-ab33-2bd467b749f5,"
    "b4cbbdb5-f216-4868-b761-6ee51364749f,"
    "75957e9b-6bcd-4b45-b48e-c225b289311f,"
    "9eb6afd2-378d-49f5-bc2c-2d964653056b,"
    "60bf29b4-dc43-4078-9215-2a1a604ffab2,"
    "a683579b-7ad4-4154-9670-8f51b344ee12,"
    "da1e0bd9-2ed1-4653-b334-9e76345b8c1e,"
    "5a8c40ff-544f-42e9-8cf6-e690b437689b,"
    "fde6e06f-db8b-4cc9-bcc8-8fcfc4dd6470,"
    "0f49eb35-5a3c-48ef-9318-d0c2dc232df4"
)

# ⚠️ Estos 2 debes actualizarlos si cambia tu sesión o recargas mucho
CSRF_TOKEN = "7msYFYPi7utugGLMHLFmcD9jDUQWzu0ZtYzb52Arb66zrO2rJRLPob5WDP8JabUssnTvvoT0sLrtSyY5o4XhJw"

COOKIE = "_oohpublicidad_session=ThJddlIrYrBSkb6ZS0SIyWZB%2B1Fw3TMMUeXeDrsQQq%2ByClvFc8ihlbH9sv1UBuTits9rVEuzsqdOviUD6AaZRRCYXtnwpGFa7srr5Dz4u4bvi%2FcAKX9LgjRkobS5UgzUyAwrSi1TEt73DquqKwbAoS5KegrTdp29dw82%2FTpnwUHd2enyqmjXboP6qqaKcY2wr7TEQjeE1nXZEB7qB4%2FbXVQflh6JvIvuKEZaKtzPPOgtC66BkEhK4eUvp6qMA%2FztyZFN0uZBNrYTGu559gBwxyZxbsduogdhdNJGR6Xd--MKfQysNzRfkbPorn--DHPpowApyl9ZAx8K5E8w4w%3D%3D"

HEADERS = {
    "accept": "application/json,text/vnd.turbo-stream.html",
    "origin": "https://maps.oohpublicidad.cl",
    "referer": "https://maps.oohpublicidad.cl/espacios-publicitarios/mapa?page%5Bcurrent%5D=1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "x-csrf-token": CSRF_TOKEN,
    "cookie": COOKIE
}

todos = []
page = 1

while True:
    print(f"\n📄 Descargando página {page}...")

    params = {
        "page[current]": page
    }

    # 👇 IMPORTANTE: multipart/form-data con files=
    files = {
        "ad_spaces[bounds]": (None, BOUNDS),
        "ad_spaces[format_ids]": (None, FORMAT_IDS),
    }

    r = requests.post(API_URL, headers=HEADERS, params=params, files=files, timeout=30)

    print("Status:", r.status_code)

    if r.status_code != 200:
        print("❌ Error HTTP")
        print(r.text[:1500])
        break

    # Si responde turbo-stream, no sirve
    if not r.text.strip().startswith("{"):
        print("⚠️ Respuesta no JSON:")
        print(r.text[:1000])
        break

    json_data = r.json()
    items = json_data.get("data", [])

    if not items:
        print("⚠️ No hay más datos")
        break

    for item in items:
        todos.append({
            "id": item.get("id"),
            "name": item.get("name"),
            "lat": item.get("lat"),
            "lng": item.get("lng"),
            "slug": item.get("slug"),
            "sku": item.get("sku"),
            "url": item.get("url"),
            "icon": item.get("icon")
        })

    meta = json_data.get("meta", {})
    pages = meta.get("pages", {})

    print(f"   → Registros acumulados: {len(todos)}")
    print(f"   → Página actual: {pages.get('current_page')}")
    print(f"   → Siguiente: {pages.get('next_page')}")
    print(f"   → Última: {pages.get('last_page')}")

    if not pages.get("next_page"):
        print("✅ Última página alcanzada")
        break

    page += 1
    time.sleep(1)

if todos:
    df = pd.DataFrame(todos)
    df.drop_duplicates(inplace=True)
    df.to_csv("soportes_vista_actual.csv", index=False, encoding="utf-8-sig")

    print("\n✅ Archivo generado: soportes_vista_actual.csv")
    print(f"📊 Total final: {len(df)} registros")
    print(df.head(20))
else:
    print("\n⚠️ No se generó CSV con datos.")