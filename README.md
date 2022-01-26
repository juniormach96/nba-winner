# NBA Winner

NBA Winner is a ETL Process to forecast winner from NBA matches.

## Installation

### Pre-Requisites
* Python >= 3.6
* Git


1. Create a folder and Clone the github repository into it

```bash
https://github.com/juniormach96/nba-winner
```
2. Create a virtual environment to isolate dependencies
```bash
python -m venv .venv
```
3. Access it

    3.1. Windows PowerShell:
    ```bash
    .venv\Scripts\Activate.ps1
    ```
    3.2. MAC OS/Linux:
    ```bash
    source venv/bin/activate
    ```
4. Install the dependencies
```bash
pip install -r requirements.txt
```


## Usage

1. Enter the names of the teams that you want to predict the matches in the file "data/matches.json", following the file format: the first name is for the away team, the second for the home team.
```bash
# data/matches.json example
{
    "MATCHES":[
       [
          "Away Team",
          "Home Team"
       ]
}
```

2. Type the following command on the terminal
```bash
python main.py
```
This will trigger the pipeline and generate a csv file at "data/predictions" with predictions from the games you've selected.

 TEAM_NAME_HOME | TEAM_NAME_AWAY | RESULT    | WINNER_FAIR_ODDS | MODEL_SCORE |
|----------------|----------------|-----------|------------------|-------------|
| Home Team      | Away Team      | home wins | 1.833            | 0.6         |

## Project Structure
```
.
├── data
│   ├── predictions              
│   │   ├──predictions.csv    # Predictions of the day
│   ├── games.csv             # Games used to train the model
│   ├── matches.json          # Teams names provided by the user
│   ├── to_predict.csv        # Games with matches of the day
├── models                    
│   ├── best_model.pkl        # Machine Learning model
├── scripts
│   ├── extract.py            # Requests games from NBA API
│   ├── load.py               # Stores games into ../data/ folder
│   ├── transform.py          # Process games
│   ├── predict.py            # Predicts new matches
├── main.py
├── requirements.txt          # Dependencies
├── train_ml.py               # Trains a new Machine Learning model
```

## Challenges
Unlikely soccer, home team is listed on the right. This caused some misinterpretations during predicting new games.

## Technologies
* NBA API: extract the data;
* Pandas: clean and process it;
* Pycaret: creates a machine learning model;
* Prefect: orchestrates ETL process
## Future Improvements
* Add SQL server;
* Add tests;
* Optimize workflow to not carry all the data through all the functions;
* Take into account days since last game;
* Dynamically scrap matches of the day.

## License
[MIT](https://choosealicense.com/licenses/mit/)
