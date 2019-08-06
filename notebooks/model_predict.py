import pandas as pd
import numpy as np
import pickle

from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical

# Note that instant_feature is in 2D format of [["win_odds", "draw_odds", "lose_odds", "odds_delta_time"]]
def predictor(league, company, instant_features):

    # Load "X_scaler"
    X_scalerfile = f"models/X-scaler_{league}.sav"
    X_scaler = pickle.load(open(X_scalerfile, 'rb'))
    # Load "target_encoder"
    y_scalerfile = 'models/target-encoder.sav'
    target_encoder = pickle.load(open(y_scalerfile, 'rb'))

    # Path to model
    # All leagues shpold be using RF models
    # KNN models are used here for html demo purposes as RF models are too large to be uploaded to Github
    model_path = f"models/{league}_{company}_knn.pkl"    

    # Load ML model from disk
    model = pickle.load(open(model_path, 'rb'))

    # Scale the instant features
    X_scaled = X_scaler.transform(instant_features)

    # Make prediction
    y_pred = model.predict(X_scaled)
    # Convert "y_pred" to categorical match result
    result_pred = target_encoder.inverse_transform(np.argmax(y_pred, axis=-1))

    # Return predicted result(s) of "W", "D", and "L" (result is in 2D format)
    return result_pred[0][0]