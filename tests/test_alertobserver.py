"""Tests for httplog.observers.AlertObserver."""
import io
import time

import pytest

from httplog.observers import AlertObserver


class DummyLogRecord:
    """LogRecord placeholder."""


@pytest.fixture
def fd():
    return io.StringIO()


@pytest.fixture
def formatter():
    class StubFormatter:
        def format_low(self, count, interval, datetime):
            return 'alarm recovered'

        def format_high(self, count, interval, datetime):
            return 'alarm triggered'

    return StubFormatter()


@pytest.fixture
def event():
    class FakeEvent:
        """
        Fake event class which enables fine control over the child thread
        execution.
        """
        def __init__(self):
            self._flag = False
            self._waiting = False

        def is_set(self):
            return self._flag

        def wait(self, timeout):
            self._waiting = True
            while self._waiting:
                time.sleep(0.01)

        def run_until_wait(self):
            self._waiting = False
            while not self._waiting:
                time.sleep(0.01)

        def stop(self):
            self._flag = True
            self._waiting = False

    return FakeEvent()


def test_no_alerts(fd, formatter, event):
    """
    AlertObserver should print no alerts at all if it is not notified
    of any log entry.
    """
    ao = AlertObserver(3, fd=fd, formatter=formatter, event=event)
    ao.start()
    event.run_until_wait()  # no print
    event.stop()
    assert fd.getvalue() == ''


def test_alert_high(fd, formatter, event):
    """
    AlertObserver should print an 'alarm triggered' alert if
    the number of log entries goes beyond the threshold.
    """
    ao = AlertObserver(3, fd=fd, formatter=formatter, event=event)
    ao.start()
    event.run_until_wait()
    for _ in range(360):
        ao.update(DummyLogRecord())
    event.run_until_wait()  # 'alarm triggered'
    event.stop()
    assert fd.getvalue() == 'alarm triggered\n'


def test_alert_high_doesnt_fire_twice(fd, formatter, event):
    """
    AlertObserver should print an 'alarm triggered' alert only once if
    the number of log entries goes beyond the threshold multiple times
    in a row.
    """
    ao = AlertObserver(3, fd=fd, formatter=formatter, event=event)
    ao.start()
    event.run_until_wait()
    for _ in range(360):
        ao.update(DummyLogRecord())
    event.run_until_wait()  # 'alarm triggered'
    for _ in range(360):
        ao.update(DummyLogRecord())
    event.run_until_wait()  # no print
    event.stop()
    assert fd.getvalue() == 'alarm triggered\n'


def test_alert_low(fd, formatter, event):
    """
    AlertObserver should print an 'alarm triggered' alert followed by
    an 'alarm recovered' alert if the number of log entries goes beyond the
    threshold and then comes back to normal.
    """
    ao = AlertObserver(3, fd=fd, formatter=formatter, event=event)
    ao.start()
    event.run_until_wait()
    for _ in range(360):
        ao.update(DummyLogRecord())
    event.run_until_wait()  # 'alarm triggered'
    for _ in range(359):
        ao.update(DummyLogRecord())
    event.run_until_wait()  # 'alarm recovered'
    event.stop()
    assert fd.getvalue() == 'alarm triggered\nalarm recovered\n'


def test_alert_low_doesnt_fire_twice(fd, formatter, event):
    """
    AlertObserver should print an 'alarm recovered' alert only once if
    the number of log entries goes beyond the threshold and then stays below it
    multiple times in a row.
    """
    ao = AlertObserver(3, fd=fd, formatter=formatter, event=event)
    ao.start()
    event.run_until_wait()
    for _ in range(360):
        ao.update(DummyLogRecord())
    event.run_until_wait()  # 'alarm triggered'
    for _ in range(359):
        ao.update(DummyLogRecord())
    event.run_until_wait()  # 'alarm recovered'
    for _ in range(359):
        ao.update(DummyLogRecord())
    event.run_until_wait()  # no print
    event.stop()
    assert fd.getvalue() == 'alarm triggered\nalarm recovered\n'
