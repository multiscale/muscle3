import time

from muscle_manager.mmp_server import MMPServicer
import muscle_manager.protocol.muscle_manager_protocol_pb2 as mmp
from google.protobuf.timestamp_pb2 import Timestamp


def test_create_servicer(logger):
    server = MMPServicer(logger)


def test_log_message(mmp_servicer):
    now = time.time()
    seconds = int(now)
    timestamp = Timestamp(seconds=seconds, nanos=int((now - seconds)*10**9))
    timestamp.FromJsonString(value="1970-01-01T00:00:00.000Z")
    message = mmp.LogMessage(
            instance_id='test_instance_id',
            operator=mmp.OPERATOR_B,
            timestamp=timestamp,
            level=mmp.LOG_LEVEL_WARNING,
            text='Testing log message')
    result = mmp_servicer.SubmitLogMessage(message, None)
    assert isinstance(result, mmp.LogResult)
