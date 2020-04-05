$.fn.show_players = function(data) {
    this.empty();
    var players = JSON.parse(data);
    players.forEach(player => {
        this.append(() => {
            str = '<tr>';
            str +='<td>'+player['player_name']+'</td>';
            str +='<td>'+player['scores']+'</td>';
            str +='<td>'+'<button type="button" class="btn btn-sm btn-secondary" data-toggle="modal"';
            str +='data-target="#Modal_Delete" data-player_id="'+player['player_id']+'"';
            str +='data-player_name="'+player['player_name']+'">取消注册</button>'+'</td>';
            str += '</tr>';
            return str;
        });
    });
}
                    