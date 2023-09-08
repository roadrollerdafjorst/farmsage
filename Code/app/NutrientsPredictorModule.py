import warnings
import joblib
import pandas as pd
import numpy as np
warnings.filterwarnings('ignore')

# Load models
model_p = joblib.load('models/rf_P-v1.pkl')
model_k = joblib.load('models/rf_K-v1.pkl')
model_n = joblib.load('models/rf_N-v1.pkl')

mapping = pd.read_csv("data/mapped_crops.csv")
mapping = dict(zip(mapping['Crops'], mapping['Key']))
# print(mapping)

def nutrients_predictor(crop, temp, humidity, rainfall, y_label):
    regressor = None
    
    if y_label == 'Label_N':
        regressor = model_n
    elif y_label == 'Label_P':
        regressor = model_p
    else:
        regressor = model_k
    
    try:    
        query = [mapping[crop.strip().lower()], temp, humidity, rainfall]
        y_pred = regressor.predict([query])
        y_pred = list(np.round(y_pred, 2))
        return y_pred[0]
    
    except Exception as msg:
        print("nutrients_predictor():", msg)
        return -1


# sample_result = nutrients_predictor('rice', 30, 80, 100, 'Label_N')
# print(sample_result)