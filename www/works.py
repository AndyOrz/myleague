from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
import competitions.scheduler.roundrobin as robin
import numpy as np
import math
import json
from www.auth import login_required, root_login_required
from www.db import get_db
from www.config import config
from tools.tools import cutList1

bp = Blueprint('works', __name__, url_prefix='/works')
cfg = config.get_cfg()['global']


@bp.route('/submit_match_result', methods=('GET', 'POST'))
@login_required
def submit_match_result():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor(dictionary=True)

        sql = '''
            select team1_score, team2_score from matches
            where match_id={}
            '''.format(request.form['match_id'])
        cur.execute(sql)
        match = cur.fetchone()
        if match['team1_score'] is not None and match[
                'team2_score'] is not None:
            return "不可重复提交！"

        team1_scores = json.loads(request.form['team1_scores'])
        team2_scores = json.loads(request.form['team2_scores'])
        team1_score = 0
        team2_score = 0

        for s in team1_scores:
            team1_score = team1_score + int(s['scores'])
            sql = '''
                update player set scores=scores+{} where player_id={}
                '''.format(s['scores'], s['player_id'])
            cur.execute(sql)
            db.commit()

        for s in team2_scores:
            team2_score = team2_score + int(s['scores'])
            sql = '''
                update player set scores=scores+{} where player_id={}
                '''.format(s['scores'], s['player_id'])
            cur.execute(sql)
            db.commit()

        sql = '''
            update matches set team1_score={}, team2_score={}
            where match_id={}
            '''.format(team1_score, team2_score, request.form['match_id'])
        cur.execute(sql)
        db.commit()

    return "OK!"


@bp.route('/create_season/<which>', methods=('GET', 'POST'))
@root_login_required
def create_season(which):
    db = get_db()
    cur = db.cursor(dictionary=True)
    season_name = request.form['name']

    sql = '''
          insert into season (season_name,season_type,season_status)
          values ("{}","{}","{}")
          '''.format(season_name, which, 'y')
    cur.execute(sql)
    db.commit()

    return redirect(url_for('background.main'))


@bp.route('/add_team/<which>', methods=('GET', 'POST'))
@login_required
def add_team(which):
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor(dictionary=True)
        if which == 'league':
            season_id = cfg['league_season_id']
        elif which == 'cup':
            season_id = cfg['cup_season_id']
        elif which == 'supercup':
            season_id = cfg['supercup_season_id']
        sql1 = '''
            insert into team (team_name, user_id, season_id)
            values('{}', {}, {})
            '''.format(request.form['team_name'], g.user['user_id'], season_id)

        cur.execute(sql1)
        db.commit()
    return redirect(url_for('league.team_manage'))


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
    return "OK"


@bp.route('/rename_team', methods=('GET', 'POST'))
@login_required
def rename_team():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor(dictionary=True)
        sql = '''
            update team set team_name="{}" where team_id={}
            '''.format(request.form['new_team_name'], request.form['team_id'])

        cur.execute(sql)
        db.commit()
    return "OK"


@bp.route('/change_season_round/<which>', methods=('GET', 'POST'))
@root_login_required
def change_season_round(which):
    season_id = request.form['season']
    round_id = request.form['round']
    if which == 'league':
        cfg['league_season_id'] = season_id
        cfg['league_round_id'] = round_id
    elif which == 'cup':
        cfg['cup_season_id'] = season_id
        cfg['cup_round_id'] = round_id
    elif which == 'supercup':
        cfg['supercup_season_id'] = season_id
        cfg['supercup_round_id'] = round_id

    config.change_and_save_cfg()
    return redirect(url_for('background.main'))


@bp.route('/get_schedule', methods=('GET', 'POST'))
@root_login_required
def get_schedule():
    db = get_db()
    cur = db.cursor(dictionary=True)
    season_id = request.form['season_id']
    sql = '''
        SELECT match_id, round_id, t1.group_id as group_id,
            t1.team_name as team1, t2.team_name as team2,
            team1_score, team2_score
        FROM matches as m, team as t1, team as t2
        WHERE m.team1_id=t1.team_id and m.team2_id=t2.team_id
            and m.season_id = {} order by round_id
        '''.format(season_id)

    cur.execute(sql)
    rounds = cutList1(cur.fetchall(), "round_id")

    return json.dumps(rounds)


@bp.route('/delete_schedule', methods=('GET', 'POST'))
@root_login_required
def delete_schedule():
    db = get_db()
    cur = db.cursor(dictionary=True)
    season_id = request.form['season_id']
    sql = '''
          update matches set team1_score=null, team2_score=null
          where season_id={}
          '''.format(season_id)
    cur.execute(sql)
    db.commit()

    sql = '''
          update player,team set scores=0
          where player.team_id=team.team_id and season_id={}
          '''.format(season_id)
    cur.execute(sql)
    db.commit()

    sql = '''
          delete from matches where season_id={}
          '''.format(season_id)
    cur.execute(sql)
    db.commit()

    return ""


@bp.route('/generate_schedule', methods=('GET', 'POST'))
@root_login_required
def generate_schedule():
    db = get_db()
    cur = db.cursor(dictionary=True)
    season_id = request.form['season_id']

    sql = '''
          select season_type from season where season_id={}
          '''.format(season_id)
    cur.execute(sql)
    season_type = cur.fetchone()['season_type']

    sql = '''
          select team_id, team_name from team where season_id={}
          '''.format(season_id)
    cur.execute(sql)
    teams = np.array(cur.fetchall())
    schedule = list()

    if season_type == 'league':
        match_gen = robin.RoundRobinScheduler(teams.tolist(), meetings=2)
        rounds = match_gen.generate_schedule()
        for round, j in zip(rounds, range(len(rounds))):
            for match in round:
                if (match[0] is not None and match[1] is not None):
                    schedule.append({
                        "round_id": j + 1,
                        "team1_id": match[0]['team_id'],
                        "team1": match[0]['team_name'],
                        "team2_id": match[1]['team_id'],
                        "team2": match[1]['team_name']
                    })
        schedule.sort(key=lambda x: x['round_id'])
        schedule = cutList1(schedule, 'round_id')

    elif season_type == 'cup':
        indeices = math.ceil(len(teams) / float(cfg['cup_group_member']))
        # 随机分组
        np.random.shuffle(teams)
        groups = np.array_split(teams, indeices)

        # 生成赛程
        for group, i in zip(groups, range(len(groups))):
            # 小组赛程
            match_gen = robin.RoundRobinScheduler(group.tolist(), meetings=1)
            rounds = match_gen.generate_schedule()
            for round, j in zip(rounds, range(len(rounds))):
                for match in round:
                    if (match[0] is not None and match[1] is not None):
                        schedule.append({
                            "round_id": j + 1,
                            "group_id": i + 1,
                            "team1_id": match[0]['team_id'],
                            "team1": match[0]['team_name'],
                            "team2_id": match[1]['team_id'],
                            "team2": match[1]['team_name']
                        })

        schedule.sort(key=lambda x: x['round_id'])
        schedule = cutList1(schedule, 'round_id')

    return json.dumps(schedule)


@bp.route('/save_schedule', methods=('GET', 'POST'))
@root_login_required
def save_schedule():
    db = get_db()
    cur = db.cursor(dictionary=True)
    season_id = request.form['season_id']
    schedule = json.loads(request.form['schedule'])

    for round in schedule:
        for match in round:
            sql = '''
                insert into matches (season_id, round_id,
                    team1_id, team2_id) values ({},{},{},{})
                '''.format(season_id, match['round_id'], match['team1_id'],
                           match['team2_id'])
            cur.execute(sql)
            db.commit()

    return "OK"


@bp.route('/get_players', methods=('GET', 'POST'))
@root_login_required
def get_players():
    db = get_db()
    cur = db.cursor(dictionary=True)
    team_id = request.form['team_id']

    sql = '''
          select player_id, player_name, scores from player where team_id={}
          order by scores desc
          '''.format(team_id)
    cur.execute(sql)
    players = cur.fetchall()

    return json.dumps(players)


@bp.route('/add_player', methods=('GET', 'POST'))
@login_required
def add_player():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor(dictionary=True)
        sql = '''
            insert into player (player_name,team_id,scores) values ("{}",{},{})
            '''.format(request.form['player_name'], request.form['team_id'], 0)

        cur.execute(sql)
        db.commit()
    return "OK"


@bp.route('/del_player', methods=('GET', 'POST'))
@login_required
def del_player():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor(dictionary=True)
        sql = '''
            delete from player where player_id={}
            '''.format(request.form['player_id'])

        cur.execute(sql)
        db.commit()
    return "OK"


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
