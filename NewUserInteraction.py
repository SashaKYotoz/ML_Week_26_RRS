import pandas as pd
import numpy as np
from pandas.core.interchange.dataframe_protocol import DataFrame


# create algorithm to get possible recipes based on last user interaction
class NewUserInteraction:
    def get_predicted_recipe(self):
        interactions_val = pd.read_csv("student_data/interactions_val.csv")
        interactions_val["rating"] = interactions_val["rating"].fillna(2)
        interactions_val = interactions_val.sort_values(by="rating", ascending=True)

        return interactions_val