import time
import random
from multiprocessing import Process, Semaphore, Lock, Event, Queue, Value
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


# Parametry stadionu
K = 20  # Maksymalna liczba kibiców
VIP_COUNT = max(1, int(0.005 * K))  # Liczba kibiców VIP
MAX_STANOWISKO = 3
MAX_OSOBY_STANOWISKO = 3

# Synchronizacja
stanowiska = [Semaphore(MAX_OSOBY_STANOWISKO) for _ in range(MAX_STANOWISKO)]
stanowisko_druzyna = [Value('i', -1) for _ in range(MAX_STANOWISKO)]  # -1 oznacza brak drużyny
stanowisko_licznik = [Value('i', 0) for _ in range(MAX_STANOWISKO)]  # Liczba osób na stanowisku

kontrola_zablokowana = Event()
kontrola_zablokowana.set()  # Domyślnie kontrola jest aktywna

mutex = Lock()

# Kolejka logów
log_queue = Queue()

# Licznik aktywnych kibiców na stadionie
aktywni_kibice = Value('i', 0)

def log(message):
    logging.info(message)

def logger():
    """Proces loggera - drukuje komunikaty z kolejki."""
    while True:
        message = log_queue.get()
        if message == "STOP":
            break
        print(message)

def dziecko_z_opiekunem(id, druzyna, wiek):
    dziecko_opiekun_sync = Semaphore(0)

    def dziecko():
        log(f"Dziecko {id} z drużyny {druzyna} wchodzi na stadion.")
        kibic(id, druzyna, "zwykły", wiek)
        dziecko_opiekun_sync.release()  # Powiadom opiekuna

    def opiekun():
        dziecko_opiekun_sync.acquire()  # Czekaj na dziecko
        log(f"Opiekun dziecka {id} z drużyny {druzyna} opuszcza stadion.")

    Process(target=dziecko).start()
    Process(target=opiekun).start()

def kibic(id, druzyna, typ, wiek):
    """Proces reprezentujący kibica."""
    if typ == "VIP":
        log(f"Kibic VIP {id} wchodzi na stadion bez kontroli.")
        with aktywni_kibice.get_lock():
            aktywni_kibice.value += 1
        return

    przepuszczeni_kibice = 0

    while not kontrola_zablokowana.is_set():
        time.sleep(0.1)  # Czeka na wznowienie kontroli

    while przepuszczeni_kibice <= 5:
        # Szukanie stanowiska dla swojej drużyny
        stanowisko_zajete = False
        for stanowisko_id in range(MAX_STANOWISKO):
            if stanowisko_druzyna[stanowisko_id].value in [-1, druzyna] and stanowiska[stanowisko_id].acquire(timeout=0.1):
                stanowisko_zajete = True
                with stanowisko_licznik[stanowisko_id].get_lock():
                    stanowisko_licznik[stanowisko_id].value += 1
                if stanowisko_druzyna[stanowisko_id].value == -1:
                    stanowisko_druzyna[stanowisko_id].value = druzyna
                log(f"Kibic {id} drużyny {druzyna} przechodzi kontrolę na stanowisku {stanowisko_id}.")
                time.sleep(random.uniform(2, 3))  # Symulacja czasu kontroli
                with stanowisko_licznik[stanowisko_id].get_lock():
                    stanowisko_licznik[stanowisko_id].value -= 1
                if stanowisko_licznik[stanowisko_id].value == 0:
                    stanowisko_druzyna[stanowisko_id].value = -1
                stanowiska[stanowisko_id].release()
                log(f"Kibic {id} drużyny {druzyna} wszedł na stadion.")
                with aktywni_kibice.get_lock():
                    aktywni_kibice.value += 1
                return

        if not stanowisko_zajete:
            przepuszczeni_kibice += 1
            time.sleep(0.1)

    log(f"Kibic {id} drużyny {druzyna} staje się agresywny i opuszcza kolejkę.")
    with aktywni_kibice.get_lock():
        aktywni_kibice.value -= 1

def pracownik_techniczny(command_queue):
    """Proces obsługujący polecenia kierownika stadionu."""
    while True:
        command = command_queue.get()

        if command == "sygnał1":
            log("Kontrola wstrzymana.")
            kontrola_zablokowana.clear()
        elif command == "sygnał2":
            log("Kontrola wznowiona.")
            kontrola_zablokowana.set()
        elif command == "sygnał3":
            log("Wszyscy kibice opuszczają stadion.")
            with aktywni_kibice.get_lock():
                aktywni_kibice.value = 0
            log("Stadion jest pusty. Powiadomiono kierownika.")
            break

def zatrzymaj_procesy(procesy):
    for p in procesy:
        if p.is_alive():
            p.terminate()
        p.join()

def symulacja():
    """Funkcja główna zarządzająca symulacją."""

    # Kolejka do komunikacji z pracownikiem technicznym
    command_queue = Queue()

    # Uruchomienie procesu pracownika technicznego
    pracownik = Process(target=pracownik_techniczny, args=(command_queue,))
    pracownik.start()

    # Startowanie procesów kibiców
    kibice = []
    for i in range(K):
        druzyna = random.choice([0, 1])  # 0 - Drużyna A, 1 - Drużyna B
        typ = "VIP" if i < VIP_COUNT else "zwykły"
        wiek = random.randint(10, 80)

        if wiek < 15:  # Dziecko
            dziecko_z_opiekunem(i, druzyna, wiek)
        else:
            p = Process(target=kibic, args=(i, druzyna, typ, wiek))
            kibice.append(p)
            p.start()

        time.sleep(random.uniform(0.1, 0.3))  # Kibice przychodzą stopniowo

    # Obsługa poleceń użytkownika
    VALID_COMMANDS = {"sygnał1", "sygnał2", "sygnał3"}
    try:
        while True:
            command = input("Podaj polecenie (sygnał1, sygnał2, sygnał3): ").strip()
            if command not in VALID_COMMANDS:
                print("Nieprawidłowe polecenie. Spróbuj ponownie.")
                continue
            command_queue.put(command)
            if command == "sygnał3":
                break
    except KeyboardInterrupt:
        log("Program zatrzymany przez użytkownika.")
    finally:
        zatrzymaj_procesy(kibice + [pracownik])
        log("Procesy zakończone.")


if __name__ == "__main__":
    symulacja()