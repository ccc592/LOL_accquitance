import time
# import tkinter as tk
# from tkinter import messagebox
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
#from win10toast import ToastNotifier
import psutil

from BdReq import BdReq
from ConfigUtils import my_config
from DbUtils import DbUtils
from GameRound import GameRound
from ImageUtils import ImageUtils


def find_process_by_name(process_name):
    for process in psutil.process_iter():
        try:
            if process.name() == process_name:
                print("\nfind process {}".format(process_name))
                return process
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None


class GameManager:
    def __init__(self):
        self.__game_process = None
        self.__baidu_req = BdReq()
        self.__game_round_list = []
        self.__data_base = DbUtils()
        self.__image_utils = ImageUtils()
        self.__filter_name = my_config.get("game_name", "friend").split(",")
        self.__filter_name.append(my_config.get("game_name", "myself"))
        #self.__toast = ToastNotifier()

        # self.__root_tk = tk.Tk()
        # self.__root_tk.withdraw()  # 隐藏主窗口

        self._app = QApplication([])
        self.__message_box = QMessageBox()

        self.__is_new_game = True

    def get_exe_process(self):
        self.__game_process = find_process_by_name("Obsidian.exe")
        while self.__game_process is None:
            time.sleep(10)
            self.__game_process = find_process_by_name("Obsidian.exe")
        return self.__game_process

    def is_filter_name(self, name):
        return name in self.__filter_name

    def run(self):
        while True:
            # 检测进程运行
            if find_process_by_name("Obsidian.exe") is not None:
                if self.__is_new_game:
                    self.__is_new_game = False
                    self.__image_utils.screenshot()
                    self.check_player()
                else:
                    time.sleep(10)
            else:
                self.__is_new_game = True
                time.sleep(10)

    def check_player(self):
        # 切割图片
        self.__image_utils.crop_image()
        # 调用ocr
        data = self.__baidu_req.request_ocr("./resource/finish_image.png")
        # 生成DateFrame结构
        now_game_round = GameRound()
        now_game_round.read_jason_data(data)
        data.clear()
        self.__game_round_list.append(now_game_round)
        # 写入数据库
        # 写入 game表
        self.__data_base.cursor.execute("""INSERT INTO game (game_name, game_date)
            VALUES("本日第{}场比赛", datetime('now','localtime'))
            """.format(len(self.__game_round_list)))
        self.__data_base.conn.commit()
        # 写入 player表
        now_game_round.save_player_data(self.__data_base.conn)
        # 写入 game_player表
        self.__data_base.cursor.execute("SELECT MAX(game_id) FROM game")
        latest_game_id = self.__data_base.cursor.fetchone()[0]
        now_game_round.save_game_player_data(self.__data_base.conn, latest_game_id)
        # 读数据库进行检测逻辑
        name_list = now_game_round.get_player_name_list()
        frequent_encounters = []
        for name in name_list:
            if self.is_filter_name(name):
                continue

            self.__data_base.cursor.execute("SELECT player_id FROM player WHERE player_name=?", (name,))
            player_id = self.__data_base.cursor.fetchone()[0]
            self.__data_base.cursor.execute(
                "SELECT game.game_date, game_player.hero_name, game_player.team_color, game_player.player_faction, player.play_count FROM game JOIN game_player ON game.game_id = game_player.game_id JOIN player ON game_player.player_id = player.player_id WHERE game_player.player_id = ? ORDER BY game.game_id DESC LIMIT 5",
                (player_id,))
            player_data = self.__data_base.cursor.fetchall()
            for index, data in enumerate(player_data):
                encounter = dict(player_name=None, hero_name=None, team_color=None, player_faction=None,
                                 game_date=None, play_count=None)
                if index == 0:
                    continue
                else:
                    encounter["player_name"] = name
                    encounter['game_date'] = data[0]
                    encounter["hero_name"] = data[1]
                    encounter["team_color"] = data[2]
                    encounter["player_faction"] = data[3]
                    encounter['play_count'] = data[4]
                    frequent_encounters.append(encounter)
                    break
        # 发送通知
        if len(frequent_encounters) > 0:
            for player in frequent_encounters:
                try:
                    # self.__toast.show_toast(
                    #     f"发现熟人({player['player_name']})，总共已经和你打过{player['play_count']}场了",
                    #     f"上次对局时间是{player['game_date']}，他的英雄是{player['hero_name']}，阵营是{player['player_faction']}，队伍是{player['team_color']}",
                    #     duration=2)
                    # messagebox.showinfo(f"发现熟人({player['player_name']})，总共已经和你打过{player['play_count']}场了",f"上次对局时间是{player['game_date']}，他的英雄是{player['hero_name']}，阵营是{player['player_faction']}，队伍是{player['team_color']}")
                    self.__message_box.setWindowTitle(f"发现熟人({player['player_name']})，总共已经和你打过{player['play_count']}场了")
                    self.__message_box.setText(f"上次对局时间是{player['game_date']}，他的英雄是{player['hero_name']}，阵营是{player['player_faction']}，队伍是{player['team_color']}")
                    self.__message_box.setWindowFlags(self.__message_box.windowFlags() | Qt.WindowStaysOnTopHint)
                    self.__message_box.exec_()
                except Exception as e:
                    print(f"Error: {e}")
