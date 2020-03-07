import mysql.connector

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host="127.0.0.1",
            user="myleague",
            password="Anqi_990321",
            database="myleague_test",
            buffered=True
        )
        # g.db.row_factory = g.db.cursor()
        
    return g.db


def init_db():
    db = get_db()

    with current_app.open_resource('../database/init.sql') as f:
        db.cursor().execute(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    