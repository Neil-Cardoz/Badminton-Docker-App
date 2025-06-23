CREATE DATABASE badminton_db;
USE badminton_db;

CREATE TABLE matches (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    team_a VARCHAR(100),
    team_b VARCHAR(100),
    winner_team VARCHAR(100),
    created_at DATETIME
);

CREATE TABLE teams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT,
    team_name VARCHAR(100),
    player_name VARCHAR(100),
    FOREIGN KEY (match_id) REFERENCES matches(match_id)
);

-- View or Table for stats
CREATE VIEW player_stats AS
SELECT 
    player_name,
    SUM(CASE WHEN winner_team = team_name THEN 1 ELSE 0 END) AS wins,
    SUM(CASE WHEN winner_team != team_name THEN 1 ELSE 0 END) AS losses
FROM teams t
JOIN matches m ON t.match_id = m.match_id
GROUP BY player_name;

-- For bar graph
CREATE VIEW player_stats_percent AS
SELECT *,
       ROUND(100.0 * wins / (wins + losses), 2) AS win_percent
FROM player_stats;
