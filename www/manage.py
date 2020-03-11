from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)
from www.auth import login_required
from www.db import get_db
import config as cfg

bp = Blueprint('manage', __name__)


@bp.route(cfg.sidebar_items['team_manage']['route'])
@login_required
def team_manage():
    db = get_db()
    cur = db.cursor(dictionary=True)

    sql = '''
        SELECT team_name, team_id FROM team
        WHERE user_id={} and season_id = {}
        '''.format(g.user['user_id'], cfg.league_season_id)

    cur.execute(sql)
    league_teams = cur.fetchall()

    sql = '''
        SELECT team_name, team_id FROM team
        WHERE user_id={} and season_id = {}
        '''.format(g.user['user_id'], cfg.cup_season_id)

    cur.execute(sql)
    cup_teams = cur.fetchall()

    return render_template('manage/team_manage.html',
                           name=cfg.sidebar_items['team_manage']['name'],
                           sidebar_items=cfg.sidebar_items,
                           league_teams=league_teams,
                           cup_teams=cup_teams
                           )


@bp.route(cfg.sidebar_items['player_register']['route'])
@login_required
def player_register():
    return render_template('manage/player_register.html',
                           name=cfg.sidebar_items['player_register']['name'],
                           sidebar_items=cfg.sidebar_items,                 
                           )
                           