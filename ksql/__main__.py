"""Know-SQL

A simple json API proxy over HTTP to Postgres.

Usage:
  ksql.py

Options:
  -h --help     Show this screen.
  -d --database Database connection string.

"""

from docopt import docopt
from werkzeug.serving import run_simple
from .ksql import make_app

arguments = docopt(__doc__, version='Know-SQL 0.1')
bind = arguments.get('--bind', '0.0.0.0')
port = arguments.get('--port', 4000)
dsn = arguments.get('--database', '')

run_simple(bind, port, make_app(dsn), use_debugger=True)
