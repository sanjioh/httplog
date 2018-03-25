from .parsers import LogRecord
from .thread_controller import ThreadController


class FileReader(ThreadController):
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
