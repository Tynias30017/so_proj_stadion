import unittest
from unittest.mock import patch
import os
import simulation

class TestSymulacjaProcessCreation(unittest.TestCase):

    @patch('os.fork', side_effect=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    @patch('os.pipe', return_value=(0, 1))
    @patch('os.close')
    @patch('os._exit')
    @patch('simulation.pracownik_techniczny')
    @patch('simulation.kibic')
    def test_process_creation(self, mock_kibic, mock_pracownik_techniczny, mock_exit, mock_close, mock_pipe, mock_fork):
        simulation.symulacja()
        self.assertEqual(mock_fork.call_count, 11)  # 1 pracownik techniczny + 10 kibiców

    @patch('os.fork', side_effect=OSError)
    @patch('os.pipe', return_value=(0, 1))
    @patch('simulation.log')
    def test_fork_error(self, mock_log, mock_pipe, mock_fork):
        simulation.symulacja()
        mock_log.assert_called_with("Błąd podczas tworzenia procesu pracownika technicznego: ")

if __name__ == '__main__':
    unittest.main()