import re

_LOG_RE = r'^(\S+) \S+ (\S+) \[[^\]]+\] "[A-Z]+ ([^ "]+)? HTTP/[0-9.]+" [0-9]{3} ([0-9]+|-)'  # noqa


class LogRecord:
    _regexp = re.compile(_LOG_RE)

    def __init__(self, line):
        match = self._regexp.match(line)
        host, authuser, resource, size = match.groups()
        self.host = host
        self.authuser = authuser
        self.size = int(size)
        self.section = f"/{resource.split('/', 2)[1]}"
