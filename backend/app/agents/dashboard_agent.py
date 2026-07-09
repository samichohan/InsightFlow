"""
Agent 10 — Dashboard Generation Agent.
Automatically builds a KPI dashboard from the dataset.
Returns structured data the frontend renders as cards + charts.
"""

import pandas as pd
import numpy as np
import json
from app.agents.base import BaseAgent, PipelineContext
from app.core.llm_client import ask_llm


def detect_kpis(df: pd.DataFrame, dataset_name: str) -> list:
    """Auto-detect KPI columns based on common business patterns."""
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = [c for c in df.select_dtypes(include=["object"]).columns
                if "date" not in c.lower() and "id" not in c.lower()]
    date_col = next((c for c in df.columns if "date" in c.lower()), None)

    kpis = []

    # Revenue / Sales / Amount KPIs
    revenue_keywords = ["revenue", "sales", "amount", "price", "profit", "income", "earning"]
    for col in num_cols:
        if any(kw in col.lower() for kw in revenue_keywords):
            kpis.append({
                "title": f"Total {col.replace('_', ' ').title()}",
                "value": round(float(df[col].sum()), 2),
                "format": "currency",
                "icon": "dollar",
                "color": "green",
                "change": _calculate_change(df, col, date_col),
            })

    # Count KPIs
    kpis.append({
        "title": "Total Records",
        "value": len(df),
        "format": "number",
        "icon": "database",
        "color": "blue",
        "change": None,
    })

    # Unique categories
    for col in cat_cols[:2]:
        kpis.append({
            "title": f"Unique {col.replace('_', ' ').title()}",
            "value": int(df[col].nunique()),
            "format": "number",
            "icon": "tag",
            "color": "purple",
            "change": None,
        })

    # Average of key numeric columns
    for col in num_cols[:2]:
        kpis.append({
            "title": f"Avg {col.replace('_', ' ').title()}",
            "value": round(float(df[col].mean()), 2),
            "format": "number",
            "icon": "chart",
            "color": "amber",
            "change": None,
        })

    return kpis[:8]  # max 8 KPI cards


def _calculate_change(df, col, date_col) -> dict | None:
    """Calculate period-over-period change if date column exists."""
    if not date_col:
        return None
    try:
        tmp = df[[date_col, col]].dropna().copy()
        tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
        tmp = tmp.dropna().sort_values(date_col)
        monthly = tmp.groupby(tmp[date_col].dt.to_period("M"))[col].sum()
        if len(monthly) >= 2:
            prev, curr = float(monthly.iloc[-2]), float(monthly.iloc[-1])
            change_pct = round(((curr - prev) / prev) * 100, 1) if prev != 0 else 0
            return {
                "percent": change_pct,
                "direction": "up" if change_pct > 0 else "down" if change_pct < 0 else "flat",
                "label": "vs last month"
            }
    except Exception:
        pass
    return None


def build_dashboard(df: pd.DataFrame, dataset_name: str,
                    insights: list, charts: dict) -> dict:
    """Build complete dashboard data structure."""
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = [c for c in df.select_dtypes(include=["object"]).columns
                if "date" not in c.lower() and "id" not in c.lower()]

    # Top performers per category
    top_performers = {}
    if cat_cols and num_cols:
        cat_col = cat_cols[0]
        num_col = num_cols[0]
        top = df.groupby(cat_col)[num_col].sum().sort_values(ascending=False).head(5)
        top_performers = {
            "category": cat_col,
            "metric": num_col,
            "data": top.to_dict(),
        }

    # Summary statistics table
    summary_stats = {}
    for col in num_cols[:5]:
        s = df[col].dropna()
        summary_stats[col] = {
            "total": round(float(s.sum()), 2),
            "average": round(float(s.mean()), 2),
            "min": round(float(s.min()), 2),
            "max": round(float(s.max()), 2),
        }

    # AI-generated executive summary
    stats_text = json.dumps({
        "rows": len(df), "columns": len(df.columns),
        "top_performers": top_performers,
        "summary_stats": summary_stats,
    }, default=str)[:1000]

    executive_summary = ask_llm(
        "You are a senior business analyst. Generate a concise executive summary.",
        f"Dataset: {dataset_name}\nStats: {stats_text}\n\nWrite a 3-4 sentence executive summary.",
        temperature=0.3, max_tokens=300
    )

    return {
        "kpi_cards": detect_kpis(df, dataset_name),
        "top_performers": top_performers,
        "summary_stats": summary_stats,
        "executive_summary": executive_summary,
        "key_insights": (insights or [])[:4],
        "chart_keys": list(charts.keys()),
    }


class DashboardAgent(BaseAgent):
    name = "dashboard"
    max_retries = 1

    def run(self, context: PipelineContext) -> dict:
        df = context.get("dataframe")
        dataset_name = context.get("dataset_name", "dataset")
        insights = context.get("insights") or []
        charts = context.get("visualization", {}).get("interactive", {}) or {}
        return build_dashboard(df, dataset_name, insights, charts)
