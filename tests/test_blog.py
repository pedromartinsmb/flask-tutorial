import pytest
from flaskr.db import get_db


def test_index(client, auth):
    response = client.get('/')
    # Before logging in, both the "Log In" and "Register" buttons should be
    # shown.
    assert b"Log In" in response.data
    assert b"Register" in response.data

    # Logs in with the "test" user.
    auth.login()

    # Opens the "index" view.
    response = client.get('/')

    # After logging in the "Log Out" button should be shown.
    assert b'Log Out' in response.data

    # After logging in the post title should be shown (see "tests/data.sql").
    assert b'test title' in response.data

    # After logging in the post date should be shown (see "tests/data.sql").
    assert b'by test on 2018-01-01' in response.data

    # After logging in, the post body should be shown (see "tests/data.sql").
    assert b'test\nbody' in response.data

    # After logging in, the "Edit" link should point to the correct "update"
    # endpoint.
    assert b'href="/1/update"' in response.data



# "@pytest.mark.parametrize" tells Pytest to run the same test function with
# different arguments. This is useful here so writting the same code multiple
# times isn't needed. Here, the "test_login_required" is called 3 times, and
# each of the tuple values is sent as the function's "path" argument.
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    # Tests if the user is redirected to the login page after trying to create,
    # update or delete a post without logging in first.
    print(response.data)
    assert response.headers["Location"] == "/auth/login"

def test_author_required(app, client, auth):
    # change the post author to another user.
    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1')
        db.commit()

    auth.login()

    # tests if the current user is unable to update or delete the post (as he's
    # not the author anymore).
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    # tests if the current user doesn't see the "Edit" link to the post.
    assert b'href="/1/update"' not in client.get('/').data

# "@pytest.mark.parametrize" tells Pytest to run the same test function with
# different arguments. This is useful here so writting the same code multiple
# times isn't needed.
@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    # Tests if the URLs correctly raises the 404 status code (as the post with
    # id == 2 doesn't exist).
    assert client.post(path).status_code == 404


def test_create(client, auth, app):

    # Logs in
    auth.login()

    # Tests if the post creation view is rendered correctly for a logged in
    # user.
    assert client.get('/create').status_code == 200

    # Creates a seconde post (the first one was inserted by the
    # "tests/data.sql" script).
    client.post('/create', data={'title': 'created', 'body': ''})

    # Checks if the post was inserted in the database
    with app.app_context():
        db = get_db()
        # fetchone()[0] returns the value of the first column and row
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2

def test_update(client, auth, app):
    
    # Logs in
    auth.login()

    # Tests if the post creation view is rendered correctly for a logged in
    # user.
    assert client.get('/1/update').status_code == 200

    # Modifies the first post (inserted by the "tests/data.sql" script).
    client.post('/1/update', data={'title': 'updated', 'body': ''})

    # Tests if the first post was indeed updated in the database
    with app.app_context():
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'

# "@pytest.mark.parametrize" tells Pytest to run the same test function with
# different arguments. This is useful here so writting the same code multiple
# times isn't needed.
@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client, auth, path):

    # Logs in
    auth.login()

    # Tries to update a post title to the empty string
    response = client.post(path, data={'title': '', 'body': ''})

    # Tests if the error is shown
    assert b'Title is required.' in response.data

def test_delete(client, auth, app):
    
    # Logs in
    auth.login()

    # Makes a delete request
    response = client.post('/1/delete')

    # Tests if the user is redirected to the "index" view
    assert response.headers["Location"] == "/"

    with app.app_context():

        # Connects to the database
        db = get_db()

        # Tries to return the deleted post
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()

        # Tests if the post is indeed deleted
        assert post is None