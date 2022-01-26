import pandas as pd
from prefect import task
from typing import List


@task
def load(dfs: List[pd.DataFrame], path: str) -> None:
    # Games
    dfs[0].to_csv(f'{path}games', index=False)
    # To predict
    dfs[1].to_csv(f'{path}to_predict', index=False)
