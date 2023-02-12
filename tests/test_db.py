import sqlite3

import pytest
from flaskr.db import get_db

def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        # With an app context, "get_db" should return the same connection each
        # time it's called
        assert db is get_db()

    # "pytest.raises" asserts if the code within raises an exception.
    # If the code indeed raises an exception, pytest.raises does not raise an
    # error. Otherwise, pytest.raises raises an error. It's used to check if a
    # desired exception occurs correctly.
    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    # After the app context, the connection should be closed
    assert 'closed' in str(e.value)


# "runner" is a fixture defined in the "conftest" module
# "monkeypatch" is a fixture from Pytest
def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    # "monkeypatch.setattr" replaces a function in a module with another
    # function. In this case, it replaces the original "init_db" with the
    # "fake_init_db" function, that records it's been called
    monkeypatch.setattr('flaskr.db.init_db', fake_init_db)

    # The runner fixture calls the "init-db" command defined in the
    # "flaskr/db.py" module (search for "@click.command('init-db')")
    result = runner.invoke(args=['init-db'])

    # Tests if the "init-db" command outputs something containing the
    # "Initialized" function
    assert 'Initialized' in result.output

    # Tests if the "fake_init_db" is indeed called by the "init-db" command
    assert Recorder.called

