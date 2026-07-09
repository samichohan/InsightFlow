"""Agent 2 — Exploratory Data Analysis Agent (pandas + numpy)."""

import pandas as pd
import numpy as np
from app.agents.base import BaseAgent, PipelineContext


def descriptive_stats(df: pd.DataFrame) -> dict:
    stats = {}
    for col in df.select_dtypes(include=[np.number]).columns:
        s = df[col].dropna()
        if s.empty:
            continue
        mode = s.mode()
        stats[col] = {
            "mean": round(float(s.mean()), 2),
            "median": round(float(s.median()), 2),
            "mode": round(float(mode[0]), 2) if not mode.empty else None,
            "std": round(float(s.std()), 2),
            "variance": round(float(s.var()), 2),
            "min": round(float(s.min()), 2),
            "max": round(float(s.max()), 2),
            "range": round(float(s.max() - s.min()), 2),
            "skewness": round(float(s.skew()), 3),
            "kurtosis": round(float(s.kurt()), 3),
        }
    return stats


def correlation_matrix(df: pd.DataFrame) -> dict:
    num = df.select_dtypes(include=[np.number])
    if num.shape[1] < 2:
        return {}
    return num.corr().round(3).to_dict()


def strong_correlations(df: pd.DataFrame, threshold: float = 0.6) -> list:
    num = df.select_dtypes(include=[np.number])
    if num.shape[1] < 2:
        return []
    corr = num.corr()
    pairs = []
    cols = corr.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            v = corr.iloc[i, j]
            if pd.notna(v) and abs(v) >= threshold:
                pairs.append({
                    "col1": cols[i], "col2": cols[j],
                    "correlation": round(float(v), 3),
                    "type": "positive" if v > 0 else "negative"
                })
    return sorted(pairs, key=lambda x: abs(x["correlation"]), reverse=True)


def category_distribution(df: pd.DataFrame) -> dict:
    cat_cols = [c for c in df.select_dtypes(include=["object", "category"]).columns
                if "date" not in c.lower() and "time" not in c.lower()]
    return {col: df[col].value_counts().head(10).to_dict() for col in cat_cols}


def unique_values(df: pd.DataFrame) -> dict:
    return {col: int(df[col].nunique()) for col in df.columns}


def run_full_eda(df: pd.DataFrame) -> dict:
    return {
        "descriptive_stats": descriptive_stats(df),
        "correlation_matrix": correlation_matrix(df),
        "strong_correlations": strong_correlations(df),
        "category_distribution": category_distribution(df),
        "unique_values": unique_values(df),
        "numeric_columns": df.select_dtypes(include=[np.number]).columns.tolist(),
        "categorical_columns": df.select_dtypes(include=["object", "category"]).columns.tolist(),
    }


class EDAAgent(BaseAgent):
    name = "eda"

    def run(self, context: PipelineContext) -> dict:
        return run_full_eda(context.get("dataframe"))
