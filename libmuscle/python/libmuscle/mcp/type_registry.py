from libmuscle.mcp.direct_client import DirectClient
from libmuscle.mcp.direct_server import DirectServer
from libmuscle.mcp.pipe_client import PipeClient
from libmuscle.mcp.pipe_server import PipeServer


# These must be in order of preference, i.e. most efficient first
client_types = [DirectClient, PipeClient]


server_types = [DirectServer, PipeServer]
