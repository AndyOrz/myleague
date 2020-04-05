from flask import (Blueprint, g, render_template)

from www.auth import login_required
from www.db import get_db
from tools.tools import cutList1
from www.config import config

bp = Blueprint('league', __name__)

cfg = config.get_cfg()['global']
sidebar_items = config.get_cfg()['sidebar_items']


@bp.route(sidebar_items['league']['route'])
@login_required
def league():
    db = get_db()
    cur = db.cursor(dictionary=True)

    # scoreboard
    sql = '''
        SELECT team_name, win, draw, lose,
            goals_for, goals_against
        FROM team, scoreboard
        WHERE team.team_id=scoreboard.team_id and team.season_id = {}
        '''.format(cfg['league_season_id'])

    cur.execute(sql)
    sb = cur.fetchall()

    for i in range(len(sb)):
        sb[i]["matches"] = sb[i]['win'] + sb[i]['draw'] + sb[i]['lose']
        sb[i]["goals_diff"] = sb[i]['goals_for'] - sb[i]['goals_against']
        sb[i]["score"] = sb[i]['win'] * 3 + sb[i]['draw']

    # 排序
    sb.sort(key=lambda x: (x['score'], x['goals_diff'], x['goals_for']),
            reverse=True)
    for i in range(len(sb)):
        sb[i]['rank'] = i + 1

    # matches
    sql = '''
        SELECT match_id, team1_id, team2_id, 
            t1.team_name as team1, t2.team_name as team2,
            team1_score, team2_score
        FROM matches as m, team as t1, team as t2
        WHERE m.team1_id=t1.team_id and m.team2_id=t2.team_id
            and m.season_id = {} and m.round_id = {}
        '''.format(cfg['league_season_id'],
                   cfg['league_round_id'])

    cur.execute(sql)
    matches = cur.fetchall()

    # scoring chart
    sql = '''
        SELECT team_name, player_name, scores
        FROM player as p, team as t
        WHERE t.season_id = {} and t.team_id=p.team_id and scores>0
        ORDER BY scores desc
        '''.format(cfg['league_season_id'])

    cur.execute(sql)
    scoring_chart = cur.fetchall()

    return render_template('league/league.html',
                           name=sidebar_items['league']['name'],
                           season_id=cfg['league_season_id'],
                           sidebar_items=sidebar_items,
                           scoreboard=sb,
                           matches=matches,
                           scoring_chart=scoring_chart)


@bp.route(sidebar_items['cup']['route'])
@login_required
def cup():
    db = get_db()
    cur = db.cursor(dictionary=True)

    # scoreboard
    sql = '''
        SELECT team_name, group_id, win, draw, lose,
            goals_for, goals_against
        FROM team, scoreboard
        WHERE team.team_id=scoreboard.team_id and team.season_id = {}
            and group_id is not null
        '''.format(cfg['cup_season_id'])

    cur.execute(sql)
    sb = cur.fetchall()

    for i in range(len(sb)):
        sb[i]["matches"] = sb[i]['win'] + sb[i]['draw'] + sb[i]['lose']
        sb[i]["goals_diff"] = sb[i]['goals_for'] - sb[i]['goals_against']
        sb[i]["score"] = sb[i]['win'] * 3 + sb[i]['draw']

    # 排序
    sb.sort(key=lambda x:
            (x['group_id'], x['score'], x['goals_diff'], x['goals_for']),
            reverse=True)

    # 切片
    new_sb = cutList1(sb, "group_id")

    # 赋排名
    for group in new_sb:
        for i in range(len(group)):
            group[i]['rank'] = i + 1

    # matches
    sql = '''
        SELECT match_id, team1_id, team2_id, 
            t1.team_name as team1, t2.team_name as team2,
            team1_score, team2_score
        FROM matches as m, team as t1, team as t2
        WHERE m.team1_id=t1.team_id and m.team2_id=t2.team_id
            and m.season_id = {} and m.round_id = {}
        '''.format(cfg['cup_season_id'],
                   cfg['cup_round_id'])

    cur.execute(sql)
    matches = cur.fetchall()

    # scoring chart
    sql = '''
        SELECT team_name, player_name, scores
        FROM player as p, team as t
        WHERE t.season_id = {} and t.team_id=p.team_id and scores>0
        ORDER BY scores desc
        '''.format(cfg['cup_season_id'])

    cur.execute(sql)
    scoring_chart = cur.fetchall()

    return render_template('league/cup.html',
                           name=sidebar_items['cup']['name'],
                           season_id=cfg['cup_season_id'],
                           sidebar_items=sidebar_items,
                           scoreboard=new_sb,
                           matches=matches,
                           scoring_chart=scoring_chart)


@bp.route(sidebar_items['supercup']['route'])
@login_required
def supercup():
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    return render_template(
        'league/supercup.html',
        name=sidebar_items['supercup']['name'],
        season_id=cfg['supercup_season_id'],
        sidebar_items=sidebar_items,
    )


@bp.route(sidebar_items['team_manage']['route'])
@login_required
def team_manage():
    db = get_db()
    cur = db.cursor(dictionary=True)

    sql = '''
        SELECT team_name, team_id FROM team
        WHERE user_id={} and season_id = {}
        '''.format(g.user['user_id'], cfg['league_season_id'])

    cur.execute(sql)
    league_teams = cur.fetchall()

    sql = '''
        SELECT team_name, team_id FROM team
        WHERE user_id={} and season_id = {}
        '''.format(g.user['user_id'], cfg['cup_season_id'])

    cur.execute(sql)
    cup_teams = cur.fetchall()

    return render_template('manage/team_manage.html',
                           name=sidebar_items['team_manage']['name'],
                           sidebar_items=sidebar_items,
                           league_teams=league_teams,
                           cup_teams=cup_teams
                           )


@bp.route(sidebar_items['player_register']['route'])
@login_required
def player_register():
    db = get_db()
    cur = db.cursor(dictionary=True)

    sql = '''
        SELECT team_name, team_id FROM team
        WHERE user_id={} and season_id = {}
        '''.format(g.user['user_id'], cfg['league_season_id'])

    cur.execute(sql)
    league_teams = cur.fetchall()

    sql = '''
        SELECT team_name, team_id FROM team
        WHERE user_id={} and season_id = {}
        '''.format(g.user['user_id'], cfg['cup_season_id'])

    cur.execute(sql)
    cup_teams = cur.fetchall()
    
    return render_template('manage/player_register.html',
                           name=sidebar_items['player_register']['name'],
                           sidebar_items=sidebar_items,
                           league_teams=league_teams,
                           cup_teams=cup_teams
                           )
