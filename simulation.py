import random
import time
from multiprocessing import Process, Queue
from controllers.fan import kibic
from controllers.worker import pracownik_techniczny
from Logger import log
from Settings import K, VIP_COUNT

def symulacja():
    """Funkcja główna zarządzająca symulacją."""
    command_queue = Queue()
    pracownik = Process(target=pracownik_techniczny, args=(command_queue,))
    pracownik.start()

    kibice = []
    for i in range(K):
        druzyna = random.choice([0, 1])
        typ = "VIP" if i < VIP_COUNT else "zwykły"
        wiek = random.randint(10, 80)
        p = Process(target=kibic, args=(i, druzyna, typ, wiek))
        kibice.append(p)
        p.start()
        time.sleep(random.uniform(0.1, 0.3))

    try:
        while True:
            command = input("Podaj polecenie (sygnał1, sygnał2, sygnał3): ").strip()
            if command in {"sygnał1", "sygnał2", "sygnał3"}:
                command_queue.put(command)
                if command == "sygnał3":
                    break
            else:
                print("Nieprawidłowe polecenie.")
    except KeyboardInterrupt:
        log("Program zatrzymany przez użytkownika.")
    finally:
        for p in kibice:
            p.terminate()
        pracownik.terminate()