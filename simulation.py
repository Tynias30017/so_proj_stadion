import random
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
            read_fd, write_fd = os.pipe()
            fan_read_fd, fan_write_fd = os.pipe()
        except OSError as e:
            log(f"Błąd podczas tworzenia rury: {e}")
            return

        # Uruchomienie procesu pracownika technicznego
        try:
            pid = os.fork()
            if pid == 0:
                os.close(write_fd)
                pracownik_techniczny(read_fd)
                os._exit(0)
            else:
                os.close(read_fd)
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
                    kibic(i, druzyna, "zwykły", wiek, shared_pipe=fan_write_fd)
                    os._exit(0)
                kibice_pids.append(pid)
                # Proces dla opiekuna (przyjmujemy wiek opiekuna jako 30 lat)
                pid = os.fork()
                if pid == 0:
                    kibic(f"opiekun-{i}", druzyna, "zwykły", 30, shared_pipe=fan_write_fd)
                    os._exit(0)
                kibice_pids.append(pid)
            else:
                # Proces dla dorosłego kibica
                pid = os.fork()
                if pid == 0:
                    kibic(i, druzyna, typ, wiek, shared_pipe=fan_write_fd)
                    os._exit(0)
                kibice_pids.append(pid)
            time.sleep(random.uniform(0.1, 0.3))

        # Obsługa poleceń użytkownika
        try:
            while True:
                command = input("Podaj polecenie (sygnał1, sygnał2, sygnał3): ").strip()
                if command in {"sygnał1", "sygnał2", "sygnał3"}:
                    try:
                        os.write(write_fd, command.encode())
                    except OSError as e:
                        log(f"Błąd podczas wysyłania polecenia do rury: {e}")
                        break
                    if command == "sygnał3":
                        break
                else:
                    print("Nieprawidłowe polecenie. Dostępne polecenia to: sygnał1, sygnał2, sygnał3.")
        except KeyboardInterrupt:
            log("Program zatrzymany przez użytkownika.")
        except OSError as e:
            log(f"Błąd systemowy podczas obsługi poleceń: {e}")
        finally:
            # Zakończenie wszystkich procesów kibiców
            for pid in kibice_pids:
                try:
                    os.kill(pid, 9)
                except OSError as e:
                    log(f"Błąd podczas zakończenia procesu kibica: {e}")

            # Zakończenie procesu pracownika technicznego
            try:
                os.kill(pid, 9)
            except OSError as e:
                log(f"Błąd podczas zakończenia procesu pracownika technicznego: {e}")

            # Zamykanie rury
            try:
                os.close(write_fd)
            except Exception as e:
                log(f"Błąd podczas zamykania rury: {e}")

            log("Zakończono program i usunięto wszystkie struktury.")

    except ValueError as ve:
        print(f"Błąd walidacji danych wejściowych: {ve}")
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")

def pracownik_techniczny(read_fd):
    """
    Funkcja obsługująca pracownika technicznego.

    Odczytuje polecenia z rury i wykonuje odpowiednie akcje w zależności od otrzymanego sygnału.
    """
    try:
        while True:
            command = os.read(read_fd, 1024).decode()
            if command == "sygnał1":
                log("Pracownik techniczny wstrzymuje wpuszczanie kibiców.")
                # Implementacja wstrzymania wpuszczania kibiców
            elif command == "sygnał2":
                log("Pracownik techniczny wznawia wpuszczanie kibiców.")
                # Implementacja wznowienia wpuszczania kibiców
            elif command == "sygnał3":
                log("Pracownik techniczny rozpoczyna opuszczanie stadionu przez kibiców.")
                # Implementacja opuszczania stadionu przez kibiców
                break
    except Exception as e:
        log(f"Błąd w procesie pracownika technicznego: {e}")
    finally:
        os.close(read_fd)
        log("Pracownik techniczny zakończył pracę.")