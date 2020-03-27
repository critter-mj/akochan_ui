import json
import subprocess
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

    def call_game_server(self, user_request: dict) -> dict:
        cmd = "./system.exe game_server "
        c = subprocess.check_output(cmd.split())
        c = c.decode('utf-8').rstrip()
        input_json = {}
        input_json["record"] = self.log_json
        request_json = user_request
        if 0 < len(self.log_json):
            last_action = self.log_json[-1]
            if last_action["type"] == "start_game":
                request_json["chicha"] = 0
                request_json["haiyama"] = create_haiyama()

        input_json["request"] = request_json
        cmd += json.dumps(input_json, separators=(',', ':'))
        c = subprocess.check_output(cmd.split()).decode('utf-8').rstrip()
        return json.loads(c)

    def loop(self, user_request):
        while True:
            recv_json = self.call_game_server(user_request)
            print(recv_json)
            user_request = {}
            #recv_json = json.loads(recv_message)
            if recv_json["msg_type"].startswith("update"):
                # to do playwavfile
                for new_action in recv_json["new_moves"]:
                    gs.log_json.append(new_action)

                gs.log_pos = len(gs.log_json) - 1
                gs.update_game_state_by_log_pos()

                eel.update(gs.view_pid)() # 括弧を二重にすると同期するらしい。
                #if "actor" in recv_json["action"] and recv_json["action"]["actor"] == gs.view_pid and recv_json["action"]["type"] != "tsumo":
                #    eel.reset_button_ui()()

                if recv_json["msg_type"] == "update":
                    if gs.log_json[-1]["type"] == "end_game":
                        gs.ui_state = UI_State.UI_DEFAULT
                        break
                    #if recv_json["action"]["type"] == "hora" or recv_json["action"]["type"] == "ryukyoku":
                    #    eel.show_end_kyoku(recv_json["action"])()
                    #    break
                elif recv_json["msg_type"] == "update_and_dahai":
                    gs.ui_state = UI_State.UI_MATCH_DAHAI
                    break
                else:
                    gs.prev_selected_pos = -1
                    gs.ui_state = UI_State.UI_MATCH_FUURO
                    break
            elif recv_json["msg_type"] == "dahai_again":
                gs.ui_state = UI_State.UI_MATCH_DAHAI
                break
            elif recv_json["msg_type"] == "fuuro_again":
                gs.prev_selected_pos = -1
                gs.ui_state = UI_State.UI_MATCH_FUURO
                break
        
        if gs.ui_state == UI_State.UI_MATCH_DAHAI or gs.ui_state == UI_State.UI_MATCH_FUURO:
            if "legal_moves" in recv_json:
                gs.legal_moves = recv_json["legal_moves"]
                def type_exist(type_str):
                    for lm in recv_json["legal_moves"]:
                        if lm[0]["type"] == type_str:
                            return True
                    return False

                if type_exist("hora"):
                    eel.activate_hora_button()()

                if type_exist("reach"):
                    eel.activate_reach_button()()

                if type_exist("daiminkan"):
                    eel.activate_daiminkan_button()()

                if type_exist("none"):
                    eel.activate_pass_button()()

                if type_exist("ryukyoku"):
                    eel.activate_ryukyoku_button()()

                if gs.ui_state == UI_State.UI_MATCH_DAHAI:
                    for lm in recv_json["legal_moves"]:
                        if lm[0]["type"] == "ankan":
                            eel.append_ankan_button(lm[0]["consumed"][0])()
                        elif lm[0]["type"] == "kakan":
                            eel.append_kakan_button(lm[0]["pai"])()

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


@eel.expose
def start_game(seed):
    gs.log_json = []
    gs.log_pos = 0
    gs.view_pid = 0
    gs.ui_state = UI_State.UI_MATCH_UPDATE
    random.seed(seed)
    gs.loop({})

if __name__ == '__main__':
     main()