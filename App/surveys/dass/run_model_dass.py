"""
This file runs the model for the DASS survey.
"""
import pickle
import random

import pandas as pd

condition = "stress"  # anxiety, depression, stress
severity = "severe"  # severe, moderate

# questions = [13, 16, 3, 34, 24, 22, 27]     # depression_severe
# questions = [13, 16, 3, 34, 24, 22] # depression_moderate
# questions = [1, 4, 9, 11, 20, 23, 30]    # anxiety_severe
# questions = [30, 20, 11, 36, 40, 9]    # anxiety_moderate
# questions = [40, 9, 11, 18, 6, 27]  # stress_severe
# questions = [11, 29, 6, 18, 27] # stress_moderate

if condition == "anxiety":
    if severity == "severe":
        questions = [1, 4, 9, 11, 20, 23, 30]
    elif severity == "moderate":
        questions = [9, 11, 20, 30, 36, 40]

elif condition == "depression":
    if severity == "severe":
        questions = [3, 13, 16, 22, 24, 27, 34]
    elif severity == "moderate":
        questions = [3, 13, 16, 22, 24, 34]

elif condition == "stress":
    if severity == "severe":
        questions = [6, 9, 11, 18, 27, 40]
    elif severity == "moderate":
        questions = [6, 11, 18, 27, 29]

with open(
    "./static/surveys_files/{0}_model_{1}.bin".format(condition, severity), "rb"
) as f:
    model = pickle.load(f)

answers = {}
# Generate answers

gender = random.randint(1, 2)
region = random.randint(0, 2)
age = random.randint(18, 100)

answers["gender"] = gender
answers["region"] = region
answers["age"] = age

for q in questions:
    a = random.randint(1, 4)
    answers["Q{}A".format(q)] = [a]

answers = pd.DataFrame.from_dict(answers)

proba = model[0].predict_proba(answers)
# predicted_label = model.predict(answer)
# print(proba[0][1])
