"""
Price recommendation engine.

Given:
- forecast_df: columns [date, product_id, forecast_units]
- products_df: product catalog with base_cost, base_price
- elasticity_df: per-product elasticity estimates (elasticity column)
- comp_ref: DataFrame(date, product_id, competitor_price) for reference

Returns DataFrame:
[date, product_id, recommended_price, expected_profit, baseline_units, elasticity_used, comp_price_ref]
"""
import numpy as np
import pandas as pd

def profit_for_price(p, cost, q0, p0, beta):
    # q(p) = q0 * (p/p0)^beta ; profit = (p - cost) * q(p)
    q = q0 * (p / p0) ** beta if p0 > 0 else q0
    return (p - cost) * q

def recommend_prices(forecast_df: pd.DataFrame, products_df: pd.DataFrame, elasticity_df: pd.DataFrame,
                     comp_ref: pd.DataFrame, min_margin: float = 0.10, comp_delta: float = 0.10) -> pd.DataFrame:

    prod = products_df.set_index("product_id")
    ela = elasticity_df.set_index("product_id") if len(elasticity_df) > 0 else pd.DataFrame()
    # index comp_ref by (date, product_id) for quick lookup
    comp_idx = comp_ref.set_index(["date","product_id"]) if (len(comp_ref) > 0 and "date" in comp_ref and "product_id" in comp_ref) else pd.DataFrame()

    recs = []
    for _, row in forecast_df.iterrows():
        pid = int(row["product_id"])
        date = row["date"]
        q0 = float(row["forecast_units"])
        # product details
        if pid not in prod.index:
            continue
        cost = float(prod.loc[pid, "base_cost"])
        p0 = float(prod.loc[pid, "base_price"])
        beta = -1.0  # default elasticity
        if pid in ela.index and pd.notna(ela.loc[pid, "elasticity"]):
            beta = float(ela.loc[pid, "elasticity"])

        # bounds
        low = cost * (1.0 + min_margin)
        high = p0 * 1.8
        comp_price = None
        if not comp_idx.empty and (date, pid) in comp_idx.index:
            comp_price = float(comp_idx.loc[(date, pid), "competitor_price"])
            low = max(low, comp_price * (1 - comp_delta))
            high = min(high, comp_price * (1 + comp_delta))

        if high <= low:
            # degenerate case, set to low
            grid = np.array([low])
        else:
            grid = np.linspace(low, high, 60)

        best_p = grid[0]
        best_profit = -np.inf
        for p in grid:
            pi = profit_for_price(p, cost, q0, p0, beta)
            if pi > best_profit:
                best_profit = pi
                best_p = p

        recs.append({
            "date": date,
            "product_id": pid,
            "recommended_price": round(float(best_p), 2),
            "expected_profit": round(float(best_profit), 2),
            "baseline_units": round(q0, 3),
            "elasticity_used": round(beta, 3) if pd.notna(beta) else None,
            "comp_price_ref": round(comp_price, 2) if comp_price is not None and not np.isnan(comp_price) else None
        })

    return pd.DataFrame(recs)
