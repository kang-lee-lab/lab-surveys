"""Define the routes for the Flask application"""

import json
from flask import render_template, request

from App import Response, app, db
from App.utils import process_response_query

from App.surveys.asq.asq_survey import (
    asq_calculate_results,
    asq_definition,
)
from App.surveys.mmpi.mmpi_survey import (
    mmpi_calculate_results,
    mmpi_questions,
    mmpi_spiderplot,
)
from App.surveys.nafld.nafld_survey import (
    nafld_calculate_results,
    nafld_features,
    nafld_chart,
)
from App.surveys.childbmi.childbmi_survey import (
    childbmi_calculate_results,
)
from App.surveys.dass.dass_survey import (
    dass_calculate_results,
    anxiety_chart,
    depression_chart,
    stress_chart,
)


@app.route("/")
def index():
    """
    Render the index page.
    :return: index.html page
    """
    return render_template("index.html")


@app.route("/in_progress")
def in_progress():
    """
    Render the in_progress page.
    :return: in_progress.html page
    """
    return render_template("in_progress.html")


@app.route("/queryNafld")
def queryNafld():
    """
    Query the database for all responses for the NAFLD survey.
    :return: queryNafld.html page
    """
    responseResults = (
        db.session.query(Response).filter(Response.response_type == "nafld").all()
    )
    responses, data = process_response_query(responseResults)
    return render_template(
        "queryNafld.html",
        responses=responses,
        data=data,
        headings=("id", "time", "results"),
    )


@app.route("/queryASQ")
def queryASQ():
    """
    Query the database for all responses for the ASQ survey.
    :return: queryASQ.html page
    """
    responseResults = (
        db.session.query(Response).filter(Response.response_type == "ASQ").all()
    )
    responses, data = process_response_query(responseResults)
    return render_template(
        "queryASQ.html",
        responses=responses,
        data=data,
        headings=("id", "time", "results"),
    )


@app.route("/queryChildBMI")
def queryChildBMI():
    """
    Query the database for all responses for the Child BMI survey.
    :return: queryChildBMI.html page
    """
    responseResults = (
        db.session.query(Response).filter(Response.response_type == "childBMI").all()
    )
    responses, data = process_response_query(responseResults)
    return render_template(
        "queryChildBMI.html",
        responses=responses,
        data=data,
        headings=("id", "time", "results"),
    )


@app.route("/queryMMPI")
def queryMMPI():
    """
    Query the database for all responses for the MMPI survey.
    :return: queryMMPI.html page
    """
    responseResults = (
        db.session.query(Response).filter(Response.response_type == "mmpi").all()
    )
    responses, data = process_response_query(responseResults, True)
    return render_template(
        "queryMMPI.html",
        responses=responses,
        data=data,
        headings=("id", "time", "results"),
    )


@app.route("/queryDassAnxiety")
def queryDassAnxiety():
    """
    Query the database for all responses for the DASS Anxiety survey.
    :return: queryDassAnxiety.html page
    """
    responseResults = (
        db.session.query(Response)
        .filter(Response.response_type == "DASS_Anxiety")
        .all()
    )
    responses, data = process_response_query(responseResults)
    return render_template(
        "queryDassAnxiety.html",
        responses=responses,
        data=data,
        headings=("id", "time", "results"),
    )


@app.route("/queryDassDepression")
def queryDassDepression():
    """
    Query the database for all responses for the DASS Depression survey.
    :return: queryDassDepression.html page
    """
    responseResults = (
        db.session.query(Response)
        .filter(Response.response_type == "DASS_Depression")
        .all()
    )
    responses, data = process_response_query(responseResults)
    return render_template(
        "queryDassDepression.html",
        responses=responses,
        data=data,
        headings=("id", "time", "results"),
    )


@app.route("/queryDassStress")
def queryDassStress():
    """
    Query the database for all responses for the DASS Stress survey.
    :return: queryDassStress.html page
    """
    responseResults = (
        db.session.query(Response)
        .filter(Response.response_type == "DASS_Anxiety")
        .all()
    )
    responses, data = process_response_query(responseResults)
    return render_template(
        "queryDassAnxiety.html",
        responses=responses,
        data=data,
        headings=("id", "time", "results"),
    )


@app.route("/asq")
def asq():
    """
    Renders the asq survey page.
    :return: asq.html page
    """
    return render_template("asq.html")


@app.route("/nafld")
def nafld():
    """
    Renders the nafld survey page.
    :return: nafld.html page
    """
    return render_template("nafld.html")


@app.route("/childbmi")
def childbmi():
    """
    Renders the childbmi survey page.
    :return: childbmi.html page
    """
    return render_template("childbmi.html")


@app.route("/mmpi")
def mmpi():
    """
    Renders the mmpi survey page.
    :return: mmpi.html page
    """
    return render_template("mmpi.html")


@app.route("/anxiety_moderate")
def anxiety_moderate():
    """
    Renders the Depression Anxiety Stress Scales survey (moderate anxiety) page.
    :return: anxiety_moderate.html page
    """
    return render_template("anxiety_moderate.html")


@app.route("/depression_moderate")
def depression_moderate():
    """
    Renders the Depression Anxiety Stress Scales survey (moderate depression) page.
    :return: depression_moderate.html page
    """
    return render_template("depression_moderate.html")


@app.route("/stress_moderate")
def stress_moderate():
    """
    Renders the Depression Anxiety Stress Scales survey (moderate stress) page.
    :return: stress_moderate.html page
    """
    return render_template("stress_moderate.html")


@app.route("/results_asq", methods=["GET", "POST"])
def results_asq():
    """
    Renders the results page for the ASQ survey.
    :return: asq_results.html page
    """
    MHR = request.form["MHR"]
    SDHR = request.form["SDHR"]
    max_RR_interval = request.form["max_RR_interval"]
    min_RR_interval = request.form["min_RR_interval"]
    mean_RR_interval = request.form["mean_RR_interval"]
    median_RR_interval = request.form["median_RR_interval"]
    SDNN = request.form["SDNN"]
    NN50 = request.form["NN50"]
    pNN50 = request.form["pNN50"]
    RMSSD = request.form["RMSSD"]
    VLF = request.form["VLF"]
    LF = request.form["LF"]
    HF = request.form["HF"]
    total = request.form["total"]
    VLF_peak = request.form["VLF_peak"]
    LF_peak = request.form["LF_peak"]
    HF_peak = request.form["HF_peak"]
    VLF_percent = request.form["VLF_percent"]
    LF_percent = request.form["LF_percent"]
    HF_percent = request.form["HF_percent"]
    LF_nu = request.form["LF_nu"]
    HF_nu = request.form["HF_nu"]
    LF_HF = request.form["LF_HF"]
    SD1 = request.form["SD1"]
    SD2 = request.form["SD2"]
    SD1_SD2 = request.form["SD1_SD2"]
    alpha = request.form["alpha"]
    alpha1 = request.form["alpha1"]
    alpha2 = request.form["alpha2"]

    hrv_input = [
        MHR,
        SDHR,
        max_RR_interval,
        min_RR_interval,
        mean_RR_interval,
        median_RR_interval,
        SDNN,
        NN50,
        pNN50,
        RMSSD,
        VLF,
        LF,
        HF,
        total,
        VLF_peak,
        LF_peak,
        HF_peak,
        VLF_percent,
        LF_percent,
        HF_percent,
        LF_nu,
        HF_nu,
        LF_HF,
        SD1,
        SD2,
        SD1_SD2,
        alpha,
        alpha1,
        alpha2,
    ]
    hrv_input = [float(i) for i in hrv_input]
    results, metadata, asq_result = asq_calculate_results(hrv_input)

    features = [
        "MHR",
        "SDHR",
        "max_RR_interval",
        "min_RR_interval",
        "mean_RR_interval",
        "median_RR_interval",
        "SDNN",
        "NN50",
        "pNN500",
        "RMSSDD",
        "VLF",
        "LF",
        "HF",
        "totall",
        "VLF_peakpeak",
        "LF_peakeak",
        "HF_peakeak",
        "VLF_percentpercent",
        "LF_percentercent",
        "HF_percentercent",
        "LF_nuu",
        "HF_nuu",
        "LF_HFF",
        "SD1",
        "SD2",
        "SD1_SD2SD2",
        "alphaa",
        "alpha1a1",
        "alpha2",
    ]

    user_inputs = {}

    for q in range(len(features)):
        user_inputs[features[q]] = float(hrv_input[q])

    inputs_json = json.dumps(user_inputs)

    response = Response("ASQ", inputs_json, results)
    db.session.add(response)
    db.session.commit()

    return render_template(
        "results_asq.html",
        p1=asq_result,  # Round value to 2 decimals
        p2=asq_definition(asq_result)[0],
        p3=asq_definition(asq_result)[1],
    )


@app.route("/results_nafld", methods=["GET", "POST"])
def results_nafld():
    """
    Renders the results page for the NAFLD survey.
    :return: results_nafld.html page
    """
    features = nafld_features()

    user_inputs = {}

    for q in features:
        user_inputs[q] = float(request.form[q])

    user_inputs["bmi"] = user_inputs["weight"] / ((user_inputs["height"] / 100) ** 2)
    results, metadata, positive = nafld_calculate_results(user_inputs)
    inputs_json = json.dumps(user_inputs)

    response = Response("nafld", inputs_json, results)
    db.session.add(response)
    db.session.commit()

    nafld_chart(positive)

    return render_template(
        "results_nafld.html",
        p1=round((positive * 100), 1),
    )


@app.route("/results_childbmi", methods=["GET", "POST"])
def results_childbmi():
    """
    Renders the results page for the childbmi survey.
    :return: results_childbmi.html page
    """
    age = float(request.form["Age"])
    age1 = float(request.form["Age1"])
    gender = int(request.form["Gender"])
    weight = float(request.form["Weight"])
    height = float(request.form["Height"])
    bmi = weight / ((height / 100) ** 2)

    user_inputs = {
        "Current age": [age],
        "Age to predict": [age1],
        "Sex": [gender],
        "Height": [height],
        "Weight": [weight],
        "BMI": [bmi],
    }

    results, metadata, pred_height, pred_weight, pred_bmi = childbmi_calculate_results(
        user_inputs
    )
    inputs_json = json.dumps(user_inputs)

    response = Response("childBMI", inputs_json, results)
    db.session.add(response)
    db.session.commit()

    return render_template(
        "results_childbmi.html",
        height=round(pred_height, 1),
        weight=round(pred_weight, 1),
        bmi=round(pred_bmi, 1),
        age=int(age1),
    )


@app.route("/results_mmpi", methods=["GET", "POST"])
def results_mmpi():
    """
    Renders the results page for the MMPI survey.
    :return: results_mmpi.html page
    """
    questions = mmpi_questions()

    user_inputs = {
        "Gender": [int(request.form["Gender"])],
        "Age": [int(request.form["Age"])],
    }

    for q in questions:
        user_inputs["Q{}".format(q)] = [int(request.form["Q{}".format(q)])]

    results, metadata, positive_proba = mmpi_calculate_results(user_inputs)
    inputs_json = json.dumps(user_inputs)

    response = Response("mmpi", inputs_json, results)
    db.session.add(response)
    db.session.commit()

    Depression = round(positive_proba["DT"] * 100, 1)
    Hypochondriasis = round(positive_proba["HsT"] * 100, 1)
    Hysteria = round(positive_proba["HyT"] * 100, 1)
    Psychopathic_Deviate = round(positive_proba["PdT"] * 100, 1)
    Masculinity_Femininity = round(positive_proba["MfT"] * 100, 1)
    Paranoia = round(positive_proba["PaT"] * 100, 1)
    Psychasthenia = round(positive_proba["PtT"] * 100, 1)
    Schizophrenia = round(positive_proba["ScT"] * 100, 1)
    Hypomania = round(positive_proba["MaT"] * 100, 1)
    Social_Introversion = round(positive_proba["SiT"] * 100, 1)

    # Input MMPI data
    mmpi_input = [
        Depression,
        Hypochondriasis,
        Hysteria,
        Psychopathic_Deviate,
        Masculinity_Femininity,
        Paranoia,
        Psychasthenia,
        Schizophrenia,
        Hypomania,
        Social_Introversion,
    ]

    mmpi_spiderplot(mmpi_input)

    return render_template(
        "results_mmpi.html",
        Depression=round(positive_proba["DT"] * 100, 1),
        Hypochondriasis=round(positive_proba["HsT"] * 100, 1),
        Hysteria=round(positive_proba["HyT"] * 100, 1),
        Psychopathic_Deviate=round(positive_proba["PdT"] * 100, 1),
        Masculinity_Femininity=round(positive_proba["MfT"] * 100, 1),
        Paranoia=round(positive_proba["PaT"] * 100, 1),
        Psychasthenia=round(positive_proba["PtT"] * 100, 1),
        Schizophrenia=round(positive_proba["ScT"] * 100, 1),
        Hypomania=round(positive_proba["MaT"] * 100, 1),
        Social_Introversion=round(positive_proba["SiT"] * 100, 1),
    )


@app.route("/results_anxiety_moderate", methods=["GET", "POST"])
def results_anxiety_moderate():
    """
    This function gets the user input from the DASS
    (moderate anxiety) survey and returns the results.
    :return: results_anxiety_moderate.html template
    """

    questions = [9, 11, 20, 30, 36, 40]

    user_inputs = {
        "gender": [int(request.form["Gender"])],
        "region": [int(request.form["Region"])],
        "age": [int(request.form["Age"])],
    }

    for q in questions:
        user_inputs["Q{}A".format(q)] = [int(request.form["Q{}".format(q)])]

    results, metadata, positive = dass_calculate_results(user_inputs, "anxiety")
    inputs_json = json.dumps(user_inputs)

    response = Response("DASS_Anxiety", inputs_json, results)
    db.session.add(response)
    db.session.commit()

    anxiety_chart(positive)

    return render_template(
        "results_anxiety_moderate.html", p1=round((positive * 100), 1)
    )


@app.route("/results_depression_moderate", methods=["GET", "POST"])
def results_depression_moderate():
    """
    This function gets the user input from the DASS
    (moderate depression) survey and returns the results.
    :return: results_depression_moderate.html template
    """
    questions = [3, 13, 16, 22, 24, 34]

    user_inputs = {
        "gender": [int(request.form["Gender"])],
        "region": [int(request.form["Region"])],
        "age": [int(request.form["Age"])],
    }

    for q in questions:
        user_inputs["Q{}A".format(q)] = [int(request.form["Q{}".format(q)])]

    results, metadata, positive = dass_calculate_results(user_inputs, "depression")
    inputs_json = json.dumps(user_inputs)

    response = Response("DASS_Depression", inputs_json, results)
    db.session.add(response)
    db.session.commit()

    depression_chart(positive)

    return render_template(
        "results_depression_moderate.html", p1=round((positive * 100), 1)
    )


@app.route("/results_stress_moderate", methods=["GET", "POST"])
def results_stress_moderate():
    """
    This function gets the user input from the DASS
    (moderate stress) survey and returns the results.
    :return: results_stress_moderate.html template
    """
    questions = [6, 11, 18, 27, 29]

    user_inputs = {
        "gender": [int(request.form["Gender"])],
        "region": [int(request.form["Region"])],
        "age": [int(request.form["Age"])],
    }

    for q in questions:
        user_inputs["Q{}A".format(q)] = [int(request.form["Q{}".format(q)])]

    results, metadata, positive = dass_calculate_results(user_inputs, "stress")
    inputs_json = json.dumps(user_inputs)

    response = Response("DASS_Stress", inputs_json, results)
    db.session.add(response)
    db.session.commit()

    stress_chart(positive)

    return render_template(
        "results_stress_moderate.html", p1=round((positive * 100), 1)
    )
