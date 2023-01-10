import pickle
import os
import pandas as pd

data_folder = "./static"

def z_score_norm(row, col, mean, stdev):
    z_score = (float(row[col]) - mean) / stdev
    return float(z_score)


def normalize(user_inputs):
    mean_std = pd.read_csv(os.path.join(data_folder, "nafld_mean_std.csv"))
    
    for col in user_inputs:
        if col != 'gender0female1male':
            mean = float(mean_std['{}_mean'.format(col)])
            stdev = float(mean_std['{}_stdev'.format(col)])
            user_inputs["{}_norm".format(col)] = user_inputs.apply(
                        lambda row: z_score_norm(row, col, mean, stdev), axis=1)
            user_inputs = user_inputs.drop([col], axis=1)
        
    return user_inputs
            
    
def run_model(model_type, user_inputs):
    '''
    Runs the specified model to generate the likelihood of NAFLD.
    It will normalize the user input using z score with mean and standard
    deviation of the data from NAFLD_filtered.csv.

    Parameters
    ----------
    model_type : Type of model ('lr', 'rf', 'svm', 'xgb', 'mlp', 'nb')
    user_inputs : pandas dataframe containing the user's input for their 
                  biomarkers in the 20 top features of NAFLD.

    Returns
    -------
    Probability of being positive in NAFLD

    '''
    with open("./static/models/nafld_models_{}.bin".format(model_type), "rb") as f:
        all_models = pickle.load(f)
        
    model = all_models['models'][0]
    
    normalized = normalize(user_inputs)
    proba = model.predict_proba(normalized)
    predicted_label = model.predict(normalized)
    
    return proba, predicted_label


if __name__ == "__main__":
    nafld_data = pd.read_csv(os.path.join(data_folder, "NAFLD_filtered.csv"))
    valid_features = ['weight', 'bmi', 'Alanine aminotransferase', 'H cholesterol', 'fastingbloodsugar_cuttoff_5point5', 'Triglycerides', 'diastolic', 'Hemoglobin', 'systolic', 'Red blood cell count', 'height', 'Platelet count', 'age', 'gender0female1male', 'Aspartate aminotransferase', 'White blood cell count', 'Lymphocyte count', 'The average hemoglobin concentration', 'Neutrophil count', 'Eosinophil count']
    inputs = nafld_data[valid_features]
    inputs = inputs.dropna()
    
    proba, label = run_model('lr', inputs)
    print('Positive probability: ', proba[0][1])
    