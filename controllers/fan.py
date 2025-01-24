import time
import random
from multiprocessing import Semaphore, Process
from Logger import log
from Settings import stanowiska, stanowisko_druzyna, stanowisko_licznik, kontrola_zablokowana, aktywni_kibice

def kibic(id, druzyna, typ, wiek):
    """Proces reprezentujący kibica."""
    if typ == "VIP":
        log(f"Kibic VIP {id} wchodzi na stadion bez kontroli.")
        with aktywni_kibice.get_lock():
            aktywni_kibice.value += 1
        return

    przepuszczeni_kibice = 0

    while not kontrola_zablokowana.is_set():
        time.sleep(0.1)  # Czeka na wznowienie kontroli

    while przepuszczeni_kibice <= 5:
        for stanowisko_id in range(len(stanowiska)):
            if stanowisko_druzyna[stanowisko_id].value in [-1, druzyna] and stanowiska[stanowisko_id].acquire(timeout=0.1):
                with stanowisko_licznik[stanowisko_id].get_lock():
                    stanowisko_licznik[stanowisko_id].value += 1
                if stanowisko_druzyna[stanowisko_id].value == -1:
                    stanowisko_druzyna[stanowisko_id].value = druzyna
                log(f"Kibic {id} drużyny {druzyna} przechodzi kontrolę na stanowisku {stanowisko_id}.")
                time.sleep(random.uniform(2, 3))  # Symulacja czasu kontroli
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
        time.sleep(0.1)

    log(f"Kibic {id} drużyny {druzyna} staje się agresywny i opuszcza kolejkę.")
    with aktywni_kibice.get_lock():
        aktywni_kibice.value -= 1