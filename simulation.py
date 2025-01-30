import random
import time
import os
from controllers.fan import kibic
from controllers.worker import pracownik_techniczny
from Logger import log
from Settings import K, VIP_COUNT, aktywni_kibice

def symulacja():
    """Funkcja główna zarządzająca symulacją."""
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
        except OSError as e:
            log(f"Błąd podczas tworzenia rury: {e}")
            return

        # Uruchomienie procesu pracownika technicznego
        try:
            pid = os.fork()
            if pid == 0:
                os.close(read_fd)
                pracownik_techniczny(write_fd)
                os._exit(0)
            else:
                os.close(write_fd)
        except OSError as e:
            log(f"Błąd podczas tworzenia procesu pracownika technicznego: {e}")
            return

        # Tworzenie procesów dla kibiców
        kibice_pids = []
        for i in range(K):
            druzyna = random.choice([0, 1])
            typ = "VIP" if i < VIP_COUNT else "zwykły"
            wiek = random.randint(10, 14)

            if wiek < 15:  # Dziecko
                log(f"Dziecko {i} z drużyny {druzyna} wchodzi z opiekunem.")
                # Proces dla dziecka i opiekuna
                pid = os.fork()
                if pid == 0:
                    kibic(i, druzyna, "zwykły", wiek, is_child=True)
                    os._exit(0)
                kibice_pids.append(pid)
                pid = os.fork()
                if pid == 0:
                    kibic(f"opiekun-{i}", druzyna, "zwykły", 30, is_child=True)
                    os._exit(0)
                kibice_pids.append(pid)
                with aktywni_kibice.get_lock():
                    aktywni_kibice.value += 2  # Dodajemy dziecko i opiekuna do liczby aktywnych kibiców
            else:
                # Proces dla dorosłego kibica
                pid = os.fork()
                if pid == 0:
                    kibic(i, druzyna, typ, wiek)
                    os._exit(0)
                kibice_pids.append(pid)
                with aktywni_kibice.get_lock():
                    aktywni_kibice.value += 1  # Dodajemy dorosłego kibica do liczby aktywnych kibiców
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
                os.close(read_fd)
            except Exception as e:
                log(f"Błąd podczas zamykania rury: {e}")

            log("Zakończono program i usunięto wszystkie struktury.")

    except ValueError as ve:
        print(f"Błąd walidacji danych wejściowych: {ve}")
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")