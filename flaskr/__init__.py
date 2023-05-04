import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    # __name__ is the name of the current Python module.
    # The app needs to know where it’s located to set up some paths,
    # and __name__ is a convenient way to tell it that.
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing.
        # overrides the default configuration with values taken from the config.py file in the instance folder
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in.
        # can also load a different configuration file instead of the instance configuration
        app.config.from_mapping(test_config)

    # ensure the instance folder exists.
    # Flask doesn’t create the instance folder automatically,
    # but it needs to be created because your project will create the SQLite database file there.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello.
    @app.route('/hello')
    def hello() -> str:
        return 'Hello, World!'

    # register the database commands.
    # init-db command should be called with a flaskr command,
    # and not with the flask command you might have used earlier when running the development server.
    # The flask command knows how to find the application instance,
    # but it doesn’t know where to find your init-db command.
    # app.cli.add_command() adds a new command that can be called with the flask command.
    from . import db
    db.init_app(app)

    # import and register the blueprint from the factory using app.register_blueprint().
    # Place the new code at the end of the factory function before returning the app.
    # The authentication blueprint will have views to register new users and to log in and log out.
    # Since those views need to know about the database, you should write a new function for that code.
    from . import auth
    app.register_blueprint(auth.bp)

    # The blog blueprint will have views to create, update, and delete blog posts.
    # Since the blog posts will be associated with the user who created them,
    # you’ll use the user’s id to look up posts later.
    # You’ll also write a function to get the post and will call it from the other views,
    # since they all need to retrieve a post by id.
    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')

    return app
