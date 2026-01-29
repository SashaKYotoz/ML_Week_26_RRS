import ast
import torch

def parse_json_column(data):
    if isinstance(data, str):
        try:
            return ast.literal_eval(data)
        except:
            return [] if "[" in data else {}
    return data

def is_recipe_available(row, user_products, user_equipment):
    recipe_equip = set(parse_json_column(row.get('required_equipment', [])))
    recipe_prods = set(parse_json_column(row.get('required_products', {})).keys())
    
    if not recipe_equip.issubset(set(user_equipment)):
        return False
        
    if not recipe_prods.issubset(set(user_products)):
        return False
        
    return True

def get_recommendations(users_df, recipes_df, recipe_embeddings, model, user_id: str, k: int = 5):
    user_rows = users_df[users_df['user_id'] == str(user_id)]
    if user_rows.empty:
        return None
    user_row = user_rows.iloc[0]

    user_inventory = set(parse_json_column(user_row['available_products']))
    user_equipment = set(parse_json_column(user_row['owned_equipment']))
    
    user_features = user_row[['taste_pref_bitterness', 'taste_pref_sweetness', 'taste_pref_acidity', 'taste_pref_body']].values.astype(float)
    user_tensor = torch.tensor(user_features, dtype=torch.float32).unsqueeze(0)

    with torch.no_grad():
        user_emb = model.user_mlp(user_tensor) 
        scores = (recipe_embeddings * user_emb).sum(dim=1)
    
    top_scores, top_indices = torch.sort(scores, descending=True)
    
    recommendations = []
    for score, idx in zip(top_scores, top_indices):
        if len(recommendations) >= k:
            break
            
        idx = idx.item()
        row = recipes_df.iloc[idx]
        
        if not is_recipe_available(row, user_inventory, user_equipment):
            continue

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