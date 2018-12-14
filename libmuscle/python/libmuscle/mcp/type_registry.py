from libmuscle.mcp.direct_client import DirectClient
from libmuscle.mcp.direct_server import DirectServer


# These must be in order of preference, i.e. most efficient first
client_types = [DirectClient]


server_types = [DirectServer]
