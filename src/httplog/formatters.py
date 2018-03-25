def _human_bytes(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return '{:.1f} {}{}'.format(num, unit, suffix)
        num /= 1024.0
    return '{:.1f} {}{}'.format(num, 'Yi', suffix)


class StatsFormatter:
    _format_string = '  {}. {} ({})'
    _titles = [
        'Top 5 users',
        'Top 5 hosts',
        'Top 5 sections',
    ]

    def format(self, rankings, bytes_transferred, record_count, record_rate):
        users, hosts, sections = rankings
        banner_start = '========== STATS START ========='
        boards = []
        for title, ranking in zip(self._titles, rankings):
            rows = '\n'.join([self._format_string.format(idx+1, *item)
                              for idx, item in enumerate(ranking)])
            board = f'{title}\n{rows}'.format(title, rows)
            boards.append(board)
        boards = '\n\n'.join(boards)
        total_records = (f'Total records processed: {record_count} '
                         f'({record_rate} records/s)')
        total_bytes = (f'Total bytes transferred: {bytes_transferred} '
                       f'({_human_bytes(bytes_transferred)})')
        banner_end = '========== STATS END ========='
        return (
            f'{banner_start}\n'
            f'{boards}\n\n'
            f'{total_records}\n'
            f'{total_bytes}\n'
            f'{banner_end}'
        )
