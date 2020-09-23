import multiprocessing as mp
import time
from ymmsl import Reference

from libmuscle.mcp.pipe_client import PipeClient
from libmuscle.mcp.pipe_server import PipeServer
import libmuscle.mcp.pipe_multiplexer as mux
from libmuscle.mcp.message import Message


def run_server(instance_id, receiver, post_office):
    server = PipeServer(instance_id, post_office)
    assert server.get_location().endswith('/{}'.format(instance_id))

    # wait for message to be sent
    while post_office.outboxes[receiver]._Outbox__queue.qsize() > 0:
        time.sleep(0.1)
    server.close()


def run_client(instance_id, server_location, receiver, message):
    assert PipeClient.can_connect_to(server_location)
    client = PipeClient(instance_id, server_location)

    message2 = client.receive(receiver)
    assert message.sender == message2.sender
    assert message.receiver == message2.receiver
    assert message.port_length == message2.port_length
    assert message.timestamp == message2.timestamp
    assert message.next_timestamp == message2.next_timestamp
    assert message.settings_overlay == message2.settings_overlay
    assert message.data == message2.data

    client.close()
    PipeClient.shutdown(instance_id)


def test_send_receive(receiver, post_office):
    message = Message(Reference('test_sender.test_port'), receiver,
                      None, 0.0, 1.0, bytes(), 'message'.encode('utf-8'))

    # prepare post office, it's about to get forked
    post_office.outboxes[receiver].deposit(message)

    # create server in separate process
    sender_instance_id = Reference('test_sender')
    mux.add_instance(sender_instance_id)
    server_proc = mp.Process(target=run_server,
                             args=(sender_instance_id, receiver, post_office),
                             name='PipeServer')
    server_proc.start()
    mux.close_instance_ends(sender_instance_id)

    # create client in separate process
    server_location = mux.get_address_for(sender_instance_id)

    recv_instance_id = Reference('test_receiver')
    mux.add_instance(recv_instance_id)
    client_proc = mp.Process(target=run_client,
                             args=(recv_instance_id, server_location, receiver,
                                   message),
                             name='PipeClient')
    client_proc.start()
    mux.close_instance_ends(recv_instance_id)

    # service connection requests
    mux.run()

    # shut down
    client_proc.join()
    server_proc.join()
