"""Generate items purchased information for each customer transaction."""
import numpy as np
import pandas as pd

from src import baskets_mocker


# pylint: disable-msg=too-many-locals
def generate_items(
    buyers_ids_arr: np.ndarray, purch_dates_arr: np.ndarray, df_catalog: pd.DataFrame
) -> pd.DataFrame:
    """Given array with purchase dates for each customer assigns items bought.

    [buyers_ids_arr, purch_dates_arr] - define all existing baskets:

    Args:
        buyers_ids_arr: array of customers_ids (one 'id' per purchase)
        purch_dates_arr: array of purchase dates (one 'date' per purchase)
        df_catalog: dataset with products, size = [cnt_products x 1]
    """
    params = baskets_mocker.PARAMS_JSON

    # Generate baskets
    return_prob = params["transactions"]["return_prob"]
    exchange_prob = params["transactions"]["exchange_prob"]
    items_cnt = params["transactions"]["items_cnt"]
    items_groups = params["transactions"]["items_groups"]

    # who will buy smth
    buyer_ids = buyers_ids_arr
    n_cust = buyers_ids_arr.shape[0]

    # generate basket ids
    items_min = min(items_cnt)
    items_max = max(items_cnt)

    basket_size = np.random.randint(items_min, items_max + 1, size=n_cust)

    raw_indx = np.ogrid[:n_cust]
    basket_id = np.array(raw_indx)

    basket_id = np.repeat(basket_id, repeats=basket_size)
    buyer_ids = np.repeat(buyer_ids, repeats=basket_size)
    dates_arr = np.repeat(purch_dates_arr, repeats=basket_size)

    # item group
    group_ids = [g for g, p in items_groups.items()]
    group_weights = [p for g, p in items_groups.items()]
    group_probs = np.array(group_weights) / np.sum(group_weights)
    tot_items = np.sum(basket_size)

    item_group = np.random.choice(group_ids, size=tot_items, p=group_probs)
    prods_map = df_catalog.groupby("product_group_id")["product_id"].agg(list).to_dict()

    items_array = np.vectorize(lambda x: np.random.choice(prods_map.get(x, [-1])))(
        item_group
    )

    flag_return = np.random.random(size=tot_items) < return_prob
    flag_exchange = np.random.random(size=tot_items) < exchange_prob

    df_trans = pd.DataFrame(
        {
            "basket_id": basket_id,
            "transaction_dt": dates_arr,
            "product_id": items_array,
            "customer_id": buyer_ids,
            "transaction_type": "purchase",
            "product_qty": 1,
            "return_qty": 0,
        }
    )

    df_trans = df_trans.merge(
        df_catalog[["product_id", "cost"]], how="left", on="product_id"
    )

    df_trans.rename(columns={"cost": "final_net_sales"}, inplace=True)

    filt = flag_return & (~flag_exchange)
    df_trans.loc[filt, "transaction_type"] = "return"
    df_trans.loc[filt, "return_qty"] = 1

    df_exchange = df_trans.loc[flag_exchange].copy()
    df_exchange["transaction_type"] = "exchange"
    df_exchange["product_qty"] = 1
    df_exchange["return_qty"] = 1
    df_exchange["final_net_sales"] = 0

    df_trans = pd.concat([df_trans, df_exchange], axis=0, ignore_index=True)

    return df_trans
