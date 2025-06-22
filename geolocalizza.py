import json
import time
import requests
import re
from SPARQLWrapper import SPARQLWrapper, JSON

# === Carica il file ===
with open("concorsi_per_regione.json", "r", encoding="utf-8") as f:
    regioni = json.load(f)

# === Funzione di geocoding con Nominatim ===
def geocode_nominatim(*queries):
    base_url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "GeoScraper/1.0"}

    for q in queries:
        if not q:
            continue
        params = {
            "q": q.strip(),
            "format": "json",
            "limit": 1,
            "countrycodes": "it"
        }
        try:
            r = requests.get(base_url, params=params, headers=headers)
            r.raise_for_status()
            results = r.json()
            if results:
                return results[0]["lat"], results[0]["lon"]
        except Exception as e:
            print(f"❌ Errore geocoding Nominatim '{q}': {e}")
        time.sleep(1)
    return None, None

# === Geocoding con Wikidata ===
def geocode_wikidata(nome_ente):
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    query = f'''
    SELECT ?coord WHERE {{
      ?item rdfs:label "{nome_ente}"@it.
      ?item wdt:P625 ?coord.
    }}
    LIMIT 1
    '''
    try:
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        if results["results"]["bindings"]:
            coords = results["results"]["bindings"][0]["coord"]["value"]
            lon, lat = coords.replace("Point(", "").replace(")", "").split(" ")
            return lat, lon
    except Exception as e:
        print(f"❌ Errore Wikidata per '{nome_ente}': {e}")
    return None, None

# === Estrai parte dopo "di" nel titolo ===
def extract_place_from_title(titolo):
    match = re.search(r"\bdi\s+([A-Z][^\d,.;\n]+)", titolo, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

# === Geolocalizzazione combinata Wikidata + Nominatim ===
for regione, concorsi in regioni.items():
    for c in concorsi:
        titolo = c.get("titolo", "")
        ente = c.get("ente", "")
        fallback_luogo = extract_place_from_title(titolo)
        query_combinata = f"{ente}, {regione}"

        lat, lon = geocode_wikidata(ente)

        if not lat or not lon:
            lat, lon = geocode_nominatim(query_combinata, ente, titolo)

        if not lat or not lon:
            lat, lon = geocode_nominatim(fallback_luogo)

        c["lat"] = lat
        c["lon"] = lon
        print(f"📍 {titolo} → {lat}, {lon}")
        time.sleep(1)

# === Salva file geolocalizzato ===
with open("concorsi_geolocalizzati.json", "w", encoding="utf-8") as f:
    json.dump(regioni, f, ensure_ascii=False, indent=2)

print("✅ File salvato: concorsi_geolocalizzati.json")

