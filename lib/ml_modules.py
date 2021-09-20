import copy
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from . import mjtypes
from . import data_proc

def forward_one(model, feature):
    model.eval()

    x = torch.from_numpy(feature.astype(np.float32)).clone()
    x = torch.unsqueeze(x, -1)
    x = torch.unsqueeze(x, 0)
    return nn.Softmax(dim=1)(model(x)).detach().numpy()[0]

class ResBlock(nn.Module):
    def __init__(self, channels):
        super(ResBlock, self).__init__()
        self.sequential = nn.Sequential(
            nn.Conv2d(channels, channels, kernel_size=(3,1), padding=(1,0), bias=False),
            #nn.BatchNorm2d(planes),
            nn.ReLU(),
            nn.Conv2d(channels, channels, kernel_size=(3,1), padding=(1,0), bias=False),
            #nn.BatchNorm2d(planes)
        )

    def forward(self, x):
        x = self.sequential(x) + x
        return F.relu(x)

class DiscardNet(nn.Module):
    def __init__(self, in_channels, channels_num, blocks_num):
        super(DiscardNet, self).__init__()
        self.preproc = nn.Sequential(
            nn.Conv2d(in_channels=in_channels, out_channels=channels_num, kernel_size=(3,1), padding=(1,0), bias=False),
            #nn.BatchNorm2d(self.channels[0]),
            nn.ReLU()
        )

        blocks = []
        for _i in range(blocks_num):
            blocks.append(ResBlock(channels_num))
        self.res_blocks = nn.Sequential(*blocks)

        self.postproc = nn.Sequential(
            nn.Conv2d(in_channels=channels_num, out_channels=1, kernel_size=(1,1), padding=(0,0), bias=False),
            #nn.Conv2d(in_channels=channels_num, out_channels=1, kernel_size=(1,1), padding=(1,0), bias=False),
            #nn.ReLU()
        )

    def forward(self, x):
        x = self.preproc(x)
        x = self.res_blocks(x)
        x = self.postproc(x)
        x = x.view(x.size(0), -1)  # [B, C, H, W] -> [B, C*H*W]
        return x

class FuuroNet(nn.Module):
    def __init__(self, in_channels, channels_num, blocks_num):
        super(FuuroNet, self).__init__()
        self.preproc = nn.Sequential(
            nn.Conv2d(in_channels=in_channels, out_channels=channels_num, kernel_size=(3,1), padding=(1,0), bias=False),
            #nn.BatchNorm2d(self.channels[0]),
            nn.ReLU()
        )

        blocks = []
        for _i in range(blocks_num):
            blocks.append(ResBlock(channels_num))
        self.res_blocks = nn.Sequential(*blocks)

        self.postproc = nn.Sequential(
            nn.Conv2d(in_channels=channels_num, out_channels=32, kernel_size=(3,1), padding=(1,0), bias=False),
            #nn.ReLU()
        )

        self.dence = nn.Sequential(
            #nn.Linear(1024,256),
            nn.Linear(1088,256),
            nn.Linear(256,2)
        )

    def forward(self, x):
        x = self.preproc(x)
        x = self.res_blocks(x)
        x = self.postproc(x)
        x = x.view(x.size(0), -1)
        x = self.dence(x)
        return x
        #return F.log_softmax(x)

class Supervised_AI():
    def __init__(self, player_id=-1):
        self.player_id = player_id
        self.models = {}
        self.model_paths = {}
        self.model_paths['dahai'] = 'supervised_model/dahai_model_cpu_state_dict.pth'
        self.model_paths['reach'] = 'supervised_model/reach_model_cpu_state_dict.pth'
        self.model_paths['chi'] = 'supervised_model/chi_model_cpu_state_dict.pth'
        self.model_paths['pon'] = 'supervised_model/pon_model_cpu_state_dict.pth'
        self.model_paths['kan'] = 'supervised_model/kan_model_cpu_state_dict.pth'
        self.model_paths['daiminkan'] = 'supervised_model/kan_model_cpu_state_dict.pth'
        self.model_paths['ankan'] = 'supervised_model/kan_model_cpu_state_dict.pth'
        self.model_paths['kakan'] = 'supervised_model/kan_model_cpu_state_dict.pth'
        self.model_inchannels = {'reach': 560, 'chi': 564, 'pon': 564, 'ankan': 567, 'daiminkan': 567, 'kakan': 567}

    def player_ids(self):
        if self.player_id == -1:
            return [0, 1, 2, 3]
        else:
            return [self.player_id]

    def predict_discard(self, legal_actions, feature):
        if 'dahai' not in self.models:
            #self.models['dahai'] = DiscardNet(560, 256, 50)
            self.models['dahai'] = DiscardNet(560, 128, 15)
            self.models['dahai'].load_state_dict(torch.load(self.model_paths['dahai']))

        predict = forward_one(self.models['dahai'], feature)
        ret = []
        for action in legal_actions:
            if action['type'] == 'dahai':
                hai_int = mjtypes.get_hai34(mjtypes.hai_str_to_int(action['pai']))
                a = copy.deepcopy(action)
                a['prob'] = predict[hai_int]
                ret.append(a)
        return ret

    def predict_others(self, action_type, feature):
        if action_type not in self.models:
            self.models[action_type] = FuuroNet(self.model_inchannels[action_type], 128, 15)
            self.models[action_type].load_state_dict(torch.load(self.model_paths[action_type]))

        predict = forward_one(self.models[action_type], feature)
        return predict[0]

    def run(self, current_record, legal_actions=None):
        ret = [[] for i in range(4)]
        legal_actions, feature = data_proc.get_current_feature(current_record, legal_actions)

        for pid in self.player_ids():
            if 'dahai' in feature[pid]:
                ret[pid].extend(self.predict_discard(filter(lambda a: a['type'] == 'dahai', legal_actions), feature[pid]['dahai']))
            if 'reach' in feature[pid]:
                ret[pid].append({'type': 'reach', 'actor': pid, 'prob': self.predict_others('reach', feature[pid]['reach'])})
            for (action, f) in feature[pid]['others']:
                a = copy.deepcopy(action)
                a['prob'] = self.predict_others(a['type'], f)
                ret[pid].append(a)
            ret[pid].extend(filter(
                lambda a: a['actor'] == pid and a['type'] not in ['dahai', 'reach', 'chi', 'pon', 'ankan', 'daiminkan', 'kakan'],
                legal_actions
            ))

        return ret

    def choose_action(self, current_record, legal_actions=None):
        assert self.player_id != -1, "player_id == -1 in choose_action"

        candidates = self.run(current_record, legal_actions)[self.player_id]

        if len(candidates) == 0:
            return None

        horas = list(filter(lambda a: a['type'] == 'hora', candidates))
        if 0 < len(horas):
            return horas[0]

        dahais = list(filter(lambda a: a['type'] == 'dahai', candidates))
        prob_threshold = 0.5
        if 0 < len(dahais):
            kans = list(filter(lambda a: a['type'] in ['ankan', 'kakan'] and prob_threshold <= a['prob'], candidates))
            kans = sorted(kans, key=lambda a: a['prob'], reverse=True)
            if 0 < len(kans):
                del kans[0]['prob']
                return kans[0]

            reach = list(filter(lambda a: a['type'] == 'reach' and prob_threshold <= a['prob'], candidates))
            if 0 < len(reach):
                del reach[0]['prob']
                return reach[0]

            dahais = sorted(dahais, key=lambda a: a['prob'], reverse=True)
            del dahais[0]['prob']
            return dahais[0]
        else:
            fuuros = list(filter(lambda a: a['type'] in ['chi', 'pon', 'daiminkan'] and prob_threshold <= a['prob'], candidates))
            fuuros = sorted(fuuros, key=lambda a: a['prob'], reverse=True)
            if 0 < len(fuuros):
                del fuuros[0]['prob']
                return fuuros[0]

            return {'type': 'none', 'actor': self.player_id}

