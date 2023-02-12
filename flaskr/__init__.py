import os

from flask import Flask

# This is the "application factory"
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        # this can be useful for passing the SECRET_KEY, for instance
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        # as in the above scenario, this will override the default
        # "app.config.from_mapping" at the beggining of the application factory
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says "hello"
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # imports the db and calls the "init_app" function to register the
    # db.py "close_db" function and adds "init_db_command" to the app
    from . import db
    db.init_app(app)

    # Blueprints imports
    from . import auth, blog
    app.register_blueprint(auth.bp)
    app.register_blueprint(blog.bp)

    # As the "index" view is under the "blog" blueprint and the "auth" views
    # referred to a plain "index" endpoint (and not "blog.index"),
    # app.add_url_rule() associates the endpoint name "index" to the "/" URL so
    # that url_for('index') or url_for('blog.index') will both work, generating
    # the same "/" URL either way.
    app.add_url_rule('/', endpoint='index')

    return app

# create_app()