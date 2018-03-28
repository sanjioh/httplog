"""
File Reader module.

This module contains the class responsible for
reading the log file.
"""
from .parsers import LogRecord
from .thread_controller import ThreadController


class FileReader(ThreadController):
    """
    Read the log file and update the observers with LogRecord objects.

    This class is responsible for reading an actively written-to log file,
    building LogRecord objects out of every single line, and updating
    the observers with those objects.
    The read operation goes from the end of the file onwards (same behaviour
    as the tail *nix command).

    Execution is performed asynchronously using a child thread.
    """

    def __init__(self, fd, *, parser=None, observers=None, event=None):
        """Initialize a FileReader object."""
        self._fd = fd
        self._parser = parser or LogRecord
        self._observers = observers or []
        super().__init__(event)

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
