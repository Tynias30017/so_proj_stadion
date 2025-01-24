from multiprocessing import Queue
from Logger import log
from Settings import kontrola_zablokowana, aktywni_kibice

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