SET foreign_key_checks = 0;  /* 先设置外键约束检查关闭 */ 

drop table if exists user;
create table user
(
	user_id int primary key auto_increment,
	user_name char(32),
	password char(64)
);

drop table if exists season;
create table season
(
	season_id int primary key auto_increment,
	season_name char(32),
	season_type char(10) /*  leage / cup / super cup  */
);

drop table if exists team;
create table team
(
	team_id int primary key auto_increment,
	team_name char(32),
	user_id int,
	season_id int,
	constraint team_user_id foreign key(user_id) references user(user_id),
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