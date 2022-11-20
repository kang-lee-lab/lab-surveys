from flask import Flask, render_template, request
from math import sqrt
import pandas as pd
import os
import pickle
import pandas as pd
import plotly.graph_objects as go
from App import app

data_folder = "./static"


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/asq')
def asq():
    return render_template('asq.html')


@app.route('/nafld')
def nafld():
    return render_template('nafld.html')


@app.route('/results_asq', methods=["GET", "POST"])
def results_asq():
    MHR = request.form['MHR']
    SDHR = request.form['SDHR']
    max_RR_interval = request.form['max_RR_interval']
    min_RR_interval = request.form['min_RR_interval']
    mean_RR_interval= request.form['mean_RR_interval']
    median_RR_interval = request.form['median_RR_interval']
    SDNN = request.form['SDNN']
    NN50 = request.form['NN50']
    pNN50 = request.form['pNN50']
    RMSSD = request.form['RMSSD']
    VLF = request.form['VLF']
    LF = request.form['LF']
    HF = request.form['HF']
    total = request.form['total']
    VLF_peak = request.form['VLF_peak']
    LF_peak = request.form['LF_peak']
    HF_peak = request.form['HF_peak']
    VLF_percent = request.form['VLF_percent']
    LF_percent = request.form['LF_percent']
    HF_percent = request.form['HF_percent']
    LF_nu = request.form['LF_nu']
    HF_nu = request.form['HF_nu']
    LF_HF = request.form['LF_HF']
    SD1 = request.form['SD1']
    SD2 = request.form['SD2']
    SD1_SD2 = request.form['SD1_SD2']
    alpha = request.form['alpha']
    alpha1 = request.form['alpha1']
    alpha2 = request.form['alpha2']

    hrv_input = [
        MHR, SDHR, max_RR_interval, min_RR_interval, mean_RR_interval, median_RR_interval, SDNN, NN50, pNN50, RMSSD,
        VLF, LF, HF, total, VLF_peak, LF_peak, HF_peak, VLF_percent, LF_percent, HF_percent, LF_nu, HF_nu, LF_HF, SD1,
        SD2, SD1_SD2, alpha, alpha1, alpha2
                 ]
    hrv_input = [float(i) for i in hrv_input]

    fs_multipliers_all = {

        'fs1': [

            0.19, 0.48, 0.8, -0.15, 0.81, -0.03, 0.86, 0.11, 0.53, 0.84,
            0.18, 0.18, 0.2, 0.19, -0.08, -0.01, -0.03, 0.38, 0.28, -0.31,
            0.29, -0.29, 0.28, 0.84, 0.87, 0.09, -0.36, -0.11, -0.33

        ],

        'fs2': [

            0.21, 0.4, 0.32, -0.39, 0.18, -0.08, 0.28, 0.1, 0.27, 0.28, 0.05,
            0.06, 0.04, 0.05, -0.1, -0.18, -0.41, 0.58, 0.9, -0.89, 0.9, -0.9,
            0.87, 0.28, 0.28, -0.11, -0.19, 0.34, -0.24

        ],

        'fs3': [

            0.08, 0.07, 0.2, -0.04, 0.12, -0.06, 0.22, -0.04, 0.06, 0.26, 0.96,
            0.96, 0.97, 0.97, 0, -0.02, 0.01, 0.09, 0.04, -0.05, 0.04, -0.04,
            0.04, 0.26, 0.19, 0.05, -0.09, 0, -0.08,

        ],

        'fs4': [

            0.2, 0.61, 0.15, -0.62, 0.14, -0.02, 0.16, 0.84, 0.66, 0.17, 0.01,
            0.01, 0.01, 0.01, -0.49, -0.2, -0.12, 0.37, 0.07, -0.13, 0.09, -0.09,
            0.09, 0.16, 0.15, 0.56, -0.23, -0.6, -0.06,

        ],

        'fs5': [

            -0.11, -0.04, -0.16, 0.07, -0.06, 0.11, -0.14, -0.1, -0.19, -0.16, -0.04,
            -0.04, -0.04, -0.04, 0.02, 0.18, 0.16, -0.19, -0.02, 0.05, -0.03, 0.03,
            -0.07, -0.16, -0.12, -0.57, 0.74, 0.31, 0.74

        ],

        'fs6': [

            0.89, 0.11, 0.14, -0.21, -0.36, -0.95, 0.13, -0.04, 0.03, 0.13, 0.04, 0.04,
            0.04, 0.04, 0.02, -0.1, 0.2, 0.1, 0.1, -0.1, 0.1, -0.1, 0.12, 0.13, 0.13,
            0.15, -0.12, -0.14, -0.06

        ]

    }

    # First element in mylist has to have mean/sd in first row of SD_mean.csv. Specify sheet name (i.e., HRV, FS)

    def better_zscore(mylist, sheet_name):
        df = pd.read_excel('App/static/SD_mean.xlsx', sheet_name=sheet_name)

        for counter, i in enumerate(mylist):

            SD = df['SD'][counter]
            mean = df['Mean'][counter]

            if sheet_name == 'SQ' and counter == 4:  # check for sq5, see equation
                mylist[counter] = (((i*-1) - mean) / SD)

            else:
                mylist[counter] = ((i - mean) / SD)

        return mylist

    def calculate_fs(hrv_list):
        fs_calculated = []
        mylist = better_zscore(hrv_list, 'HRV')

        for key, i in fs_multipliers_all.items():
            x = 0

            for count, n in enumerate(mylist):
                x += n*i[count]

            fs_calculated.append(x)

        return fs_calculated

    def calculate_sq(fs_list):
        zscored_fs = better_zscore(fs_list, 'FS')
        sq = []

        # second z-scoring
        for i in zscored_fs:
            x = sqrt(i+4)*-1

            sq.append(x)

        zscored_sq = better_zscore(sq, 'SQ')
        sq = []

        for i in zscored_sq:
            x = (i*10)+50

            sq.append(x)

        spiderplot(sq)  # testing spiderplot

        return sq

    def calculate_asq(sq_list):
        mylist = [sum(sq_list)/6]

        asq = better_zscore(mylist, 'ASQ')
        asq = [(i*10)+50 for i in asq]

        return asq

    def pipeline():
        fs = calculate_fs(hrv_input)
        sq = calculate_sq(fs)
        asq = calculate_asq(sq)

        return asq

    def spiderplot(sq_list):

        # draw spiderplot

        df = pd.DataFrame(dict(
            r=sq_list,
            theta=['SQ1', 'SQ2', 'SQ3',
                   'SQ4', 'SQ5', 'SQ6']))
        # fig = px.line_polar(df, r='r', theta='theta', line_close=True)

        fig = go.Figure()

        # change background color for different ranges

        values = [20, 10, 10, 10, 10, 10, 10]
        colors = [

            'rgba(0, 141, 25, 0.8)',
            'rgba(0, 172, 1, 0.8)',
            'rgba(38, 189, 0, 0.8)',
            'rgba(151, 229, 0, 0.8)',
            'rgba(218, 240, 0, 0.8)',
            'rgba(255, 204, 0, 1)',
            'rgba(255, 34, 0, 1)'

                ]

        for t in range(0, len(colors)):
            fig.add_trace(go.Barpolar(
                r=[values[t]],
                width=360,
                marker_color=[colors[t]],
                opacity=0.6,
                name='Range ' + str(t + 1),
                showlegend=False

            ))
            t = t + 1

        fig.add_trace(go.Scatterpolar(
            text=['SQ1', 'SQ2', 'SQ3',
                   'SQ4', 'SQ5', 'SQ6'],
            r=sq_list,
            mode='lines+text+markers',
            fill='toself',
            fillcolor='rgba(0, 0, 255, 0.4)',
            textposition='bottom center',
            marker=dict(color='blue'),
            name='Your ASQ'))

        fig.update_layout(
            showlegend=False, polar = dict(angularaxis = dict(showticklabels = False)),
            font=dict(size=20)
        )

        fig.write_image('App/static/plotly_output.png', width=1000, height=1000)

    return render_template('results_asq.html', p1=round(pipeline()[0], 1))  # round value to 1 decimal


def normalize(user_inputs):
    mean_std = pd.read_csv(os.path.join(data_folder, "nafld_mean_std.csv"))
    norm = {}
    
    for inputs in user_inputs:
        if inputs != 'gender0female1male':
            mean = float(mean_std['{}_mean'.format(inputs)])
            stdev = float(mean_std['{}_stdev'.format(inputs)])
            z_scored = (user_inputs[inputs] - mean) / stdev
            
            norm[inputs+"_norm"] = [z_scored]
        else:
            norm[inputs] = [user_inputs[inputs]]
            
    return norm


@app.route('/results_nafld', methods=["GET", "POST"])
def results_nafld():
    weight = float(request.form['Weight'])
    height = float(request.form['Height'])
    bmi = weight/((height/100)**2)
    aln_atf = float(request.form['Aln_Atf'])
    hdl_chol = float(request.form['HDL_Chol'])
    fbscp5= float(request.form['FBSCP5'])
    triglycerides = float(request.form['Triglycerides'])
    dbp = float(request.form['DBP'])
    hemoglobin = float(request.form['Hemoglobin'])
    sbp = float(request.form['SBP'])
    rbcc = float(request.form['RBCC'])
    platelet = float(request.form['Platelet'])
    age = float(request.form['Age'])
    gender = int(request.form['Gender'])
    as_atf = float(request.form['As_Atf'])
    wbcc = float(request.form['WBCC'])
    lc = float(request.form['LC'])
    avg_hem = float(request.form['Avg_hem'])
    nc = float(request.form['NC'])
    ec = float(request.form['EC'])
    
    user_inputs = {
        'weight': weight,
         'bmi': bmi,
         'Alanine aminotransferase': aln_atf,
         'H cholesterol': hdl_chol,
         'fastingbloodsugar_cuttoff_5point5': fbscp5,
         'Triglycerides': triglycerides,
         'diastolic': dbp,
         'Hemoglobin': hemoglobin,
         'systolic': sbp,
         'Red blood cell count': rbcc,
         'height': height,
         'Platelet count': platelet,
         'age': age,
         'gender0female1male': gender,
         'Aspartate aminotransferase': as_atf,
         'White blood cell count': wbcc,
         'Lymphocyte count': lc,
         'The average hemoglobin concentration': avg_hem,
         'Neutrophil count': nc,
         'Eosinophil count': ec
        }
    
    inputs_norm = normalize(user_inputs)
    
    with open("./static/models_lr.bin", "rb") as f:
        all_models = pickle.load(f)
        
    model = all_models['models'][0]
    proba = model.predict_proba(pd.DataFrame.from_dict(inputs_norm)) 
    
    positive = proba[0][1] # Positive probability
    
    return render_template('results_nafld.html'), positive
