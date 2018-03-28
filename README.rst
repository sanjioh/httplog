httplog
=======

This software consumes an actively written-to w3c-formatted HTTP access log
(Common Log Format - https://en.wikipedia.org/wiki/Common_Log_Format)
and produces statistics and warnings based on the content
and the frequency of the log records.

Prerequisites
-------------

- Python 3.6

This software is tested on Mac OS 10.13.3 and Ubuntu 17.10.

Installation
------------

This guide assumes you have a working setup of Python 3.6.

- create a Python virtual environment and activate it (assuming Bash as shell)

  ::

    python3.6 -m venv httplog_venv
    source httplog_venv/bin/activate

- clone this repository and ``cd`` into it

  ::

    git clone https://github.com/sanjioh/httplog
    cd httplog

- install httplog

  ::

    pip install .

Usage
-----

::

    usage: httplog [-h] [--threshold THRESHOLD] filename

    Monitor live web server logs.

    positional arguments:
      filename              Path to the log file to monitor.

    optional arguments:
      -h, --help            show this help message and exit
      --threshold THRESHOLD, -t THRESHOLD
                            Alert threshold (requests/s).

Example
-------

::

    $ httplog -t 5 /var/log/webserver/access.log

Output
------

``httplog`` shows traffic statistics on the terminal every 10 seconds.
These data are based on the log entries the tool processes over the whole
execution lifetime:

::

    ==================== STATS ====================
    Top 5 users
      1. ian (463)
      2. josh (456)
      3. cassidy (454)
      4. carl (449)
      5. frank (436)

    Top 5 hosts
      1. 12.44.22.11 (816)
      2. 34.65.35.86 (439)
      3. 11.66.122.12 (417)
      4. 11.3.6.2 (398)
      5. 12.0.1.3 (391)

    Top 5 sections
      1. / (955)
      2. /apache_pb.gif (938)
      3. /computers (500)
      4. /art (494)
      5. /top.html (491)

    Total records processed: 4334 (86.7 records/s avg)
    Total bytes transferred: 907275009 (865.2 MiB)

If the average request rate (reqs/s) over the last 2 minutes raises above the user-specified
threshold (``--threshold`` or ``-t`` switch), ``httplog`` will show a warning message:

::

    ==================== ALERT ====================
    High traffic generated an alert - hits = 10397
    (86.6 reqs/s avg over the last 120s)
    Triggered at 2018-03-28 21:25:29


If the average request rate (reqs/s) over the last 2 minutes falls back to normal
(below the threshold), ``httplog`` will show a recovery message:

::

    ==================== ALERT ====================
    Traffic is back to normal - hits = 284
    (2.4 reqs/s avg over the last 120s)
    Recovered at 2018-03-28 21:27:29

Tests
-----

Simply run ``tox`` from the repository root.

Possible improvements
---------------------
- ``observers.StatsObserver`` could be improved by using data structures (binary search trees) that keep items sorted
  upon insertion, as opposed to the usage of dictionaries, whose (key, value) pairs need to be sorted (by value)
  every time a ranking has to be calculated (current implementation).
- Log parsing can be refined to cover edge cases or to be more tolerant to errors within the log file.
- The tool could be reimplemented without using child threads by adopting an asynchronous event-based framework,
  such as ``asyncio`` or ``Twisted``. Performance should be comparable, but unit testing would be simpler.

Notes
-----

- this project uses an ``src`` directory layout to prevent packaging errors and to enforce
  testing against a ``pip``-installed copy of the program (as opposed to the one in the
  current working directory) [1]_ [2]_

.. [1] https://hynek.me/articles/testing-packaging/
.. [2] https://blog.ionelmc.ro/2014/05/25/python-packaging/
