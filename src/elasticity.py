"""
Estimate log-log price elasticity per product using OLS with controls.

Outputs DataFrame columns:
- product_id, elasticity, r2, n, p_value, conf_low, conf_high
"""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from .utils import guard_log

def estimate_elasticity(df_clean: pd.DataFrame) -> pd.DataFrame:
    use_cols = ["date","product_id","units_sold","price","competitor_price","is_promo","ok_for_elasticity"]
    gdf = df_clean[use_cols].copy()
    gdf = gdf[gdf["ok_for_elasticity"] == 1].copy()

    results = []
    for pid, grp in gdf.groupby("product_id"):
        if len(grp) < 30:
            results.append({
                "product_id": pid, "elasticity": np.nan, "r2": np.nan, "n": len(grp),
                "p_value": np.nan, "conf_low": np.nan, "conf_high": np.nan
            })
            continue

        grp = grp.sort_values("date").copy()
        grp["ln_q"] = guard_log(grp["units_sold"].astype(float))
        grp["ln_p"] = guard_log(grp["price"].astype(float))
        grp["ln_comp"] = guard_log(grp["competitor_price"].astype(float))

        X = grp[["ln_p","ln_comp","is_promo"]].astype(float)
        X = sm.add_constant(X)
        y = grp["ln_q"]

        try:
            model = sm.OLS(y, X).fit()
            beta = model.params.get("ln_p", np.nan)
            r2 = model.rsquared
            pval = model.pvalues.get("ln_p", np.nan)
            if "ln_p" in model.params.index:
                ci = model.conf_int().loc["ln_p"].values
                conf_low, conf_high = float(ci[0]), float(ci[1])
            else:
                conf_low = conf_high = np.nan

            results.append({
                "product_id": pid,
                "elasticity": float(beta) if np.isfinite(beta) else np.nan,
                "r2": float(r2) if np.isfinite(r2) else np.nan,
                "n": int(len(grp)),
                "p_value": float(pval) if np.isfinite(pval) else np.nan,
                "conf_low": conf_low,
                "conf_high": conf_high
            })
        except Exception:
            results.append({
                "product_id": pid, "elasticity": np.nan, "r2": np.nan, "n": len(grp),
                "p_value": np.nan, "conf_low": np.nan, "conf_high": np.nan
            })

    return pd.DataFrame(results)
