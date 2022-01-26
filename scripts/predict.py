from typing import List
from datetime import date
import pandas as pd
import pandas as pd
from prefect import task
from pycaret.classification import *


@task
def predict(dfs: List[pd.DataFrame]) -> None:
    path = 'data/predictions/'
    # Load model
    model = load_model('models/best_model')
    # Calculate score
    features = dfs[0].drop('WINNER', axis=1)
    target = dfs[0]['WINNER']
    model_score = np.round(model.score(X=features, y=target), 3)
    # Predict
    result = predict_model(model, data=dfs[1])
    # Replace label
    result['RESULT'] = np.where(result['Label'] == 1, 'home wins', 'away wins')
    # Add score
    result['MODEL_SCORE'] = model_score
    # Calculate fair odds
    result['WINNER_FAIR_ODDS'] = np.round(1/result['Score'], 3)
    # Filter columns
    result = result[['TEAM_NAME_HOME', 'TEAM_NAME_AWAY',
                     'RESULT', 'WINNER_FAIR_ODDS', 'MODEL_SCORE']]
    result.to_csv(
        f'{path}predictions_{date.today().strftime("%Y-%m-%d")}', index=False)
