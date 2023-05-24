"""Mocks transactional data for retail usecase."""
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd

# Parameters to mock customer purchase behaviour.
PARAMS_JSON: Dict[str, Any] = {
    "lifetime_years": [0.5, 2.5],
    #
    "first_trans": {
        "no_trans": 0.1,  # registered, but not transacted
        "lost_perc": 0.5,  # leave after first transaction
        # made first transaction and registered in the same day
        "reg_purch_prob": 0.6,
        "month_after_reg": [0, 3],
    },
    "transactions": {
        "freq_cnt": [3, 10],  # per year
        "return_prob": 0.05,
        "exchange_prob": 0.05,
        # items per basket
        "items_cnt": [1, 5],
        # format
        # {item_group_id: weight/probability, ...}
        "items_groups": {1: 100, 2: 100, 3: 100, 4: 100, 5: 100, 6: 10},
    },
}


# pylint: disable-msg=too-many-locals
def generate_transactions(
    df_customers: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Parameters to mock customer purchase behaviour.

    Returns:
        purch_dates_full: list of dates when purchases were made
                          (can have duplicates if two customers bought on a same date).
                          size = [n_total_baskets x 1]
        buyers_ids_full:  list of corresponding customers for each purchase.
                          i.e. each date from 'purch_dates_full'
                          will have a corresponding customer id.
                          size = [n_total_baskets x 1]
    """
    np.random.seed(332)

    params = PARAMS_JSON

    customer_id = df_customers["customer_id"].values
    n_cust = customer_id.shape[0]

    reg_dates = df_customers["registration_dt"].values
    reg_dates = pd.Series(pd.to_datetime(reg_dates))

    # Flag that customer will register but won't transact
    notrans_prob = params["first_trans"]["no_trans"]
    no_first_trans_flag = np.random.random(size=n_cust) <= notrans_prob

    #  Dealing with first transaction
    #

    reg_purch_prob = params["first_trans"]["reg_purch_prob"]
    reg_arr = np.random.random(size=n_cust) <= reg_purch_prob

    months_min = min(params["first_trans"]["month_after_reg"])
    months_max = max(params["first_trans"]["month_after_reg"])

    months_arr = months_min + (months_max - months_min) * np.random.random(size=n_cust)
    months_arr[reg_arr] = 0

    first_trans_date = reg_dates + months_arr * pd.Timedelta(days=30)

    # purchase date
    active_date = first_trans_date.copy()
    active_date[no_first_trans_flag] = None

    # first purchase
    buyers_tr1_ids = customer_id[active_date.notna()].copy()
    purch_tr1_date = active_date[active_date.notna()].copy()

    # who will leave after first transaction
    lost_perc = params["first_trans"]["lost_perc"]
    no_second_trans_flag = np.random.random(size=n_cust) <= lost_perc

    # lost after first trans
    active_date[no_second_trans_flag] = None

    # Subsequent transactions:

    # lifetime in months
    life_max = 12 * max(params["lifetime_years"])
    life_min = 12 * min(params["lifetime_years"])
    lifetime_months = life_min + (life_max - life_min) * np.random.rand(n_cust)
    last_date = reg_dates + lifetime_months * pd.Timedelta(days=30)

    freq_min = min(params["transactions"]["freq_cnt"])
    freq_max = max(params["transactions"]["freq_cnt"])
    freq_arr = np.random.randint(freq_min, freq_max + 1, size=customer_id.shape[0])

    buyers_ids_full = [buyers_tr1_ids]
    purch_dates_full = [purch_tr1_date.dt.strftime("%Y-%m-%d")]

    n_active = 1

    while n_active > 0:
        # print(n_active, end=" " * 100 + "\r")
        n_active = active_date.notna().sum()

        filt_active = active_date.notna()
        delta_mm = np.random.exponential(1 / freq_arr[filt_active], size=n_active)
        active_date[filt_active] = active_date[filt_active] + delta_mm * pd.Timedelta(
            days=365
        )
        active_date[active_date > last_date] = None

        buyers_tr = customer_id[active_date.notna()].copy()
        purch_date = active_date[active_date.notna()].copy()

        buyers_ids_full.append(buyers_tr)
        purch_dates_full.append(purch_date.dt.strftime("%Y-%m-%d"))

    buyers_ids_full = np.concatenate(buyers_ids_full)
    purch_dates_full = np.concatenate(purch_dates_full)

    return (buyers_ids_full, purch_dates_full)
