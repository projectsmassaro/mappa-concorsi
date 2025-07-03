# geolocalizza.py
import json
import time
import requests
import re
import os
from datetime import datetime

base_path = os.path.dirname(os.path.abspath(__file__))
input_path = os.path.join(base_path, "concorsi_per_regione.json")
output_path = os.path.join(base_path, "concorsi_geolocalizzati.json")
log_path = os.path.join(base_path, "logs", "errori.log")
os.makedirs(os.path.join(base_path, "logs"), exist_ok=True)

def log_error(msg):
    with open(log_path, "a") as log:
        log.write(f"[{datetime.now()}] ❌ {msg}\n")

# === Carica il file ===
if not os.path.exists(input_path):
    log_error("File concorsi_per_regione.json non trovato.")
    raise FileNotFoundError("File concorsi_per_regione.json mancante.")

with open(input_path, "r", encoding="utf-8") as f:
    regioni = json.load(f)

def geocode_location(*queries):
    base_url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "GeoScraper/1.0"}

    for q in queries:
        if not q: continue
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
            log_error(f"Errore geocoding '{q}': {e}")
        time.sleep(1)
    return None, None

def extract_place_from_title(titolo):
    match = re.search(r"\bdi\s+([A-Z][^\d,.;\n]+)", titolo, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

for regione, concorsi in regioni.items():
    for c in concorsi:
        titolo = c.get("titolo", "")
        ente = c.get("ente", "")
        fallback_luogo = extract_place_from_title(titolo)
        query_combinata = f"{ente}, {regione}"

        lat, lon = geocode_location(query_combinata, ente, titolo)

        if not lat or not lon:
            lat, lon = geocode_location(fallback_luogo)

        c["lat"] = lat
        c["lon"] = lon
        print(f"📍 {titolo} → {lat}, {lon}")
        time.sleep(1)

try:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(regioni, f, ensure_ascii=False, indent=2)
    print(f"✅ File salvato: {output_path}")
except Exception as e:
    log_error(f"Errore salvataggio geolocalizzato: {e}")

