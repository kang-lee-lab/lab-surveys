import json
import pickle

import pandas as pd
import pygal
from flask import render_template, request
from pygal.style import Style

from App import Response, app, db
from App.surveys.asq.calculate import asq_definition, fs_multipliers, pipeline
from App.surveys.nafld.run_model_nafld import normalize

data_folder = "App/static"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/in_progress")
def in_progress():
    return render_template("in_progress.html")


@app.route("/queryNafld")
def queryNafld():
    responseResults = (
        db.session.query(Response).filter(Response.response_type == "nafld").all()
    )
    data = []
    responses = []
    for response in responseResults:
        temp = []
        temp.append(response.id)
        temp.append(response.time_stamp)
        string = response.response_answers
        string = string.replace("{", "")
        string = string.replace("'", "")
        string = string.replace("}", "")
        response_list = [string.split(","), response.id]
        responses.append(response_list)

        temp.append(round(float(response.response_results), 3))
        data.append(temp)
    return render_template(
        "queryNafld.html",
        responses=responses,
        data=data,
        headings=("id", "time", "results"),
    )


@app.route("/queryASQ")
def queryASQ():
    responseResults = (
        db.session.query(Response).filter(Response.response_type == "ASQ").all()
    )
    data = []
    responses = []
    for response in responseResults:
        temp = []
        temp.append(response.id)
        temp.append(response.time_stamp)
        string = response.response_answers
        string = string.replace("{", "")
        string = string.replace("'", "")
        string = string.replace("}", "")
        response_list = [string.split(","), response.id]
        responses.append(response_list)

        temp.append(round(float(response.response_results), 3))
        data.append(temp)
    return render_template(
        "queryASQ.html",
        responses=responses,
        data=data,
        headings=("id", "time", "results"),
    )


@app.route("/queryChildBMI")
def queryChildBMI():
    responseResults = (
        db.session.query(Response).filter(Response.response_type == "childBMI").all()
    )
    data = []
    responses = []
    for response in responseResults:
        temp = []
        temp.append(response.id)
        temp.append(response.time_stamp)
        string = response.response_answers
        string = string.replace("{", "")
        string = string.replace("'", "")
        string = string.replace("}", "")
        response_list = [string.split(","), response.id]
        responses.append(response_list)
        temp.append(round(float(response.response_results), 3))
        data.append(temp)
    return render_template(
        "queryChildBMI.html",
        responses=responses,
        data=data,
        headings=("id", "time", "results"),
    )


@app.route("/queryMMPI")
def queryMMPI():
    responseResults = (
        db.session.query(Response).filter(Response.response_type == "mmpi").all()
    )
    data = []
    responses = []
    for response in responseResults:
        temp = []
        temp.append(response.id)
        temp.append(response.time_stamp)
        string = response.response_answers
        string = string.replace("{", "")
        string = string.replace("'", "")
        string = string.replace("}", "")
        response_str = response.response_results
        response_str = response_str.replace("{", "")
        response_str = response_str.replace("}", "")
        response_str = response_str.replace("'", "")
        response_list = [string.split(","), response.id]
        responses.append(response_list)
        temp.append(response_str)
        data.append(temp)
    return render_template(
        "queryMMPI.html",
        responses=responses,
        data=data,
        headings=("id", "time", "results"),
    )


@app.route("/queryDassAnxiety")
def queryDassAnxiety():
    responseResults = (
        db.session.query(Response)
        .filter(Response.response_type == "DASS_Anxiety")
        .all()
    )
    data = []
    responses = []
    for response in responseResults:
        temp = []
        temp.append(response.id)
        temp.append(response.time_stamp)
        string = response.response_answers
        string = string.replace("{", "")
        string = string.replace("'", "")
        string = string.replace("}", "")
        response_list = [string.split(","), response.id]
        responses.append(response_list)

        temp.append(float(response.response_results))
        data.append(temp)
    return render_template(
        "queryDassAnxiety.html",
        responses=responses,
        data=data,
        headings=("id", "time", "results"),
    )


@app.route("/queryDassDepression")
def queryDassDepression():
    responseResults = (
        db.session.query(Response)
        .filter(Response.response_type == "DASS_Depression")
        .all()
    )
    data = []
    responses = []
    for response in responseResults:
        temp = []
        temp.append(response.id)
        temp.append(response.time_stamp)
        string = response.response_answers
        string = string.replace("{", "")
        string = string.replace("'", "")
        string = string.replace("}", "")
        response_list = [string.split(","), response.id]
        responses.append(response_list)

        temp.append(float(response.response_results))
        data.append(temp)
    return render_template(
        "queryDassDepression.html",
        responses=responses,
        data=data,
        headings=("id", "time", "results"),
    )


@app.route("/queryDassStress")
def queryDassStress():
    responseResults = (
        db.session.query(Response)
        .filter(Response.response_type == "DASS_Anxiety")
        .all()
    )
    data = []
    responses = []
    for response in responseResults:
        temp = []
        temp.append(response.id)
        temp.append(response.time_stamp)
        string = response.response_answers
        string = string.replace("{", "")
        string = string.replace("'", "")
        string = string.replace("}", "")
        response_list = [string.split(","), response.id]
        responses.append(response_list)

        temp.append(float(response.response_results))
        data.append(temp)
    return render_template(
        "queryDassAnxiety.html",
        responses=responses,
        data=data,
        headings=("id", "time", "results"),
    )


@app.route("/asq")
def asq():
    return render_template("asq.html")


@app.route("/nafld")
def nafld():
    return render_template("nafld.html")


@app.route("/childbmi")
def childbmi():
    return render_template("childbmi.html")


@app.route("/mmpi")
def mmpi():
    return render_template("mmpi.html")


@app.route("/anxiety_moderate")
def anxiety_moderate():
    return render_template("anxiety_moderate.html")


@app.route("/depression_moderate")
def depression_moderate():
    return render_template("depression_moderate.html")


@app.route("/stress_moderate")
def stress_moderate():
    return render_template("stress_moderate.html")


@app.route("/results_asq", methods=["GET", "POST"])
def results_asq():
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
    fs_multipliers_all = fs_multipliers()
    asq_result = round(pipeline(hrv_input, fs_multipliers_all)[0], 2)

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
    results_json = json.dumps(asq_result)

    response = Response("ASQ", inputs_json, results_json)
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
    features = [
        "H cholesterol",
        "weight",
        "height",
        "Red blood cell count",
        "systolic",
        "Alanine aminotransferase",
        "The average hemoglobin concentration",
        "Triglycerides",
        "Eosinophil count",
        "diastolic",
        "Platelet count",
        "Lymphocyte count",
        "White blood cell count",
        "age",
        "Total bilirubin",
        "Cholinesterase",
        "Leucine aminopeptidase",
        "Alkaline phosphatase",
        "gender0female1male",
    ]

    user_inputs = {}

    for q in features:
        user_inputs[q] = float(request.form[q])

    user_inputs["bmi"] = user_inputs["weight"] / ((user_inputs["height"] / 100) ** 2)

    inputs_norm = normalize(user_inputs)

    with open("App/static/surveys_files/nafld/nafld_models_lr.bin", "rb") as f:
        all_models = pickle.load(f)

    model = all_models["models"][0]
    proba = model.predict_proba(pd.DataFrame.from_dict(inputs_norm))
    positive = proba[0][1]  # Positive probability

    inputs_json = json.dumps(user_inputs)
    results_json = json.dumps(positive)

    response = Response("nafld", inputs_json, results_json)
    db.session.add(response)
    db.session.commit()

    p1 = round((positive * 100), 1)

    custom_style = Style(
        value_font_size=45,
        background="transparent",
        # foreground_strong="#FFFFFF",
        font_family="googlefont:Arial",
    )

    gauge = pygal.SolidGauge(  # half_pie = True,
        inner_radius=0.70,
        show_legend=False,
        style=custom_style,
        explicit_size=True,
        height=500,
        width=500,
    )

    percent_formatter = lambda x: "{:.10g}%".format(x)
    gauge.value_formatter = percent_formatter

    gauge.add("", [{"value": p1, "min_value": 0, "max_value": 100, "color": "#0000EE"}])

    gauge.render_to_png("App/static/nafld_chart.png")

    return render_template(
        "results_nafld.html",
        p1=round((positive * 100), 1),
    )


@app.route("/results_childbmi", methods=["GET", "POST"])
def results_childbmi():
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

    with open("App/static/surveys_files/childbmi/childbmi_model_height.bin", "rb") as f:
        height_model = pickle.load(f)
        pred_height = height_model.predict(pd.DataFrame(user_inputs)).tolist()[0]
    with open("App/static/surveys_files/childbmi/childbmi_model_weight.bin", "rb") as f:
        weight_model = pickle.load(f)
        pred_weight = weight_model.predict(pd.DataFrame(user_inputs)).tolist()[0]
    with open("App/static/surveys_files/childbmi/childbmi_model_bmi.bin", "rb") as f:
        bmi_model = pickle.load(f)
        pred_bmi = bmi_model.predict(pd.DataFrame(user_inputs)).tolist()[0]

    inputs_json = json.dumps(user_inputs)
    results_json = json.dumps(pred_bmi)

    response = Response("childBMI", inputs_json, results_json)
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

    user_inputs = {}

    user_inputs["Gender"] = [int(request.form["Gender"])]
    user_inputs["Age"] = [int(request.form["Age"])]

    for q in questions:
        user_inputs["Q{}".format(q)] = [int(request.form["Q{}".format(q)])]

    user_inputs = pd.DataFrame.from_dict(user_inputs)

    with open("App/static/surveys_files/mmpi/mmpi_models.bin", "rb") as f:
        all_models = pickle.load(f)

    positive_proba = {}

    for condition in status:
        q = all_models[condition][1]
        q = ["Gender", "Age"] + q
        model = all_models[condition][0]

        answer = user_inputs[q]

        proba = model.predict_proba(answer)
        positive_proba[condition] = proba[0][1]

    inputs_json = json.dumps(user_inputs.to_dict())
    results_json = json.dumps(positive_proba)

    response = Response("mmpi", inputs_json, results_json)
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

    # Style
    custom_style = Style(
        value_font_size=32,
        background="transparent",
        font_family="googlefont:Arial",
        title_font_size=32,
    )

    # Function to create a gauge chart
    def create_gauge_chart(title, value):
        gauge = pygal.SolidGauge(
            inner_radius=0.70,
            show_legend=False,
            style=custom_style,
            explicit_size=True,
            height=500,
            width=500,
            title=title,
        )

        percent_formatter = lambda x: "{:.10g}%".format(x)
        gauge.value_formatter = percent_formatter

        gauge.add(
            "A",
            [{"value": value, "min_value": 0, "max_value": 100, "color": "#0000EE"}],
        )

        return gauge

    # Input data
    titles = [
        "Depression",
        "Hypochondriasis",
        "Hysteria",
        "Psychopathic Deviate",
        "Masculine",
        "Paranoia",
        "Psychasthenia",
        "Schizophrenia",
        "Hypomania",
        "Social Introversion",
    ]
    values = [
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

    # Create and render the charts
    for i in range(10):
        gauge = create_gauge_chart(titles[i], values[i])
        gauge.render_to_png(f"App/static/mmpi_{titles[i]}_chart.png")

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
    questions = [9, 11, 20, 30, 36, 40]

    user_inputs = {}

    user_inputs["gender"] = [int(request.form["Gender"])]
    user_inputs["region"] = [int(request.form["Region"])]
    user_inputs["age"] = [int(request.form["Age"])]

    for q in questions:
        user_inputs["Q{}A".format(q)] = [int(request.form["Q{}".format(q)])]

    user_inputs = pd.DataFrame.from_dict(user_inputs)

    with open("App/static/surveys_files/dass/anxiety_model_moderate.bin", "rb") as f:
        model = pickle.load(f)

    proba = model[0].predict_proba(user_inputs)
    positive = proba[0][1]

    inputs_json = json.dumps(user_inputs.to_dict())
    results_json = json.dumps(positive)

    response = Response("DASS_Anxiety", inputs_json, results_json)
    db.session.add(response)
    db.session.commit()

    p1 = round((positive * 100), 1)

    custom_style = Style(
        value_font_size=45,
        background="transparent",
        # foreground_strong="#FFFFFF",
        font_family="googlefont:Arial",
    )

    gauge = pygal.SolidGauge(  # half_pie = True,
        inner_radius=0.70,
        show_legend=False,
        style=custom_style,
        explicit_size=True,
        height=500,
        width=500,
    )

    percent_formatter = lambda x: "{:.10g}%".format(x)
    gauge.value_formatter = percent_formatter

    gauge.add("", [{"value": p1, "min_value": 0, "max_value": 100, "color": "#0000EE"}])

    gauge.render_to_png("App/static/anxiety_moderate_chart.png")

    return render_template(
        "results_anxiety_moderate.html", p1=round((positive * 100), 1)
    )


@app.route("/results_depression_moderate", methods=["GET", "POST"])
def results_depression_moderate():
    questions = [3, 13, 16, 22, 24, 34]

    user_inputs = {}

    user_inputs["gender"] = [int(request.form["Gender"])]
    user_inputs["region"] = [int(request.form["Region"])]
    user_inputs["age"] = [int(request.form["Age"])]

    for q in questions:
        user_inputs["Q{}A".format(q)] = [int(request.form["Q{}".format(q)])]

    user_inputs = pd.DataFrame.from_dict(user_inputs)

    with open("App/static/surveys_files/dass/depression_model_moderate.bin", "rb") as f:
        model = pickle.load(f)

    proba = model[0].predict_proba(user_inputs)
    positive = proba[0][1]

    inputs_json = json.dumps(user_inputs.to_dict())
    results_json = json.dumps(positive)

    response = Response("DASS_Depression", inputs_json, results_json)
    db.session.add(response)
    db.session.commit()

    p1 = round((positive * 100), 1)

    custom_style = Style(
        value_font_size=45,
        background="transparent",
        # foreground_strong="#FFFFFF",
        font_family="googlefont:Arial",
    )

    gauge = pygal.SolidGauge(  # half_pie = True,
        inner_radius=0.70,
        show_legend=False,
        style=custom_style,
        explicit_size=True,
        height=500,
        width=500,
    )

    percent_formatter = lambda x: "{:.10g}%".format(x)
    gauge.value_formatter = percent_formatter

    gauge.add("", [{"value": p1, "min_value": 0, "max_value": 100, "color": "#0000EE"}])

    gauge.render_to_png("App/static/depression_moderate_chart.png")

    return render_template(
        "results_depression_moderate.html", p1=round((positive * 100), 1)
    )


@app.route("/results_stress_moderate", methods=["GET", "POST"])
def results_stress_moderate():
    questions = [6, 11, 18, 27, 29]

    user_inputs = {}

    user_inputs["gender"] = [int(request.form["Gender"])]
    user_inputs["region"] = [int(request.form["Region"])]
    user_inputs["age"] = [int(request.form["Age"])]

    for q in questions:
        user_inputs["Q{}A".format(q)] = [int(request.form["Q{}".format(q)])]

    user_inputs = pd.DataFrame.from_dict(user_inputs)

    with open("App/static/surveys_files/dass/stress_model_moderate.bin", "rb") as f:
        model = pickle.load(f)

    proba = model[0].predict_proba(user_inputs)
    positive = proba[0][1]

    inputs_json = json.dumps(user_inputs.to_dict())
    results_json = json.dumps(positive)

    response = Response("DASS_Stress", inputs_json, results_json)
    db.session.add(response)
    db.session.commit()

    p1 = round((positive * 100), 1)

    custom_style = Style(
        value_font_size=45,
        background="transparent",
        # foreground_strong="#FFFFFF",
        font_family="googlefont:Arial",
    )

    gauge = pygal.SolidGauge(  # half_pie = True,
        inner_radius=0.70,
        show_legend=False,
        style=custom_style,
        explicit_size=True,
        height=500,
        width=500,
    )

    percent_formatter = lambda x: "{:.10g}%".format(x)
    gauge.value_formatter = percent_formatter

    gauge.add("", [{"value": p1, "min_value": 0, "max_value": 100, "color": "#0000EE"}])

    gauge.render_to_png("App/static/stress_moderate_chart.png")

    return render_template(
        "results_stress_moderate.html", p1=round((positive * 100), 1)
    )
