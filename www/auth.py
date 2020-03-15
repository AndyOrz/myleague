import functools
import sys

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from www.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor(dictionary=True)
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = '请输入用户名.'
        elif not password:
            error = '请输入密码.'
        else:
            cur.execute(
                'SELECT user_id FROM user WHERE user_name = "{}"'
                .format(username)
            )
            if cur.fetchone() is not None:
                error = '用户 {} 已存在.'.format(username)

        if error is None:
            cur.execute('''INSERT INTO user (user_name, password, pri)
                VALUES ("{}", "{}", 10)'''.format(
                username, generate_password_hash(password)))
            db.commit()
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor(dictionary=True)
        username = request.form['username']
        password = request.form['password']
        error = None
        cur.execute(
            'SELECT * FROM user WHERE user_name = "{}"'.format(username)
        )
        user = cur.fetchone()

        if user is None:
            error = '用户名不存在.'
        elif check_password_hash(user['password'], password) is False:
            error = '密码错误.'

        if error is None:
            session.clear()
            session['user_id'] = user['user_id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute(
            'SELECT user_id, user_name, pri FROM user WHERE user_id = {}'.format(
                user_id))
        g.user = cur.fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        print(request.remote_addr, g.user['user_name'], file=sys.stderr)
        return view(**kwargs)

    return wrapped_view


def root_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if int(g.user['pri']) != 0:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view


@bp.route('/repassword')
@login_required
def repassword():
    return "莫得"
