from ymmsl import Reference

from libmuscle.mcp.pipe_server import PipeServer
import libmuscle.mcp.pipe_multiplexer as mux


def test_server_shutdown(post_office):
    mux.add_instance('test_instance')
    server = PipeServer(Reference('test_instance'), post_office)
    mux.close_mux_ends('test_instance')
    server.close()
    mux.close_all_pipes()
