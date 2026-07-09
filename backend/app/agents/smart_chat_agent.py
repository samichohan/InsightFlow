"""
agents/smart_chat_agent.py — AI Data Copilot

The most advanced agent in the system. Features:
1. INTELLIGENT AGENT ROUTING — auto-decides which agent to use
2. COLUMN AUTO-DETECT — if user asks about "price" but column is "revenue", maps it
3. CONVERSATION MEMORY — last 10 messages remembered (follow-up questions work)
4. LANGUAGE AUTO-DETECT — replies in user's language (English/Urdu/Hindi/Hinglish)
5. STREAMING SUPPORT — word by word output (used by /chat/stream endpoint)
6. CHART GENERATION FROM CHAT — "show me a bar chart" generates a chart inline
7. SQL + PANDAS EXECUTION — real data operations, not hallucinated answers
"""

import json
import re
import pandas as pd
import numpy as np
from app.core.llm_client import ask_llm, ask_llm_stream
from app.core.logging_config import logger

# ── Agent Router Prompt ────────────────────────────────────────────────────
ROUTER_PROMPT = """You are an AI assistant routing engine. Based on the user's message,
decide which agent/action to use. Return ONLY one of these exact strings:

- sql        → user wants to query/filter data (show top 10, filter by, list where)
- pandas     → user wants calculations/aggregations (average, sum, group by, compare)
- chart      → user wants a visualization (show chart, plot, visualize, bar chart, pie)
- forecast   → user wants predictions (predict, forecast, next month, future)
- clean      → user wants data cleaning (remove duplicates, fill missing, clean)
- insights   → user wants AI business insights or analysis summary
- recommend  → user wants recommendations or suggestions
- report     → user wants to generate a report or download
- general    → general question about the dataset (what columns, how many rows, describe)
"""

# ── Main Chat Prompt ───────────────────────────────────────────────────────
CHAT_SYSTEM_PROMPT = """You are an expert AI Data Analyst Copilot. You have access
to the user's dataset and can answer any question about it.

Key Rules:
1. LANGUAGE: Auto-detect user's language. If they write in Urdu/Hindi/Hinglish,
   reply in that language. Default is English.
2. ACCURACY: Only use exact numbers from the provided data context. Never guess.
3. COLUMN MAPPING: If user asks about a column that doesn't exist, find the closest
   matching column and answer using that (e.g., "price" → "revenue" if no price column).
4. THOROUGHNESS: Give complete, detailed answers with specific numbers (2-5 sentences).
5. FOLLOW-UPS: Remember conversation history for context-aware replies.
6. SUGGESTIONS: After answering, suggest 2-3 relevant follow-up questions.

Format your response as:
ANSWER: [your detailed answer here]
FOLLOW_UPS: [question1] | [question2] | [question3]
"""


def detect_language(text: str) -> str:
    """Simple language detection based on character sets."""
    urdu_chars = set("ابتثجحخدذرزسشصضطظعغفقکگلمنوہیءآاة")
    hindi_chars = set("अआइईउऊएऐओऔकखगघचछजझटठडढणतथदधनपफबभमयरलवशषसहक")

    char_set = set(text)
    if char_set & urdu_chars:
        return "urdu"
    if char_set & hindi_chars:
        return "hindi"

    # Roman Urdu detection (common words)
    roman_urdu = ["kya", "hai", "mujhe", "mera", "meri", "kitna", "kaisa",
                  "batao", "bata", "kar", "karo", "wala", "wali", "ke", "se",
                  "me", "bhai", "yaar", "chalte"]
    words = text.lower().split()
    if sum(1 for w in words if w in roman_urdu) >= 2:
        return "hinglish"

    return "english"


def find_closest_column(asked_col: str, available_cols: list) -> str | None:
    """
    Column auto-detect — maps user's column name to actual dataset column.
    Example: user says 'price' but dataset has 'revenue' → returns 'revenue'
    """
    asked_lower = asked_col.lower().replace(" ", "_")

    # Exact match first
    for col in available_cols:
        if col.lower() == asked_lower:
            return col

    # Keyword synonyms mapping
    synonyms = {
        "price": ["revenue", "amount", "cost", "sales", "price", "value", "income"],
        "revenue": ["revenue", "sales", "income", "amount", "price", "earning"],
        "sales": ["sales", "revenue", "amount", "income", "units_sold", "quantity"],
        "profit": ["profit", "revenue", "income", "earning", "margin"],
        "customer": ["customer", "client", "user", "buyer", "name"],
        "product": ["product", "item", "category", "name", "sku"],
        "date": ["date", "time", "order_date", "created_at", "timestamp"],
        "quantity": ["quantity", "units", "amount", "count", "qty", "units_sold"],
        "category": ["category", "type", "segment", "group", "class"],
        "region": ["region", "area", "location", "city", "state", "country"],
        "age": ["age", "years", "dob"],
        "salary": ["salary", "wage", "income", "pay", "compensation"],
    }

    # Check if asked column has a known synonym
    asked_keywords = asked_lower.split("_")
    for keyword in asked_keywords:
        if keyword in synonyms:
            for synonym in synonyms[keyword]:
                for col in available_cols:
                    if synonym in col.lower():
                        return col

    # Partial match
    for col in available_cols:
        if asked_lower in col.lower() or col.lower() in asked_lower:
            return col

    return None


def build_data_context(df: pd.DataFrame, question: str) -> str:
    """Build a rich data context string for the LLM."""
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = [c for c in df.select_dtypes(include=["object"]).columns
                if "date" not in c.lower()]
    date_col = next((c for c in df.columns if "date" in c.lower()), None)

    # Pre-calculate relevant aggregations
    aggregations = {}
    for cat in cat_cols[:3]:
        for num in num_cols[:3]:
            try:
                grp = df.groupby(cat)[num].agg(["sum", "mean", "count"]).round(2)
                aggregations[f"{num}_by_{cat}"] = grp.head(10).to_dict()
            except:
                pass

    # Overall stats
    overall = {}
    for col in num_cols[:5]:
        s = df[col].dropna()
        overall[col] = {
            "total": round(float(s.sum()), 2),
            "mean": round(float(s.mean()), 2),
            "min": round(float(s.min()), 2),
            "max": round(float(s.max()), 2),
            "count": int(s.count()),
        }

    context = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "numeric_columns": num_cols,
        "categorical_columns": cat_cols,
        "date_column": date_col,
        "overall_statistics": overall,
        "aggregations_by_category": aggregations,
        "sample_data": df.head(3).to_dict(orient="records"),
    }

    return json.dumps(context, default=str, indent=2)


def route_to_agent(question: str) -> str:
    """Determine which agent to use based on the question."""
    q_lower = question.lower()

    # Chart keywords
    chart_kw = ["chart", "plot", "graph", "visualize", "visualization", "show me",
                 "bar chart", "pie chart", "line chart", "histogram", "scatter"]
    if any(kw in q_lower for kw in chart_kw):
        return "chart"

    # Forecast keywords
    forecast_kw = ["predict", "forecast", "future", "next month", "next year",
                   "estimate", "projection", "trend prediction"]
    if any(kw in q_lower for kw in forecast_kw):
        return "forecast"

    # SQL keywords
    sql_kw = ["top", "bottom", "filter", "where", "show records", "list",
              "find records", "get rows", "select", "show me records"]
    if any(kw in q_lower for kw in sql_kw):
        return "sql"

    # Pandas/calculation keywords
    pandas_kw = ["average", "total", "sum", "count", "group by", "compare",
                 "highest", "lowest", "maximum", "minimum", "calculate",
                 "aggregate", "per category", "by region", "by month"]
    if any(kw in q_lower for kw in pandas_kw):
        return "pandas"

    # Cleaning keywords
    clean_kw = ["clean", "remove duplicate", "fill missing", "drop null",
                "handle outlier", "fix data"]
    if any(kw in q_lower for kw in clean_kw):
        return "clean"

    # Report keywords
    report_kw = ["generate report", "create report", "download report",
                 "export report", "make report"]
    if any(kw in q_lower for kw in report_kw):
        return "report"

    # Insight keywords
    insight_kw = ["insight", "analysis", "analyze", "summary", "overview",
                  "tell me about", "explain", "describe dataset"]
    if any(kw in q_lower for kw in insight_kw):
        return "insights"

    # Recommendation keywords
    rec_kw = ["recommend", "suggestion", "what should", "advice",
              "improvement", "strategy"]
    if any(kw in q_lower for kw in rec_kw):
        return "recommend"

    return "general"


def process_chat_message(
    df: pd.DataFrame,
    question: str,
    dataset_name: str,
    conversation_history: list = None,
    pre_computed: dict = None,
) -> dict:
    """
    Main chat processing function.
    Returns: {answer, agent_used, chart_data, follow_ups, language}
    """
    language = detect_language(question)
    agent_type = route_to_agent(question)
    chart_data = None
    additional_data = None

    logger.info(f"Chat routing → agent: {agent_type}, language: {language}")

    # ── Column auto-detection ────────────────────────────────────────────
    # Extract potential column names from question and map to actual columns
    available_cols = list(df.columns)
    column_mapping_note = ""

    # Find any word in question that looks like a column reference
    words = re.findall(r'\b[a-z_]+\b', question.lower())
    for word in words:
        if len(word) > 3:  # skip short words
            mapped = find_closest_column(word, available_cols)
            if mapped and mapped.lower() != word:
                column_mapping_note = f"Note: '{word}' was interpreted as column '{mapped}'. "
                break

    # ── Agent-specific processing ────────────────────────────────────────
    if agent_type == "sql":
        from app.agents.sql_agent import nl_to_sql, execute_sql_on_df
        sql = nl_to_sql(question, available_cols, df.head(3).to_dict(orient="records"))
        result = execute_sql_on_df(df, sql)
        if "error" not in result:
            additional_data = result
            context_for_llm = f"SQL Result: {json.dumps(result, default=str)[:800]}"
        else:
            context_for_llm = build_data_context(df, question)

    elif agent_type == "pandas":
        from app.agents.pandas_agent import nl_to_pandas_code, execute_pandas_code
        dtypes = {col: str(dt) for col, dt in df.dtypes.items()}
        code = nl_to_pandas_code(question, available_cols, dtypes, df.head(2).to_dict(orient="records"))
        result = execute_pandas_code(df, code)
        if "error" not in result:
            additional_data = result
            context_for_llm = f"Pandas Result: {json.dumps(result.get('data', ''), default=str)[:800]}"
        else:
            context_for_llm = build_data_context(df, question)

    elif agent_type == "chart":
        from app.agents.visualization_agent import generate_interactive_charts
        charts = generate_interactive_charts(df)
        # Pick most relevant chart type based on question
        chart_kw_map = {
            "bar": "bar_chart", "pie": "pie_chart", "line": "line_chart",
            "histogram": "histogram", "scatter": "scatter_plot",
            "heatmap": "heatmap", "box": "box_plot", "area": "area_chart"
        }
        q_lower = question.lower()
        selected_chart = "bar_chart"  # default
        for kw, chart_key in chart_kw_map.items():
            if kw in q_lower and chart_key in charts:
                selected_chart = chart_key
                break
        chart_data = charts.get(selected_chart, list(charts.values())[0] if charts else None)
        context_for_llm = f"Generated a {selected_chart.replace('_',' ')} chart from the dataset."

    elif agent_type == "forecast":
        context_for_llm = build_data_context(df, question)

    else:
        # General / insights / recommend — use full data context
        context_for_llm = build_data_context(df, question)

    # ── Language instruction ─────────────────────────────────────────────
    lang_instruction = {
        "urdu": "Reply in Urdu script (اردو).",
        "hindi": "Reply in Hindi (हिंदी).",
        "hinglish": "Reply in Roman Urdu/Hinglish (mix of English and Urdu in Roman script).",
        "english": "",
    }.get(language, "")

    # ── Build final prompt ───────────────────────────────────────────────
    system = CHAT_SYSTEM_PROMPT
    if lang_instruction:
        system += f"\n\nLANGUAGE INSTRUCTION: {lang_instruction}"

    user_prompt = f"""Dataset: {dataset_name}
{column_mapping_note}
Data Context:
{context_for_llm[:2000]}

User Question: {question}

Pre-computed context from previous analysis:
- Insights available: {bool(pre_computed and pre_computed.get('insights'))}
- Charts available: {bool(pre_computed and pre_computed.get('charts'))}

Answer the question thoroughly using the exact data provided above."""

    response = ask_llm(system, user_prompt,
                       temperature=0.3, max_tokens=800)

    # Parse ANSWER and FOLLOW_UPS
    answer = response
    follow_ups = []

    if "ANSWER:" in response:
        parts = response.split("FOLLOW_UPS:")
        answer = parts[0].replace("ANSWER:", "").strip()
        if len(parts) > 1:
            follow_ups = [q.strip() for q in parts[1].split("|") if q.strip()]

    if column_mapping_note and column_mapping_note not in answer:
        answer = f"_{column_mapping_note}_\n\n{answer}"

    return {
        "answer": answer,
        "agent_used": agent_type,
        "chart_data": chart_data,
        "additional_data": additional_data,
        "follow_ups": follow_ups[:3],
        "language": language,
    }


async def stream_chat_message(
    df: pd.DataFrame,
    question: str,
    dataset_name: str,
    conversation_history: list = None,
):
    """Async generator for streaming chat responses."""
    language = detect_language(question)
    context = build_data_context(df, question)

    lang_instruction = {
        "urdu": "Reply in Urdu.",
        "hindi": "Reply in Hindi.",
        "hinglish": "Reply in Roman Urdu/Hinglish.",
    }.get(language, "")

    system = CHAT_SYSTEM_PROMPT
    if lang_instruction:
        system += f"\n\nLANGUAGE: {lang_instruction}"

    prompt = f"""Dataset: {dataset_name}
Data: {context[:2000]}
Question: {question}"""

    async for chunk in ask_llm_stream(
        system, prompt,
        conversation_history=conversation_history,
        temperature=0.4
    ):
        yield chunk
