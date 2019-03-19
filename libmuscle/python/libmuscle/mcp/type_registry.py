from libmuscle.mcp.direct_client import DirectClient
from libmuscle.mcp.direct_server import DirectServer
from libmuscle.mcp.pipe_client import PipeClient
from libmuscle.mcp.pipe_server import PipeServer
from libmuscle.mcp.tcp_client import TcpClient
from libmuscle.mcp.tcp_server import TcpServer


# These must be in order of preference, i.e. most efficient first
client_types = [DirectClient, PipeClient, TcpClient]


server_types = [DirectServer, PipeServer, TcpServer]
