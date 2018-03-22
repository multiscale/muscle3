from libmuscle.logging import LogLevel, LogMessage, Timestamp
from libmuscle.mmp_client import MMPClient
from libmuscle.operator import Operator


def test_logging(mmp_server, caplog):
    client = MMPClient()
    message = LogMessage(
            instance_id='test_logging',
            operator=Operator.O_F,
            timestamp=Timestamp(2.0),
            level=LogLevel.CRITICAL,
            text='Integration testing')
    client.submit_log_message(message)

    assert caplog.records[0].name == 'test_logging'
    assert caplog.records[0].operator == 'O_F'
    assert caplog.records[0].time_stamp == '1970-01-01T00:00:02Z'
    assert caplog.records[0].levelname == 'CRITICAL'
    assert caplog.records[0].message == 'Integration testing'
