import pandas as pd
import numpy as np
import ast
from RecommendsFilter import RecommendsFilter
from ColdStartRecommender import ColdStartRecommender

if __name__ == "__main__":
    recommender = ColdStartRecommender()

    print("--- Generic Top Rated ---")
    print(recommender.get_recommendations(n_recommendations=3))

    user_prefs = {
        'equipment': ['espresso_machine', 'grinder'],
        'products': ['coffee_beans'],
        'taste': [0.8, 0.1, 0.6, 0.9, 3]
    }
    print("\n--- Personalized Cold Start ---")
    print(recommender.get_recommendations(preferences=user_prefs, n_recommendations=3))