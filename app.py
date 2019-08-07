import json
import pandas as pd
import numpy as np
import pickle

from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.utils import to_categorical

from flask import Flask, render_template, url_for, request

from notebooks.model_predict import predictor
from notebooks.scrapper_pred import live_scrapper

# Create app
app = Flask(__name__)

# Home route
@app.route('/')
def index():
    '''Return the homepage.'''
    return render_template('index.html')

# Route for prediction webpage 
@app.route('/prediction')
def index_pred():
    '''Return prediction webpage.'''
    return render_template('prediction.html')

# Route to retrieve league info from prediction.html and return prediction results
@app.route('/league', methods=['POST'])
def matches_request():

    # Retrieve league info
    league = request.form['league']

    # For leagues other than MLS, data are from randomly selected week of matches in 2018/2019 season as new season has not started
    if league != "MLS":

        data = pd.read_csv(f'data/{league}_S2018-2019_testweek.csv')

        # ONLY USE THE FOLLOWING FIVE LINES OF CODES LOCALLY WHERE RF MODELS ARE AVAILABLE AND ARE BEING USED 
        # # Save odds data from 12Bet (for PremierLeague save those from WilliamHill as well)
        # if league == "PremierLeague":
        #     data = data.loc[(data["company"] == "12Bet") | (data["company"] == "WilliamHill"), :].reset_index()
        # else:
        #     data = data.loc[data["company"] == "12Bet", :].reset_index()

        data = data.loc[data["company"] == "12Bet", :].reset_index()

    # For ongoing MLS, data are lively scrapped
    else:
        # Live scraping MLS data
        data = live_scrapper(league)

    # List to store predicted result for every odds record
    pred = []
    # Make prediction through all odds records
    for i in range(len(data)):
        pred.append(predictor(league, data.company[i], [[data.win_odds[i], data.draw_odds[i],\
            data.lose_odds[i], data.odds_delta_time[i]]]))

    # Save prediction results in "data"
    data["pred"] = pred

    # Remove unnecessary columns
    data = data[["home", "away", "company", "pred", "result"]]

    # Dict to store match info
    matches_dict = {}

    for company in ["12Bet", "WilliamHill"]:
        # Grab all data that uses iterated company's odds
        data_ana = data.loc[data["company"] == company, :].reset_index()
        
        for i in range(len(data_ana.home.unique())):
            matches_dict[f'match{i}'] = {}
            # Single match
            match_pred = data_ana.loc[data_ana["home"] == data_ana.home.unique()[i], :]
            # Counts of predicted results for iterated home team
            pred_ct = match_pred.pred.value_counts()

            matches_dict[f'match{i}']['League'] = league
            matches_dict[f'match{i}']['Company'] = company
            matches_dict[f'match{i}']['Home'] = data_ana.home.unique()[i]
            matches_dict[f'match{i}']['Away'] = data_ana.away.unique()[i]
            matches_dict[f'match{i}']['Result'] = match_pred.result.unique()[0]

            for j in range(len(pred_ct.keys())):
                # Change datatype from np.int64 to int to be JSON serializable
                matches_dict[f'match{i}'][f'Pred_{pred_ct.keys()[j]} (ct)'] = int(pred_ct.values[j])

    # Return "matches_dict" to "prediction.html"    
    return render_template('prediction.html', matches=matches_dict)

# Run app
if __name__ == "__main__":
    app.run(debug=True)   