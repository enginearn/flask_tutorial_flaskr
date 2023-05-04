from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

# bp = Blueprint() creates a Blueprint named 'blog'.
# Like the application object, the blueprint needs to know where it’s defined,
# so __name__ is passed as the second argument.
# The url_prefix will be prepended to all the URLs associated with the blueprint.
# Since the blog will define views that create, edit, and delete the posts,
# the URL will need to accept an argument that specifies the id of the post to work with.
# A real URL will look like /1/delete where 1 is the id of the post to delete.
# This id is going to be the second part of the URL, so <int:id> is used.
# An int converter is used to ensure that the id is an integer.
bp = Blueprint('blog', __name__)

# bp.route associates the URL / with the index view function.
# When Flask receives a request to /, it will call the index view and use the return value as the response.
# The view function returns the rendered template.
# render_template() will render a template containing the posts.
# render_template() takes the name of the template and a variable list of template arguments.
# The template arguments are used in the template for rendering.
# For example, post['title'] will be used in index.html to render the post title.
# The index.html template will extend the base.html template that was generated by the application factory.
# The index.html template will have a block named body.
# The base.html template has a block named body that child templates can fill in.
# Since index.html is inheriting from base.html, the block in index.html replaces the block in base.html,
# thus replacing the whole body.
# The base.html template has a block named body that child templates can fill in.
# Since index.html is inheriting from base.html, the block in index.html replaces the block in base.html,
# thus replacing the whole body.
# The url_for() function generates the URL to a view based on a name and arguments.
# The name associated with a view is also called the endpoint, and by default it’s the same as the name of the view function.
# url_for() generates the URL for the blog.index view.
# This is significantly better than writing the URL directly as it allows you to change the URL later without changing all code that links to it.
# Linking to index() would be done with url_for('index') because index is the name of the view function.
# url_for() can generate URLs to static files like style.css.
# It takes the name of the static file as the first argument and the filename relative to the flaskr/static directory as the filename.
# To generate a URL to the style.css file, use url_for('static', filename='style.css').
# The file is in a static folder inside the flaskr package so it has the name static.
# The name static is not special, it can be changed.
# The blog.index part is the name of the view function.
# The blog part is the name of the blueprint, and the . is a special character that separates the two.
# Since this is a relative URL, it will be relative to the current page.
# If the current URL is /post/1, the url_for('blog.index') will return /post.
# If the current URL is /post/, the url_for('blog.index') will return /post/.
# If the current URL is /, the url_for('blog.index') will return /.
# The index view will return all posts, most recent first.
# In SQL, this is done with an ORDER BY clause.
# By default, results are returned in ascending order.
# The DESC keyword can be added to invert the ordering.
# The ? is a placeholder for a value that will be supplied later.
# The trailing comma in ('created',) is necessary because without the comma Python would interpret ('created') as a string with brackets around it.
# Including a comma makes it a tuple.
# The query returns a list of tuples.
@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
        ).fetchall()
    return render_template('blog/index.html', posts=posts)

# The create view works the same as the auth register view.
# Either the form is displayed, or the posted data is validated and the post is added to the database or an error is shown.
# The login_required decorator you wrote earlier is used on the blog views.
# A user must be logged in to visit these views, otherwise they will be redirected to the login page.
# The create and update views look very similar.
# The main difference is that the update view uses a post object and an UPDATE query instead of an INSERT.
# Since nearly all the code is the same, you can use a function to avoid duplicating code.
# The get_post function will be used to get a post and call abort() if a post with the given id doesn’t exist.
# The post is returned and can then be used to update an existing post in the update view.
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title'] # request.form is a special type of dict mapping submitted form keys and values.
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'
        else:
            db = get_db()
            # The author is set to the id of the logged in user.
            # Since you added the author column to the post table when setting up the database,
            # there is no need to modify the INSERT statement to store it.
            # The database takes care of storing the relationship.
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id']) # g.user is set in the auth blueprint.
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


# Both the update and delete views will need to fetch a post by id and check if the author matches the logged in user.
# To avoid duplicating code, you can write a function to get the post and call it from each view.
# The post is fetched before the other view code to ensure it exists before continuing.
# If a post with the given id doesn’t exist, a 404 error is returned.
# If the logged in user is not the author, a 403 Forbidden error is returned.
# Otherwise the post is returned and can be used later.
# The post is queried by id and joined with the user who wrote it.
# One result is expected, so fetchone() is used.
# If the result doesn’t exist, abort() is called.
# Otherwise, the result is returned.
# The check_author argument is defined so that the function can be used to get a post without checking the author.
# This would be useful if you wrote a view to show an individual post on a page,
# where the user doesn’t matter because they’re not modifying the post.
# The update view uses the get_post function and checks if the logged in user is the author.
# If they are, the post data is fetched and the form is displayed.
# If they are not, a 403 Forbidden status is returned.
# If the user is the author, the existing data is pre-populated in the form.
# When the form is submitted, it validates the input and updates the post.
# After the update, the user is redirected to the post’s page.
# Since the update view uses a URL with an argument, a post id, a post_id argument is added to view.
# A real URL for a post looks like /1/update.
# Flask will capture the 1, ensure it’s an int, and pass it as the post_id argument.
# If you don’t specify int: and instead do <id>, it will be a string.
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username' # The author_id and username columns are added to the SELECT statement.
        ' FROM post p JOIN user u ON p.author_id = u.id' # The post is joined with the user table to get the username.
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id)) # abort() will raise a special exception that returns an HTTP status code.
        # It takes an optional message to show with the error, otherwise a default message is used.
        # 404 means “Not Found”, and 403 means “Forbidden”.
        # (The difference between 403 and 401 is that with 401, Flask will send a WWW-Authenticate header and a 401 status code,
        # indicating to the client that authentication is required.)
        # These are common HTTP status codes that are used when something goes wrong with a route.
        # You’ve already used 404 when a URL doesn’t exist, and you’ll use 403 for an unauthorized access attempt.
        # In each case, you’ll show an HTML page instead of the default message.
        # The 404 and 403 pages will use the base.html template, so they’ll have the same look and feel as the rest of the application.
        # The 404 page will have a message telling the user that the requested post was not found.
        # The 403 page will have a message telling the user they don’t have permission to mo
        # The check_author argument is defined so that the function can be used to get a post without checking the author.
        # This would be useful if you wrote a view to show an individual post on a page,
        # where the user doesn’t matter because they’re not modifying the post.
        # The update view uses the get_post function and checks if the logged in user is the author.
        # If they are, the post data is fetched and the form is displayed.
        # If they are not, a 403 Forbidden status is returned.
        # If the user is the author, the existing data is pre-populated in the form.
        # When the form is submitted, it validates the input and updates the post.
        # After the update, the user is redirected to the post’s page.
        # Since the update view uses a URL with an argument, a post id, a post_id argument is added to view.
        # A real URL for a post looks like /1/update.
        # Flask will capture the 1, ensure it’s an int, and pass it as the post_id argument.
        # If you don’t specify int: and instead do <id>, it will be a string.
    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required # A user must be logged in to visit these views, otherwise they will be redirected to the login page.
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title'] # request.form is a special type of dict mapping submitted form keys and values.
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            # The author is set to the id of the logged in user.
            # Since you added the author column to the post table when setting up the database,
            # there is no need to modify the INSERT statement to store it.
            # The database takes care of storing the relationship.
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id) # g.user is set in the auth blueprint.
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

# The delete view doesn’t have its own template, the delete button is part of update.html and posts to the /<id>/delete URL.
# Since there is no template, it will only handle the POST method, and the GET method will produce a 405 Method Not Allowed error.
# After deleting the post, the user is redirected to the index view.
# url_for() generates the URL to the index view.
# Note that you don’t have to pass any arguments here, since it’s the same URL as the index view.
# If you look at the index view, you’ll see it’s handling the GET method and has a special case to filter by author.
# That’s why the author_id is added to url_for(), as a query string.
# The url_for() function generates URLs using the name associated with the view.
# The name is the same as the view function name, blog.index.
# A variable argument is appended to the URL with <> enclosing it.
# For example, a URL for the user profile endpoint with a user id of 5 would look like /profile/5.
# If the variable part contains a converter, it’s applied to the rule variable.
# You can register multiple rules for the same view function by using a different rule string with the same endpoint name.
# Flask uses the endpoint name to find the associated view.
# It’s common to have the endpoint be the same as the name of the view function, but that’s not a requirement.
# The url_for() function generates the URL to the given endpoint.
# The url_for() function generates URLs using the name associated with the view.
# The name is the same as the view function name, blog.index.
# A variable argument is appended to the URL with <> enclosing it.
# For example, a URL for the user profile endpoint with a user id of 5 would look like /profile/5.
# If the variable part contains a converter, it’s applied to the rule variable.
# You can register multiple rules for the same view function by using a different rule string with the same endpoint name.
# Flask uses the endpoint name to find the associated view.
# It’s common to have the endpoint be the same as the name of the view function, but that’s not a requirement.
# The url_for() function generates the URL to the given endpoint.
# The url_for() function generates URLs using the name associated with the view.
# The name is the same as the view function name, blog.index.
# A variable argument is appended to the URL with <> enclosing it.
@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    # The get_post function returns a post if the id exists, otherwise it will return a 404 Not Found error.
    # If the check_author argument of get_post is True, then the author of the post is checked against the logged in user.
    # If they don’t match, a 403 Forbidden error is returned.
    # If the check_author argument is False, then get_post returns without checking the author.
    # This is used to get a post without checking the author, which is used to load an existing post into the form to edit.
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
