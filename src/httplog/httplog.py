"""Log file monitoring tool."""
import signal

from .file_reader import FileReader
from .observers import AlertObserver, StatsObserver


def main():
    """Program entry point."""
    so = StatsObserver()
    ao = AlertObserver(10)

    fd = open('test.log')
    fr = FileReader(fd, observers=[so, ao])

    def sighandler(signum, frame):
        print('Shutting down...')
        so.stop()
        ao.stop()
        fr.stop()
        fd.close()
        print('Goodbye!')

    signal.signal(signal.SIGINT, sighandler)

    so.start()
    ao.start()
    fr.start()


if __name__ == '__main__':
    main()
