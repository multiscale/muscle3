from libmuscle.outbox import Outbox
from libmuscle.mcp.message import Message

from copy import copy
import pytest

from ymmsl import Reference


@pytest.fixture
def outbox():
    return Outbox()


@pytest.fixture
def message():
    Ref = Reference.from_string
    return Message(
            Ref('sender.out'), Ref('receiver.in'),
            'testing'.encode('utf-8'))


def test_create_outbox():
    box = Outbox()
    assert box._Outbox__queue == []


def test_deposit_message(outbox, message):
    outbox.deposit(message)
    assert outbox._Outbox__queue == [message]


def test_retrieve_message(outbox, message):
    outbox._Outbox__queue = [message]
    assert outbox.retrieve() == message


def test_deposit_retrieve_order(outbox, message):
    m1 = copy(message)
    m2 = copy(message)

    outbox.deposit(m1)
    outbox.deposit(m2)

    assert outbox.retrieve() == m1
    assert outbox.retrieve() == m2
