import json
import time
import requests
import re
from concurrent.futures import ThreadPoolExecutor

# Cache per i risultati di geocoding
geocode_cache = {}

# Ritardo iniziale tra le richieste
delay = 1

def geocode_location(query):
    global delay
    if not query:
        return None, None

    # Controlla se il risultato è già in cache
    if query in geocode_cache:
        return geocode_cache[query]

    base_url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "MyGeocodingApp/1.0 (mail@amassaro.com)"}
    params = {
        "q": query.strip(),
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
            geocode_cache[query] = (lat, lon)
            return lat, lon
    except requests.exceptions.RequestException as req_err:
        print(f"❌ Errore durante il geocoding di '{query}': {req_err}")

    # Aumenta il ritardo in caso di errore
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

def process_concorsi(regioni):
    with ThreadPoolExecutor(max_workers=5) as executor:
        for regione, concorsi in regioni.items():
            for c in concorsi:
                titolo = c.get("titolo", "")
                ente = c.get("ente", "")
                fallback_luogo = extract_place_from_title(titolo)
                query_combinata = f"{ente}, {regione}"

                # Invia la richiesta di geocoding in parallelo
                future = executor.submit(geocode_location, query_combinata)
                lat, lon = future.result()

                if not lat or not lon:
                    simplified_query = simplify_query(query_combinata)
                    future = executor.submit(geocode_location, simplified_query)
                    lat, lon = future.result()

                c["lat"] = lat
                c["lon"] = lon
                print(f"📍 {titolo} → {lat}, {lon}")

# Carica il file
with open("concorsi_per_regione.json", "r", encoding="utf-8") as f:
    regioni = json.load(f)

# Geolocalizzazione
process_concorsi(regioni)

# Salva file geolocalizzato
with open("concorsi_geolocalizzati.json", "w", encoding="utf-8") as f:
    json.dump(regioni, f, ensure_ascii=False, indent=2)

print("✅ File salvato: concorsi_geolocalizzati.json")

