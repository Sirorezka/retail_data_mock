"""Data mocker that simulates customer behaviour."""

import os

from src import baskets_mocker, catalog_mocker, customers_mocker, items_mocker

# this is an example in which order you should call each function


def main():
    """Pipeline that generates all mocked datasets."""
    output_dir: str = "mocked_data"

    # product catalog
    df_catalog = catalog_mocker.generate_catalog()

    # customers databse
    df_customers = customers_mocker.generate_customers()

    # transactions
    (buyers_ids_arr, purch_dates_arr) = baskets_mocker.generate_transactions(
        df_customers
    )
    df_trans = items_mocker.generate_items(buyers_ids_arr, purch_dates_arr, df_catalog)

    # saving all outputs in the parquet
    file_catalog = os.path.join(output_dir, "product_catalog.parquet")
    df_catalog.to_parquet(file_catalog)

    file_trans = os.path.join(output_dir, "transactions.parquet")
    df_trans.to_parquet(file_trans)

    file_customers = os.path.join(output_dir, "customers.parquet")
    df_customers.to_parquet(file_customers)

    print("Mocked Data generated")


if __name__ == "__main__":
    main()
