import os
from Logger import log
from Settings import kontrola_zablokowana, aktywni_kibice

def pracownik_techniczny(read_fd):
    """
    Funkcja obsługująca pracownika technicznego.

    Odczytuje polecenia z rury i wykonuje odpowiednie akcje w zależności od otrzymanego sygnału.
    """
    try:
        while True:
            command = os.read(read_fd, 1024).decode()
            log(f"Otrzymano sygnał: {command}")
            if command == "sygnał1":
                log("Pracownik techniczny wstrzymuje wpuszczanie kibiców.")
            elif command == "sygnał2":
                log("Pracownik techniczny wznawia wpuszczanie kibiców.")
            elif command == "sygnał3":
                log("Pracownik techniczny rozpoczyna opuszczanie stadionu przez kibiców.")
                break
            elif command in {"tak", "nie"}:
                # Handle temporary pipe communication
                try:
                    temp_read_fd, temp_write_fd = os.pipe()
                    log(f"Tworzenie tymczasowej rury: read_fd={temp_read_fd}, write_fd={temp_write_fd}")
                    fan_command = command
                    log(f"Otrzymano wartość bron od kibica: {fan_command}")
                    if fan_command == "tak":
                        os.write(temp_write_fd, "1".encode())
                        log("Wysłano odpowiedź: 1 (NIE WPUSZCZONY)")
                    else:
                        os.write(temp_write_fd, "0".encode())
                        log("Wysłano odpowiedź: 0 (WPUSZCZONY)")
                except Exception as e:
                    log(f"Błąd podczas obsługi tymczasowej rury: {e}")
                finally:
                    os.close(temp_read_fd)
                    os.close(temp_write_fd)
                    log("Zamknięto tymczasową rurę.")
            else:
                log(f"Nieznany sygnał: {command}")
    except Exception as e:
        log(f"Błąd w procesie pracownika technicznego: {e}")
    finally:
        os.close(read_fd)
        log("Pracownik techniczny zakończył pracę.")