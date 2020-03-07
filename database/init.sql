SET foreign_key_checks = 0;  /* 先设置外键约束检查关闭 */ 

drop table if exists user;
create table user
(
    user_id int primary key auto_increment,
    user_name char(32),
    password char(94)
);

drop table if exists season;
create table season
(
    season_id int primary key auto_increment,
    season_name char(32),
    season_type char(10), /*  leage / cup / super cup  */
    season_status char(1) /*是否可用*/
);

drop table if exists team;
create table team
(
    team_id int primary key auto_increment,
    team_name char(32),
    user_id int,
    season_id int,
    /*注释此行是为了暂时屏蔽登录功能
    constraint team_user_id foreign key(user_id) references user(user_id),*/
    constraint team_season_id foreign key(season_id) references season(season_id)
);


drop table if exists matches;
create table matches
(
    match_id int primary key auto_increment,
    season_id int,
    round smallint,
    team1_id int,
    team2_id int,
    team1_score tinyint,
    team2_score tinyint,
    constraint match_season_id foreign key(season_id) references season(season_id)
);


drop table if exists scoreboard;
create table scoreboard
(
    season_id int,
    team_id int,
    win tinyint,
    draw tinyint,
    lose tinyint,
    goals_for smallint,
    goals_against smallint,
    primary key(season_id,team_id)
);


drop table if exists player;
create table player
(
    player_id int primary key auto_increment,
    player_name varchar(32),
    team_id int,
    season_id int,
    scores smallint,
    constraint player_season_id foreign key(season_id) references season(season_id),
    constraint player_team_id foreign key(team_id) references team(team_id)
);

SET foreign_key_checks = 1; /* 开启外键约束检查，以保持表结构完整性 */ 

DELIMITER $
create trigger update_score after update on matches for each row
begin
    /*新增比赛结果*/
    if (old.team1_score is null and old.team2_score is null 
        and new.team1_score is not null and new.team2_score is not null)
    then
        if (new.team1_score>new.team2_score) then
            update scoreboard set win=win+1, goals_for=goals_for+new.team1_score,
                goals_against=goals_against+new.team2_score
            where team_id=new.team1_id;
            update scoreboard set lose=lose+1, goals_for=goals_for+new.team2_score,
                goals_against=goals_against+new.team1_score
            where team_id=new.team2_id;
        elseif (new.team1_score=new.team2_score) then
            update scoreboard set draw=draw+1, goals_for=goals_for+new.team1_score,
                goals_against=goals_against+new.team2_score
            where team_id=new.team1_id;
            update scoreboard set draw=draw+1, goals_for=goals_for+new.team2_score,
                goals_against=goals_against+new.team1_score
            where team_id=new.team2_id;
        else
            update scoreboard set lose=lose+1, goals_for=goals_for+new.team1_score,
                goals_against=goals_against+new.team2_score
            where team_id=new.team1_id;
            update scoreboard set win=win+1, goals_for=goals_for+new.team2_score,
                goals_against=goals_against+new.team1_score
            where team_id=new.team2_id;
        end if;
    end if;

    /*删除比赛结果*/
    if (old.team1_score is not null and old.team2_score is not null 
        and new.team1_score is null and new.team2_score is null)
    then
        if (old.team1_score>old.team2_score) then
            update scoreboard set win=win-1, goals_for=goals_for-old.team1_score,
                goals_against=goals_against-old.team2_score
            where team_id=new.team1_id;
            update scoreboard set lose=lose-1, goals_for=goals_for-old.team2_score,
                goals_against=goals_against-old.team1_score
            where team_id=new.team2_id;
        elseif (old.team1_score=old.team2_score) then
            update scoreboard set draw=draw-1, goals_for=goals_for-old.team1_score,
                goals_against=goals_against-old.team2_score
            where team_id=new.team1_id;
            update scoreboard set draw=draw-1, goals_for=goals_for-old.team2_score,
                goals_against=goals_against-old.team1_score
            where team_id=new.team2_id;
        else
            update scoreboard set lose=lose-1, goals_for=goals_for-old.team1_score,
                goals_against=goals_against-old.team2_score
            where team_id=new.team1_id;
            update scoreboard set win=win-1, goals_for=goals_for-old.team2_score,
                goals_against=goals_against-old.team1_score
            where team_id=new.team2_id;
        end if;
    end if;

end $
DELIMITER ;