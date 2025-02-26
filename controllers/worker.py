from multiprocessing import Queue
from Logger import log
from Settings import kontrola_zablokowana, aktywni_kibice
import os

def pracownik_techniczny(read_fd, koniec_meczu=None):
    """
    Funkcja pracownika technicznego obsługująca polecenia.

    Parametry:
    read_fd (int): Deskryptor pliku do odczytu z rury.
    """
    try:
        while True:
            command = read_fd.recv()
            if command:
                if command == "sygnał1":
                    # Obsługa sygnału 1
                    print("Otrzymano sygnał 1")
                    kontrola_zablokowana.clear()
                elif command == "sygnał2":
                    # Obsługa sygnału 2
                    print("Otrzymano sygnał 2")
                    kontrola_zablokowana.set()
                elif command == "sygnał3":
                    # Obsługa sygnału 3 i zakończenie pracy
                    print("Otrzymano sygnał 3, zakończenie pracy")
                    koniec_meczu.set()
                    break
                else:
                    print(f"Nieznane polecenie: {command}")
    except OSError as e:
        print(f"Błąd podczas odczytu z rury: {e}")
