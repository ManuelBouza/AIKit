"""Captura de metadata de EventStream sin cambiar la regla terminal (Task 2)."""

from __future__ import annotations

from session_stream import EventStream


def test_event_stream_captures_assistant_message_id() -> None:
    stream = EventStream(lambda _session: None)
    stream.feed(
        b'{"type":"step_start","sessionID":"ses_1","part":{"messageID":"msg_1"}}\n'
    )
    assert stream.assistant_message_id == "msg_1"
    assert stream.assistant_message_mismatch is False
    assert stream.terminal is False


def test_event_stream_absent_message_id_stays_unaccredited() -> None:
    stream = EventStream(lambda _session: None)
    stream.feed(b'{"type":"step_start","sessionID":"ses_1","part":{}}\n')
    assert stream.assistant_message_id is None
    assert stream.assistant_message_mismatch is False


def test_event_stream_conflicting_message_ids_preserve_ambiguity() -> None:
    stream = EventStream(lambda _session: None)
    stream.feed(
        b'{"type":"step_start","sessionID":"ses_1","part":{"messageID":"msg_1"}}\n'
    )
    stream.feed(b'{"type":"text","sessionID":"ses_1","part":{"messageID":"msg_2"}}\n')
    assert stream.assistant_message_id is None
    assert stream.assistant_message_mismatch is True


def test_event_stream_session_mismatch_does_not_change_terminal_rule() -> None:
    stream = EventStream(lambda _session: None)
    stream.feed(
        b'{"type":"step_start","sessionID":"ses_1","part":{"messageID":"msg_1"}}\n'
    )
    stream.feed(
        b'{"type":"step_finish","sessionID":"ses_2",'
        b'"part":{"reason":"stop","messageID":"msg_1"}}\n'
    )
    assert stream.session_mismatch is True
    assert stream.terminal is False


def test_event_stream_terminal_marker_still_required() -> None:
    stream = EventStream(lambda _session: None)
    stream.feed(
        b'{"type":"step_start","sessionID":"ses_1","part":{"messageID":"msg_1"}}\n'
    )
    stream.feed(
        b'{"type":"step_finish","sessionID":"ses_1",'
        b'"part":{"reason":"stop","messageID":"msg_1"}}\n'
    )
    assert stream.assistant_message_id == "msg_1"
    assert stream.terminal is True


def test_event_stream_repeated_same_message_id_is_not_mismatch() -> None:
    stream = EventStream(lambda _session: None)
    stream.feed(
        b'{"type":"step_start","sessionID":"ses_1","part":{"messageID":"msg_1"}}\n'
    )
    stream.feed(b'{"type":"text","sessionID":"ses_1","part":{"messageID":"msg_1"}}\n')
    assert stream.assistant_message_id == "msg_1"
    assert stream.assistant_message_mismatch is False
