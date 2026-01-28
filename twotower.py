import torch
import torch.nn as nn

class TwoTowerModel(nn.Module):
    def __init__(self, user_dim=4, item_dim=4, embedding_dim=32): 
        super(TwoTowerModel, self).__init__()
        
        self.user_mlp = nn.Sequential(
            nn.Linear(user_dim, 64),
            nn.ReLU(),
            nn.Linear(64, embedding_dim)  
        )
        
        self.item_mlp = nn.Sequential(
            nn.Linear(item_dim, 64),
            nn.ReLU(),
            nn.Linear(64, embedding_dim)
        )

    def forward(self, user_features, item_features):
        user_embedding = self.user_mlp(user_features)
        item_embedding = self.item_mlp(item_features)
        
        score = (user_embedding * item_embedding).sum(dim=1)
        
        return score
