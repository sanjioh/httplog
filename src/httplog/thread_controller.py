import threading


class ThreadController:
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
