from tensorflow.keras.models import load_model
import pandas as pd

savedModel = load_model('model/nn_model_exp_prediction.h5')
# savedModel.summary()

input_data = pd.DataFrame([
    [0, 5],
    [1, 10],
    [0, 40],
    [1, 100],
    [1, 100],
    [1, 20],
    [1, 16],
    [1, 17],
    [0, 300],
    [1, 40]
], columns=['IS_CORRECT', 'Duration'])

predictions = savedModel.predict(input_data)

print("Data untuk prediksi:\n", input_data)
print("Hasil prediksi:\n", predictions.flatten())
