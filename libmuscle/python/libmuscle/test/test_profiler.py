from libmuscle.profiling import (
        ProfileEvent, ProfileEventType, ProfileTimestamp)

import time


def test_recording_events(mocked_profiler) -> None:
    profiler, _ = mocked_profiler

    t1 = ProfileTimestamp()
    t2 = ProfileTimestamp()
    e = ProfileEvent(ProfileEventType.REGISTER, t1, t2)

    profiler.record_event(e)

    assert e.start_time == t1
    assert e.stop_time == t2


def test_auto_stop_time(mocked_profiler) -> None:
    profiler, _ = mocked_profiler

    t1 = ProfileTimestamp()
    e = ProfileEvent(ProfileEventType.SEND, t1)

    profiler.record_event(e)

    assert e.start_time == t1
    assert e.stop_time is not None
    assert e.start_time.nanoseconds < e.stop_time.nanoseconds


def test_send_to_manager(profiler_comm_int_10ms, mocked_profiler) -> None:
    profiler, mock_mmp_client = mocked_profiler

    e1 = ProfileEvent(ProfileEventType.RECEIVE, ProfileTimestamp())
    profiler.record_event(e1)

    time.sleep(0.1)
    assert mock_mmp_client.sent_events == [e1]

    mock_mmp_client.sent_events = None
    e2 = ProfileEvent(ProfileEventType.RECEIVE, ProfileTimestamp())
    profiler.record_event(e2)

    time.sleep(0.1)
    assert mock_mmp_client.sent_events == [e2]

    mock_mmp_client.sent_events = None
    profiler.set_level('none')
    e3 = ProfileEvent(ProfileEventType.RECEIVE, ProfileTimestamp())
    profiler.record_event(e3)

    time.sleep(0.1)
    assert mock_mmp_client.sent_events is None
