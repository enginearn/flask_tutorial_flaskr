import sqlite3

import click
from flask import current_app, g


# g is a special object that is unique for each request.
# It is used to store data that might be accessed by multiple functions during the request.
# The connection is stored and reused instead of creating a new connection if get_db is called a second time in the same request.
# current_app is another special object that points to the Flask application handling the request.
# Since you used an application factory, there is no application object when writing the rest of your code.
# get_db will be called when the application has been created and is handling a request,
# so current_app can be used.
def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        # sqlite3.connect() establishes a connection to the file pointed at by the DATABASE configuration key.
        # This file doesn’t have to exist yet, and won’t until you initialize the database later.
        g.db = sqlite3.connect(
            # current_app is another special object that points to the Flask application handling the request.
            # Since you used an application factory, there is no application object when writing the rest of your code.
            # get_db will be called when the application has been created and is handling a request,
            # so current_app can be used.
            current_app.config['DATABASE'],
            # sqlite3.Row tells the connection to return rows that behave like dicts.
            # This allows accessing the columns by name.
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # sqlite3.Row tells the connection to return rows that behave like dicts.
        # This allows accessing the columns by name.
        g.db.row_factory = sqlite3.Row

    return g.db


# close_db checks if a connection was created by checking if g.db was set.
# If the connection exists, it is closed.
# Further down you will tell your application about the close_db function in the application factory so that it is called after each request.
def close_db(e=None) -> None:
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db() -> None:
    db = get_db()

    # open_resource() opens a file relative to the flaskr package,
    # which is useful since you won’t necessarily know where that location is when deploying the application later.
    # get_db returns a database connection, which is used to execute the commands read from the file.
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


# click.command() defines a command line command called init-db
# that calls the init_db function and shows a success message to the user.
# You can read Command Line Interface to learn more about writing commands.
@click.command('init-db')
# The init-db command should be called with a flaskr command,
# and not with the flask command you might have used earlier when running the development server.
# The flask command knows how to find the application instance,
# but the script that gets imported doesn’t.
# Exporting FLASK_APP=flaskr sets the application instance,
# and it’s used by the other commands.
# Similarly, python -m flask run will work but python -m flaskr won’t.
# Instead you must use FLASK_APP=flaskr and python -m flask run.
def init_db_command() -> None:
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    # app.cli.add_command() adds a new command that can be called with the flask command.
    # The name of the command is init-db and it calls the init_db function.
    app.cli.add_command(init_db_command)
