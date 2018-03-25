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
    _banner_start = f"{20*'='} STATS {20*'='}"
    _format_string = '  {}. {} ({})'
    _titles = [
        'Top 5 users',
        'Top 5 hosts',
        'Top 5 sections',
    ]
    _banner_end = ''

    def format(self, rankings, bytes_transferred, record_count, record_rate):
        users, hosts, sections = rankings
        boards = []
        for title, ranking in zip(self._titles, rankings):
            rows = '\n'.join([self._format_string.format(idx+1, *item)
                              for idx, item in enumerate(ranking)])
            board = f'{title}\n{rows}'.format(title, rows)
            boards.append(board)
        boards = '\n\n'.join(boards)
        total_records = (f'Total records processed: {record_count} '
                         f'({record_rate} records/s avg)')
        total_bytes = (f'Total bytes transferred: {bytes_transferred} '
                       f'({_human_bytes(bytes_transferred)})')
        return (
            f'{self._banner_start}\n'
            f'{boards}\n\n'
            f'{total_records}\n'
            f'{total_bytes}\n'
            f'{self._banner_end}'
        )


class AlertFormatter:
    _banner_start = f"{20*'='} ALERT {20*'='}"
    _time_format = '%Y-%m-%d %H:%M:%S'
    _format_strings = {
        'high': ('High traffic generated an alert - hits = {}\n'
                 '({} reqs/s avg over the last {}s)\n'
                 'Triggered at {}'),
        'low': ('Traffic is back to normal - hits = {}\n'
                '({} reqs/s avg over the last {}s)\n'
                'Recovered at {}'),
    }
    _banner_end = ''

    def _format(self, alert, count, interval, datetime):
        avg = round(count / interval)
        info = self._format_strings[alert].format(
            count, avg, interval, datetime.strftime(self._time_format))
        return (
            f'{self._banner_start}\n'
            f'{info}\n'
            f'{self._banner_end}'
        )

    def format_low(self, count, interval, datetime):
        return _green(self._format('low', count, interval, datetime))

    def format_high(self, count, interval, datetime):
        return _red(self._format('high', count, interval, datetime))
