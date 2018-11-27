from ymmsl import Reference

from libmuscle.mcp.message import Message


def test_create() -> None:
    sender = Reference.from_string('sender.port')
    receiver = Reference.from_string('receiver.port')
    data = (12345).to_bytes(2, 'little', signed=True)
    msg = Message(sender, receiver, data)
    assert msg.sender == sender
    assert msg.receiver == receiver
    assert msg.data == data
