import io
import time

import pytest

from httplog.observers import AlertObserver


class DummyLogEntry:
    pass


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
    ao = AlertObserver(3, fd=fd, formatter=formatter, event=event)
    ao.start()
    event.run_until_wait()
    event.stop()
    assert fd.getvalue() == ''


def test_alert_high(fd, formatter, event):
    ao = AlertObserver(3, fd=fd, formatter=formatter, event=event)
    ao.start()
    event.run_until_wait()
    for _ in range(360):
        ao.update(DummyLogEntry())
    event.run_until_wait()
    event.stop()
    assert fd.getvalue() == 'alarm triggered\n'


def test_alert_high_doesnt_fire_twice(fd, formatter, event):
    ao = AlertObserver(3, fd=fd, formatter=formatter, event=event)
    ao.start()
    event.run_until_wait()
    for _ in range(360):
        ao.update(DummyLogEntry())
    event.run_until_wait()
    for _ in range(360):
        ao.update(DummyLogEntry())
    event.run_until_wait()
    event.stop()
    assert fd.getvalue() == 'alarm triggered\n'


def test_alert_low(fd, formatter, event):
    ao = AlertObserver(3, fd=fd, formatter=formatter, event=event)
    ao.start()
    event.run_until_wait()
    for _ in range(360):
        ao.update(DummyLogEntry())
    event.run_until_wait()
    for _ in range(359):
        ao.update(DummyLogEntry())
    event.run_until_wait()
    event.stop()
    assert fd.getvalue() == 'alarm triggered\nalarm recovered\n'


def test_alert_low_doesnt_fire_twice(fd, formatter, event):
    ao = AlertObserver(3, fd=fd, formatter=formatter, event=event)
    ao.start()
    event.run_until_wait()
    for _ in range(360):
        ao.update(DummyLogEntry())
    event.run_until_wait()
    for _ in range(359):
        ao.update(DummyLogEntry())
    event.run_until_wait()
    for _ in range(359):
        ao.update(DummyLogEntry())
    event.run_until_wait()
    event.stop()
    assert fd.getvalue() == 'alarm triggered\nalarm recovered\n'
