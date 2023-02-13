import sqlite3

import click

# The "current_app" object points to the Flask application handling the request
from flask import current_app
# The "g" object is unique for each request, and holds data that might be 
# reused throughout the request lifespan (e.g. the db connection)
from flask import g

def get_db():
    """
        Returns the current db connection of the request.

        If it doesn't exist, creates a connection and returns it.
    """

    # In case the request has no connection (g.db), creates a connection object
    if 'db' not in g:
        g.db = sqlite3.connect(
            # Use the "config['DATABASE']" as the db location (see the application factory)
            current_app.config['DATABASE'],
            # ?
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # tells the connection to return rows that behave like dicts
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    """
        Closes the connection if it exists
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    """
        Initizalizes (or recreates) the database running the schemas.sql file
    """
    db = get_db()

    # open_resource opens a file relative to the flaskr package
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# the @click.command annotation defines a command line command called "init-db"
# that calls the "init_db" function and shows a success message to the user
@click.command('init-db')
def init_db_command():
    """
        Clear the existing data and create new tables.
    """
    init_db()
    click.echo('Initialized the database.')

# The "close_db" and "init_db_command" functions need to be registered in the
# app. Since the app is created by a factory function, the instance isn't
# available when writing functions here. So, the following function takes an
# app object and does the registration
def init_app(app):
    """
        Registers the init_db_command and close_db functions to an app
    """

    # the "teardown_appcontext" register a function to be called after
    # returning the response
    app.teardown_appcontext(close_db)

    # the "cli.add_command" adds a new command that can be called with the
    # "flask" command
    app.cli.add_command(init_db_command)

    # init_db_command()