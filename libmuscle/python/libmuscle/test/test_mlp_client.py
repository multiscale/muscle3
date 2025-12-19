import msgpack
from unittest.mock import MagicMock, patch
from time import sleep

from libmuscle.mcp.protocol import RequestType
from libmuscle.mlp_client import MLPClient


def test_create_mlp_client():
    with patch('libmuscle.mlp_client.TcpTransportClient') as mock_ttc:
        client = MLPClient('node_name', 'location')
        assert client._node_name == 'node_name'
        assert client._transport_client == mock_ttc.return_value
        mock_ttc.assert_called_with('location')


def test_close_mlp_client():
    with patch('libmuscle.mlp_client.TcpTransportClient'):
        client = MLPClient('node_name', 'location')
        client.close()
        client._transport_client.close.assert_called_once()


def test_report_usage():
    with patch('libmuscle.mlp_client.TcpTransportClient') as mock_ttc:
        mock_ttc.return_value.call.return_value = (msgpack.packb([0]), None)
        client = MLPClient('node_name', 'location')

        with patch('libmuscle.mlp_client.psutil') as mock_psutil:
            mock_process = MagicMock()
            mock_process.cpu_percent.return_value = 10.0
            mock_process.memory_info.return_value.vms = 1000
            mock_psutil.Process.return_value = mock_process

            client.report_usage([('instance1', 123)])
            sleep(1.5)  # necessary because of async nature of usage reporting
            client.report_usage([('instance1', 123)])

            mock_psutil.Process.assert_called_with(123)
            mock_process.cpu_percent.assert_called()
            mock_process.memory_info.assert_called()

            expected_usage = {'instance1': [10.0, 1000]}
            expected_request = [
                    RequestType.REPORT_USAGE.value,
                    'node_name', expected_usage]

            args, _ = client._transport_client.call.call_args
            decoded_request = msgpack.unpackb(args[0], raw=False)
            assert decoded_request == expected_request


def test_report_usage_no_pids():
    with patch('libmuscle.mlp_client.TcpTransportClient'):
        client = MLPClient('node_name', 'location')
        client.report_usage([])
        client._transport_client.call.assert_not_called()
