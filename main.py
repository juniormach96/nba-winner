from prefect import Flow
from scripts import(
    extract as ex,
    transform as tr,
    load as ld,
    predict as pr
)


def prefect_flow():
    with Flow(name='nba_etl_pipeline') as flow:
        games = ex.extract()
        games = tr.pre_select_features(games)
        games = tr.drop_few_games_teams(games)
        dfs = tr.add_moving_average(games)
        dfs = tr.separate_bottom_games(dfs)
        dfs = tr.add_today_matchups(dfs)
        dfs = tr.group_teams(dfs)
        dfs = tr.create_target(dfs)
        ld.load(dfs=dfs,
                path='data/')
        pr.predict(dfs)
    return flow


if __name__ == '__main__':
    flow = prefect_flow()
    flow.run()
