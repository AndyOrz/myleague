from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)
from www.auth import root_login_required
from www.db import get_db
from www.config import get_cfg_global, get_sidebar_items_bg

cfg = get_cfg_global()
sidebar_items_bg = get_sidebar_items_bg()

bp = Blueprint('background', __name__, url_prefix=cfg['background']['prefix'])


@bp.route(sidebar_items_bg['main']['route'])
@root_login_required
def main():
    db = get_db()
    cur = db.cursor(dictionary=True)
    return render_template('background/main.html',
                           name=sidebar_items_bg['main']['name'],
                           sidebar_items=sidebar_items_bg)
