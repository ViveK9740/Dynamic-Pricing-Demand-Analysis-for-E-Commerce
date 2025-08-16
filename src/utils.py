"""
Utility functions: data generation (if missing), basic helpers.
"""
import os
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

def makedirs_safely(path):
    os.makedirs(path, exist_ok=True)

def guard_log(x, floor=1e-6):
    return np.log(np.clip(x, floor, None))

def recent_or_mean(series, window=14):
    s = series.dropna()
    if len(s) == 0:
        return 0.0
    return float(s.tail(window).mean())

def ensure_data_exists(data_dir: str):
    """
    If expected data files are missing, generate synthetic demo data and create clean_data.csv.
    Writes: products.csv, sales_history.csv, competitor_prices.csv, clean_data.csv to data_dir.
    """
    makedirs_safely(data_dir)
    products_path = os.path.join(data_dir, "products.csv")
    sales_path = os.path.join(data_dir, "sales_history.csv")
    comp_path = os.path.join(data_dir, "competitor_prices.csv")
    clean_path = os.path.join(data_dir, "clean_data.csv")

    # If clean_data already exists, assume prior step done
    if os.path.exists(clean_path) and os.path.exists(products_path):
        return

    # If any of the core CSVs missing, generate synthetic dataset
    if not (os.path.exists(products_path) and os.path.exists(sales_path) and os.path.exists(comp_path)):
        print("Missing input files — generating synthetic demo data...")
        _generate_synthetic(products_path, sales_path, comp_path)

    # Merge and create clean_data.csv
    print("Merging and preparing clean_data.csv...")
    products = pd.read_csv(products_path)
    sales = pd.read_csv(sales_path, parse_dates=["date"])
    comp = pd.read_csv(comp_path, parse_dates=["date"])

    df = (sales.merge(comp, on=["date","product_id"], how="left")
              .merge(products, on="product_id", how="left"))

    # Basic feature engineering
    df["is_promo"] = df["is_promo"].astype(int)
    df["is_stockout"] = df["is_stockout"].astype(int)
    df["price"] = df["price"].astype(float)
    df["competitor_price"] = df["competitor_price"].astype(float)
    df["base_cost"] = df["base_cost"].astype(float)

    df["revenue"] = (df["price"] * df["units_sold"]).round(2)
    df["margin"] = ((df["price"] - df["base_cost"]) * df["units_sold"]).round(2)

    df["date"] = pd.to_datetime(df["date"])
    df["dow"] = df["date"].dt.dayofweek
    df["is_weekend"] = (df["dow"] >= 5).astype(int)
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year

    # Rolling / lagging
    df = df.sort_values(["product_id","date"]).copy()
    df["lag1_units"] = df.groupby("product_id")["units_sold"].shift(1)
    df["lag7_units"] = df.groupby("product_id")["units_sold"].shift(7)
    df["roll7_units_mean"] = df.groupby("product_id")["units_sold"].rolling(7, min_periods=1).mean().reset_index(level=0, drop=True)
    df["roll14_units_mean"] = df.groupby("product_id")["units_sold"].rolling(14, min_periods=1).mean().reset_index(level=0, drop=True)

    # Flag usable rows for elasticity
    df["ok_for_elasticity"] = ((df["is_stockout"] == 0) & (df["units_sold"] > 0)).astype(int)

    df.to_csv(clean_path, index=False)
    print(f"Saved clean data to: {clean_path}")

def _generate_synthetic(products_path, sales_path, comp_path):
    """
    Generate simple synthetic data sets for demo purposes.
    """
    np.random.seed(42)
    n_days = 240
    n_products = 30
    start = pd.Timestamp("2024-12-01")
    dates = pd.date_range(start, periods=n_days, freq="D")

    categories = ["Electronics","Home & Kitchen","Beauty","Sports","Books"]
    brands = ["Astra","Novac","Zephyr","Lumio","Kairo","Vanta"]

    products = []
    for pid in range(1, n_products+1):
        base_cost = float(np.round(np.random.uniform(50, 1500),2))
        base_price = float(np.round(base_cost * np.random.uniform(1.15,1.6),2))
        products.append({
            "product_id": pid,
            "product_name": f"Prod {pid}",
            "category": np.random.choice(categories),
            "brand": np.random.choice(brands),
            "base_cost": base_cost,
            "base_price": base_price
        })
    pd.DataFrame(products).to_csv(products_path, index=False)

    sales_rows = []
    comp_rows = []
    for p in products:
        pid = p["product_id"]
        cost = p["base_cost"]
        base_price = p["base_price"]
        comp_price = base_price * np.random.uniform(0.9, 1.05)
        price = base_price
        for d in dates:
            # small random walk on prices
            comp_price += np.random.normal(0, base_price*0.002)
            price += 0.2*(comp_price - price) + np.random.normal(0, base_price*0.001)
            price = max(price, cost*1.1)
            comp_price = max(comp_price, cost*1.05)
            promo = int(np.random.rand() < 0.06)
            stockout = int(np.random.rand() < 0.02)
            # simple demand model
            mean_q = np.clip(20 + (np.random.randn()*2) + (promo*10), 0, None)
            qty = int(np.random.poisson(mean_q)) if not stockout else 0
            sales_rows.append({
                "date": d.date().isoformat(),
                "product_id": pid,
                "price": float(round(price,2)),
                "is_promo": promo,
                "is_stockout": stockout,
                "units_sold": qty,
                "revenue": round(price*qty,2),
                "margin": round((price - cost)*qty,2)
            })
            comp_rows.append({
                "date": d.date().isoformat(),
                "product_id": pid,
                "competitor_price": float(round(comp_price,2))
            })
    pd.DataFrame(sales_rows).to_csv(sales_path, index=False)
    pd.DataFrame(comp_rows).to_csv(comp_path, index=False)
