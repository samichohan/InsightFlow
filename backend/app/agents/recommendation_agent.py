"""Agent 5 — Recommendation Agent (depends on Agent 4 insights)."""

from app.agents.base import BaseAgent, PipelineContext
from app.core.llm_client import ask_llm

SYSTEM_PROMPT = """You are a Business Strategy Consultant. Based on the provided
business insights from data analysis, generate detailed, actionable recommendations.

Rules:
- Always respond in English
- Each recommendation must be specific, measurable, and actionable
- Include expected business impact for each recommendation
- Provide 6-8 recommendations in priority order (highest ROI first)
- Format: '- [PRIORITY] Recommendation: explanation (Expected Impact: ...)'
- Cover: revenue growth, cost reduction, risk mitigation, customer retention, operations
"""


def generate_recommendations(insights: list, dataset_name: str) -> list:
    insights_text = "\n".join(f"- {i}" for i in insights)

    prompt = f"""Business insights for dataset '{dataset_name}':

{insights_text}

Generate 6-8 specific, actionable business recommendations based on these insights.
For each recommendation, include the expected business impact.
Return ONLY bullet points starting with '- '"""

    response = ask_llm(SYSTEM_PROMPT, prompt, temperature=0.4, max_tokens=1200)
    lines = [l.strip().lstrip("-").strip() for l in response.split("\n")
             if l.strip() and l.strip().startswith("-")]
    return lines or [l.strip() for l in response.split("\n") if l.strip()]


class RecommendationAgent(BaseAgent):
    name = "recommendations"
    max_retries = 2

    def run(self, context: PipelineContext) -> list:
        insights = context.get("insights") or []
        return generate_recommendations(insights, context.get("dataset_name", "dataset"))
