"""Log file monitoring tool."""
import re
import signal
import threading
import time


class LogRecord:
    _regexp = re.compile(
        r'^(\S+) (\S+) (\S+) \[([^\]]+)\] '
        r'"([A-Z]+) ([^ "]+)? HTTP/[0-9.]+" '
        r'([0-9]{3}) ([0-9]+|-)',
    )

    def __init__(self, line):
        match = self._regexp.match(line)
        (host, ident, authuser, date, method,
         resource, status, size) = match.groups()
        self.host = host
        self.ident = ident
        self.authuser = authuser
        self.date = date
        self.method = method
        self.resource = resource
        self.status = status
        self.size = int(size)
        self.section = f"/{resource.split('/', 2)[1]}"


class ThreadManager:
    def __init__(self):
        self._thread = None
        self._closing = threading.Event()

    def start(self):
        if self._thread is None and not self._closing.is_set():
            self._thread = threading.Thread(target=self._run)
            self._thread.start()

    def stop(self):
        self._closing.set()
        self._thread.join()
        self._thread = None
        self._closing.clear()


class FileReader(ThreadManager):
    def __init__(self, fd, *, parser=None, observers=None):
        self._fd = fd
        self._parser = parser or LogRecord
        self._observers = observers or []
        super().__init__()

    def _tail(self):
        self._fd.seek(0, 2)
        while not self._closing.is_set():
            line = self._fd.readline()
            if not line:
                self._closing.wait(0.1)
                continue
            yield line

    def _run(self):
        for line in self._tail():
            record = self._parser(line)
            for observer in self._observers:
                observer.update(record)


class StatsFormatter:
    _format_string = '{}. {} ({})'
    _titles = [
        'Users Top 5',
        'Hosts Top 5',
        'Sections Top 5',
    ]

    def format(self, rankings, transferred_bytes, record_count, record_rate):
        users, hosts, sections = rankings
        for tr in zip(self._titles, rankings):
            title, ranking = tr
            print(title)
            for idx, item in enumerate(ranking):
                print(self._format_string.format(idx+1, *item))
        print(f'Total records processed: {record_count} '
              f'({record_rate} records/s)')
        transferred_megabytes = int(transferred_bytes / (1024 * 1024))
        print(f'Transferred bytes: {transferred_bytes} '
              f'({transferred_megabytes} MB)')


class StatsObserver(ThreadManager):
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
                    / (self._clock.time() - self._start_time)
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


class AlertObserver(ThreadManager):
    def __init__(self, threshold, lock=None):
        self._threshold = threshold
        self._lock = lock or threading.Lock()
        self._count = self._prev_count = 0
        self._threshold_passed = False

    def _run(self):
        while not self._closing.is_set():
            with self._lock:
                if (
                    self._count - self._prev_count >= self._threshold
                    and not self._threshold_passed
                ):
                    print('high traffic')  # TODO: add time
                    self._threshold_passed = True

                if (
                    self._count - self._prev_count < self._threshold
                    and self._threshold_passed
                ):
                    print('low traffic')  # TODO: add time
                    self._threshold_passed = False

                self._prev_count = self._count

            self._closing.wait(120)

    def update(self, record):
        with self._lock:
            self._count += 1


def main():

    so = StatsObserver()

    fd = open('test.log')
    fr = FileReader(fd, observers=[so])

    def sighandler(signum, frame):
        print('Shutting down...')
        so.stop()
        fr.stop()
        fd.close()
        print('Goodbye!')

    signal.signal(signal.SIGINT, sighandler)

    so.start()
    fr.start()


if __name__ == '__main__':
    main()
