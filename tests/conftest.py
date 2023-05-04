import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture # fixture is a function that runs before each test function
def app():
    # create and open a temporary file, returning the file object and the path to it
    db_fd, db_path = tempfile.mkstemp()

    # create the app with the test config
    app = create_app({
        'TESTING': True, # tells Flask that the app is in test mode
        'DATABASE': db_path, # overrides the DATABASE config value
    })

    # create the database and load test data
    with app.app_context(): # tells Flask to use the app_context
        init_db()
        get_db().executescript(_data_sql)

    yield app # yields the app object for tests to use

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    # creates a test client for the app
    return app.test_client()


@pytest.fixture
def runner(app):
    # creates a runner that can call the Click commands registered with the app
    return app.test_cli_runner()


class AuthActions(object):
    def __init__(self, client) -> None:
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture # fixture is a function that runs before each test function
def auth(client):
    return AuthActions(client)
