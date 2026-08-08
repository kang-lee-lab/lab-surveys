"""
This file contains the functions that calculate the Average Stress
Quotient (ASQ) and Stress Quotient (SQ1-6) scores.
"""
from math import sqrt
import pandas as pd
from typing import List, Dict

def pipeline(hrv_input: List[float]) -> List[float]:
    """
    Calculates ASQ given a list of HRV values and FS multipliers.
    :param hrv_input: list of HRV values
    :return: tuple of (rounded ASQ value, formatted SQ data dict)
    """
    fs_multipliers_all = fs_multipliers()
    fs = calculate_fs(hrv_input, fs_multipliers_all)
    sq = calculate_sq(fs)
    asq = calculate_asq(sq)
    formatted_sq_data = format_sq(sq)
    rounded_asq = round(asq[0], 2)

    return rounded_asq, formatted_sq_data


def fs_multipliers():
    """
    This function returns all the multipliers for the FS scores.
    :return: list of fs multipliers
    """
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
def better_zscore(mylist: List[float], sheet_name: str) -> List[float]:
    """
    Calculates z-scores using reference population means and SDs.
    :param mylist: list of HRV/SQ/FS/ASQ values
    :param sheet_name: Sheet name (i.e., SQ, HRV, FS, ASQ)
    :return: list of z-scores
    """
    df = pd.read_excel(
        "surveys/static/survey_files/asq/asq_SD_mean.xlsx", sheet_name=sheet_name
    )
    for counter, i in enumerate(mylist):
        sd = df["SD"][counter]
        mean = df["Mean"][counter]
        mylist[counter] = (i - mean) / sd
    return mylist


def calculate_fs(
    hrv_list: List[float], fs_multipliers_all: Dict[str, List[float]]
) -> List[float]:
    """
    Calculates FS given a list of HRV values.
    :param hrv_list: list of HRV values
    :param fs_multipliers_all: dictionary of FS multipliers
    :return: list of calculated FS values
    """
    fs_calculated = []
    mylist = better_zscore(hrv_list, "HRV")
    for _, i in fs_multipliers_all.items():
        x = 0
        for count, n in enumerate(mylist):
            x += n * i[count]
        fs_calculated.append(x)

    return fs_calculated


def calculate_sq(fs_list: List[float]) -> List[float]:
    """
    Calculates SQ1-6 given a list of FS values.
    SQ_N = [Z[sqrt(Z[FS_N] + 4)] * -1] * 10 + 50  (for SQ1-4 & SQ6)
    SQ_5 = [Z[sqrt(Z[FS_5] + 4)]]       * 10 + 50
    :param fs_list: list of FS values
    :return: list of calculated SQ values
    """
    zscored_fs = better_zscore(fs_list, "FS")
    sqrt_values = [sqrt(z + 4) for z in zscored_fs]
    zscored_sq = better_zscore(sqrt_values, "SQ")

    sq = []
    for counter, z in enumerate(zscored_sq):
        if counter == 4:  # SQ5: no negation
            sq.append(z * 10 + 50)
        else:  # SQ1-4, SQ6: negate after z-scoring
            sq.append(z * -10 + 50)
    return sq


def calculate_asq(sq_list: List[float]) -> List[float]:
    """
    Calculates ASQ given a list of SQ values.
    :param sq_list: list of SQ values
    :return: list of calculated ASQ values
    """
    mylist = [sum(sq_list) / 6]
    asq = better_zscore(mylist, "ASQ")
    asq = [(i * 10) + 50 for i in asq]
    return asq

def format_sq(sq_list: List[float]) -> Dict[str, float]:
    sq_labels = ["SQ1", "SQ2", "SQ3", "SQ4", "SQ5", "SQ6"]
    return {label: sq_list[i] for i, label in enumerate(sq_labels)}