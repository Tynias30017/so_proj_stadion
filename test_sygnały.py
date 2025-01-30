import unittest
import os
import time
from multiprocessing import Process
from simulation import pracownik_techniczny

class TestSymulacja(unittest.TestCase):
    def setUp(self):
        self.read_fd, self.write_fd = os.pipe()
        self.worker_process = Process(target=pracownik_techniczny, args=(self.read_fd,))
        self.worker_process.start()
        os.close(self.read_fd)

    def tearDown(self):
        os.write(self.write_fd, 'sygnał3'.encode('utf-8'))
        self.worker_process.join()
        os.close(self.write_fd)

    def test_sygnał1(self):
        os.write(self.write_fd, 'sygnał1'.encode('utf-8'))
        time.sleep(1)  # Czekaj na przetworzenie sygnału
        # Tutaj możesz dodać dodatkowe asercje, aby sprawdzić stan systemu

    def test_sygnał2(self):
        os.write(self.write_fd, 'sygnał2'.encode('utf-8'))
        time.sleep(1)  # Czekaj na przetworzenie sygnału
        # Tutaj możesz dodać dodatkowe asercje, aby sprawdzić stan systemu

if __name__ == '__main__':
    unittest.main()