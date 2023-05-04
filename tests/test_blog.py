import pytest
from flaskr.db import get_db


def test_index(client, auth):
    response = client.get('/') # assert that the index page requires a login
    assert b"Log In" in response.data # assert that the index page requires a login
    assert b"Register" in response.data # assert that the index page requires a login

    auth.login() # assert that the index page requires a login
    response = client.get('/') # assert that the index page requires a login
    assert b"Log Out" in response.data # assert that the index page requires a login
    assert b'test title' in response.data # assert that the post is on the page
    assert b'by test on 2018-01-01' in response.data # assert that the post is on the page
    assert b'test\nbody' in response.data # assert that the post is on the page
    assert b'href="/1/update"' in response.data # assert that the post is on the page

@pytest.mark.parametrize('path', ( # parametrize decorator calls the test function multiple times with different arguments
    '/create', # assert that the create page requires a login
    '/1/update', # assert that the update page requires a login
    '/1/delete', # assert that the delete page requires a login
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers['Location'] == '/auth/login' # assert that the page redirects to the login URL


def test_author_required(app, client, auth):
    # change the post author to another user
    with app.app_context():
        db = get_db()
        db.execute('UPDATE post SET author_id = 2 WHERE id = 1') # assert that the update page exists
        db.commit()

    auth.login() # assert that the update page exists
    # current user can't modify other user's post
    assert client.post('/1/update').status_code == 403 # assert that the update page exists
    assert client.post('/1/delete').status_code == 403 # assert that the delete page exists
    # current user doesn't see edit link
    assert b'href="/1/update"' not in client.get('/').data # assert that the update page exists


@pytest.mark.parametrize('path', ( # parametrize decorator calls the test function multiple times with different arguments
    '/2/update', # assert that the update page exists
    '/2/delete', # assert that the delete page exists
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404 # assert that the update page exists


def test_create(client, auth, app):
    auth.login() # assert that the create page loads successfully
    assert client.get('/create').status_code == 200 # assert that the create page loads successfully
    client.post('/create', data={'title': 'created', 'body': ''}) # assert that the create page loads successfully

    with app.app_context(): # assert that the post was inserted into the database
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM post').fetchone()[0]
        assert count == 2


def test_update(client, auth, app):
    auth.login() # assert that the update page loads successfully
    assert client.get('/1/update').status_code == 200 # assert that the update page loads successfully
    client.post('/1/update', data={'title': 'updated', 'body': ''}) # assert that the update page loads successfully

    with app.app_context(): # assert that the post was updated in the database
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post['title'] == 'updated'


@pytest.mark.parametrize('path', ( # parametrize decorator calls the test function multiple times with different arguments
    '/create', # assert that the create page loads successfully
    '/1/update', # assert that the update page loads successfully
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''}) # assert that the title is required
    assert b'Title is required.' in response.data # assert that the title is required


def test_delete(client, auth, app):
    auth.login() # assert that the delete link is present for logged in users
    response = client.post('/1/delete') # assert that the delete link is present for logged in users
    assert response.headers['Location'] == 'http://localhost/' # assert that the delete link is present for logged in users

    with app.app_context(): # assert that the post was deleted from the database
        db = get_db()
        post = db.execute('SELECT * FROM post WHERE id = 1').fetchone()
        assert post is None
