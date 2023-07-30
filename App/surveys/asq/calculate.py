from math import sqrt

import pandas as pd
import plotly.graph_objects as go


def fs_multipliers():
    fs_multipliers_all = {
        "fs1": [
            0.19,
            0.48,
            0.8,
            -0.15,
            0.81,
            -0.03,
            0.86,
            0.11,
            0.53,
            0.84,
            0.18,
            0.18,
            0.2,
            0.19,
            -0.08,
            -0.01,
            -0.03,
            0.38,
            0.28,
            -0.31,
            0.29,
            -0.29,
            0.28,
            0.84,
            0.87,
            0.09,
            -0.36,
            -0.11,
            -0.33,
        ],
        "fs2": [
            0.21,
            0.4,
            0.32,
            -0.39,
            0.18,
            -0.08,
            0.28,
            0.1,
            0.27,
            0.28,
            0.05,
            0.06,
            0.04,
            0.05,
            -0.1,
            -0.18,
            -0.41,
            0.58,
            0.9,
            -0.89,
            0.9,
            -0.9,
            0.87,
            0.28,
            0.28,
            -0.11,
            -0.19,
            0.34,
            -0.24,
        ],
        "fs3": [
            0.08,
            0.07,
            0.2,
            -0.04,
            0.12,
            -0.06,
            0.22,
            -0.04,
            0.06,
            0.26,
            0.96,
            0.96,
            0.97,
            0.97,
            0,
            -0.02,
            0.01,
            0.09,
            0.04,
            -0.05,
            0.04,
            -0.04,
            0.04,
            0.26,
            0.19,
            0.05,
            -0.09,
            0,
            -0.08,
        ],
        "fs4": [
            0.2,
            0.61,
            0.15,
            -0.62,
            0.14,
            -0.02,
            0.16,
            0.84,
            0.66,
            0.17,
            0.01,
            0.01,
            0.01,
            0.01,
            -0.49,
            -0.2,
            -0.12,
            0.37,
            0.07,
            -0.13,
            0.09,
            -0.09,
            0.09,
            0.16,
            0.15,
            0.56,
            -0.23,
            -0.6,
            -0.06,
        ],
        "fs5": [
            -0.11,
            -0.04,
            -0.16,
            0.07,
            -0.06,
            0.11,
            -0.14,
            -0.1,
            -0.19,
            -0.16,
            -0.04,
            -0.04,
            -0.04,
            -0.04,
            0.02,
            0.18,
            0.16,
            -0.19,
            -0.02,
            0.05,
            -0.03,
            0.03,
            -0.07,
            -0.16,
            -0.12,
            -0.57,
            0.74,
            0.31,
            0.74,
        ],
        "fs6": [
            0.89,
            0.11,
            0.14,
            -0.21,
            -0.36,
            -0.95,
            0.13,
            -0.04,
            0.03,
            0.13,
            0.04,
            0.04,
            0.04,
            0.04,
            0.02,
            -0.1,
            0.2,
            0.1,
            0.1,
            -0.1,
            0.1,
            -0.1,
            0.12,
            0.13,
            0.13,
            0.15,
            -0.12,
            -0.14,
            -0.06,
        ],
    }
    return fs_multipliers_all


# First element in mylist has to have mean/sd in first row of asq_SD_mean.csv.
# Specify sheet name (i.e., HRV, FS)
def better_zscore(mylist, sheet_name):
    df = pd.read_excel("App/static/asq_SD_mean.xlsx", sheet_name=sheet_name)
    for counter, i in enumerate(mylist):
        SD = df["SD"][counter]
        mean = df["Mean"][counter]
        if sheet_name == "SQ" and counter == 4:  # check for sq5, see equation
            mylist[counter] = ((i * -1) - mean) / SD
        else:
            mylist[counter] = (i - mean) / SD
    return mylist


def calculate_fs(hrv_list, fs_multipliers_all):
    fs_calculated = []
    mylist = better_zscore(hrv_list, "HRV")
    for _, i in fs_multipliers_all.items():
        x = 0
        for count, n in enumerate(mylist):
            x += n * i[count]
        fs_calculated.append(x)

    return fs_calculated


def calculate_sq(fs_list):
    zscored_fs = better_zscore(fs_list, "FS")
    sq = []

    # second z-scoring
    for i in zscored_fs:
        x = sqrt(i + 4) * -1
        sq.append(x)

    zscored_sq = better_zscore(sq, "SQ")
    sq = []
    for i in zscored_sq:
        x = (i * 10) + 50
        sq.append(x)

    spiderplot(sq)  # testing spiderplot
    return sq


def calculate_asq(sq_list):
    mylist = [sum(sq_list) / 6]
    asq = better_zscore(mylist, "ASQ")
    asq = [(i * 10) + 50 for i in asq]
    return asq


def pipeline(hrv_input, fs_multipliers_all):
    fs = calculate_fs(hrv_input, fs_multipliers_all)
    sq = calculate_sq(fs)
    asq = calculate_asq(sq)
    return asq


def spiderplot(sq_list):
    # draw spiderplot
    df = pd.DataFrame(
        dict(
            r=sq_list,
            theta=["HRV-D1", "HRV-D2", "HRV-D3", "HRV-D3", "HRV-D5", "HRV-D6"],
        )
    )
    # fig = px.line_polar(df, r='r', theta='theta', line_close=True)
    fig = go.Figure()

    # change background color for different ranges
    values = [20, 10, 10, 10, 10, 10, 10]
    colors = [
        "rgba(0, 141, 25, 0.8)",
        "rgba(0, 172, 1, 0.8)",
        "rgba(38, 189, 0, 0.8)",
        "rgba(151, 229, 0, 0.8)",
        "rgba(218, 240, 0, 0.8)",
        "rgba(255, 204, 0, 1)",
        "rgba(255, 34, 0, 1)",
    ]

    for t in range(0, len(colors)):
        fig.add_trace(
            go.Barpolar(
                r=[values[t]],
                width=360,
                marker_color=[colors[t]],
                opacity=0.6,
                name="Range " + str(t + 1),
                showlegend=False,
            )
        )
        t += 1

    # add actual sq values to each sq1-6
    text = [
        i + " (" + str(round(sq_list[count], 2)) + ")"
        for count, i in enumerate(df["theta"].tolist())
    ]

    fig.add_trace(
        go.Scatterpolar(
            text=text,
            r=sq_list,
            mode="lines+text+markers",
            fill="toself",
            fillcolor="rgba(0, 0, 255, 0.4)",
            textposition="bottom center",
            marker=dict(color="blue"),
            name="Your ASQ",
        )
    )

    fig.update_layout(
        showlegend=False,
        polar=dict(angularaxis=dict(showticklabels=False)),
        font=dict(size=20),
    )

    fig.write_image("App/static/plotly_output.png", width=1000, height=1000)


def asq_definition(asq_result):
    x = ""

    asq_table = {  # Explains what ASQ means
        range(0, 20): ["Extremely High", "Emerald"],
        range(21, 30): ["High", "Dark Green"],
        range(31, 40): ["Slightly High", "Green"],
        range(41, 59): ["Average", "Light Green"],
        range(60, 69): ["Slightly Low", "Yellow"],
        range(70, 79): ["Low", "Orange"],
        range(80, 120): ["Extremely low", "Red"],
    }

    for key in asq_table:
        if int(asq_result) in key:
            x = asq_table[key]
            break

    return x
