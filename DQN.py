import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T

import random

from utils import *

memory = np.load('train_2.npy').item()

class DQN(nn.Module):

    def __init__(self, h, w, outputs):
    	self.M = config.N**2
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(self.M)
        #self.bn1 = nn.BatchNorm2d(16)
        self.fc2 = nn.Linear(self.M)
        #self.bn2 = nn.BatchNorm2d(32)
        self.fc3 = nn.Linear(self.M)
        #self.bn3 = nn.BatchNorm2d(32)

        self.head = nn.Linear(self.M)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        return self.head(x)


def optimize_model():
	transitions = random.sample(memory, BATCH_SIZE)
