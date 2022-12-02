from libmuscle.profiling import ProfileEvent, ProfileEventType
from libmuscle.timestamp import Timestamp


def test_recording_events(mocked_profiler) -> None:
    profiler, _ = mocked_profiler

    t1 = Timestamp()
    t2 = Timestamp()
    e = ProfileEvent(ProfileEventType.REGISTER, t1, t2)

    profiler.record_event(e)

    assert e.start_time == t1
    assert e.stop_time == t2
    assert e in profiler._events


def test_auto_stop_time(mocked_profiler) -> None:
    profiler, _ = mocked_profiler

    t1 = Timestamp()
    e = ProfileEvent(ProfileEventType.SEND, t1)

    profiler.record_event(e)

    assert e.start_time == t1
    assert e.stop_time is not None
    assert e.start_time.seconds < e.stop_time.seconds


def test_send_to_manager(mocked_profiler) -> None:
    profiler, mock_mmp_client = mocked_profiler

    for i in range(99):
        e1 = ProfileEvent(ProfileEventType.RECEIVE, Timestamp())
        profiler.record_event(e1)

    assert mock_mmp_client.sent_events is None

    e2 = ProfileEvent(ProfileEventType.RECEIVE, Timestamp())
    profiler.record_event(e2)

    assert mock_mmp_client.sent_events is not None
    assert len(mock_mmp_client.sent_events) == 100
    assert e1 in mock_mmp_client.sent_events
    assert e2 in mock_mmp_client.sent_events
