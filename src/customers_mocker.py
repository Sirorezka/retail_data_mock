"""Mocks customer profile dataset."""
# pylint: disable=too-many-locals
from typing import Any, Dict

import numpy as np
import pandas as pd

# Parameters to mock customer profile dataset.
PARAMS_JSON: Dict[str, Any] = {
    # date on which customers database was collected
    # in ideal world you don't see any customers registered after BASE_DT
    "base_date": "2023-04-01",
    "n_customers": 10000,
    "registration_dt": ["2020-01-01", "2023-04-01"],
    "age": [20, 60],
    "gender_cd": {"Male": 0.2, "Female": 0.4, "Other": 0.2, np.nan: 0.1},
    # randomization seed
    "seed": 401,
}


def generate_customers() -> pd.DataFrame:
    """Mock customer profile dataset.

    Return:
    df_customers - size of [n_customers x 1]
    """
    params = PARAMS_JSON

    base_date = params["base_date"]
    n_new_cust = params["n_customers"]
    seed = params["seed"]
    np.random.seed(seed)

    # generate customer id
    raw_idx = np.ogrid[0:n_new_cust]
    customer_id = np.array(raw_idx)

    # generate registration date
    reg_max = max(params["registration_dt"])
    reg_min = min(params["registration_dt"])
    reg_diff = (pd.to_datetime(reg_max) - pd.to_datetime(reg_min)).days

    arr = np.random.randint(0, reg_diff + 1, size=n_new_cust)
    reg_dates = pd.to_datetime(reg_min) + arr * pd.Timedelta(days=1)
    reg_dates = pd.to_datetime(reg_dates).strftime("%Y-%m-%d")

    # generate age
    age_max = max(params["age"])
    age_min = min(params["age"])
    ages_arr = age_min + (age_max - age_min) * np.random.rand(n_new_cust)

    cur_date = pd.to_datetime(base_date)
    birth_date = pd.to_datetime(cur_date) - ages_arr * 365 * pd.Timedelta(days=1)
    birth_date = pd.to_datetime(birth_date).strftime("%Y-%m-%d")

    # gender
    vals = [x for x, y in params["gender_cd"].items()]
    weights = [y for x, y in params["gender_cd"].items()]
    # normalize weights to probs
    probs = np.array(weights) / sum(weights)

    gender_arr = np.random.choice(vals, size=n_new_cust, p=probs)

    df_customers = pd.DataFrame(
        {
            "customer_id": customer_id + 30000,
            "gender_cd": gender_arr,
            "registration_dt": reg_dates,
            "birthdate_dt": birth_date,
            "base_dt": base_date,
        }
    )

    filt = df_customers["base_dt"] < df_customers["registration_dt"]
    df_customers.loc[filt, "registration_dt"] = None

    return df_customers
