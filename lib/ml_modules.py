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

class Supervised_AI():
    def __init__(self):
        self.player_ids = [0, 1, 2, 3]
        self.dahai_model_path = 'supervised_model/discard_model_cpu_state_dict.pth'
        self.dahai_model = None

    def predict_discard(self, legal_actions, feature):
        if self.dahai_model is None:
            self.dahai_model = DiscardNet(560, 256, 50)
            self.dahai_model.load_state_dict(torch.load(self.dahai_model_path))

        predict = forward_one(self.dahai_model, feature)
        print(predict)
        ret = []
        for action in legal_actions:
            if action['type'] == 'dahai':
                hai_int = mjtypes.get_hai34(mjtypes.hai_str_to_int(action['pai']))
                a = copy.deepcopy(action)
                a['prob'] = predict[hai_int]
                ret.append(a)
        return ret

    def run(self, current_record):
        ret = [[] for i in range(4)]
        legal_actions, feature = data_proc.get_legal_actions_and_feature(current_record)

        for pid in self.player_ids:
            if 'discard' in feature[pid]:
                ret[pid].extend(self.predict_discard(legal_actions, feature[pid]['discard']))

        return ret

