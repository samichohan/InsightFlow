"""
Agent 9 — Pandas Code Generation & Execution Agent.
Converts natural language to Pandas code, executes safely, returns results.
"""

import pandas as pd
import numpy as np
import traceback
from app.agents.base import BaseAgent, PipelineContext
from app.core.llm_client import ask_llm

SYSTEM_PROMPT = """You are an expert Python/Pandas developer. Generate safe Pandas
code to answer the user's data analysis question.

Rules:
- The DataFrame is always named 'df'
- Return ONLY the Python code — no explanation, no markdown backticks
- The last line must assign the result to a variable named 'result'
- 'result' can be: a DataFrame, Series, number, string, or dict
- Never use file I/O, imports (pandas/numpy already imported), or system calls
- Keep code simple and readable
- For aggregations use groupby, agg, describe etc.
- Always handle NaN values with dropna() or fillna() where needed
"""


def nl_to_pandas_code(question: str, columns: list, dtypes: dict, sample: list) -> str:
    prompt = f"""DataFrame columns and types: {dtypes}
Sample rows: {sample[:2]}

User question: {question}

Generate Pandas code. Last line must assign answer to 'result'."""
    return ask_llm(SYSTEM_PROMPT, prompt, temperature=0.1, max_tokens=400)


def execute_pandas_code(df: pd.DataFrame, code: str) -> dict:
    # Clean code
    clean_code = code.strip()
    for fence in ["```python", "```Python", "```"]:
        if clean_code.startswith(fence):
            clean_code = clean_code[len(fence):]
    clean_code = clean_code.rstrip("`").strip()

    # Safety: block dangerous operations
    blocked = ["import os", "import sys", "open(", "exec(", "eval(", "__import__",
               "subprocess", "shutil", "rmdir", "remove", "system("]
    for b in blocked:
        if b in clean_code:
            return {"error": f"Blocked operation detected: {b}", "code": clean_code}

    # Execute in sandboxed namespace
    namespace = {"df": df.copy(), "pd": pd, "np": np, "result": None}
    try:
        exec(clean_code, namespace)
        result = namespace.get("result")

        # Convert result to serializable format
        if isinstance(result, pd.DataFrame):
            return {
                "code": clean_code,
                "result_type": "dataframe",
                "data": result.head(50).to_dict(orient="records"),
                "columns": result.columns.tolist(),
                "shape": list(result.shape),
            }
        elif isinstance(result, pd.Series):
            return {
                "code": clean_code,
                "result_type": "series",
                "data": result.to_dict(),
            }
        elif isinstance(result, (int, float, np.integer, np.floating)):
            return {
                "code": clean_code,
                "result_type": "number",
                "data": float(result),
            }
        else:
            return {
                "code": clean_code,
                "result_type": "text",
                "data": str(result),
            }
    except Exception as e:
        return {"error": str(e), "code": clean_code, "traceback": traceback.format_exc()}


class PandasAgent(BaseAgent):
    name = "pandas_agent"
    max_retries = 1

    def run(self, context: PipelineContext) -> dict:
        df = context.get("dataframe")
        question = context.get("user_question", "")

        code = nl_to_pandas_code(
            question,
            list(df.columns),
            {col: str(dt) for col, dt in df.dtypes.items()},
            df.head(2).to_dict(orient="records")
        )

        result = execute_pandas_code(df, code)

        # Add explanation
        if "error" not in result:
            result["explanation"] = ask_llm(
                "You are a data analyst. Explain analysis results briefly and clearly.",
                f'Question: "{question}"\nResult: {str(result.get("data", ""))[:500]}\n\nExplain in 2-3 sentences.',
                temperature=0.3, max_tokens=200
            )

        return result
