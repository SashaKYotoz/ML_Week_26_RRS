from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict
import torch
import pandas as pd
import numpy as np
from twotower import TwoTowerModel
from fastapi.middleware.cors import CORSMiddleware
import ast 

app = FastAPI()


origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "https://saleable-calceolate-carolyne.ngrok-free.dev",
]

model = None
users_df = None
recipes_df = None
recipe_embeddings = None 
recipe_ids = None


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RecipeRecommendation(BaseModel):
    recipe_id: str
    recipe_name: str
    description: str
    taste_bitterness: str
    taste_sweetness: str
    taste_acidity: str
    taste_body: str
    strength: str
    portion_size_ml: str
    preparation_time_minutes: str
    difficulty: str
    required_products: Dict[str, str] 
    required_equipment: List[str]     
    tags: List[str]                  
    score: float

users_df = pd.read_csv('student_data/users.csv').fillna(0)
recipes_df = pd.read_csv('student_data/recipes.csv').fillna(0)

model = TwoTowerModel(user_dim=4, item_dim=4, embedding_dim=32)
model.load_state_dict(torch.load('model_weights.pth', map_location=torch.device('cpu')))
model.eval()

recipe_features = recipes_df[['taste_bitterness', 'taste_sweetness', 'taste_acidity', 'taste_body']].values
recipe_tensor = torch.tensor(recipe_features, dtype=torch.float32)

with torch.no_grad():
    recipe_embeddings = model.item_mlp(recipe_tensor)

def parse_json_column(data):
    """Допоміжна функція, якщо в CSV списки збережені як рядки '["item1", "item2"]'"""
    if isinstance(data, str):
        try:
            return ast.literal_eval(data)
        except:
            return [] if "[" in data else {}
    return data

def get_recommendations(user_id: str, k: int = 5):
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
        idx = idx.item()
        row = recipes_df.iloc[idx]
        
        recommendations.append({
            "recipe_id": str(row['recipe_id']),
            "recipe_name": row.get('name', ""),
            "description": row.get('description', ""),
            "taste_bitterness": str(row['taste_bitterness']),
            "taste_sweetness": str(row['taste_sweetness']),
            "taste_acidity": str(row['taste_acidity']),
            "taste_body": str(row['taste_body']),
            "strength": str(row.get('strength', "")),
            "portion_size_ml": str(row.get('portion_size_ml', "")),
            "preparation_time_minutes": str(row.get('preparation_time_minutes', "")),
            "difficulty": str(row.get('difficulty', "")),
            "required_products": parse_json_column(row.get('required_products', {})),
            "required_equipment": parse_json_column(row.get('required_equipment', [])),
            "tags": parse_json_column(row.get('tags', [])),
            "score": float(score) * 5
        })
        
    return recommendations

@app.get("/predict", response_model=List[RecipeRecommendation])
def predict_top_k(
    user_id: str, 
    k: int =5 
):
    results = get_recommendations(user_id, k)
    
    if results is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    
    return results