import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import (
    check_password_hash, generate_password_hash
)
from flaskr.db import get_db

# The authentication blueprint will have views to register new users and to log in and log out.
# Since this will be views that users interact with,
# the templates will go in the auth folder inside the templates folder.
# The Blueprint is named 'auth'.
# Like the application object, the blueprint needs to know where it’s defined,
# so __name__ is passed as the second argument.
# The url_prefix will be prepended to all the URLs associated with the blueprint.
# This blueprint will be used for the authentication views,
# so it needs to know that all the URLs will be prefixed with /auth.
# When using a blueprint, the name of the blueprint is prepended to the name of the function,
# so login view function is accessible as auth.login,
# because you added it to the auth blueprint.
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register() -> str:
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # get_db returns a database connection, which is used to execute the command passed as the first argument.
        # g is a special object that is unique for each request.
        # It is used to store data that might be accessed by multiple functions during the request.
        # The connection is stored and reused instead of creating a new connection if get_db is called a second time in the same request.
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        # The query uses the fetchone() method to fetch one result.
        # If the query returned no results, it returns None.
        # Later, fetchall() is used, which returns a list of all results.
        # The result is a tuple of values, one for each column in the table.
        # If the query returned no results, it returns an empty list.
        if error is None:
            try:
                db.execute(
                    # The question marks (?, ?) are placeholders for the values,
                    # and will be replaced by the values in the tuple on the second argument to execute().
                    # Using placeholders is not required,
                    # but it is a good idea since it protects against SQL injection attacks by escaping the values
                    # automatically.
                    'INSERT INTO user (username, password) VALUES (?, ?)',
                    (username, generate_password_hash(password))
                )
                # After storing the user, the user is redirected to the login page.
                # url_for() generates the URL for the login view based on its name.
                # This is preferable to writing the URL directly as it allows you to change the URL later without changing all code that links to it.
                db.commit()
            except db.IntegrityError:
                error = f'User {username} is already registered.'
            else:
                return redirect(url_for('auth.login'))

        # If validation fails, the error is shown to the user.
        # flash() stores messages that can be retrieved when rendering the template.
        # get_flashed_messages() returns and clears the messages from the session.
        # Since you’ll want to display those messages after a redirect, you’ll call get_flashed_messages() in the base template,
        # so that it’s executed for each request.
        flash(error)

    # When the user initially navigates to auth/register,
    # or there was an validation error, an HTML page with the registration form should be shown.
    # render_template() will render a template containing the HTML,
    # which you’ll write in the next step of the tutorial.
    return render_template('auth/register.html')


# To log in, a user submits a form with their username and password.
# The view will check that username exists and that the password is correct.
# Then the user’s id is stored in a new session, which cookie is sent to the browser.
# The browser then sends it back with subsequent requests.
# Flask securely signs the data so that it can’t be tampered with.
# You can access the session in view functions as if it were a dictionary.
# The actual data is stored in a cookie on the browser.
# Flask securely signs the cookie so that the user can’t modify it.
# The user can look at the contents of the cookie, but not modify it unless they know the secret key used for signing.
# In this view, you check if username and password are valid.
# If they are valid, then the user’s id is stored in a new session.
# The name of the session is 'user_id'.
@bp.route('/login', methods=('GET', 'POST'))
def login() -> str:
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            # The query uses the fetchone() method to fetch one result.
            # If the query returned no results, it returns None.
            # Later, fetchall() is used, which returns a list of all results.
            # The result is a tuple of values, one for each column in the table.
            # If the query returned no results, it returns an empty list.
            'SELECT * FROM user WHERE username = ?',
            (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            # session is a dict that stores data across requests.
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


# bp.before_app_request() registers a function that runs before the view function, no matter what URL is requested.
# load_logged_in_user checks if a user id is stored in the session and gets that user’s data from the database,
# storing it on g.user, which lasts for the length of the request.
# If there is no user id, or if the id doesn’t exist, g.user will be None.
# Checking if g.user is set or not makes it possible to load that user’s information on every page load,
# if they’re logged in.
# You could instead hardcode the user into view functions.
# However, that code would need to be repeated for each view.
# You can use a decorator to run code before the view function,
# so it will be loaded for each view.
@bp.before_app_request
def load_logged_in_user() -> None:
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            # The query uses the fetchone() method to fetch one result.
            # If the query returned no results, it returns None.
            # Later, fetchall() is used, which returns a list of all results.
            # The result is a tuple of values, one for each column in the table.
            # If the query returned no results, it returns an empty list.
            'SELECT * FROM user WHERE id = ?',
            (user_id,)
        ).fetchone()


# To log out, you need to remove the user id from the session.
# Then load_logged_in_user won’t load a user on subsequent requests.
# To log out, you can remove the user id from the session.
@bp.route('/logout')
def logout() -> str:
    session.clear()
    return redirect(url_for('index'))


def login_required(view) -> str:
    @functools.wraps(view)
    def wrapped_view(**kwargs) -> str:
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
