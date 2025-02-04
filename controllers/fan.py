import time
import random
import os
from Logger import log
from Settings import stanowiska, stanowisko_druzyna, stanowisko_licznik, kontrola_zablokowana, aktywni_kibice

def kibic(id, druzyna, typ, wiek, bron, is_child=False, shared_pipe=None):
    if typ == "VIP":
        log(f"Kibic VIP {id} wchodzi na stadion bez kontroli.")
        with aktywni_kibice.get_lock():
            aktywni_kibice.value += 1
        return

    przepuszczeni_kibice = 0

    while not kontrola_zablokowana.is_set():
        time.sleep(0.1)

    while True:
        for stanowisko_id in range(len(stanowiska)):
            if stanowisko_druzyna[stanowisko_id].value in [-1, druzyna] and stanowiska[stanowisko_id].acquire(timeout=0.1):
                with stanowisko_licznik[stanowisko_id].get_lock():
                    stanowisko_licznik[stanowisko_id].value += 1
                    liczba_osob = stanowisko_licznik[stanowisko_id].value
                if stanowisko_druzyna[stanowisko_id].value == -1:
                    stanowisko_druzyna[stanowisko_id].value = druzyna
                log(f"Kibic {id} drużyny {druzyna} przechodzi kontrolę na stanowisku {stanowisko_id}. Liczba osób na stanowisku: {liczba_osob}.")

                # Create a temporary pipe for communication
                temp_read_fd, temp_write_fd = os.pipe()
                try:
                    # Send the value of bron
                    os.write(temp_write_fd, str(bron).encode())
                    log(f"Kibic {id} wysłał wartość bron: {bron}")

                    # Send the temporary pipe file descriptors to the worker
                    os.write(shared_pipe, f"{temp_read_fd},{temp_write_fd}".encode())

                    response = os.read(temp_read_fd, 1024).decode()
                    log(f"Kibic {id} otrzymał odpowiedź: {response}")
                    if response == "1":
                        log(f"Kibic {id} drużyny {druzyna} nie został wpuszczony, ponieważ posiadał broń.")
                        return
                finally:
                    os.close(temp_read_fd)
                    os.close(temp_write_fd)
                    log("Zamknięto tymczasową rurę.")

                time.sleep(random.uniform(2, 3))
                with stanowisko_licznik[stanowisko_id].get_lock():
                    stanowisko_licznik[stanowisko_id].value -= 1
                if stanowisko_licznik[stanowisko_id].value == 0:
                    stanowisko_druzyna[stanowisko_id].value = -1
                stanowiska[stanowisko_id].release()
                log(f"Kibic {id} drużyny {druzyna} wszedł na stadion.")
                with aktywni_kibice.get_lock():
                    aktywni_kibice.value += 1
                return

        przepuszczeni_kibice += 1
        if przepuszczeni_kibice > 5:
            log(f"Kibic {id} drużyny {druzyna} blokuje kolejkę, czekając na zwolnienie miejsca.")
        time.sleep(2)