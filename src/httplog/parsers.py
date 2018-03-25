import re


class LogRecord:
    _regexp = re.compile(  # TODO constant?
        r'^(\S+) (\S+) (\S+) \[([^\]]+)\] '
        r'"([A-Z]+) ([^ "]+)? HTTP/[0-9.]+" '
        r'([0-9]{3}) ([0-9]+|-)',
    )

    def __init__(self, line):
        match = self._regexp.match(line)
        (host, ident, authuser, date, method,
         resource, status, size) = match.groups()
        self.host = host
        self.ident = ident
        self.authuser = authuser
        self.date = date
        self.method = method
        self.resource = resource
        self.status = status
        self.size = int(size)
        self.section = f"/{resource.split('/', 2)[1]}"
