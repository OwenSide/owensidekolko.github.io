CREATE TABLE IF NOT EXISTS games (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    board TEXT,
    winner TEXT
);

CREATE TABLE IF NOT EXISTS moves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id INTEGER,
    move_number INTEGER,
    player TEXT,
    position INTEGER,
    FOREIGN KEY (game_id) REFERENCES games(id)
);