$.fn.show_schedule = function(data) {
    this.empty();
    var rounds = JSON.parse(data);
    rounds.forEach(matches => {
        this.append(() => {
            str = '<div class="card">';
            str += '<div class="card-header">第' + matches[0]['round_id'] + '轮</div>';
            str += '<div class="card-body">';
            matches.forEach(match => {
                str += match['team1'] + ' vs ' + match['team2'];
                if (match['team1_score'] != null && match['team2_score'] != null)
                    str+='&emsp;'+match['team1_score']+'-'+match['team2_score']+ '<br>';
                else str+= '<br>';
            });
            str += '</div></div>';
            return str;
        });
    });
}
