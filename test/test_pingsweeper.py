import unittest
from unittest.mock import patch, MagicMock
from ipaddress import ip_network, ip_address

# import the functions to be tested
from ..main.pingsweep import get_os_type, pinger, nslookup, ping_sweeper, get_user_input, get_ip_range


class TestPingSweep(unittest.TestCase):

    @patch('platform.system')
    def test_get_os_type(self, mock_system):
        mock_system.return_value = 'Windows'
        self.assertEqual(get_os_type(), 'Windows')
        mock_system.return_value = 'Linux'
        self.assertEqual(get_os_type(), 'Unix')

    @patch('subprocess.run')
    def test_pinger_windows_up(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0,
                                          stdout='Reply from 192.168.1.1: bytes=32 time=1ms TTL=128\n\nPing statistics for 192.168.1.1:\nPackets: Sent = 1, Received = 1, Lost = 0 (0% loss),\nApproximate round trip times in milli-seconds:\nMinimum = 1ms, Maximum = 1ms, Average = 1ms')
        result, is_up = pinger('192.168.1.1', 1, 0.25)
        self.assertTrue(is_up)
        self.assertIn('Status: UP', result)

    @patch('subprocess.run')
    def test_pinger_windows_down(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout='')
        result, is_up = pinger('192.168.1.1', 1, 0.25)
        self.assertFalse(is_up)
        self.assertIn('Status: DOWN', result)

    @patch('subprocess.run')
    def test_nslookup(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0,
                                          stdout='Server:  dns.google\nAddress:  8.8.8.8\n\nName:    example.com\nAddress:  93.184.216.34')
        hostname = nslookup('93.184.216.34')
        self.assertEqual(hostname, 'example.com')

    @patch('subprocess.run')
    @patch('pingsweep.nslookup')
    def test_ping_sweeper(self, mock_nslookup, mock_run):
        mock_nslookup.return_value = 'example.com'
        mock_run.return_value = MagicMock(returncode=0,
                                          stdout='Reply from 192.168.1.1: bytes=32 time=1ms TTL=128\n\nPing statistics for 192.168.1.1:\nPackets: Sent = 1, Received = 1, Lost = 0 (0% loss),\nApproximate round trip times in milli-seconds:\nMinimum = 1ms, Maximum = 1ms, Average = 1ms')

        ip_list = [ip_address('192.168.1.1'), ip_address('192.168.1.2')]
        with patch('pingsweep.save_results'):
            ping_sweeper(ip_list, batch_size=2, timeout=0.25, count=1)

    @patch('builtins.input', side_effect=['192.168.1.0/24'])
    def test_get_user_input(self, mock_input):
        result = get_user_input("Enter subnet in CIDR notation: ")
        self.assertEqual(result, ip_network('192.168.1.0/24'))

    @patch('builtins.input', side_effect=['192.168.1.10', '192.168.1.20'])
    def test_get_ip_range(self, mock_input):
        result = get_ip_range()
        expected_result = [ip_address(ip) for ip in
                           range(int(ip_address('192.168.1.10')), int(ip_address('192.168.1.20')) + 1)]
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()