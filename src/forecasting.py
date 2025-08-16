"""
Forecast units_sold per product for next N days using SARIMAX with exogenous regressors.

The function returns DataFrame with columns: date (ISO), product_id, forecast_units
"""
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
from .utils import recent_or_mean

def forecast_per_product(df_clean: pd.DataFrame, horizon_days: int = 30) -> pd.DataFrame:
    out = []
    for pid, g in df_clean.groupby("product_id"):
        g = g.sort_values("date").copy()
        y = g["units_sold"].astype(float)
        exog = g[["price","competitor_price","is_promo"]].astype(float)

        # fallback to mean if very few points
        if len(g) < 60 or y.sum() == 0:
            mean_q = float(y.mean())
            future_dates = pd.date_range(g["date"].max() + pd.Timedelta(days=1), periods=horizon_days, freq="D")
            for d in future_dates:
                out.append({"date": d.date().isoformat(), "product_id": int(pid), "forecast_units": mean_q})
            continue

        order = (1,0,0)
        seasonal_order = (1,0,0,7)  # weekly seasonality
        try:
            model = SARIMAX(y, order=order, seasonal_order=seasonal_order, exog=exog,
                            enforce_stationarity=False, enforce_invertibility=False)
            res = model.fit(disp=False, method="powell", maxiter=50)
        except Exception:
            # fallback mean
            mean_q = float(y.mean())
            future_dates = pd.date_range(g["date"].max() + pd.Timedelta(days=1), periods=horizon_days, freq="D")
            for d in future_dates:
                out.append({"date": d.date().isoformat(), "product_id": int(pid), "forecast_units": mean_q})
            continue

        future_dates = pd.date_range(g["date"].max() + pd.Timedelta(days=1), periods=horizon_days, freq="D")
        f_price = recent_or_mean(g["price"])
        f_comp = recent_or_mean(g["competitor_price"])
        f_exog = pd.DataFrame({
            "price": [f_price]*horizon_days,
            "competitor_price": [f_comp]*horizon_days,
            "is_promo": [0]*horizon_days
        })

        try:
            pred = res.get_forecast(steps=horizon_days, exog=f_exog).predicted_mean
            for d, q in zip(future_dates, pred):
                out.append({"date": d.date().isoformat(), "product_id": int(pid), "forecast_units": max(float(q), 0.0)})
        except Exception:
            mean_q = float(y.mean())
            for d in future_dates:
                out.append({"date": d.date().isoformat(), "product_id": int(pid), "forecast_units": mean_q})

    return pd.DataFrame(out)
