from datetime import date
import json
import numpy as np
import pandas as pd
from prefect import task
from typing import List


@task
def pre_select_features(games: pd.DataFrame) -> pd.DataFrame:
   # Select some features
    features = ['TEAM_NAME', 'GAME_ID',
                'GAME_DATE', 'PTS', 'PLUS_MINUS', 'MATCHUP']
    return games[features]


@task
def drop_few_games_teams(games: pd.DataFrame) -> pd.DataFrame:
    # Find how many games each team has played
    # And sort by the GAME_DATE
    n_games = (games.groupby('TEAM_NAME').
               agg({'TEAM_NAME': 'count'}).
               rename({'TEAM_NAME': 'N_GAMES'}, axis=1).
               reset_index())

    games = pd.merge(games, n_games, on='TEAM_NAME',
                     how='left').sort_values('GAME_DATE')
    # Exclude teams with few games
    return games[games['N_GAMES'] > 100]


@task
def add_moving_average(games: pd.DataFrame) -> pd.DataFrame:
    # Add empty line at bottom to receive moving average values
    # from previous columns
    for team in games.TEAM_NAME.unique():
        games = games.append({
            'TEAM_NAME': team,
            'GAME_DATE': date.today().strftime('%Y-%m-%d')}, ignore_index=True)

    # Filter numerical columns to not iterate over unnecessary columns
    num_cols = list(games.select_dtypes('number').columns)
    # Exclude columns you don't want to iterate over
    exclude = ['N_GAMES']
    num_cols = [col for col in num_cols if col not in exclude]
    # Add TEAM_NAME to group by it
    num_cols.append('TEAM_NAME')
    # Add moving average dinamically
    for window in [1, 5, 10, 15, 20, 25, 30, 40, 50, 60]:
        for col in num_cols:
            if col != 'TEAM_NAME':
                games[f'avg_last_{window}_{col}'] = games.groupby('TEAM_NAME')[col].transform(
                    lambda x: x.rolling(window, closed='left').mean())
    return games


@task
def separate_bottom_games(games: pd.DataFrame) -> List[pd.DataFrame]:
    # Separate Bottom Games to use them on prediction
    to_predict = games.tail(len(games.TEAM_NAME.unique()))
    print(to_predict)
    # Drop nulls (early season games and bottom ones)
    games.dropna(inplace=True)
    return [games, to_predict]


@task
def add_today_matchups(dfs: List[pd.DataFrame]) -> List[pd.DataFrame]:
    # Load matches
    with open('data/matches.json') as json_file:
        matches = json.load(json_file)
        json_file.close()
    response = []
    # Add matchup from matches file
    for i in range(len(matches['MATCHES'])):
        # Get teams names
        away_team = matches['MATCHES'][i][0]
        home_team = matches['MATCHES'][i][1]
        # filter only these two teams on the df
        teams = dfs[1].loc[dfs[1]['TEAM_NAME'].isin(
            [home_team, away_team])].copy()
        # Add fake GAME_ID to merge later
        teams['GAME_ID'] = i
        # Add matchup
        teams['MATCHUP'] = np.where(
            teams['TEAM_NAME'] == home_team,
            f'{home_team} @ {away_team}',
            f'{home_team} vs {away_team}')
        # Append to response
        response.append(teams)

    return [dfs[0], pd.concat(response)]


@task
def group_teams(dfs: List[pd.DataFrame]) -> List[pd.DataFrame]:
    response = []
    for df in dfs:
        # Home teams have '@' at matchup attribute, away teams have vs
        mask = df['MATCHUP'].str.contains('vs', na=False)
        away_teams = df[mask]
        home_teams = df[~mask]
        # Put teams side by side
        df = pd.merge(away_teams, home_teams, on=['GAME_ID', 'GAME_DATE', ], suffixes=(
            '_AWAY', '_HOME')).sort_values('GAME_DATE')
        # Append to response
        response.append(df)
    return response


@task
def create_target(dfs: List[pd.DataFrame]) -> List[pd.DataFrame]:
    response = []
    for df in dfs:
        # Create target
        # 1 FOR HOME TEAM WIN
        # O FOR AWAY TEAM WIN
        df['WINNER'] = (df['PTS_HOME'] > df['PTS_AWAY']).astype(int)
        # Remove in-game columns
        df = df.drop(['PTS_HOME', 'PTS_AWAY', 'PLUS_MINUS_HOME',
                     'PLUS_MINUS_AWAY'], axis=1)
        response.append(df)
    return response
