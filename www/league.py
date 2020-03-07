from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from www.auth import login_required
from www.db import get_db

bp = Blueprint('league', __name__)
sidebar_items = ["联赛", "杯赛", "超级杯"]
season_id = 1
round_id = 1


@bp.route('/')
@login_required
def index():
    db = get_db()
    cur = db.cursor(dictionary=True)

    # scoreboard
    sql = '''
        SELECT team_name, win, draw, lose,
            goals_for, goals_against
        FROM team, scoreboard
        WHERE team.team_id=scoreboard.team_id and team.season_id = {}
        order by rank
        '''.format(season_id)

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
        SELECT match_id, t1.team_name as team1, t2.team_name as team2,
            team1_score, team2_score
        FROM matches as m, team as t1, team as t2
        WHERE m.team1_id=t1.team_id and m.team2_id=t2.team_id
            and m.season_id = {} and m.round = {}
        '''.format(season_id, round_id)

    cur.execute(sql)
    matches = cur.fetchall()

    return render_template(
        'league/index.html',
        sidebar_items=sidebar_items,
        scoreboard=sb,
        matches=matches
    )


@bp.route('/submit_match_result', methods=('GET', 'POST'))
def submit_match_result():
    if request.method == 'POST':
        db = get_db()
        cur = db.cursor(dictionary=True)

        sql = '''
            update matches set team1_score={}, team2_score={}
            where match_id={}
            '''.format(request.form['team1_score'],
                       request.form['team2_score'],
                       request.form['match_id'])

        cur.execute(sql)
        db.commit()
    return redirect(url_for('index'))
