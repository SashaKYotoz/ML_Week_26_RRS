import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from twotower import TwoTowerModel

app = FastAPI()

model = None
users_df = None
recipes_df = None
recipe_embeddings = None 
recipe_ids = None        

class PredictRequest(BaseModel):
    user_id: str
    k: int = 5

class RecipeRecommendation(BaseModel):
    recipe_id: str
    recipe_name: str
    score: float
   
users_df = pd.read_csv('student_data/users.csv').fillna(0)
recipes_df = pd.read_csv('student_data/recipes.csv').fillna(0)


model = TwoTowerModel(user_dim=4, item_dim=4, embedding_dim=32)
model.load_state_dict(torch.load('model_weights.pth'))

model.eval() 

recipe_features = recipes_df[['taste_bitterness', 'taste_sweetness', 'taste_acidity', 'taste_body']].values
recipe_tensor = torch.tensor(recipe_features, dtype=torch.float32)

with torch.no_grad():
    recipe_embeddings = model.item_mlp(recipe_tensor)
    
recipe_ids = recipes_df['recipe_id'].values
    

def get_recommendations(user_id: str, k: int=5):
    user_row = users_df[users_df['user_id'] == user_id]
    if user_row.empty:
        return None
    
    user_features = user_row[['taste_pref_bitterness', 'taste_pref_sweetness', 'taste_pref_acidity', 'taste_pref_body']].values
    user_tensor = torch.tensor(user_features, dtype=torch.float32)

    with torch.no_grad():
        user_emb = model.user_mlp(user_tensor) 
        
        scores = (recipe_embeddings * user_emb).sum(dim=1)
    
    top_scores, top_indices = torch.topk(scores, k)
    
    recommendations = []
    for score, idx in zip(top_scores, top_indices):
        r_id = recipe_ids[idx.item()]
        r_name = recipes_df[recipes_df['recipe_id'] == r_id]['recipe_name'].values[0] if 'recipe_name' in recipes_df.columns else f"Recipe {r_id}"
        
        recommendations.append({
            "recipe_id": r_id,
            "recipe_name": r_name,
            "score": 5*score
        })
        
    return recommendations

@app.post("/predict", response_model=List[RecipeRecommendation])
def predict_top_k(request: PredictRequest):
    results = get_recommendations(request.user_id, request.k)
    
    if results is None:
        raise HTTPException(status_code=404, detail=f"User {request.user_id} not found")
    
    return results
