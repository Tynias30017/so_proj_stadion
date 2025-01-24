import logging

# Konfiguracja loggera
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Logi na konsolę
        logging.FileHandler("stadion.log")  # Logi do pliku
    ]
)

def log(message):
    logging.info(message)