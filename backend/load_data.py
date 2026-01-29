import pandas as pd
from twotower import TwoTowerModel
import torch

def load_model():
    model = TwoTowerModel(user_dim=4, item_dim=4, embedding_dim=32)
    model.load_state_dict(torch.load('./model_weights.pth', map_location=torch.device('cpu')))
    model.eval()
    return model

def load_df():
    users_df = pd.read_csv('../student_data/users.csv').fillna(0)
    recipes_df = pd.read_csv('../student_data/recipes.csv').fillna(0)

    return users_df, recipes_df

def load_recipe_embeddings(model, recipes_df):
    recipe_features = recipes_df[['taste_bitterness', 'taste_sweetness', 'taste_acidity', 'taste_body']].values
    recipe_tensor = torch.tensor(recipe_features, dtype=torch.float32)

    with torch.no_grad():
        recipe_embeddings = model.item_mlp(recipe_tensor)
        
    return recipe_embeddings