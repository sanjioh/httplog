"""
Formatters module.

This module includes classes that can be used to
properly format strings to be showed on the terminal.
"""


def _human_bytes(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return '{:.1f} {}{}'.format(num, unit, suffix)
        num /= 1024.0
    return '{:.1f} {}{}'.format(num, 'Yi', suffix)


def _green(s):
    return f'\033[92m{s}\033[0m'


def _red(s):
    return f'\033[91m{s}\033[0m'


class StatsFormatter:
    """Format statistics about log records."""

    _banner_start = f"{20*'='} STATS {20*'='}"
    _row = '  {}. {} ({})'
    _titles = [
        'Top 5 users',
        'Top 5 hosts',
        'Top 5 sections',
    ]
    _total_records = 'Total records processed: {} ({:.1f} records/s avg)'
    _total_bytes = 'Total bytes transferred: {} ({})'
    _banner_end = ''

    def format(self, rankings, bytes_transferred, record_count, record_rate):
        """Build a visually appealing representation of log file statistics."""
        users, hosts, sections = rankings
        boards = []
        for title, ranking in zip(self._titles, rankings):
            rows = '\n'.join([self._row.format(idx+1, *item)
                              for idx, item in enumerate(ranking)])
            board = f'{title}\n{rows}'
            boards.append(board)
        boards = '\n\n'.join(boards)
        total_records = self._total_records.format(record_count, record_rate)
        total_bytes = self._total_bytes.format(
            bytes_transferred, _human_bytes(bytes_transferred))

        return (
            f'{self._banner_start}\n'
            f'{boards}\n\n'
            f'{total_records}\n'
            f'{total_bytes}\n'
            f'{self._banner_end}'
        )


class AlertFormatter:
    """Format alert messages for 'triggered/recovered alarm' events."""

    _banner_start = f"{20*'='} ALERT {20*'='}"
    _time_format = '%Y-%m-%d %H:%M:%S'
    _alerts = {
        'high': ('High traffic generated an alert - hits = {}\n'
                 '({:.1f} reqs/s avg over the last {}s)\n'
                 'Triggered at {}'),
        'low': ('Traffic is back to normal - hits = {}\n'
                '({:.1f} reqs/s avg over the last {}s)\n'
                'Recovered at {}'),
    }
    _banner_end = ''

    def _format(self, alert, count, interval, datetime):
        avg = count / interval
        message = self._alerts[alert].format(
            count, avg, interval, datetime.strftime(self._time_format))
        return (
            f'{self._banner_start}\n'
            f'{message}\n'
            f'{self._banner_end}'
        )

    def format_low(self, count, interval, datetime):
        """Build 'alarm recovered' alert message."""
        return _green(self._format('low', count, interval, datetime))

    def format_high(self, count, interval, datetime):
        """Build 'alarm triggered' alert message."""
        return _red(self._format('high', count, interval, datetime))
