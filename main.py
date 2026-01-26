import pandas as pd
import numpy as np

users = pd.read_csv("student_data/users.csv")
recipes = pd.read_csv("student_data/recipes.csv")


i = int(input())



# def prepare_users(users_local):
#     users_local.drop(columns=["username"], inplace=True)
#     users_local.drop(columns=["account_created"], inplace=True)
#     users_local["preferred_portion_size"] = users_local["preferred_portion_size"].map({'small': [1,0,0], 'medium': [0]})
#     return users_local


# users = prepare_users(users)
#
# print(users.preferred_portion_size)
# interactions_train = pd.read_csv("student_data/interactions_train.csv")
# interactions_val = pd.read_csv("student_data/interactions_val.csv")
# interactions_val_cold = pd.read_csv("student_data/interactions_val_cold.csv")
# cold_users = pd.read_json("student_data/cold_users.json")