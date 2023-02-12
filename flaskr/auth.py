import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

# Creates a blueprint named "auth"
# It needs to know where it's defined, so "__name__" is required
# url_prefix will be prepended to all the URLs under the blueprint
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():

    # When the route is activated from its own submit button, the information
    # is registered
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                # "redirect" redirects to another URL
                # "url_for" generates the URL for a view based on its name
                return redirect(url_for("auth.login"))

        # "flash" stores massages that can be retrieved when rendering the
        # template
        flash(error)

    # "render_template" renders a template containing HTML
    # The route execution only gets this far if the route was activated from
    # the GET method
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        # "fetchone" 
        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        # "check_password_hash" takes a hash and a valor. If the hash of the
        # value is equal to the hash taken as the first argument, returns True.
        # Else, returns False.
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        # "session" is a dict that stores data across requests.
        # This data is stored in a cookie that is sent to the browser.
        # Flask securely signs the data so that it can't be tampered with.
        #
        # If the user entered the correct credentials, the session is saved
        # with the user info as long as the user remains logged in. This
        # session data is available to other views.
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        # "flash" stores massages that can be retrieved when rendering the
        # template
        flash(error)

    # "render_template" renders a template containing HTML
    return render_template('auth/login.html')

# Functions annotated with "before_app_request" run before the view function,
# no matter what URL is requested
@bp.before_app_request
def load_logged_in_user():
    # Tries to get the "user_id" from the session
    user_id = session.get('user_id')

    # The "g" object is unique for each request, and holds data that might be 
    # reused throughout the request lifespan (e.g. the db connection)
    # This is useful here because this function will be called for every single
    # app route. Thus, g.user will be checked constantly by routes to verify if
    # the user is logged, i.e. if the user info is in the session data.
    if user_id is None:
        g.user = None
    # If the "user_id" exists, retrieves from the db the entire "user" dict
    else:
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()

# To logout, just remove the user id from the session.
# This way, when any route is activated, the "load_logged_in_user" function
# (annotated with @bp.before_app_request) will define "g.user" as None.
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Creating, editing and deleting blog posts will require a user to be logged
# in. A decorator can be used to check this for each view it's applied to.
# This way, the "if g.user is None" block won't need to be repeatedly used
# in every view.
#
# In other words, every view that "subscribes" to the "login_required" function
# will check wether "g.user is None", in which case the function redirects to
# the login page. Otherwise, the original view is called and continues
# normally.
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view