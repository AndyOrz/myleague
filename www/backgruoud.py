from flask import (Blueprint, flash, g, redirect, render_template, request,
                   url_for)
from www.auth import root_login_required
from www.db import get_db
from www.config import config

cfg = config.get_cfg_global()['default']
sidebar_items_bg = config.get_sidebar_items_bg()

bp = Blueprint('background', __name__)


@bp.route(sidebar_items_bg['main']['route'])
@root_login_required
def main():
    db = get_db()
    cur = db.cursor(dictionary=True)
    league_list = dict()
    cup_list = dict()
    supercup_list = dict()

    # 联赛
    sql = '''select season_id, season_name from season
             where season_type='league' and season_status='y'
          '''
    cur.execute(sql)
    league = cur.fetchall()

    for l in league:
        league_list[l['season_id']] = l['season_name']

    # 杯赛
    sql = '''select season_id, season_name from season
             where season_type='cup' and season_status='y'
          '''
    cur.execute(sql)
    cup = cur.fetchall()

    for l in cup:
        cup_list[l['season_id']] = l['season_name']

    # 超级杯
    sql = '''select season_id, season_name from season
             where season_type='supercup' and season_status='y'
          '''
    cur.execute(sql)
    supercup = cur.fetchall()

    for l in supercup:
        supercup_list[l['season_id']] = l['season_name']

    return render_template('background/main.html',
                           name=sidebar_items_bg['main']['name'],
                           sidebar_items=sidebar_items_bg,
                           current_cfg=cfg,
                           league_list=league_list,
                           cup_list=cup_list,
                           supercup_list=supercup_list)


@bp.route(sidebar_items_bg['league']['route'])
@root_login_required
def league():
    db = get_db()
    cur = db.cursor(dictionary=True)

    sql = '''
        SELECT team_name, team_id FROM team
        WHERE season_id = {}
        '''.format(cfg['league_season_id'])

    cur.execute(sql)
    league_teams = cur.fetchall()



    return render_template('background/league.html',
                           name=sidebar_items_bg['main']['name'],
                           sidebar_items=sidebar_items_bg,
                           current_cfg=cfg,
                           league_teams=league_teams
                           )


@bp.route(sidebar_items_bg['cup']['route'])
@root_login_required
def cup():
    db = get_db()
    cur = db.cursor(dictionary=True)

    return render_template('background/cup.html',
                           name=sidebar_items_bg['cup']['name'],
                           sidebar_items=sidebar_items_bg)    


@bp.route(sidebar_items_bg['supercup']['route'])
@root_login_required
def supercup():
    db = get_db()
    cur = db.cursor(dictionary=True)

    return render_template('background/supercup.html',
                           name=sidebar_items_bg['supercup']['name'],
                           sidebar_items=sidebar_items_bg)    