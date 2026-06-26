"""
RackMind AI

Runbook Agent
"""

from services.vector_service import search_runbooks
from services.gemini_service import generate


def answer_question(question: str) -> str:
    """
    Answer a question using indexed runbooks.
    """

    docs = search_runbooks(question)

    if not docs:

        return """
No matching runbook entries were found.

Please index a runbook before asking questions.
"""

    context = "\n\n".join(docs)

    prompt = f"""
You are a senior Cisco data center engineer.

Use ONLY the supplied runbook.

If the answer is not contained in the runbook,
say so.

========================

RUNBOOK

{context}

========================

QUESTION

{question}

========================

Provide:

• Answer

• Explanation

• Recommended Actions
"""

    return generate(prompt)