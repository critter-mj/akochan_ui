import sys
import copy
import json
import subprocess
import eel
import pathlib
import argparse

from lib.util import *
from lib.mjtypes import *
from lib.tenhou_convlog import *
from lib.data_proc import *
from lib import ml_modules

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

    def open_file(self, file_name):
        self.log_json = read_log_json('./log/' + file_name)
        self.log_pos = 0
        return 0

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
        game_record = []
        for action in self.log_json:
            if action["type"] == "start_kyoku":
                game_record = [game_record[0]]
            game_record.append(action)
        input_json["record"] = game_record
        request_json = user_request
        if 0 < len(self.log_json):
            last_action = self.log_json[-1]
            if last_action["type"] == "start_game":
                request_json["chicha"] = 0
                request_json["haiyama"] = create_haiyama()
            elif last_action["type"] == "hora" or last_action["type"] == "ryukyoku":
                request_json["haiyama"] = create_haiyama()

        input_json["request"] = request_json
        cmd += json.dumps(input_json, separators=(',', ':'))
        print("---cmd---")
        print(cmd)
        c = subprocess.check_output(cmd.split()).decode('utf-8').rstrip()
        print("---recv")
        print(c)
        return json.loads(c)

    def loop(self, user_request):
        while True:
            recv_json = self.call_game_server(user_request)
            user_request = {}
            if recv_json["msg_type"].startswith("update"):
                # to do playwavfile
                for new_action in recv_json["new_moves"]:
                    self.log_json.append(new_action)
                    if (("actor" in new_action and new_action["actor"] == self.view_pid and new_action["type"] != "tsumo") or
                        (new_action["type"] == "start_kyoku")):
                        eel.reset_button_ui_game()()

                self.log_pos = len(self.log_json) - 1
                self.update_game_state_by_log_pos()

                eel.update_game(self.view_pid)() # 括弧を二重にすると同期するらしい。
                # 現状他家のツモ牌を表示することができていない。self.log_jsonの長さを条件にreturnすると、その巡のツモは見えるので、同期処理の問題と思われる。

                if recv_json["msg_type"] == "update":
                    if self.log_json[-1]["type"] == "end_game":
                        self.ui_state = UI_State.UI_DEFAULT
                        break
                    if self.log_json[-1]["type"] == "hora" or self.log_json[-1]["type"] == "ryukyoku":
                        eel.show_end_kyoku(self.log_json[-1])()
                        # to do ダブロン対応
                        break
                elif recv_json["msg_type"] == "update_and_dahai":
                    self.ui_state = UI_State.UI_MATCH_DAHAI
                    break
                else:
                    self.prev_selected_pos = -1
                    self.ui_state = UI_State.UI_MATCH_FUURO
                    break
            elif recv_json["msg_type"] == "dahai_again":
                self.ui_state = UI_State.UI_MATCH_DAHAI
                break
            elif recv_json["msg_type"] == "fuuro_again":
                self.prev_selected_pos = -1
                self.ui_state = UI_State.UI_MATCH_FUURO
                break
        
        if self.ui_state == UI_State.UI_MATCH_DAHAI or self.ui_state == UI_State.UI_MATCH_FUURO:
            if "legal_moves" in recv_json:
                self.legal_moves = recv_json["legal_moves"]
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

                if self.ui_state == UI_State.UI_MATCH_DAHAI:
                    for lm in recv_json["legal_moves"]:
                        if lm[0]["type"] == "ankan":
                            eel.append_ankan_button(lm[0]["consumed"][0])()
                        elif lm[0]["type"] == "kakan":
                            eel.append_kakan_button(lm[0]["pai"])()

gs = Global_State()

@eel.expose
def get_log(view_pid):
    if view_pid == -1:
        return gs.log_json

    return [mask_action(j, view_pid) for j in gs.log_json]

@eel.expose
def get_log_pos():
    return gs.log_pos

@eel.expose
def get_log_len():
    return len(gs.log_json)

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
    return gs.open_file(file_name)

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

def do_pon_chi(c1, c2):
    assert gs.ui_state == UI_State.UI_MATCH_FUURO, "do_pon_chi gs.ui_state is not UI_MATCH_FUURO"
    assert is_valid_hai(c1) and is_valid_hai(c2), "do_pon_chi hai is not valid"
    gs.ui_state = UI_State.UI_MATCH_UPDATE
    hai = hai_str_to_int(gs.log_json[-1]["pai"])
    target = gs.log_json[-1]["actor"]
    consumed = [c1, c2]
    consumed.sort(key=lambda hai: haikind(hai)*100 + hai)
    gs.prev_selected_pos = -1 # update_and_fuuro の時にperv_selected_pos = -1にしているため不要かもしれない。
    if haikind(c1) == haikind(c2):
        gs.loop(make_pon(gs.view_pid, target, hai, consumed))
    else:
        gs.loop(make_chi(gs.view_pid, target, hai, consumed))

# 打牌を行うときに、send_stringし更新を待ってから描画を行うとなぜかとても動作が遅いため、合法な打牌である場合先に描画してからsend_stringする。
def update_tehai_ui_if_legal_dahai(action_json):
    for moves in gs.legal_moves:
        if moves[0] == action_json:
            game_state = copy.deepcopy(gs.game_state)
            game_state.go_next_state(action_json)
            eel.update_game_child2(game_state.to_json(gs.view_pid), gs.view_pid)()
            break

@eel.expose
def tehai_clicked(pos):
    print("tehai_clicked: " + str(pos))
    tehai_list = get_sorted_tehai(gs.game_state.player_state[gs.view_pid].tehai)
    if gs.ui_state == UI_State.UI_MATCH_DAHAI:
        gs.ui_state = UI_State.UI_MATCH_UPDATE
        if pos == len(tehai_list):
            hai = gs.game_state.player_state[gs.view_pid].prev_tsumo
            tsumogiri = True
        else:
            hai = tehai_list[pos]
            tsumogiri = False

        action_json = make_dahai(gs.view_pid, hai, tsumogiri)
        update_tehai_ui_if_legal_dahai(action_json)
        gs.loop(action_json)
    elif gs.ui_state == UI_State.UI_MATCH_FUURO and 0 <= gs.prev_selected_pos and pos == gs.prev_selected_pos:
        gs.prev_selected_pos = -1
        #gs.tehai_info.update(gs.game_state.player_state[gs.view_pid], gs.HAI_IMAGE)
    elif gs.ui_state == UI_State.UI_MATCH_FUURO and 0 <= gs.prev_selected_pos and is_valid_hai(tehai_list[gs.prev_selected_pos]):
        do_pon_chi(tehai_list[gs.prev_selected_pos], tehai_list[pos])
    elif gs.ui_state == UI_State.UI_MATCH_FUURO:
        gs.prev_selected_pos = pos
        #gs.tehai_info.update(gs.game_state.player_state[gs.view_pid], gs.HAI_IMAGE)

@eel.expose
def do_hora():
    if gs.ui_state == UI_State.UI_MATCH_DAHAI or gs.ui_state == UI_State.UI_MATCH_FUURO:
        gs.ui_state = UI_State.UI_MATCH_UPDATE
        hai = hai_str_to_int(gs.log_json[-1]["pai"])
        target = gs.log_json[-1]["actor"]
        gs.loop(make_hora(gs.view_pid, target, hai))

@eel.expose
def do_reach():
    if gs.ui_state == UI_State.UI_MATCH_DAHAI:
        gs.ui_state = UI_State.UI_MATCH_UPDATE
        gs.loop(make_reach(gs.view_pid))

@eel.expose
def do_pass():
    if gs.ui_state == UI_State.UI_MATCH_FUURO:
        gs.ui_state = UI_State.UI_MATCH_UPDATE
        gs.loop(make_none(gs.view_pid))

@eel.expose
def do_kyushukyuhai():
    if gs.ui_state == UI_State.UI_MATCH_DAHAI or gs.ui_state == UI_State.UI_MATCH_FUURO:
        gs.ui_state = UI_State.UI_MATCH_UPDATE
        gs.loop(make_kyushukyuhai(gs.view_pid))

@eel.expose
def do_daiminkan():
    assert gs.ui_state == UI_State.UI_MATCH_FUURO, "do_daiminkan gs.ui_state is not UI_MATCH_FUURO"
    gs.ui_state = UI_State.UI_MATCH_UPDATE
    hai = hai_str_to_int(gs.log_json[-1]["pai"])
    target = gs.log_json[-1]["actor"]
    if hai % 10 == 5 and hai < 30:
        gs.loop(make_daiminkan_aka(gs.view_pid, target, hai))
    else:
        gs.loop(make_daiminkan_default(gs.view_pid, target, hai))

@eel.expose
def do_ankan(hai_str):
    assert gs.ui_state == UI_State.UI_MATCH_DAHAI, "do_ankan gs.ui_state is not UI_MATCH_DAHAI"
    hai = haikind(hai_str_to_int(hai_str))
    if hai % 10 == 5 and hai < 30:
        gs.loop(make_ankan_aka(gs.view_pid, hai))
    else:
        gs.loop(make_ankan_default(gs.view_pid, hai))

@eel.expose
def do_kakan(hai_str):
    assert gs.ui_state == UI_State.UI_MATCH_DAHAI, "do_kakan gs.ui_state is not UI_MATCH_DAHAI"
    hai = hai_str_to_int(hai_str)
    if hai % 10 == 5 and hai < 30:
        gs.loop(make_kakan_aka(gs.view_pid, hai))
    else:
        gs.loop(make_kakan_default(gs.view_pid, hai))

@eel.expose
def confirm_end_kyoku():
    gs.loop({})

def main(args):
    if args.tenhou_convlog:
        if args.year != None:
            proc_year(args.year)
        else:
            print("please specify year")
    elif args.dump_feature:
        if args.input_logdir is None:
            print("please specify input_logdir")
        elif args.input_regex is None:
            print("please specify input_regex")
        elif args.output_npzdir is None:
            print("please specify output_npzdir")
        else:
            proc_batch_mjailog(args.input_logdir, args.input_regex, args.output_npzdir, args.update)
    elif args.check_model:
        game_record = read_log_json('log/haifu_log_1001_0.json')
        current_record = game_record[:args.log_line]
        ai = ml_modules.Supervised_AI(args.player_id)

        if args.player_id == -1:
            ret = ai.run(current_record)
            for pid in range(4):
                for action in ret[pid]:
                    print(action)
        else:
            current_record = [mask_action(j, args.player_id) for j in current_record]
            current_record[0]['player_id'] = args.player_id
            ret = ai.choose_action(current_record)
            print(ret)

    else:
        eel.init("web")
        eel.start("main.html")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--tenhou_convlog', action='store_true')
    parser.add_argument('--year')
    parser.add_argument('--dump_feature', action='store_true')
    parser.add_argument('--input_logdir')
    parser.add_argument('--input_regex')
    parser.add_argument('--output_npzdir')
    parser.add_argument('--update', action='store_true')
    parser.add_argument('--check_model', action='store_true')
    parser.add_argument('--log_line', type=int, default=0)
    parser.add_argument('--player_id', type=int, default=-1, choices=[-1, 0, 1, 2, 3])

    argv = copy.deepcopy(sys.argv)
    # The following process replaces '--argfile xx.txt' with the contents of xx.txt.
    for i in range(len(argv) - 1):
        if argv[i] == '--argfile':
            with open(argv[i+1], 'r') as f:
                argv = argv[:i] + f.read().split() + argv[i+2:]
            break

    args = parser.parse_args(argv[1:])
    main(args)
