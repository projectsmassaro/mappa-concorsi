import subprocess
import datetime
import logging
import os

# === Configura logging ===
log_path = os.path.join("logs", "errori.log")
os.makedirs("logs", exist_ok=True)
logging.basicConfig(filename=log_path, level=logging.INFO)

def log(msg):
    time = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    logging.info(f"{time} {msg}")
    print(f"{time} {msg}")

def esegui(script):
    try:
        log(f"🚀 Eseguo: {script}")
        subprocess.run(["python3", script], check=True)
        log(f"✅ Completato: {script}")
    except subprocess.CalledProcessError as e:
        log(f"❌ Errore in {script}: {e}")

def aggiorna_git():
    try:
        log("🔄 Git add/commit/push...")
        subprocess.run(["git", "add", "."], cwd="/home/user/mappa-concorsi", check=True)
        subprocess.run(["git", "commit", "-m", "🤖 Aggiornamento automatico dati"], cwd="/home/user/mappa-concorsi", check=True)
        subprocess.run(["git", "push", "origin", "main"], cwd="/home/user/mappa-concorsi", check=True)
        log("✅ Dati pushati su Git")
    except subprocess.CalledProcessError as e:
        log(f"❌ Errore Git: {e}")

def invia_notifica_telegram():
    try:
        log("📨 Invio notifica Telegram...")
        subprocess.run(["python3", "/home/user/mappa-concorsi/notifica_telegram.py"], check=True)
        log("✅ Notifica Telegram inviata")
    except subprocess.CalledProcessError as e:
        log(f"❌ Errore invio Telegram: {e}")

def main():
    esegui("/home/user/mappa-concorsi/scarica_regioni.py")
    esegui("/home/user/mappa-concorsi/geolocalizza.py")
    aggiorna_git()
    invia_notifica_telegram()

if __name__ == "__main__":
    main()

