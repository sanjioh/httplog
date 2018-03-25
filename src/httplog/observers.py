import threading
import time

from .thread_controller import ThreadController
from .formatters import StatsFormatter


class StatsObserver(ThreadController):
    def __init__(self, formatter=None, lock=None, clock=None):
        self._formatter = formatter or StatsFormatter()
        self._lock = lock or threading.Lock()
        self._clock = clock or time
        self._users = {}
        self._hosts = {}
        self._sections = {}
        self._record_count = 0
        self._transferred_bytes = 0
        self._start_time = self._clock.time()
        super().__init__()

    def _run(self):
        while not self._closing.is_set():
            with self._lock:
                rankings = [
                    sorted(counter.items(), key=lambda x: x[1])[:-6:-1]
                    for counter in (self._users, self._hosts, self._sections)
                ]
                record_rate = int(
                    self._record_count
                    / (self._clock.time() - self._start_time),
                )

                self._formatter.format(
                    rankings,
                    self._transferred_bytes,
                    self._record_count,
                    record_rate,
                )
            self._closing.wait(10)

    def update(self, record):
        with self._lock:
            self._record_count += 1
            self._transferred_bytes += record.size
            user = record.authuser
            self._users[user] = self._users.setdefault(user, 0) + 1
            host = record.host
            self._hosts[host] = self._hosts.setdefault(host, 0) + 1
            section = record.section
            self._sections[section] = self._sections.setdefault(section, 0) + 1


class AlertObserver(ThreadController):
    def __init__(self, threshold, lock=None):
        self._threshold = threshold
        self._lock = lock or threading.Lock()
        self._count = 0
        self._threshold_passed = False
        super().__init__()

    def _run(self):
        prev_count = 0
        while not self._closing.is_set():
            with self._lock:
                if (
                    self._count - prev_count >= self._threshold
                    and not self._threshold_passed
                ):
                    print('high traffic')  # TODO: add time
                    self._threshold_passed = True

                if (
                    self._count - prev_count < self._threshold
                    and self._threshold_passed
                ):
                    print('low traffic')  # TODO: add time
                    self._threshold_passed = False

                prev_count = self._count

            self._closing.wait(5)  # TODO 2 min

    def update(self, record):
        with self._lock:
            self._count += 1
