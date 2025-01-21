from multiprocessing import Process, Semaphore, Lock, Event, Queue
import time
import random

# Parametry stadionu
K = 20  # Maksymalna liczba kibiców
VIP_COUNT = max(1, int(0.005 * K))  # Liczba kibiców VIP
MAX_STANOWISKO = 3
MAX_OSOBY_STANOWISKO = 3

# Synchronizacja
stanowiska = [Semaphore(MAX_OSOBY_STANOWISKO) for _ in range(MAX_STANOWISKO)]
kontrola_zablokowana = Event()
kontrola_zablokowana.set()  # Domyślnie kontrola jest aktywna
mutex = Lock()

# Kolejka logów
log_queue = Queue()

def log(message):
    """Wysyła wiadomość do loggera."""
    log_queue.put(f"[{time.strftime('%H:%M:%S')}] {message}")

def logger():
    """Proces loggera - drukuje komunikaty z kolejki."""
    while True:
        message = log_queue.get()
        if message == "STOP":
            break
        print(message)

def kibic(id, drużyna, typ):
    """Proces reprezentujący kibica."""
    if typ == "VIP":
        log(f"Kibic VIP {id} wchodzi na stadion bez kontroli.")
        return

    log(f"Kibic {id} drużyny {drużyna} czeka w kolejce.")
    while not kontrola_zablokowana.is_set():
        time.sleep(0.1)  # Czeka na wznowienie kontroli

    with mutex:
        stanowisko_id = random.randint(0, MAX_STANOWISKO - 1)
        stanowiska[stanowisko_id].acquire()

    log(f"Kibic {id} drużyny {drużyna} przechodzi kontrolę na stanowisku {stanowisko_id}.")
    time.sleep(random.uniform(0.5, 2))  # Symulacja czasu kontroli
    stanowiska[stanowisko_id].release()
    log(f"Kibic {id} drużyny {drużyna} wszedł na stadion.")

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
            break

def symulacja():
    """Funkcja główna zarządzająca symulacją."""
    # Uruchomienie loggera
    log_process = Process(target=logger)
    log_process.start()

    # Kolejka do komunikacji z pracownikiem technicznym
    command_queue = Queue()

    # Uruchomienie procesu pracownika technicznego
    pracownik = Process(target=pracownik_techniczny, args=(command_queue,))
    pracownik.start()

    # Startowanie procesów kibiców
    kibice = []
    for i in range(K):
        drużyna = random.choice(["A", "B"])
        typ = "VIP" if i < VIP_COUNT else "zwykły"
        p = Process(target=kibic, args=(i, drużyna, typ))
        kibice.append(p)
        p.start()
        time.sleep(random.uniform(0.1, 0.3))  # Kibice przychodzą stopniowo

    # Obsługa poleceń użytkownika
    try:
        while True:
            command = input("Podaj polecenie (sygnał1, sygnał2, sygnał3): ").strip()
            command_queue.put(command)
            if command == "sygnał3":
                break
    except KeyboardInterrupt:
        print("Program zatrzymany przez użytkownika.")

    # Oczekiwanie na zakończenie procesów kibiców
    for p in kibice:
        p.join()

    # Zakończenie procesu loggera
    log_queue.put("STOP")
    log_process.join()

if __name__ == "__main__":
    symulacja()