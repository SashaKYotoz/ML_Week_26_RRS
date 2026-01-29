import ast
import numpy as np
import pandas as pd
from typing import List

class RecommendsFilter:
    def get_recipe_recommendations(self, user_id, n_recommendations, users_path="student_data/users.csv", recipes_path="student_data/recipes.csv"):
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

            if not req_prods.issubset(user_products):
                continue

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

    def get_interaction_recommendations(self, user_id, n_recommendations,
                                        interactions_path="student_data/interactions_train.csv",
                                        recipes_path="student_data/recipes.csv"):
        try:
            interactions = pd.read_csv(interactions_path)
            recipes = pd.read_csv(recipes_path)
        except FileNotFoundError:
            return []

        interactions["rating"] = interactions["rating"].fillna(2.5)
        user_history = interactions[interactions["user_id"] == user_id]

        if user_history.empty:
            popular_recipes = interactions.groupby("recipe_id")["rating"].mean().sort_values(ascending=False)
            top_ids = popular_recipes.head(n_recommendations).index
            return recipes[recipes["recipe_id"].isin(top_ids)]["name"].tolist()

        recipes["strength_norm"] = recipes["strength"] / 5.0
        feature_cols = ["taste_bitterness", "taste_sweetness", "taste_acidity", "taste_body", "strength_norm"]

        merged_history = pd.merge(user_history, recipes, on="recipe_id")

        if merged_history.empty:
            return []

        user_weights = merged_history["rating"]
        user_profile = np.average(merged_history[feature_cols], axis=0, weights=user_weights)

        seen_recipes = user_history["recipe_id"].unique()
        candidates = recipes[~recipes["recipe_id"].isin(seen_recipes)].copy()

        candidate_vectors = candidates[feature_cols].values
        distances = np.linalg.norm(candidate_vectors - user_profile, axis=1)

        candidates["match_score"] = distances
        recommendations = candidates.sort_values("match_score", ascending=True)

        return recommendations["name"].head(n_recommendations).tolist()

def ndcg_at_k(relevances: List[float], k: int) -> float:
    relevances = relevances[:k]
    dcg = sum(rel / np.log2(i + 2) for i, rel in enumerate(relevances))
    ideal_relevances = sorted(relevances, reverse=True)
    idcg = sum(rel / np.log2(i + 2) for i, rel in enumerate(ideal_relevances))
    return dcg / idcg if idcg > 0 else 0.0

def evaluate_model(val_path, train_path, recipes_path, n_users_limit=None, k=5):
    val_df = pd.read_csv(val_path).fillna(2.5)
    recipes_df = pd.read_csv(recipes_path).fillna(2.5)

    name_to_id = pd.Series(recipes_df.recipe_id.values, index=recipes_df.name).to_dict()
    recommender = RecommendsFilter()
    ndcg_scores = []

    unique_users = val_df['user_id'].unique()
    if n_users_limit:
        unique_users = unique_users[:n_users_limit]
        
    print(f"Num of users {len(unique_users)}...")
    
    for i, user_id in enumerate(unique_users):
        user_val_data = val_df[val_df['user_id'] == user_id]
        truth_dict = dict(zip(user_val_data['recipe_id'], user_val_data['rating']))

        try:
            rec_names = recommender.get_interaction_recommendations(
                user_id=user_id,
                n_recommendations=k,
                interactions_path=train_path, 
                recipes_path=recipes_path
            )
        except Exception as e:
            print(f"Error for user {user_id}: {e}")
            rec_names = []
            
        relevances = [float(truth_dict.get(name_to_id.get(name), 0)) for name in rec_names]
        score = ndcg_at_k(relevances, k)
        ndcg_scores.append(score)
        
        if (i + 1) % 10 == 0:
            print(f"Handled {i + 1} users. Avg NDCG@{k}: {np.mean(ndcg_scores):.4f}")

    mean_ndcg = np.mean(ndcg_scores)
    print(f"Avg NDCG@{k}: {mean_ndcg:.4f}")
    return mean_ndcg

if __name__ == "__main__":
    evaluate_model(
        val_path="student_data/interactions_val.csv",       
        train_path="student_data/interactions_train.csv",   
        recipes_path="student_data/recipes.csv",            
        n_users_limit=200,                      
        k=5                                     
    )