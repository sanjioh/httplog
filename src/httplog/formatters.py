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
