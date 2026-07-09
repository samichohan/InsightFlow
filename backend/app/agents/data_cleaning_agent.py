"""Agent 1 — Data Cleaning Agent (pandas + numpy)."""

import pandas as pd
import numpy as np
import os
from app.agents.base import BaseAgent, PipelineContext
from app.core.config import settings


def analyze_quality(df: pd.DataFrame) -> dict:
    total_rows, total_cols = len(df), len(df.columns)
    missing = df.isnull().sum()

    missing_report = {
        col: {"count": int(missing[col]), "percent": round((missing[col] / total_rows) * 100, 2)}
        for col in df.columns if missing[col] > 0
    }

    duplicate_count = int(df.duplicated().sum())
    dtypes = {col: str(dt) for col, dt in df.dtypes.items()}

    # Outliers (IQR)
    outliers = {}
    for col in df.select_dtypes(include=[np.number]).columns:
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        n = int(((df[col] < q1 - 1.5*iqr) | (df[col] > q3 + 1.5*iqr)).sum())
        if n > 0:
            outliers[col] = n

    total_cells = total_rows * total_cols or 1
    total_missing = int(missing.sum())
    completeness = 100 - (total_missing / total_cells * 100)
    dup_penalty = (duplicate_count / total_rows * 100) if total_rows else 0
    quality_score = max(0, round(completeness - dup_penalty, 2))

    suggestions = []
    if missing_report:
        suggestions.append("Fill missing values: use median for numeric columns, mode for categorical.")
    if duplicate_count:
        suggestions.append(f"Remove {duplicate_count} duplicate rows using drop_duplicates().")
    if outliers:
        suggestions.append(f"Outliers detected in {list(outliers.keys())} — review or cap them.")
    if not suggestions:
        suggestions.append("Dataset is clean — no major issues found!")

    return {
        "total_rows": total_rows,
        "total_columns": total_cols,
        "data_types": dtypes,
        "missing_values": missing_report,
        "total_missing_cells": total_missing,
        "duplicate_rows": duplicate_count,
        "outliers": outliers,
        "data_quality_score": quality_score,
        "suggestions": suggestions,
    }


def clean_dataset(df: pd.DataFrame, strategy: str = "auto") -> pd.DataFrame:
    cleaned = df.drop_duplicates().copy()
    if strategy == "drop":
        return cleaned.dropna().reset_index(drop=True)
    for col in cleaned.select_dtypes(include=[np.number]).columns:
        if cleaned[col].isnull().sum() > 0:
            cleaned[col] = cleaned[col].fillna(cleaned[col].median())
    for col in cleaned.select_dtypes(include=["object", "category"]).columns:
        if cleaned[col].isnull().sum() > 0:
            mode = cleaned[col].mode()
            cleaned[col] = cleaned[col].fillna(mode[0] if not mode.empty else "Unknown")
    return cleaned.reset_index(drop=True)


def save_cleaned_csv(df: pd.DataFrame, project_id: str) -> str:
    path = os.path.join(settings.UPLOAD_DIR, f"{project_id}_cleaned.csv")
    df.to_csv(path, index=False)
    return path


class DataCleaningAgent(BaseAgent):
    name = "data_cleaning"

    def run(self, context: PipelineContext) -> dict:
        df = context.get("dataframe")
        return analyze_quality(df)
