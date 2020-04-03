from lib.mjtypes import *

class Data_Processor:
    def __init__(self):
        self.x_discard = []
        self.y_discard = []
        self.c_discard = 0

    def process_record(self, game_record):
        game_state = get_game_state_start_kyoku(json.loads(INITIAL_START_KYOKU))
        for i, action in enumerate(game_record):
            if action["type"] == "start_kyoku":
                game_state = get_game_state_start_kyoku(action)
            else:
                game_state.go_next_state(action)
            if action["type"] == "tsumo":
                if game_record[i+1]["type"] == "dahai" or game_record[i+1]["type"] == "reach":
                    x = game_state.to_numpy(action["actor"])
                    self.x_discard.append(x)

                    y = np.zeros(34, dtype=np.int)
                    i_dahai = i+1 if game_record[i+1]["type"] == "dahai" else i+2
                    hai = hai_str_to_int(game_record[i_dahai]["pai"])
                    y[get_hai34(hai)] = 1
                    self.y_discard.append(y)

    def dump(self, dir_path, threshold):
        if threshold < len(self.y_discard):
            np.savez(dir_path + "/discard_" + str(self.c_discard), self.x_discard, self.y_discard)
            self.x_discard = []
            self.y_discard = []
            self.c_discard += 1
                    
    