"""Know-SQL

A simple json API proxy over HTTP to Postgres.

Usage:
  ksql.py

Options:
  -h --help      Show this screen.
  -i --interface Interface. [Default: 0.0.0.0]
  -p --port      Port.      [Default: 4000]
"""

from docopt import docopt
from werkzeug.serving import run_simple
from .ksql import app

arguments = docopt(__doc__, version='Know-SQL 0.1')
bind = arguments.get('--bind', '0.0.0.0')
port = arguments.get('--port', 4000)

run_simple(bind, port, app, use_debugger=True)
