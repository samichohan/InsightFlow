"""Agent 6 — Forecasting Agent (scikit-learn Linear/Polynomial Regression)."""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from app.agents.base import BaseAgent, PipelineContext


def forecast(df: pd.DataFrame, date_col: str, value_col: str,
             periods_ahead: int = 3, use_polynomial: bool = False) -> dict:

    tmp = df[[date_col, value_col]].dropna().copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
    tmp = tmp.dropna().sort_values(date_col)

    monthly = tmp.groupby(tmp[date_col].dt.to_period("M"))[value_col].sum().reset_index()
    monthly.columns = ["period", value_col]

    if len(monthly) < 3:
        return {"error": "Need at least 3 time periods for forecasting."}

    X = np.arange(len(monthly)).reshape(-1, 1)
    y = monthly[value_col].values

    model = (make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
             if use_polynomial else LinearRegression())
    model.fit(X, y)

    y_pred = model.predict(X)
    r2  = round(float(r2_score(y, y_pred)), 4)
    mae = round(float(mean_absolute_error(y, y_pred)), 2)
    mse = round(float(mean_squared_error(y, y_pred)), 2)

    future_X = np.arange(len(monthly), len(monthly) + periods_ahead).reshape(-1, 1)
    future_vals = np.maximum(model.predict(future_X), 0)

    last_period = monthly["period"].iloc[-1]
    future_periods = [str(last_period + i) for i in range(1, periods_ahead + 1)]

    return {
        "historical_periods": monthly["period"].astype(str).tolist(),
        "historical_values": [round(float(v), 2) for v in y],
        "forecasted_periods": future_periods,
        "forecasted_values": [round(float(v), 2) for v in future_vals],
        "model_type": "Polynomial Regression (deg 2)" if use_polynomial else "Linear Regression",
        "r2_score": r2,
        "mae": mae,
        "mse": mse,
        "accuracy_percent": round(max(0, r2) * 100, 1),
    }


class ForecastingAgent(BaseAgent):
    name = "forecasting"

    def run(self, context: PipelineContext) -> dict:
        return forecast(
            context.get("dataframe"),
            context.get("date_column"),
            context.get("value_column"),
            context.get("periods_ahead", 3),
            context.get("use_polynomial", False),
        )
