import time
import random
from time import sleep
import os
from Logger import log
from Settings import stanowiska, stanowisko_druzyna, stanowisko_licznik, kontrola_zablokowana, aktywni_kibice

def kibic(id, druzyna, typ, wiek, is_child=False, shared_pipe=None, koniec_meczu=None):
    """
    Proces reprezentujący kibica.

    Parametry:
    id (int): Identyfikator kibica.
    druzyna (int): Drużyna kibica (0 lub 1).
    typ (str): Typ kibica ('VIP' lub 'zwykły').
    wiek (int): Wiek kibica.
    is_child (bool): Czy kibic jest dzieckiem.
    shared_pipe (Optional[int]): Opcjonalny deskryptor rury do komunikacji.
    """
    if typ == "VIP":
        log(f"Kibic VIP {id} wchodzi na stadion bez kontroli.")
        with aktywni_kibice.get_lock():
            aktywni_kibice.value += 1
        return

    przepuszczeni_kibice = 0

    while not kontrola_zablokowana.is_set():
        time.sleep(0.1)  # Czeka na wznowienie kontroli

    while True:
        for stanowisko_id in range(len(stanowiska)):
            if stanowisko_druzyna[stanowisko_id].value in [-1, druzyna] and stanowiska[stanowisko_id].acquire(timeout=0.1):
                # if shared_pipe:
                    # shared_pipe.send(stanowisko_id)
                    #stanowisko_id = int(os.read(shared_pipe, 1).decode())
                with stanowisko_licznik[stanowisko_id].get_lock():
                    stanowisko_licznik[stanowisko_id].value += 1
                    liczba_osob = stanowisko_licznik[stanowisko_id].value
                if stanowisko_druzyna[stanowisko_id].value == -1:
                    stanowisko_druzyna[stanowisko_id].value = druzyna
                log(f"Kibic {id} drużyny {druzyna} przechodzi kontrolę na stanowisku {stanowisko_id}. Liczba osób na stanowisku: {liczba_osob}.")
                time.sleep(random.uniform(2, 3))  # Symulacja czasu kontroli
                if random.random() < 0.2:
                    log(f"Kibic {id} drużyny {druzyna} posiada bron.")
                    os._exit(0)

                with stanowisko_licznik[stanowisko_id].get_lock():
                    stanowisko_licznik[stanowisko_id].value -= 1
                if stanowisko_licznik[stanowisko_id].value == 0:
                    stanowisko_druzyna[stanowisko_id].value = -1
                stanowiska[stanowisko_id].release()
                log(f"Kibic {id} drużyny {druzyna} wszedł na stadion.")
                with aktywni_kibice.get_lock():
                    aktywni_kibice.value += 1
                koniec_meczu.wait()
                sleep(1)
                log(f"Kibic {id} drużyny {druzyna} opuścił stadion")
                return

        przepuszczeni_kibice += 1
        if przepuszczeni_kibice > 5:
            log(f"Kibic {id} drużyny {druzyna} blokuje kolejkę, czekając na zwolnienie miejsca.")
        time.sleep(0.1)