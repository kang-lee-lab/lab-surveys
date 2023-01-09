import pickle
import pandas as pd
import random

condition = "anxiety" # anxiety, depression, stress

# questions = [13, 16, 3, 34, 24, 22, 27]     # depression_severe
# questions = [13, 16, 3, 34, 24] # depression_moderate
# questions = [1, 4, 9, 11, 20, 23, 30]    # anxiety_severe
# questions = [30, 20, 11, 36, 40]    # anxiety_moderate
# questions = [40, 9, 11, 18, 6, 27]  # stress_severe

if condition == "anxiety":
    questions = [1, 4, 9, 11, 20, 23, 30]  
elif condition == "depression":
    questions = [3, 13, 16, 22, 24, 27, 34]
elif condition == "stress":
    questions = [6, 9, 11, 18, 27, 40]

with open("./static/{}_model_severe.bin".format(condition), "rb") as f:
    model = pickle.load(f)

answers = {}
# Generate answers

gender = random.randint(1, 2)
region = random.randint(0, 2)
age = random.randint(18, 100)

answers['gender'] = gender
answers['region'] = region
answers['age'] = age

for q in questions:
    a = random.randint(1, 4) 
    answers['Q{}A'.format(q)] = [a]

answers = pd.DataFrame.from_dict(answers)

proba = model[0].predict_proba(answers)
# predicted_label = model.predict(answer)
print(proba[0][1])