import pytest
from flask import g, session
from flaskr.db import get_db

def test_register(client, app):
    
    # "client.get" makes a GET request and gets the response. This checks if
    # the page would be returned correctly when accessed by the browser (not
    # in the case of its own "submit" button being pressed)
    assert client.get('/auth/register').status_code == 200

    # "client.post" makes a POST request and gets the response. This mimics
    # the behaviour of the "submit" button, sending 'a' as both username and
    # password
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a'}
    )
    # This tests if the user would be redirected to the "auth.login" endpoint
    # after registering a user
    assert response.headers["Location"] == "/auth/login"

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None

# "@pytest.mark.parametrize" tells Pytest to run the same test function with
# different arguments. This is useful here so writting the same code multiple
# times isn't needed.
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'Username is required.'),
    ('a', '', b'Password is required.'),
    ('test', 'test', b'already registered'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data


# The tests for the "login" view are similar to those for "register".
# Rather than testing the data in the db, "session" should have "user_id" set
# after loggin in.
def test_login(client, auth):
    
    # "client.get" makes a GET request and gets the response. This checks if
    # the page would be returned correctly when accessed by the browser (not
    # in the case of its own "submit" button being pressed).
    assert client.get('/auth/login').status_code == 200

    # This tests if the user would be redirected to the "index" endpoint after
    # successfully logging in.
    response = auth.login()
    assert response.headers["Location"] == "/"

    # Creating a context here is necessary to access the "session" variable
    # without raising an error.
    with client:
        client.get('/')
        # Tests if the session has the "user_id" attribute correctly set after
        # the login
        assert session['user_id'] == 1
        # Tests if the username of the user making the request is 'test' 
        assert g.user['username'] == 'test'

# "@pytest.mark.parametrize" tells Pytest to run the same test function with
# different arguments. This is useful here so writting the same code multiple
# times isn't needed.
@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        # Tests if the "user_id" is not defined after the logout
        assert 'user_id' not in session