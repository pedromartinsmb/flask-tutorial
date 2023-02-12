import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort
from flaskr.db import get_db

from flaskr.auth import login_required

# Creates a blueprint named "blog"
# It needs to know where it's defined, so "__name__" is required
# This blueprint does not have a "url_prefix", so the "index" view will be the
# main index.
bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            # The "g" object is unique for each request, and holds data that might be 
            # reused throughout the request lifespan (e.g. the db connection)
            # This is useful here because this function will be called for every single
            # app route. Thus, g.user will be checked constantly by routes to verify if
            # the user is logged, i.e. if the user info is in the session data.
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

# As both "update" and "delete" functionalities need to validate if the user is
# the owner of the post, it makes sense to have a "get_post" function
def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    # The "abort()" function raises a special exception that returns a HTTP
    # status code
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

# If the "id" in the route is not specified as "int", it will be treated as a
# string
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):

    # Calling "get_post(id)" without explicitly setting "check_author=False"
    # keeps the post ownership check, i.e. a post will be returned by the
    # function only if the user is the author
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    # Calling "get_post(id)" without explicitly setting "check_author=False"
    # keeps the post ownership check, i.e. a post will be returned by the
    # function only if the user is the author
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))