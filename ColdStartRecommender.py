import pandas as pd
import numpy as np
import ast


class ColdStartRecommender:
    def __init__(self, recipes_path="student_data/recipes.csv",
                 interactions_path="student_data/interactions_train.csv"):
        self.recipes = pd.read_csv(recipes_path)
        self.interactions = pd.read_csv(interactions_path)

        # Pre-calculate global recipe stats for "No Preference" users
        self.recipe_stats = self._calculate_weighted_ratings()

    def _calculate_weighted_ratings(self, min_votes=3):
        """
        Calculates a weighted score to avoid recommending recipes
        with a single 5.0 rating.
        Formula: (v / (v+m) * R) + (m / (v+m) * C)
        """
        # Fill NA ratings with neutral 2.5 before calculating
        self.interactions["rating"] = self.interactions["rating"].fillna(2.5)

        stats = self.interactions.groupby("recipe_id")["rating"].agg(['mean', 'count'])

        C = stats['mean'].mean()  # Mean vote across the whole report
        m = min_votes  # Minimum votes required to be listed

        # Filter for recipes that actually exist in the recipes table
        stats = stats[stats.index.isin(self.recipes["recipe_id"])]

        def weighted_rating(x):
            v = x['count']
            R = x['mean']
            return (v / (v + m) * R) + (m / (v + m) * C)

        stats['weighted_score'] = stats.apply(weighted_rating, axis=1)
        return stats

    def get_recommendations(self, preferences=None, n_recommendations=5):
        """
        preferences: dict (optional) containing:
            - 'equipment': list of strings
            - 'products': list of strings
            - 'taste': list of floats [bitter, sweet, acid, body, strength (0-5)]
        """

        # SCENARIO 1: Completely Absent User (No Preferences)
        # Return top rated recipes by weighted global score
        if not preferences:
            top_ids = self.recipe_stats.sort_values('weighted_score', ascending=False).head(n_recommendations).index
            return self.recipes[self.recipes['recipe_id'].isin(top_ids)][['name', 'description']].to_dict('records')

        # SCENARIO 2: Cold User with Selected Preferences
        # Filter by constraints, then sort by taste similarity
        filtered_recipes = self.recipes.copy()

        user_equip = set(preferences.get('equipment', []))
        user_prods = set(preferences.get('products', []))
        # Default taste to balanced (0.5) and medium strength (2.5/5 -> 0.5) if missing
        user_taste = np.array(preferences.get('taste', [0.5, 0.5, 0.5, 0.5, 2.5]))

        # Normalize strength in user input to 0-1 matches recipe data structure
        if len(user_taste) == 5 and user_taste[4] > 1:
            user_taste[4] = user_taste[4] / 5.0

        valid_recipes = []

        for _, recipe in filtered_recipes.iterrows():
            # 1. Hard Filter: Equipment & Products
            try:
                req_equip = set(ast.literal_eval(recipe['required_equipment']))
                req_prods_dict = ast.literal_eval(recipe['required_products'])
                req_prods = set(req_prods_dict.keys())
            except (ValueError, SyntaxError):
                continue

            # If user lacks equipment or products, skip
            if not req_equip.issubset(user_equip):
                continue
            if not req_prods.issubset(user_prods):
                continue

            # 2. Soft Sort: Taste Distance
            recipe_profile = np.array([
                recipe['taste_bitterness'],
                recipe['taste_sweetness'],
                recipe['taste_acidity'],
                recipe['taste_body'],
                recipe['strength'] / 5.0
            ])

            # Euclidean distance: Lower is better (closer match)
            distance = np.linalg.norm(user_taste - recipe_profile)

            valid_recipes.append({
                'name': recipe['name'],
                'match_score': distance,
                'difficulty': recipe['difficulty']
            })

        # Sort by smallest distance (best match)
        valid_recipes.sort(key=lambda x: x['match_score'])

        return valid_recipes[:n_recommendations]