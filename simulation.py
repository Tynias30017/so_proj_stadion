import multiprocessing
import random
from multiprocessing import Event
import time
import os
from controllers.fan import kibic
from controllers.worker import pracownik_techniczny
from Logger import log
from Settings import K, VIP_COUNT

def symulacja():
    """
    Główna funkcja zarządzająca symulacją.

    Waliduje liczbę kibiców i VIP-ów, inicjalizuje rurę do komunikacji,
    uruchamia proces pracownika technicznego oraz procesy dla kibiców.
    Obsługuje polecenia użytkownika i kończy wszystkie procesy po zakończeniu symulacji.
    """
    try:
        # Walidacja liczby kibiców i VIP-ów
        if K <= 0:
            raise ValueError("Liczba kibiców (K) musi być większa od 0.")
        if VIP_COUNT < 0 or VIP_COUNT >= K:
            raise ValueError(
                "Liczba VIP-ów (VIP_COUNT) musi być większa lub równa 0 i mniejsza niż liczba kibiców (K).")

        # Inicjalizacja rury do komunikacji
        try:
            read_fd, write_fd = multiprocessing.Pipe()
        except OSError as e:
            log(f"Błąd podczas tworzenia rury: {e}")
            return

        #Inicjalizacja eventu koniec_meczu
        koniec_meczu = Event()

        # Uruchomienie procesu pracownika technicznego
        try:
            pid = os.fork()
            if pid == 0:
                pracownik_techniczny(read_fd, koniec_meczu)
                os._exit(0)
        except OSError as e:
            log(f"Błąd podczas tworzenia procesu pracownika technicznego: {e}")
            return

        # Tworzenie procesów dla kibiców
        kibice_pids = []
        for i in range(K):
            druzyna = random.choice([0, 1])
            typ = "VIP" if i < VIP_COUNT else "zwykły"
            wiek = random.randint(20, 80)

            if wiek < 15:  # Dziecko
                log(f"Dziecko {i} z drużyny {druzyna} wchodzi z opiekunem.")
                # Proces dla dziecka
                pid = os.fork()
                if pid == 0:
                    kibic(i, druzyna, "zwykły", wiek, is_child=True, shared_pipe=write_fd, koniec_meczu=koniec_meczu)
                    os._exit(0)
                kibice_pids.append(pid)
                # Proces dla opiekuna (przyjmujemy wiek opiekuna jako 30 lat)
                pid = os.fork()
                if pid == 0:
                    kibic(f"opiekun-{i}", druzyna, "zwykły", 30, shared_pipe=write_fd, koniec_meczu=koniec_meczu)
                    os._exit(0)
                kibice_pids.append(pid)
            else:
                # Proces dla dorosłego kibica
                pid = os.fork()
                if pid == 0:
                    kibic(i, druzyna, typ, wiek, shared_pipe=write_fd, koniec_meczu=koniec_meczu)
                    os._exit(0)
                kibice_pids.append(pid)
            time.sleep(random.uniform(0.1, 0.3))

        # Obsługa poleceń użytkownika
        try:
            while not koniec_meczu.is_set():
                command = input("Podaj polecenie (sygnał1, sygnał2, sygnał3): ").strip()
                write_fd.send(command)
        except KeyboardInterrupt:
            log("Program zatrzymany przez użytkownika.")
        except OSError as e:
            log(f"Błąd systemowy podczas obsługi poleceń: {e}")
        finally:
            # Zakończenie wszystkich procesów kibiców
            for pid in kibice_pids:
                try:
                    os.waitpid(pid, 0)
                    # os.kill(pid, 9)
                except OSError as e:
                    log(f"Błąd podczas zakończenia procesu kibica: {e}")
            try:
                write_fd.close()
            except Exception as e:
                log(f"Błąd podczas zamykania rury: {e}")

            log("Zakończono program i usunięto wszystkie struktury.")

    except ValueError as ve:
        print(f"Błąd walidacji danych wejściowych: {ve}")
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")
        raise e

