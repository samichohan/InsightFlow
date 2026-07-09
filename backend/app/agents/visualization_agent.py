"""Agent 3 — Visualization Agent (matplotlib + seaborn + plotly)."""

import os, uuid, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from app.agents.base import BaseAgent, PipelineContext
from app.core.config import settings

sns.set_style("whitegrid")

CHART_COLORS = ["#38bdf8", "#818cf8", "#34d399", "#fbbf24", "#f472b6", "#fb7185"]


def _true_cat_cols(df):
    return [c for c in df.select_dtypes(include=["object","category"]).columns
            if "date" not in c.lower() and "time" not in c.lower()]


def _save(fig, prefix: str) -> str:
    name = f"{prefix}_{uuid.uuid4().hex[:8]}.png"
    path = os.path.join(settings.CHART_DIR, name)
    fig.savefig(path, bbox_inches="tight", dpi=120)
    plt.close(fig)
    return path


# ── Static PNGs (for reports) ──────────────────────────────────────────────
def bar_chart_static(df, cat_col, num_col, top_n=10) -> str:
    data = df.groupby(cat_col)[num_col].sum().sort_values(ascending=False).head(top_n)
    fig, ax = plt.subplots(figsize=(9,5))
    sns.barplot(x=data.values, y=data.index, hue=data.index, ax=ax, palette="viridis", legend=False)
    ax.set_title(f"{num_col} by {cat_col}")
    return _save(fig, "bar")


def line_chart_static(df, date_col, num_col) -> str:
    tmp = df[[date_col, num_col]].dropna().copy()
    tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
    tmp = tmp.dropna().sort_values(date_col)
    grp = tmp.groupby(tmp[date_col].dt.to_period("M"))[num_col].sum()
    fig, ax = plt.subplots(figsize=(10,5))
    ax.plot(grp.index.astype(str), grp.values, marker="o", color="#38bdf8")
    ax.set_title(f"{num_col} Trend Over Time")
    plt.xticks(rotation=45)
    return _save(fig, "line")


def pie_chart_static(df, cat_col, top_n=6) -> str:
    counts = df[cat_col].value_counts().head(top_n)
    fig, ax = plt.subplots(figsize=(7,7))
    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%", startangle=90,
           colors=sns.color_palette("pastel"))
    ax.set_title(f"Distribution of {cat_col}")
    return _save(fig, "pie")


def histogram_static(df, col, bins=20) -> str:
    fig, ax = plt.subplots(figsize=(8,5))
    sns.histplot(df[col].dropna(), bins=bins, kde=True, ax=ax, color="#16a34a")
    ax.set_title(f"Distribution of {col}")
    return _save(fig, "hist")


def scatter_static(df, x, y) -> str:
    fig, ax = plt.subplots(figsize=(8,6))
    sns.scatterplot(data=df, x=x, y=y, ax=ax, color="#7c3aed")
    ax.set_title(f"{y} vs {x}")
    return _save(fig, "scatter")


def box_plot_static(df, num_col, cat_col=None) -> str:
    fig, ax = plt.subplots(figsize=(8,5))
    if cat_col:
        sns.boxplot(data=df, x=cat_col, y=num_col, ax=ax, palette="Set2")
        plt.xticks(rotation=45)
    else:
        sns.boxplot(y=df[num_col].dropna(), ax=ax, color="#f472b6")
    ax.set_title(f"Box Plot — {num_col}")
    return _save(fig, "box")


def heatmap_static(df) -> str | None:
    num = df.select_dtypes(include=[np.number])
    if num.shape[1] < 2:
        return None
    fig, ax = plt.subplots(figsize=(8,6))
    sns.heatmap(num.corr(), annot=True, cmap="coolwarm", center=0, fmt=".2f", ax=ax)
    ax.set_title("Correlation Heatmap")
    return _save(fig, "heatmap")


# ── Interactive Plotly (for frontend) ─────────────────────────────────────
def generate_interactive_charts(df: pd.DataFrame) -> dict:
    charts = {}
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = _true_cat_cols(df)
    date_col = next((c for c in df.columns if "date" in c.lower() or "time" in c.lower()), None)

    try:
        if cat_cols and num_cols:
            grp = df.groupby(cat_cols[0])[num_cols[0]].sum().sort_values(ascending=False).head(10)
            fig = px.bar(x=grp.values, y=grp.index, orientation="h",
                         color=grp.values, color_continuous_scale="Viridis",
                         labels={"x": num_cols[0], "y": cat_cols[0]},
                         title=f"{num_cols[0]} by {cat_cols[0]}")
            charts["bar_chart"] = json.loads(fig.to_json())
    except: pass

    try:
        if date_col and num_cols:
            tmp = df[[date_col, num_cols[0]]].dropna().copy()
            tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
            tmp = tmp.dropna().sort_values(date_col)
            grp = tmp.groupby(tmp[date_col].dt.to_period("M"))[num_cols[0]].sum()
            fig = px.line(x=grp.index.astype(str), y=grp.values, markers=True,
                          labels={"x":"Month","y":num_cols[0]}, title=f"{num_cols[0]} Trend")
            charts["line_chart"] = json.loads(fig.to_json())
    except: pass

    try:
        if cat_cols:
            counts = df[cat_cols[0]].value_counts().head(6)
            fig = px.pie(values=counts.values, names=counts.index,
                         title=f"Distribution of {cat_cols[0]}", color_discrete_sequence=CHART_COLORS)
            charts["pie_chart"] = json.loads(fig.to_json())
    except: pass

    try:
        if num_cols:
            fig = px.histogram(df, x=num_cols[0], nbins=20,
                               title=f"Distribution of {num_cols[0]}", color_discrete_sequence=["#38bdf8"])
            charts["histogram"] = json.loads(fig.to_json())
    except: pass

    try:
        if len(num_cols) >= 2:
            fig = px.scatter(df, x=num_cols[0], y=num_cols[1],
                             title=f"{num_cols[1]} vs {num_cols[0]}", color_discrete_sequence=["#818cf8"])
            charts["scatter_plot"] = json.loads(fig.to_json())
    except: pass

    try:
        if cat_cols and num_cols:
            fig = px.box(df, x=cat_cols[0], y=num_cols[0],
                         title=f"Box Plot — {num_cols[0]} by {cat_cols[0]}", color_discrete_sequence=CHART_COLORS)
            charts["box_plot"] = json.loads(fig.to_json())
    except: pass

    try:
        if len(num_cols) >= 2:
            corr = df[num_cols].corr().round(2)
            fig = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns.tolist(),
                                             y=corr.columns.tolist(), colorscale="RdBu", zmid=0,
                                             text=corr.values, texttemplate="%{text}"))
            fig.update_layout(title="Correlation Heatmap")
            charts["heatmap"] = json.loads(fig.to_json())
    except: pass

    try:
        if date_col and num_cols:
            tmp = df[[date_col, num_cols[0]]].dropna().copy()
            tmp[date_col] = pd.to_datetime(tmp[date_col], errors="coerce")
            tmp = tmp.dropna().sort_values(date_col)
            grp = tmp.groupby(tmp[date_col].dt.to_period("M"))[num_cols[0]].sum()
            fig = px.area(x=grp.index.astype(str), y=grp.values,
                          labels={"x":"Month","y":num_cols[0]}, title=f"{num_cols[0]} Area Chart",
                          color_discrete_sequence=["#34d399"])
            charts["area_chart"] = json.loads(fig.to_json())
    except: pass

    return charts


def generate_static_charts(df: pd.DataFrame) -> dict:
    charts = {}
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = _true_cat_cols(df)
    date_col = next((c for c in df.columns if "date" in c.lower() or "time" in c.lower()), None)

    if cat_cols and num_cols:
        try: charts["bar"] = bar_chart_static(df, cat_cols[0], num_cols[0])
        except: pass
    if date_col and num_cols:
        try: charts["line"] = line_chart_static(df, date_col, num_cols[0])
        except: pass
    if cat_cols:
        try: charts["pie"] = pie_chart_static(df, cat_cols[0])
        except: pass
    if num_cols:
        try: charts["histogram"] = histogram_static(df, num_cols[0])
        except: pass
    if len(num_cols) >= 2:
        try: charts["scatter"] = scatter_static(df, num_cols[0], num_cols[1])
        except: pass
    if cat_cols and num_cols:
        try: charts["box"] = box_plot_static(df, num_cols[0], cat_cols[0])
        except: pass
    if len(num_cols) >= 2:
        try:
            h = heatmap_static(df)
            if h: charts["heatmap"] = h
        except: pass

    return charts


class VisualizationAgent(BaseAgent):
    name = "visualization"

    def run(self, context: PipelineContext) -> dict:
        df = context.get("dataframe")
        interactive = generate_interactive_charts(df)
        static = generate_static_charts(df)
        context.set("static_charts", static)
        return {"interactive": interactive, "static_paths": static}
