import pathlib
import subprocess

from lib.util import *
from lib.mjtypes import *

class Data_Processor:
    def __init__(self):
        self.x_discard = []
        self.y_discard = []

        self.x_chi = []
        self.y_chi = []

        self.x_pon = []
        self.y_pon = []

        self.x_daiminkan = []
        self.y_daiminkan = []

        self.x_kakan = []
        self.y_kakan = []

        self.x_ankan = []
        self.y_ankan = []

        self.x_reach = []
        self.y_reach = []

    def get_legal_moves(self, current_record):
        cmd = "./system.exe legal_action "
        input_json = {}
        input_json["record"] = current_record
        cmd += json.dumps(input_json, separators=(',', ':'))
        c = subprocess.check_output(cmd.split()).decode('utf-8').rstrip()
        return json.loads(c)

    def process_record(self, game_record):
        game_state = get_game_state_start_kyoku(json.loads(INITIAL_START_KYOKU))
        current_record = []
        for i, action in enumerate(game_record):
            if action["type"] == "start_kyoku":
                game_state = get_game_state_start_kyoku(action)
                current_record = [current_record[0]]
            else:
                game_state.go_next_state(action)
            current_record.append(action)
            if action["type"] == "tsumo" or action["type"] == "chi" or action["type"] == "pon":
                if game_record[i+1]["type"] == "dahai" or game_record[i+1]["type"] == "reach":
                    x = game_state.to_numpy(action["actor"])
                    self.x_discard.append(x)

                    y = np.zeros(34, dtype=np.int)
                    i_dahai = i+1 if game_record[i+1]["type"] == "dahai" else i+2
                    hai = hai_str_to_int(game_record[i_dahai]["pai"])
                    y[get_hai34(hai)] = 1
                    self.y_discard.append(y)
            
            if action["type"] == "tsumo" or action["type"] == "dahai":
                legal_actions = self.get_legal_moves(current_record)
                for legal_action in legal_actions:
                    if legal_action["type"] == "chi":
                        if ((game_record[i+1]["type"] == "hora" and game_record[i+1]["actor"] != legal_action["actor"]) or
                            (game_record[i+1]["type"] == "pon" and game_record[i+1]["actor"] != legal_action["actor"]) or
                            (game_record[i+1]["type"] == "daiminkan" and game_record[i+1]["actor"] != legal_action["actor"])):
                            continue
                        x = game_state.to_numpy(legal_action["actor"])
                        self.x_chi.append(x)
                        self.y_chi.append(1 if legal_action == game_record[i+1] else 0)
                    if legal_action["type"] == "pon":
                        if game_record[i+1]["type"] == "hora" and game_record[i+1]["actor"] != legal_action["actor"]:
                            continue
                        x = game_state.to_numpy(legal_action["actor"])
                        self.x_pon.append(x)
                        self.y_pon.append(1 if legal_action == game_record[i+1] else 0)
                    if legal_action["type"] == "daiminkan":
                        if game_record[i+1]["type"] == "hora" and game_record[i+1]["actor"] != legal_action["actor"]:
                            continue
                        x = game_state.to_numpy(legal_action["actor"])
                        self.x_daiminkan.append(x)
                        self.y_daiminkan.append(1 if legal_action == game_record[i+1] else 0)
                    if legal_action["type"] == "kakan":
                        x = game_state.to_numpy(legal_action["actor"])
                        self.x_kakan.append(x)
                        self.y_kakan.append(1 if legal_action == game_record[i+1] else 0)
                    if legal_action["type"] == "ankan":
                        x = game_state.to_numpy(legal_action["actor"])
                        self.x_ankan.append(x)
                        self.y_ankan.append(1 if legal_action == game_record[i+1] else 0)
                    if legal_action["type"] == "reach":
                        x = game_state.to_numpy(legal_action["actor"])
                        self.x_reach.append(x)
                        self.y_reach.append(1 if legal_action == game_record[i+1] else 0)

    def dump_child(self, dir_path, tenhou_id, action_type, X, Y):
        if 0 < len(Y):
            out_dir_pathstr = dir_path + "/" + action_type + "/" + tenhou_id[:4] + "/" + tenhou_id[:8]
            out_dir = pathlib.Path(out_dir_pathstr)
            if not out_dir.is_dir():
                out_dir.mkdir(parents=True)
            np.savez(out_dir_pathstr + "/" + action_type + "_" + tenhou_id, X, Y)
            X.clear()
            Y.clear()

    def dump(self, dir_path, tenhou_id):
        self.dump_child(dir_path, tenhou_id, "discard", self.x_discard, self.y_discard)
        self.dump_child(dir_path, tenhou_id, "chi", self.x_chi, self.y_chi)
        self.dump_child(dir_path, tenhou_id, "pon", self.x_pon, self.y_pon)
        self.dump_child(dir_path, tenhou_id, "daiminkan", self.x_daiminkan, self.y_daiminkan)
        self.dump_child(dir_path, tenhou_id, "kakan", self.x_kakan, self.y_kakan)
        self.dump_child(dir_path, tenhou_id, "ankan", self.x_ankan, self.y_ankan)
        self.dump_child(dir_path, tenhou_id, "reach", self.x_reach, self.y_reach)

def proc_tenhou_mjailog(tenhou_id):
    dp = Data_Processor()
    game_record = read_log_json("tenhou_mjailog/" + tenhou_id[:4] + "/" + tenhou_id[:8] + "/" + tenhou_id + ".json")
    dp.process_record(game_record)
    dp.dump("tenhou_npz", tenhou_id)                 
    