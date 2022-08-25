SELECT *
FROM levelupapi_gametype g
ORDER BY g.label;

SELECT * FROM auth_user;
SELECT * FROM authtoken_token;
-- **table name not the fixture name**
SELECT * FROM levelupapi_gamer;
SELECT * FROM levelupapi_game;
SELECT * FROM levelupapi_event;


SELECT 
    e.id,
    e.description,
    e.date, 
    e.time,
    e.game_id,
    game.title AS game_name,
    e.organizer_id,
    u.first_name||' '||u.last_name AS full_name
FROM levelupapi_event e
JOIN levelupapi_gamer g ON g.id = e.organizer_id
JOIN auth_user u ON u.id = g.user_id
JOIN levelupapi_game game ON game.id = e.game_id;
