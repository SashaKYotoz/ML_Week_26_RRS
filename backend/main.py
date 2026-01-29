from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from schemas import RecipeRecommendation
from load_data import load_model, load_df, load_recipe_embeddings
from recommendations import get_recommendations
from typing import List
from fastapi.templating import Jinja2Templates
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

model = load_model()
users_df, recipes_df = load_df()
recipe_embeddings = load_recipe_embeddings(model, recipes_df)

origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

@app.get("/predict", response_model=List[RecipeRecommendation])
def predict_top_k(
    user_id: str, 
    k: int =5 
):
    results = get_recommendations(users_df, recipes_df, recipe_embeddings, model, user_id, k)
    if results is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    
    return results

    
app.mount("/", StaticFiles(directory=BASE_DIR / "../front", html=True), name="front")

@app.get('/')
def home(request: Request):
    return templates.TemplateResponse(
        "index.html", 
        {"request": request} 
    )
