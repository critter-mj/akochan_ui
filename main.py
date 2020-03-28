import json
import eel

from lib.mjtypes import *

class UI_State(IntEnum):
    UI_DEFAULT = 0 # デフォルト
    UI_MATCH_UPDATE = 1 # 対局中、AI処理更新中
    UI_MATCH_DAHAI = 2 # 対局中、打牌待機中
    UI_MATCH_FUURO = 3 # 対局中、副露待機中

class Global_State:
    def __init__(self):
        self.log_json = []
        self.log_pos = 0
        self.game_state = get_game_state_start_kyoku(json.loads(INITIAL_START_KYOKU))
        self.view_pid = 0
        self.ui_state = UI_State.UI_DEFAULT
        self.prev_selected_pos = -1
        self.legal_moves = []

        self.context = None
        self.socket = None

    def update_game_state_by_log_pos(self):
        if self.log_json[self.log_pos]["type"] == "start_kyoku":
            self.game_state = get_game_state_start_kyoku(self.log_json[self.log_pos])
        else:
            kyoku_init_pos = self.log_pos
            while 0 <= kyoku_init_pos and self.log_json[kyoku_init_pos]["type"] != "start_kyoku":
                kyoku_init_pos -= 1
            if kyoku_init_pos == -1:
                return
            print("kyoku_init_pos:", kyoku_init_pos)
            self.game_state = get_game_state_start_kyoku(self.log_json[kyoku_init_pos])
            for i in range(kyoku_init_pos + 1, self.log_pos + 1):
                self.game_state.go_next_state(self.log_json[i])

gs = Global_State()

def main():
    eel.init("web")
    eel.start("main.html")

@eel.expose
def get_log(view_pid):
    if view_pid == -1:
        return gs.log_json

    return [mask_action(j, view_pid) for j in gs.log_json]

@eel.expose
def get_log_pos():
    return gs.log_pos

@eel.expose
def get_view_pid():
    return gs.view_pid

@eel.expose
def change_view_pid(add):
    gs.view_pid = (gs.view_pid + add) % 4
    return gs.view_pid

@eel.expose
def get_game_state(view_pid):
    return gs.game_state.to_json(view_pid)

@eel.expose
def open_file_name(file_name):
    gs.log_json = []
    gs.log_pos = 0
    with open('./log/' + file_name, encoding="utf-8") as f:
        l = f.readlines()
        for i in range(len(l)):
            gs.log_json.append(json.loads(l[i]))

    return 0
    # to do error handle
    #return gs.log_json

@eel.expose
def log_pos_selected(pos):
    print(pos)
    gs.log_pos = pos
    gs.update_game_state_by_log_pos()
    return gs.game_state.to_json(-1)

if __name__ == '__main__':
     main()