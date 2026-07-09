"""Agent 4 — Business Insight Agent (Groq LLM + Prompt Engineering)."""

import json
from app.agents.base import BaseAgent, PipelineContext
from app.core.llm_client import ask_llm

SYSTEM_PROMPT = """You are a Senior Business Data Analyst with 10+ years of experience
working with Fortune 500 companies. Analyze the provided dataset statistics and generate
detailed, professional business insights.

Rules:
- Always respond in English by default
- Use specific numbers from the data (exact values, percentages)
- Each insight must be a complete, well-explained sentence (2-3 lines)
- Provide exactly 8-10 insights ordered by business importance
- Cover: data quality, top performers, trends, correlations, anomalies, risks, opportunities
- Use professional business language like a consulting report
- Format: return ONLY bullet points starting with '- '
"""


def generate_insights(quality_report: dict, eda_report: dict, dataset_name: str) -> list:
    context = {
        "dataset": dataset_name,
        "rows": quality_report.get("total_rows"),
        "columns": quality_report.get("total_columns"),
        "quality_score": quality_report.get("data_quality_score"),
        "duplicates": quality_report.get("duplicate_rows"),
        "missing_values": quality_report.get("missing_values"),
        "statistics": eda_report.get("descriptive_stats"),
        "strong_correlations": eda_report.get("strong_correlations"),
        "top_categories": eda_report.get("category_distribution"),
        "unique_values": eda_report.get("unique_values"),
    }

    prompt = f"""Dataset '{dataset_name}' complete statistics:

{json.dumps(context, indent=2, default=str)}

Generate 8-10 detailed business insights. Each insight should include the specific
number/percentage from the data and explain its business significance.
Return ONLY bullet points starting with '- '"""

    response = ask_llm(SYSTEM_PROMPT, prompt, temperature=0.3, max_tokens=1500)
    lines = [l.strip().lstrip("-").strip() for l in response.split("\n")
             if l.strip() and l.strip().startswith("-")]
    return lines or [l.strip() for l in response.split("\n") if l.strip()]


class InsightAgent(BaseAgent):
    name = "insights"
    max_retries = 2

    def run(self, context: PipelineContext) -> list:
        return generate_insights(
            context.get("data_cleaning") or {},
            context.get("eda") or {},
            context.get("dataset_name", "dataset")
        )
