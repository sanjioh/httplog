"""Log file monitoring tool."""
import argparse
import signal
import sys
import threading

from .file_reader import FileReader
from .observers import AlertObserver, StatsObserver


def _cli():
    parser = argparse.ArgumentParser(
        description='Monitor live web server logs.',
    )
    parser.add_argument(
        'filename',
        help='Path to the log file to monitor.',
    )
    parser.add_argument(
        '--threshold', '-t',
        type=int,
        default=100,
        help='Alert threshold (requests/s).',
    )
    args = parser.parse_args()
    return args.filename, args.threshold


def main():
    """Program entry point."""
    filename, threshold = _cli()

    try:
        fd = open(filename)
    except OSError as e:
        sys.exit(f'File "{filename}" cannot be opened ({e.strerror}).')

    lock = threading.Lock()
    so = StatsObserver(lock=lock)
    ao = AlertObserver(threshold, lock=lock)
    fr = FileReader(fd, observers=[so, ao])

    def sighandler(signum, frame):
        print('\nShutting down...')
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
