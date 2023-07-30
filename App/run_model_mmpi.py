import pickle
import random

import pandas as pd

status = ["DT", "HsT", "HyT", "MaT", "MfT", "PaT", "PdT", "PtT", "ScT", "SiT"]

questions = [
    2,
    3,
    6,
    7,
    8,
    9,
    12,
    18,
    21,
    22,
    23,
    24,
    27,
    32,
    33,
    35,
    37,
    38,
    42,
    51,
    57,
    63,
    64,
    67,
    68,
    71,
    76,
    82,
    84,
    91,
    93,
    94,
    97,
    102,
    103,
    106,
    107,
    110,
    117,
    119,
    120,
    122,
    123,
    124,
    127,
    128,
    134,
    141,
    145,
    152,
    155,
    157,
    163,
    164,
    167,
    168,
    170,
    175,
    177,
    178,
    179,
    181,
    187,
    192,
    201,
    202,
    220,
    224,
    229,
    230,
    231,
    234,
    238,
    245,
    267,
    268,
    272,
    278,
    279,
    281,
    289,
    292,
    296,
    298,
    301,
    315,
    316,
    318,
    321,
    324,
    339,
    342,
    346,
    350,
    358,
    360,
    370,
    383,
    471,
    527,
]

with open("./static/models/mmpi_models.bin", "rb") as f:
    all_models = pickle.load(f)

answers = {}
# Generate answers
for q in questions:
    a = random.randint(0, 2)
    answers["Q{}".format(q)] = [a]

age = random.randint(18, 100)
gender = random.randint(0, 1)

answers["Age"] = age
answers["Gender"] = gender

answers = pd.DataFrame.from_dict(answers)

for condition in status:
    q = all_models[condition][1]
    q = ["Gender", "Age"] + q
    model = all_models[condition][0]

    answer = answers[q]

    proba = model.predict_proba(answer)
    print(proba[0][1])
