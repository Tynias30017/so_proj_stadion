from multiprocessing import Semaphore, Value, Event

# Parametry stadionu
K = 10  # Maksymalna liczba kibiców
VIP_COUNT = max(1, int(0.005 * K))  # Liczba kibiców VIP
MAX_STANOWISKO = 3
MAX_OSOBY_STANOWISKO = 3

# Synchronizacja
stanowiska = [Semaphore(MAX_OSOBY_STANOWISKO) for _ in range(MAX_STANOWISKO)]
stanowisko_druzyna = [Value('i', -1) for _ in range(MAX_STANOWISKO)]  # -1 oznacza brak drużyny
stanowisko_licznik = [Value('i', 0) for _ in range(MAX_STANOWISKO)]  # Liczba osób na stanowisku

kontrola_zablokowana = Event()
kontrola_zablokowana.clear()  # Domyślnie kontrola jest aktywna

aktywni_kibice = Value('i', 0)