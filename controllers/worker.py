from multiprocessing import Queue
from Logger import log
from Settings import kontrola_zablokowana, aktywni_kibice
import os

def pracownik_techniczny(read_fd, fan_read_fd):
    """
    Funkcja pracownika technicznego obsługująca polecenia.

    Parametry:
    read_fd (int): Deskryptor pliku do odczytu z rury.
    """
    try:
        while True:
            command = os.read(read_fd, 1024).decode()
            if command:
                if command == "sygnał1":
                    # Obsługa sygnału 1
                    print("Otrzymano sygnał 1")
                elif command == "sygnał2":
                    # Obsługa sygnału 2
                    print("Otrzymano sygnał 2")
                elif command == "sygnał3":
                    # Obsługa sygnału 3 i zakończenie pracy
                    print("Otrzymano sygnał 3, zakończenie pracy")
                    break
                    # Read and log PIDs from fans
                try:
                    pid = os.read(fan_read_fd, 1024).decode()
                    if pid:
                        log(f"Kibic o PID {pid} wszedł na stadion.")
                except OSError as e:
                        log(f"Błąd podczas odczytu PID z rury: {e}")

                except Exception as e:
                    log(f"Błąd w procesie pracownika technicznego: {e}")
                finally:
                    os.close(read_fd)
                    os.close(fan_read_fd)
                    log("Pracownik techniczny zakończył pracę.")
    except OSError as e:
        print(f"Błąd podczas odczytu z rury: {e}")
    finally:
        os.close(read_fd)