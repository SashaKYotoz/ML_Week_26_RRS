from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any
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
    
    u_username: str
    u_owned_equipment: Any         
    u_available_products: Any
    u_taste_bitterness: str
    u_taste_sweetness: str
    u_taste_acidity: str
    u_taste_body: str
    u_preferred_strength: str
    u_preferred_portion_size: str
    u_dietary_restrictions: Any

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
    if isinstance(data, str):
        try:
            return ast.literal_eval(data)
        except:
            return [] if "[" in data else {}
    return data

def get_recommendations(user_id: str, k: int = 5):
    user_rows = users_df[users_df['user_id'] == str(user_id)]
    
    if user_rows.empty:
        return None
    user_row = user_rows.iloc[0]
    
    user_features = user_row[['taste_pref_bitterness', 'taste_pref_sweetness', 'taste_pref_acidity', 'taste_pref_body']].values.astype(float)
    user_tensor = torch.tensor(user_features, dtype=torch.float32).unsqueeze(0)

    with torch.no_grad():
        user_emb = model.user_mlp(user_tensor) 
        scores = (recipe_embeddings * user_emb).sum(dim=1)
    
    top_scores, top_indices = torch.topk(scores, k)
    
    recommendations = []
    for score, idx in zip(top_scores, top_indices):
        idx = idx.item()
        row = recipes_df.iloc[idx]
        
        rec_name = row['recipe_name'] if 'recipe_name' in row else row.get('name', f"Recipe {row['recipe_id']}")

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
            
            "u_username": str(user_row['username']),
            "u_owned_equipment": parse_json_column(user_row['owned_equipment']),
            "u_available_products": parse_json_column(user_row['available_products']),
            "u_taste_bitterness": str(user_row['taste_pref_bitterness']),
            "u_taste_sweetness": str(user_row['taste_pref_sweetness']),
            "u_taste_acidity": str(user_row['taste_pref_acidity']),
            "u_taste_body": str(user_row['taste_pref_body']),
            "u_preferred_strength": str(user_row['preferred_strength']),
            "u_preferred_portion_size": str(user_row['preferred_portion_size']),
            "u_dietary_restrictions": parse_json_column(user_row['dietary_restrictions']),

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