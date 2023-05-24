"""Mocks product catalog dataset."""
# pylint: disable=too-many-locals
from itertools import product
from typing import Any, Dict, List

import numpy as np
import pandas as pd

# Parameters to mock product catalog.
PARAMS_JSON: List[Dict[str, Any]] = [
    # for each group all combinations of brands and categories will be generated
    # prices will be random in given range
    {
        "product_group_id": 1,
        "brand": "ASOS",
        "category_l1": "Clothes",
        "category_l2": ["Pants", "Shorts", "Jeans"],
        "price": [40, 80],
    },
    {
        "product_group_id": 2,
        "brand": "ASOS",
        "category_l1": "Clothes",
        "category_l2": ["T-shirt", "Socks", "Underwear"],
        "price": [10, 30],
    },
    {
        "product_group_id": 2,
        "brand": "ASOS",
        "category_l1": "Clothes",
        "category_l2": ["Shirts", "formal"],
        "price": [80, 120],
    },
    {
        "product_group_id": 3,
        "brand": "ASOS",
        "category_l1": "Clothes",
        "category_l2": ["Outwear", "jacket"],
        "price": [300, 350],
    },
    {
        "product_group_id": 4,
        "brand": "Nike",
        "category_l1": "Sportswear",
        "category_l2": ["Running", "Yoga", "Functional", "Football"],
        "price": [50, 80],
    },
    {
        "product_group_id": 5,
        "brand": ["Nike", "Reebok", "ASOS"],
        "category_l1": "Sportswear",
        "category_l2": ["Trainers", "Football shoes"],
        "price": [80, 500],
    },
    {
        "product_group_id": 6,
        "brand": ["Nike", "Reebok", "ASOS"],
        "category_l1": "Gifts",
        "category_l2": ["gift card", "gift basket"],
        "price": [100, 100],
    },
]


def generate_catalog() -> pd.DataFrame:
    """Create mock dataset with products that customers may bue.

    Products are groupped together. Each group has a group id.
    To simulate transactions we will use "product_group_id" instead
    of each "product_id". This means that all products in groups
    are interchangeable. Also this ease creating dataset with many products.

    Returns:
    df_catalog - size of [n_products x 1]
    """
    np.random.seed(44)

    products = PARAMS_JSON

    catalog = []
    for prod_gr in products:
        gr_id = prod_gr["product_group_id"]

        brands = prod_gr["brand"]
        brands = [brands] if isinstance(brands, str) else brands

        category_l1 = prod_gr["category_l1"]
        category_l1 = [category_l1] if isinstance(category_l1, str) else category_l1

        category_l2 = prod_gr["category_l2"]
        category_l2 = [category_l2] if isinstance(category_l2, str) else category_l2

        # create combinations of all items
        items_mult = product(brands, category_l1, category_l2)
        items = list(items_mult)
        n_items = len(items)

        price_min = min(prod_gr["price"])
        price_max = max(prod_gr["price"])
        costs = price_min + np.random.random(size=n_items) * (price_max - price_min)
        costs = [costs] if isinstance(costs, int) else costs

        for i in range(n_items):
            new_prod = list(items[i]) + [costs[i]] + [gr_id]
            catalog.append(new_prod)

    df_catalog = pd.DataFrame(catalog)
    df_catalog.columns = [
        "brand",
        "category_level1_typ",
        "category_level2_typ",
        "cost",
        "product_group_id",
    ]

    raw_index = np.ogrid[: df_catalog.shape[0]]
    df_catalog["product_id"] = 20000 + np.array(raw_index)

    return df_catalog
