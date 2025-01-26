import random
import time
from multiprocessing import Process, Queue
from controllers.fan import kibic
from controllers.worker import pracownik_techniczny
from Logger import log
from Settings import K, VIP_COUNT


def symulacja():
    """Funkcja główna zarządzająca symulacją."""
    try:
        # Walidacja liczby kibiców i VIP-ów
        if K <= 0:
            raise ValueError("Liczba kibiców (K) musi być większa od 0.")
        if VIP_COUNT < 0 or VIP_COUNT >= K:
            raise ValueError(
                "Liczba VIP-ów (VIP_COUNT) musi być większa lub równa 0 i mniejsza niż liczba kibiców (K).")

        # Inicjalizacja kolejki poleceń
        try:
            command_queue = Queue()
        except OSError as e:
            log(f"Błąd podczas tworzenia kolejki poleceń: {e}")
            return

        # Uruchomienie procesu pracownika technicznego
        try:
            pracownik = Process(target=pracownik_techniczny, args=(command_queue,))
            pracownik.start()
        except OSError as e:
            log(f"Błąd podczas tworzenia procesu pracownika technicznego: {e}")
            return

        # Tworzenie procesów dla kibiców
        kibice = []
        for i in range(K):
            druzyna = random.choice([0, 1])
            typ = "VIP" if i < VIP_COUNT else "zwykły"
            wiek = random.randint(10, 80)
            try:
                p = Process(target=kibic, args=(i, druzyna, typ, wiek))
                kibice.append(p)
                p.start()
            except OSError as e:
                log(f"Błąd podczas tworzenia procesu kibica {i}: {e}")
                return
            time.sleep(random.uniform(0.1, 0.3))

        # Obsługa poleceń użytkownika
        try:
            while True:
                command = input("Podaj polecenie (sygnał1, sygnał2, sygnał3): ").strip()
                if command in {"sygnał1", "sygnał2", "sygnał3"}:
                    try:
                        command_queue.put(command)
                    except OSError as e:
                        log(f"Błąd podczas wysyłania polecenia do kolejki: {e}")
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
            for p in kibice:
                try:
                    p.terminate()
                except OSError as e:
                    log(f"Błąd podczas zakończenia procesu kibica: {e}")

            # Zakończenie procesu pracownika technicznego
            try:
                pracownik.terminate()
            except OSError as e:
                log(f"Błąd podczas zakończenia procesu pracownika technicznego: {e}")


            # Można usunąć kolejki i inne struktury systemowe, np.:
            try:
                command_queue.close()  # Zamykanie kolejki
            except Exception as e:
                log(f"Błąd podczas zamykania kolejki: {e}")

            log("Zakończono program i usunięto wszystkie struktury.")

    except ValueError as ve:
        print(f"Błąd walidacji danych wejściowych: {ve}")
    except Exception as e:
        print(f"Wystąpił nieoczekiwany błąd: {e}")