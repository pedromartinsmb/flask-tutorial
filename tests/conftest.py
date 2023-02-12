# This file contains "fixtures", which are setup functions that each test will
# use.

import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

# Opens the "data.sql" in the "tests" directory and saves the testing SQL
# script in the "_data_sql" variable
with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

# NOTE
# "fixtures" are functions annotated with @pytest.fixture.
# Pytest uses fixtures by matching their function names with then names of
# arguments. If a function takes an argument named "X", Pytest tries to find a
# fixture function named "X", calls it and passes the returned value to the
# test function that has the argument named "X".

@pytest.fixture
def app():
    # Creates a temp file and returns a tuple/pair (fd, name) where "fd" is the
    # file descriptor returned by os.open, and "name" is the filename
    db_fd, db_path = tempfile.mkstemp()

    # This creates the app (see flaskr/__init__.py) passing the "test_config"
    # dict to configure the app for testing (instead of using the local
    # development configuration)
    #
    # "'TESTING': True" tells Flask that the app is in test mode
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path
    })

    # "app.app_context()" creates a context that will make "current_app" point
    # to this application.
    # This is needed because an app context is only created automatically when
    # handling a request or when a CLI command is run.
    #
    # Here, the test database is initiated (or created) in the "tests"
    # directory and the test insert script is executed.
    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    # "yield" produces a value, returns it and carry on with the remaining code
    yield app

    # After the test is over, the temporary database file is closed and removed
    os.close(db_fd)
    os.unlink(db_path)

# This fixture is used by tests that make requests to the app without running
# the server
@pytest.fixture
def client(app):
    return app.test_client()

# This fixture is used by tests that calls Click commands registered with the
# application
@pytest.fixture
def runner(app):
    return app.test_cli_runner()


# This class is defined so the authentication related requests won't need to be
# written multiple times.
class AuthActions(object):
    def __init__(self, client):
        self._client = client

    # This function make the log in with the 'test' user, already inserted as
    # part of the test data in the app fixture (see "tests/data.sql").
    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')

# This fixture provides a way to call auth.login() in a test to log in as the
# "test" user, already inserted in the test database by the "app" fixture
# (see "tests/data.sql").
@pytest.fixture
def auth(client):
    return AuthActions(client)