import io
import time

from httplog.observers import AlertObserver


class StubFormatter:
    def format_low(self, count, interval, datetime):
        # return f'LOW|{count}|{interval}|{datetime.isoformat()}'
        return 'alarm recovered'

    def format_high(self, count, interval, datetime):
        # return f'HIGH|{count}|{interval}|{datetime.isoformat()}'
        return 'alarm triggered'


class DummyLogEntry:
    pass


class FakeEvent:
    def __init__(self):
        self._flag = False
        self.do_wait = True
        self.waiting = False

    def is_set(self):
        return self._flag

    def set(self):
        self._flag = True

    def clear(self):
        self._flag = False

    def wait(self, timeout):
        self.waiting = True
        while self.do_wait:
            time.sleep(0.1)
        self.do_wait = True

    def wake(self):
        self.waiting = False
        self.do_wait = False

    def wait_for_pause(self):
        while not self.waiting:
            time.sleep(0.1)


def test_alert_high():
    fd = io.StringIO()
    fmt = StubFormatter()
    event = FakeEvent()
    ao = AlertObserver(3, fd=fd, formatter=fmt, event=event)
    ao.start()
    while not event.waiting:
        time.sleep(0.1)
    for _ in range(361):
        ao.update(DummyLogEntry())
    event.waiting = False
    event.do_wait = False
    while not event.waiting:
        time.sleep(0.1)
    event.set()
    event.do_wait = False
    assert fd.getvalue() == 'alarm triggered\n'


def test_alert_high_doesnt_fire_twice():
    fd = io.StringIO()
    fmt = StubFormatter()
    event = FakeEvent()
    ao = AlertObserver(3, fd=fd, formatter=fmt, event=event)
    ao.start()
    event.wait_for_pause()
    for _ in range(361):
        ao.update(DummyLogEntry())
    event.wake()
    event.wait_for_pause()
    for _ in range(361):
        ao.update(DummyLogEntry())
    event.wake()
    event.wait_for_pause()
    event.set()
    event.wake()
    assert fd.getvalue() == 'alarm triggered\n'
