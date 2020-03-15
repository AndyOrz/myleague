from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
import competitions.scheduler.roundrobin as robin
import numpy as np
import math
from www.auth import login_required, root_login_required
from www.db import get_db
from www.config import config

bp = Blueprint('works', __name__)
cfg = config.get_cfg_global()


@bp.route('/submit_match_result', methods=('GET', 'POST'))
@login_required
def submit_match_result():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor(dictionary=True)
        sql = '''
            update matches set team1_score={}, team2_score={}
            where match_id={}
            '''.format(request.form['team1_score'],
                       request.form['team2_score'], request.form['match_id'])

        cur.execute(sql)
        db.commit()
    return redirect(url_for('index'))


@bp.route('/add_league_team', methods=('GET', 'POST'))
@login_required
def add_league_team():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor(dictionary=True)
        sql1 = '''
            insert into team (team_name, user_id, season_id)
            values('{}', {}, {})
            '''.format(request.form['team_name'], g.user['user_id'],
                       cfg['league_season_id'])

        cur.execute(sql1)
        db.commit()
    return redirect(url_for('manage.team_manage'))


@bp.route('/add_cup_team', methods=('GET', 'POST'))
@login_required
def add_cup_team():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor(dictionary=True)
        sql2 = '''
            insert into team (team_name, user_id, season_id)
            values('{}', {}, {})
            '''.format(request.form['team_name'], g.user['user_id'],
                       cfg['cup_season_id'])
        cur.execute(sql2)
        db.commit()
    return redirect(url_for('manage.team_manage'))


@bp.route('/del_team', methods=('GET', 'POST'))
@login_required
def del_team():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor(dictionary=True)
        sql = '''
            delete from team where team_id={}
            '''.format(request.form['team_id'])

        cur.execute(sql)
        db.commit()
    return redirect(url_for('manage.team_manage'))


@bp.route('/change_season_round/<which>', methods=('GET', 'POST'))
@root_login_required
def change_season_round(which):
    season_id = request.form['season'].split('-', 1)[0]
    round_id = request.form['round']
    if which == 'league':
        cfg.set('default', 'league_season_id', season_id)
        cfg.set('default', 'league_round_id', round_id)
    elif which == 'cup':
        cfg.set('default', 'cup_season_id', season_id)
        cfg.set('default', 'cup_round_id', round_id)
    elif which == 'supercup':
        cfg.set('default', 'supercup_season_id', season_id)
        cfg.set('default', 'supercup_round_id', round_id)

    with open('./www/config/global.conf', 'w') as f:
        cfg.write(f)
    return str(round_id) + "  " + str(season_id) + "  " + which


@bp.route('/cup_chouqian')
@root_login_required
def cup_chouqian():
    db = get_db()
    cur = db.cursor(dictionary=True)
    output = str()

    sql = '''
          select team_id, team_name from team where season_id={}
          '''.format(cfg['cup_season_id'])
    cur.execute(sql)
    teams = np.array(cur.fetchall())
    indeices = math.ceil(len(teams) / float(cfg['cup_group_member']))

    # 删除原来的记录
    sql = 'delete from matches where season_id={}'.format(cfg['cup_season_id'])
    cur.execute(sql)
    db.commit()

    if len(teams) == 0:
        return "清空赛程"
    # 随机分组
    np.random.shuffle(teams)
    groups = np.array_split(teams, indeices)

    # 生成赛程
    for group, i in zip(groups, range(len(groups))):
        output += "group" + chr(65 + i) + ":<br>"
        # 输出分组结果
        for team in group:
            sql = '''update team set group_id={}
                  where team_id={}'''.format(i, team['team_id'])
            cur.execute(sql)
            db.commit()

        # 小组赛程
        match_gen = robin.RoundRobinScheduler(group.tolist(), meetings=1)
        rounds = match_gen.generate_schedule()
        for round, j in zip(rounds, range(len(rounds))):
            output += "&ensp;round " + str(j + 1) + "<br>"
            for match in round:
                if (match[0] is not None and match[1] is not None):
                    output += "&ensp;&ensp;" + str(match[0]['team_name'])
                    output += " vs " + str(match[1]['team_name']) + "<br>"
                    sql = '''
                          insert into matches (season_id, round_id,
                            team1_id, team2_id) values
                            ({}, {}, {}, {})
                          '''.format(cfg['cup_season_id'], j + 1,
                                     match[0]['team_id'], match[1]['team_id'])
                    cur.execute(sql)
                    db.commit()
    return output
