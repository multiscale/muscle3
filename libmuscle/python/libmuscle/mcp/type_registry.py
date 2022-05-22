from libmuscle.mcp.tcp_transport_client import TcpTransportClient
from libmuscle.mcp.tcp_transport_server import TcpTransportServer


# These must be in order of preference, i.e. most efficient first
transport_client_types = [TcpTransportClient]


transport_server_types = [TcpTransportServer]
