#!/usr/bin/env python3
"""
Orchestrator for the dynamic pricing project.
Creates outputs/elasticity_results.csv, outputs/forecast_demand.csv, outputs/price_recommendations.csv
"""

import os
import pandas as pd

from src.elasticity import estimate_elasticity
from src.forecasting import forecast_per_product
from src.optimizer import recommend_prices
from src.utils import ensure_data_exists, makedirs_safely

BASE = os.path.dirname(__file__)
DATA = os.path.join(BASE, "data")
OUT = os.path.join(BASE, "outputs")

def main():
    makedirs_safely(OUT)
    # Ensure data exists (generates demo data if missing)
    ensure_data_exists(DATA)

    # Load cleaned merged data (clean_data.csv will be created by ensure_data_exists)
    clean_path = os.path.join(DATA, "clean_data.csv")
    df = pd.read_csv(clean_path, parse_dates=["date"])

    # Load product & competitor files for further use
    products = pd.read_csv(os.path.join(DATA, "products.csv"))
    comp = pd.read_csv(os.path.join(DATA, "competitor_prices.csv"), parse_dates=["date"])

    print("Estimating elasticity per product...")
    ela_df = estimate_elasticity(df)
    ela_out = os.path.join(OUT, "elasticity_results.csv")
    ela_df.to_csv(ela_out, index=False)
    print(f"Wrote: {ela_out}")

    print("Forecasting demand (30 days)...")
    fcst_df = forecast_per_product(df, horizon_days=30)
    fcst_out = os.path.join(OUT, "forecast_demand.csv")
    fcst_df.to_csv(fcst_out, index=False)
    print(f"Wrote: {fcst_out}")

    # For competitor guardrail in optimization, create a comp_future table mapping (date, product_id) to a comp price
    # Here we hold last known competitor price per product
    last_comp = (comp.sort_values(['product_id','date'])
                   .groupby('product_id').tail(1)[['product_id','competitor_price']]
                   .set_index('product_id')['competitor_price'])
    comp_future = fcst_df.copy()
    comp_future['competitor_price'] = comp_future['product_id'].map(last_comp).fillna(comp['competitor_price'].mean())
    comp_future = comp_future[['date','product_id','competitor_price']]

    print("Computing recommended prices...")
    rec_df = recommend_prices(fcst_df, products, ela_df, comp_future, min_margin=0.10, comp_delta=0.10)
    rec_out = os.path.join(OUT, "price_recommendations.csv")
    rec_df.to_csv(rec_out, index=False)
    print(f"Wrote: {rec_out}")

    print("Pipeline finished successfully.")

if __name__ == "__main__":
    main()
