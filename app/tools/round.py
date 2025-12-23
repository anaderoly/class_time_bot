import numpy as np
import pandas as pd


def stable_round(s: pd.Series, p: int) -> pd.Series:
    dec = 10**p
    floor = np.floor(s * dec) / dec
    rest = int(round((s.sum() - floor.sum()) * dec))

    if rest > 0:
        floor.iloc[np.argsort(s - floor, kind="stable")[-rest:]] += 1/dec

    return floor