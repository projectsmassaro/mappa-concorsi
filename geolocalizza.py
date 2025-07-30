import json
import time
import requests
import re

# Cache per i risultati di geocoding
geocode_cache = {}

# Ritardo iniziale tra le richieste
delay = 1

def geocode_location(*queries):
    base_url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "MyGeocodingApp/1.0 (mail@amassaro.com)"}

    for q in queries:
        if not q:
            continue

        # Controlla se il risultato è già in cache
        if q in geocode_cache:
            return geocode_cache[q]

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
                lat, lon = results[0]["lat"], results[0]["lon"]
                # Memorizza il risultato in cache
                geocode_cache[q] = (lat, lon)
                return lat, lon
        except requests.exceptions.HTTPError as http_err:
            print(f"❌ Errore HTTP durante il geocoding di '{q}': {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"❌ Errore di richiesta durante il geocoding di '{q}': {req_err}")

        # Aumenta il ritardo in caso di errore
        global delay
        delay = min(delay * 2, 10)  # Raddoppia il ritardo, massimo 10 secondi
        time.sleep(delay)

    return None, None

def extract_place_from_title(titolo):
    match = re.search(r"\bdi\s+([A-Z][^\d,.;\n]+)", titolo, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

def simplify_query(query):
    # Rimuovi dettagli meno rilevanti dalla query
    return re.sub(r'\(.*?\)|"|\'', '', query).strip()

# Carica il file
with open("concorsi_per_regione.json", "r", encoding="utf-8") as f:
    regioni = json.load(f)

# Geolocalizzazione
for regione, concorsi in regioni.items():
    for c in concorsi:
        titolo = c.get("titolo", "")
        ente = c.get("ente", "")
        fallback_luogo = extract_place_from_title(titolo)
        query_combinata = f"{ente}, {regione}"

        lat, lon = geocode_location(query_combinata, ente, titolo)
        if not lat or not lon:
            simplified_query = simplify_query(query_combinata)
            lat, lon = geocode_location(simplified_query, fallback_luogo)

        c["lat"] = lat
        c["lon"] = lon
        print(f"📍 {titolo} → {lat}, {lon}")

# Salva file geolocalizzato
with open("concorsi_geolocalizzati.json", "w", encoding="utf-8") as f:
    json.dump(regioni, f, ensure_ascii=False, indent=2)

print("✅ File salvato: concorsi_geolocalizzati.json")

