$.fn.show_players = function (players) {
    this.empty();
    this.append()
    players.forEach(player => {
        this.append(() => {
            str = '<tr>';
            str += '<td data-player_id="' + player['player_id'] + '">' + player['player_name'] + '</td>';
            str += '<td><input type="number" class="form-control" style="width: 80px" value="0"' + '></td>';
            str += '</tr>';
            return str;
        });
    });
}

$.fn.get_scores = function () {
    var score_list = [];
    this.each((i, e) => {
        var player_id = $(e).children("td:eq(0)").data('player_id');
        var scores = $(e).children("td:eq(1)").find('input').val();
        if (scores > 0)
            score_list.push({
                player_id: player_id,
                scores: scores
            })
    });
    return score_list
}