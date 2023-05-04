import sqlite3

import pytest
from flaskr.db import get_db


def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db() # assert that get_db returns the same connection each time it's called

    with pytest.raises(sqlite3.ProgrammingError) as e: # assert that get_db is closed
        db.execute('SELECT 1')

    assert 'closed' in str(e.value) # assert that get_db is closed


def test_init_db_command(runner, monkeypatch): # monkeypatch is a pytest fixture
    class Recorder(object): # create a class that records calls to its methods
        called = False

    def fake_init_db(): # create a fake init_db function that records that it's been called
        Recorder.called = True

    monkeypatch.setattr('flaskr.db.init_db', fake_init_db) # replace init_db with the fake function
    result = runner.invoke(args=['init-db']) # invoke the command line command
    assert 'Initialized' in result.output # assert that the output is what you expect
    assert Recorder.called # assert that the function was called
