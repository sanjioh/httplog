import sys
import threading
import time
from datetime import datetime

from .formatters import AlertFormatter, StatsFormatter
from .thread_controller import ThreadController


class StatsObserver(ThreadController):
    _interval = 10   # TODO 10 secs

    def __init__(self, *, fd=None, formatter=None, lock=None, clock=None,
                 event=None):
        self._fd = fd or sys.stdout
        self._formatter = formatter or StatsFormatter()
        self._lock = lock or threading.Lock()
        self._clock = clock or time
        self._users = {}
        self._hosts = {}
        self._sections = {}
        self._record_count = 0
        self._bytes_transferred = 0
        self._start_time = self._clock.time()
        super().__init__(event)

    def _run(self):
        while not self._closing.is_set():
            with self._lock:
                rankings = [
                    sorted(counter.items(), key=lambda x: x[1])[:-6:-1]
                    for counter in (self._users, self._hosts, self._sections)
                ]
                record_rate = round(
                    self._record_count
                    / (self._clock.time() - self._start_time),
                )

                if self._record_count > 0:
                    print(
                        self._formatter.format(
                            rankings,
                            self._bytes_transferred,
                            self._record_count,
                            record_rate,
                        ),
                        file=self._fd,
                    )

            self._closing.wait(self._interval)

    def update(self, record):
        with self._lock:
            self._record_count += 1
            self._bytes_transferred += record.size
            user = record.authuser
            self._users[user] = self._users.setdefault(user, 0) + 1
            host = record.host
            self._hosts[host] = self._hosts.setdefault(host, 0) + 1
            section = record.section
            self._sections[section] = self._sections.setdefault(section, 0) + 1


class AlertObserver(ThreadController):
    _interval = 120  # TODO 2 min

    # TODO: fix kw-only args on everything
    def __init__(self, threshold, *, fd=None, formatter=None, lock=None,
                 event=None):
        self._threshold = threshold * self._interval
        self._fd = fd or sys.stdout
        self._formatter = formatter or AlertFormatter()
        self._lock = lock or threading.Lock()
        self._count = 0
        self._threshold_passed = False
        super().__init__(event)

    def _run(self):
        while not self._closing.is_set():
            with self._lock:
                now = datetime.now()
                if (
                    self._count >= self._threshold
                    and not self._threshold_passed
                ):
                    print(
                        self._formatter.format_high(
                            self._count,
                            self._interval,
                            now,
                        ),
                        file=self._fd,
                    )
                    self._threshold_passed = True

                if (
                    self._count < self._threshold
                    and self._threshold_passed
                ):
                    print(
                        self._formatter.format_low(
                            self._count,
                            self._interval,
                            now,
                        ),
                        file=self._fd,
                    )
                    self._threshold_passed = False

                self._count = 0

            self._closing.wait(self._interval)

    def update(self, record):
        with self._lock:
            self._count += 1
