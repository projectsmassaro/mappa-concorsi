import subprocess
import datetime
import logging
import os

# Configura il logging
log_path = os.path.join("logs", "errori.log")
os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename=log_path, level=logging.INFO)

def log(msg):
    time = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    logging.info(f"{time} {msg}")
    print(f"{time} {msg}")

def esegui(script):
    try:
        log(f"Eseguo: {script}")
        subprocess.run(["python3", script], check=True)
        log(f"✅ Completato: {script}")
    except subprocess.CalledProcessError as e:
        log(f"❌ Errore in {script}: {e}")

def aggiorna_git():
    try:
        log("🔄 Git add/commit/push...")
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "🤖 Aggiornamento automatico dati"], check=True)
        subprocess.run(["git", "push"], check=True)
        log("✅ Dati pushati su Git")
    except subprocess.CalledProcessError as e:
        log(f"❌ Errore Git: {e}")

def main():
    esegui("scarica_regioni.py")
    esegui("geolocalizza.py")
    aggiorna_git()

if __name__ == "__main__":
    main()

