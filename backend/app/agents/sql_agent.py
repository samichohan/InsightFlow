"""
Agent 8 — SQL Query Agent.
Converts natural language to SQL, executes on in-memory SQLite, returns results.
Uses SQLite (no external DB needed) so it works even without PostgreSQL.
"""

import sqlite3
import pandas as pd
import tempfile
import os
from app.agents.base import BaseAgent, PipelineContext
from app.core.llm_client import ask_llm

SYSTEM_PROMPT = """You are an expert SQL query writer. The user has a dataset
loaded into a SQLite table. Generate a valid SQLite SQL query based on the user's
natural language request.

Rules:
- The table is always named 'dataset'
- Return ONLY the SQL query — no explanation, no markdown, no backticks
- Use standard SQLite syntax
- For TOP N queries use LIMIT N
- Always handle case-insensitivity with LOWER() when filtering text
- Never use DROP, DELETE, UPDATE, INSERT, or any destructive operations
"""


def nl_to_sql(question: str, columns: list, sample_rows: list) -> str:
    """Convert natural language question to SQL query."""
    col_info = ", ".join(f"{col}" for col in columns)
    sample = str(sample_rows[:3]) if sample_rows else ""

    prompt = f"""Table name: dataset
Columns: {col_info}
Sample data: {sample}

User question: {question}

Generate a SQLite SQL query to answer this question."""

    return ask_llm(SYSTEM_PROMPT, prompt, temperature=0.1, max_tokens=300)


def execute_sql_on_df(df: pd.DataFrame, sql_query: str) -> dict:
    """Execute SQL query on DataFrame using in-memory SQLite."""
    # Clean up the query (remove markdown if LLM added it)
    query = sql_query.strip()
    for prefix in ["```sql", "```SQL", "```"]:
        if query.startswith(prefix):
            query = query[len(prefix):]
    query = query.rstrip("`").strip()

    # Safety check — no destructive operations
    dangerous = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE"]
    if any(word in query.upper() for word in dangerous):
        return {"error": "Destructive SQL operations are not allowed.", "query": query}

    try:
        # Load DataFrame into in-memory SQLite
        conn = sqlite3.connect(":memory:")
        df.to_sql("dataset", conn, if_exists="replace", index=False)

        result_df = pd.read_sql_query(query, conn)
        conn.close()

        return {
            "sql_query": query,
            "result": result_df.to_dict(orient="records"),
            "columns": result_df.columns.tolist(),
            "row_count": len(result_df),
        }
    except Exception as e:
        return {"error": str(e), "query": query}


class SQLAgent(BaseAgent):
    name = "sql_agent"
    max_retries = 1

    def run(self, context: PipelineContext) -> dict:
        df = context.get("dataframe")
        question = context.get("user_question", "")

        sql = nl_to_sql(
            question,
            list(df.columns),
            df.head(3).to_dict(orient="records")
        )
        result = execute_sql_on_df(df, sql)

        # Generate explanation
        if "error" not in result:
            explanation_prompt = f"""The user asked: "{question}"
The SQL query was: {result['sql_query']}
The result has {result['row_count']} rows.

Write a brief, clear explanation of what the query does and what the result means
for the business. 2-3 sentences."""
            result["explanation"] = ask_llm(
                "You are a data analyst explaining SQL results clearly.",
                explanation_prompt, temperature=0.3, max_tokens=200
            )

        return result
