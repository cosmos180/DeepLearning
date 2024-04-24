'''
Author       : bughero jinxinhou@tuputech.com
Date         : 2024-03-27 18:17:58
LastEditors  : bughero jinxinhou@tuputech.com
LastEditTime : 2024-03-28 12:42:33
FilePath     : /DeepLearning/python/DeepLearningPython/pytorch/model_net/ConvNet.py
Description  : 

Copyright (c) 2024 by Antyme, All Rights Reserved. 
'''
from torch import nn

# 定义模型


class ConvNet(nn.Module):
    def __init__(self):
        super(ConvNet, self).__init__()
        self.layer1 = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=5, stride=1, padding=2),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2))
        self.layer2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=5, stride=1, padding=2),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2))
        # self.layer3 = nn.Sequential(
        #     nn.Conv2d(64, 32, kernel_size=5, stride=1, padding=2),
        #     nn.ReLU(),
        #     nn.MaxPool2d(kernel_size=2, stride=2))
        self.drop_out = nn.Dropout()
        self.fc1 = nn.Linear(7 * 7 * 64, 1000)
        self.fc2 = nn.Linear(1000, 10)

    def forward(self, x):
        out = self.layer1(x)
        out = self.layer2(out)
        # out = self.layer3(out)
        out = out.reshape(out.size(0), -1)
        out = self.drop_out(out)
        out = self.fc1(out)
        return self.fc2(out)
