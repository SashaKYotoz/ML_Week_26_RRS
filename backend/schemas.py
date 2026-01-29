from pydantic import BaseModel
from typing import List, Dict, Any

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