import pandas as pd

from ConfigUtils import my_config


class GameRound:
    def __init__(self):
        self.__current_game_pd = pd.DataFrame(
            columns=["team_color", "player_faction", "player_name", "hero_name"])
        self.__myself_name = my_config.get("game_name", "myself")

    def read_jason_data(self, json_data):
        data_ocr = [ele["words"] for ele in json_data["words_result"]]
        insert_value = []

        for i, ele in enumerate(data_ocr[:5]):
            insert_value.append({"team_color": "blue", "player_faction": None, "hero_name": ele})

        for i, ele in enumerate(data_ocr[5:10]):
            insert_value[i]["player_name"] = ele

        for i, ele in enumerate(data_ocr[10:15]):
            insert_value.append({"team_color": "red", "player_faction": None, "hero_name": ele})

        for i, ele in enumerate(data_ocr[15:20]):
            insert_value[i + 5]["player_name"] = ele

        self.__current_game_pd = self.__current_game_pd.append(pd.DataFrame(insert_value), ignore_index=True)

        self.judge_faction()

        print(self.__current_game_pd)

    def judge_faction(self):
        if self.__current_game_pd['player_name'].head(5).str.contains(self.__myself_name).any():
            self.__current_game_pd.iloc[:5, self.__current_game_pd.columns.get_loc("player_faction")] = "友方"
            self.__current_game_pd.iloc[5:10, self.__current_game_pd.columns.get_loc("player_faction")] = "敌方"
        else:
            self.__current_game_pd.iloc[:5, self.__current_game_pd.columns.get_loc("player_faction")] = "敌方"
            self.__current_game_pd.iloc[5:10, self.__current_game_pd.columns.get_loc("player_faction")] = "友方"

    def save_player_data(self, db_con):
        cursor = db_con.cursor()
        for index, row in self.__current_game_pd.iterrows():
            cursor.execute("SELECT play_count FROM player WHERE player_name=?", (row["player_name"],))
            result = cursor.fetchone()
            if result:
                now_play_count = result[0] + 1
                cursor.execute(
                    "UPDATE player SET play_count=? WHERE player_name=?",
                    (now_play_count, row["player_name"]))
            else:
                cursor.execute(
                    "INSERT INTO player (player_name, play_count) VALUES (?,?)",
                    (row["player_name"], 1))

            db_con.commit()

    def save_game_player_data(self, db_con, game_id):
        cursor = db_con.cursor()
        for index, row in self.__current_game_pd.iterrows():
            cursor.execute("SELECT player_id FROM player WHERE player_name=?", (row["player_name"],))
            player_id = cursor.fetchone()[0]
            cursor.execute(
                "INSERT INTO game_player (game_id, player_id, player_name, hero_name, team_color, player_faction) VALUES (?,?,?,?,?,?)",
                (game_id, player_id, row["player_name"], row["hero_name"], row["team_color"], row["player_faction"]))

        db_con.commit()

    def get_player_name_list(self):
        return self.__current_game_pd["player_name"].tolist()
