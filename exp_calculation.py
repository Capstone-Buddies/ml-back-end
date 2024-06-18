from tensorflow.keras.models import load_model
import pandas as pd
import numpy as np

model = load_model('model/nn_model_exp_prediction.h5')


def calculate_exp(data):
    data = pd.DataFrame(data, columns=['IS_CORRECT', 'Duration'])
    exp = model.predict(data)
    expTotal = np.sum(exp.flatten())
    return expTotal
