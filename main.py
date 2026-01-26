import pandas as pd
import numpy as np
import ast

def get_recipe_recommendations(user_id, n_recommendations, users_path, recipes_path):

    try:
        users_df = pd.read_csv(users_path)
        recipes_df = pd.read_csv(recipes_path)
    except FileNotFoundError as e:
        return [f"Error: File not found - {e}"]

    user_row = users_df[users_df['user_id'] == user_id]
    if user_row.empty:
        return [f"Error: User ID {user_id} not found."]

    user = user_row.iloc[0]

    try:
        user_equip = set(ast.literal_eval(user['owned_equipment']))
        user_products = set(ast.literal_eval(user['available_products']))
    except (ValueError, SyntaxError):
        return ["Error: Could not parse user equipment or product data."]

    user_prefs = np.array([
        user['taste_pref_bitterness'],
        user['taste_pref_sweetness'],
        user['taste_pref_acidity'],
        user['taste_pref_body'],
        user['preferred_strength'] / 5.0
    ])

    recommendations = []

    for _, recipe in recipes_df.iterrows():

        try:
            req_equip = set(ast.literal_eval(recipe['required_equipment']))
            req_prods_dict = ast.literal_eval(recipe['required_products'])
            req_prods = set(req_prods_dict.keys())
        except (ValueError, SyntaxError):
            continue
        if not req_equip.issubset(user_equip):
            continue

        # If user is missing ANY required ingredient, skip
        if not req_prods.issubset(user_products):
            continue

        # --- Soft Constraints: Calculate Similarity Score ---
        recipe_profile = np.array([
            recipe['taste_bitterness'],
            recipe['taste_sweetness'],
            recipe['taste_acidity'],
            recipe['taste_body'],
            recipe['strength'] / 5.0
        ])

        distance = np.linalg.norm(user_prefs - recipe_profile)

        recommendations.append({
            'recipe_name': recipe['name'],
            'description': recipe['description'],
            'match_score': distance
        })

    recommendations.sort(key=lambda x: x['match_score'])

    return [rec['recipe_name'] for rec in recommendations[:n_recommendations]]


if __name__ == "__main__":
    target_user_id = 'user_00000'
    num_recs = 5

    print(f"Generating {num_recs} recommendations for {target_user_id}...")
    results = get_recipe_recommendations(target_user_id, num_recs,"student_data/users.csv", "student_data/recipes.csv")

    for i, recipe in enumerate(results, 1):
        print(f"{i}. {recipe}")