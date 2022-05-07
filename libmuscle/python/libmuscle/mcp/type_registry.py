from libmuscle.mcp.tcp_client import TcpClient
from libmuscle.mcp.tcp_server import TcpServer


# These must be in order of preference, i.e. most efficient first
client_types = [TcpClient]


server_types = [TcpServer]
