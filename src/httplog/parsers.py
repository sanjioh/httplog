"""
Parsers module.

This module includes a default implementation of log record parser
for the Common Log Format.
"""
import re

_LOG_RE = r'^(\S+) \S+ (\S+) \[[^\]]+\] "[A-Z]+ ([^ "]+)? HTTP/[0-9.]+" [0-9]{3} ([0-9]+|-)'  # noqa


class LogRecord:
    """
    Parse a log line in Common Log Format.

    This class uses a regexp to parse a log line. Parsing happens
    at initialization time: the newly returned object has
    attributes whose values come from fields found in the log line.
    """

    _regexp = re.compile(_LOG_RE)

    def __init__(self, line):
        """Parse log line and initialize a LogRecord object."""
        match = self._regexp.match(line)
        host, authuser, resource, size = match.groups()
        self.host = host
        self.authuser = authuser
        self.size = int(size)
        self.section = f"/{resource.split('/', 2)[1]}"
