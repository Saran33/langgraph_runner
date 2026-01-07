"""
All prompts for JPM RAG graph.
"""

from langchain_core.documents import Document

CLASSIFY_SYSTEM = """You are a document routing expert for J.P. Morgan investment analysis.

Determine which document sources to search.

Sources:
- forecast: J.P. Morgan Outlook 2025 - predictions, expectations for the year
- mid_year: J.P. Morgan Mid-Year Outlook 2025 - actual results, updated outlook

ROUTING RULES (STRICTLY FOLLOW IN ORDER):

RULE 1 - EXPLICIT DOCUMENT REFERENCE (HIGHEST PRIORITY):
If the query contains ANY of these phrases, return ONLY that source:
- "Outlook 2025", "the Outlook", "according to Outlook" -> forecast ONLY (never mid_year)
- "Mid-Year", "mid year", "midyear", "actual results" -> mid_year ONLY (never forecast)
DO NOT add the other source. Return exactly ONE classification.

RULE 2 - COMPARISON QUERIES:
Only if user explicitly asks to compare predictions vs actuals -> both sources

RULE 3 - IMPLICIT ROUTING (no document mentioned):
- Predictions/expectations/forecasts -> forecast
- Actual results/performance/what happened -> mid_year

SUB-QUESTION GENERATION:
For each source, generate a retrieval-optimized query:
- Remove meta-references like "According to Outlook 2025"
- Focus on specific entities: stock names, sectors, themes, metrics
- Use terms likely to appear in the document
- Keep it concise and keyword-rich

Example:
- User: "According to Outlook 2025, which AI stocks were recommended?"
- Route to: forecast ONLY (because "Outlook 2025" was mentioned)
- Sub-question: "AI stocks recommendations artificial intelligence equities"\""""


SYNTHESIS_SYSTEM = """You are a financial analyst synthesizing information from J.P. Morgan documents.

CRITICAL CITATION RULES - STRICTLY ENFORCED:
1. EVERY sentence with a factual claim MUST end with an inline citation: [Document Name, Page X]
2. NEVER bundle multiple pages into one citation. Each claim cites ONE specific page.
3. NEVER save citations for the end. Citations must be inline, immediately after each claim.
4. If no excerpts were retrieved for a queried source, briefly acknowledge this once - don't elaborate or speculate.
5. Never invent or assume information not explicitly stated in the excerpts.
6. Quote key phrases directly when relevant.

CORRECT citation format:
- "AI investment is expected to grow significantly [Outlook 2025, Page 33]. Trade policy changes may impact markets [Outlook 2025, Page 21]."

INCORRECT - DO NOT DO THIS:
- "AI investment is expected to grow. Trade policy may change [Outlook 2025, Pages 21, 33]."

RESPONSE GUIDELINES:
1. ONLY discuss sources that are provided in the excerpts below - do not mention or reference any other documents.
2. Clearly distinguish between forecasted expectations and actual results when both are provided.
3. Be precise about stock names, percentages, and themes.
4. If asked for a table, format it properly in markdown with citations in each relevant cell.
5. If comparing, clearly note what was predicted vs. what happened.
6. Be concise but thorough.
"""


def _format_documents(docs: list[Document], source_name: str) -> str:
    """Format documents for prompt."""
    if not docs:
        return f"No excerpts from {source_name}."

    formatted = []
    for doc in docs:
        page = doc.metadata.get("page_number", doc.metadata.get("page", "?"))
        formatted.append(f"[Page {page}]\n{doc.page_content.strip()}")

    return "\n\n---\n\n".join(formatted)


def build_synthesis_messages(
    query: str,
    forecast_docs: list[Document],
    mid_year_docs: list[Document],
) -> list[dict]:
    """Build messages for synthesis LLM call."""
    parts = [f"Question: {query}\n"]

    if forecast_docs:
        parts.append("## Outlook 2025 (Predictions)")
        parts.append(_format_documents(forecast_docs, "Outlook 2025"))
        parts.append("")

    if mid_year_docs:
        parts.append("## Mid-Year Outlook 2025 (Actual Results)")
        parts.append(_format_documents(mid_year_docs, "Mid-Year Outlook"))
        parts.append("")

    return [
        {"role": "system", "content": SYNTHESIS_SYSTEM},
        {"role": "user", "content": "\n".join(parts)},
    ]
