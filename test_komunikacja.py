import unittest
from unittest.mock import patch
import os
import simulation

class TestSymulacjaCommandHandling(unittest.TestCase):

    @patch('os.write')
    @patch('builtins.input', side_effect=['sygnał1', 'sygnał2', 'sygnał3'])
    @patch('os.fork', return_value=1)
    @patch('os.pipe', return_value=(0, 1))
    @patch('os.close')
    def test_command_handling(self, mock_close, mock_pipe, mock_fork, mock_input, mock_write):
        simulation.symulacja()
        self.assertEqual(mock_write.call_count, 3)

if __name__ == '__main__':
    unittest.main()