import sqlite3


class DbUtils:
    def __init__(self):
        # 连接数据库时，设置成中国时区
        self.conn = sqlite3.connect('./database/game.db', detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.cursor = self.conn.cursor()

        # Create tables for game, player and game_player
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS game (
            game_id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_name TEXT NOT NULL,
            game_date DATETIME NOT NULL
        );
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS player (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            play_count INTEGER NOT NULL DEFAULT 0
        );
        ''')

        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_player (
            game_id INTEGER NOT NULL,
            player_id INTEGER NOT NULL,
            player_name TEXT NOT NULL,
            hero_name TEXT NOT NULL,
            team_color TEXT NOT NULL,
            player_faction TEXT NOT NULL,
            PRIMARY KEY (game_id, player_id),
            FOREIGN KEY (game_id) REFERENCES game(game_id),
            FOREIGN KEY (player_id) REFERENCES player(player_id)
        );
        ''')

        self.conn.commit()

    def __del__(self):
        self.conn.close()


