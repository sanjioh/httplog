"""
Thread controller module.

This module contains the base class used by
every other piece of logic which relies on
thread-based asynchronous execution.
"""
import threading


class ThreadController:
    """Start and stop a child thread gracefully."""

    def __init__(self, event=None):
        """Initialize a ThreadController object."""
        self._thread = None
        self._closing = event or threading.Event()

    def start(self):
        """
        Run core logic in a child thread.

        The _run() internal method must be provided by subclasses.
        """
        if self._thread is None and not self._closing.is_set():
            self._thread = threading.Thread(target=self._run)
            self._thread.start()

    def stop(self):
        """Stop the child thread."""
        self._closing.set()
        self._thread.join()
        self._thread = None
        self._closing.clear()
