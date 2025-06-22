from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import time
import json
import re
from datetime import datetime

BASE_URL = "https://www.concorsipubblici.com"
REGIONI_URL = BASE_URL + "/concorsi/regione"

# === Slugify con casi speciali ===
def slugify(name):
    name = name.lower()\
               .replace("à", "a").replace("è", "e").replace("é", "e")\
               .replace("ù", "u").replace("ì", "i").replace("ò", "o")\
               .replace("’", "").replace("'", "")
    
    special_cases = {
        "friuli venezia giulia": "friuli_venezia_giulia",
        "trentino alto adige": "trentino_alto_adige",
        "valle d'aosta": "valle_d_aosta",
        "emilia romagna": "emilia_romagna"
    }

    if name in special_cases:
        return special_cases[name]

    return name.replace(" ", "-")

# === Headless Firefox ===
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)

print("🔁 Carico elenco delle regioni...")
driver.get(REGIONI_URL)
time.sleep(3)
soup = BeautifulSoup(driver.page_source, "html.parser")

region_links = soup.select("div#facet-localita ul li a")
regioni = {}
oggi = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

for a in region_links:
    nome_regione_raw = a.get_text(strip=True)
    solo_nome = re.sub(r'\d+', '', nome_regione_raw).strip()
    slug = slugify(solo_nome)
    url_regione = f"{BASE_URL}/concorsi/regione/loc/{slug}"

    print(f"\n📍 {solo_nome} → {url_regione}")
    driver.get(url_regione)
    time.sleep(5)
    regione_soup = BeautifulSoup(driver.page_source, "html.parser")
    concorsi = []

    for art in regione_soup.select("div.views-row article"):
        try:
            titolo_tag = art.select_one("h2.contest-title a")
            titolo = titolo_tag.text.strip()
            url_bando = BASE_URL + titolo_tag.get("href")
            ente = art.select_one("div.field--name-field-authority a").text.strip()
            scadenza = art.select_one("time").text.strip()

            # Converti scadenza da "gg/mm/aaaa" a oggetto datetime
            try:
                giorno, mese, anno = map(int, scadenza.split("/"))
                data_scadenza = datetime(anno, mese, giorno)
            except Exception as e:
                print(f"⚠️ Data non valida per: {titolo} → {scadenza}")
                continue

            # Filtro: solo concorsi non scaduti
            if data_scadenza >= oggi:
                concorsi.append({
                    "titolo": titolo,
                    "ente": ente,
                    "url": url_bando,
                    "scadenza": scadenza
                })
        except Exception as e:
            print(f"⚠️ Errore in un bando: {e}")
            continue

    regioni[solo_nome] = concorsi
    print(f"✅ Trovati {len(concorsi)} concorsi validi")

driver.quit()

# === Salva file ===
with open("concorsi_per_regione.json", "w", encoding="utf-8") as f:
    json.dump(regioni, f, ensure_ascii=False, indent=2)

print("\n🎉 File salvato: concorsi_per_regione.json")

