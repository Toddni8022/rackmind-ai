"""
RackMind AI

Runbook Agent
"""

from services.vector_service import search_runbooks
from services.gemini_service import generate


def answer_question_local(question: str) -> str:
    """
    Answer from indexed runbooks without using Gemini.
    """

    docs = search_runbooks(question)

    if not docs:

        return """
No matching runbook entries were found.

Please index a runbook before asking questions.
"""

    snippets = []

    for doc in docs:
        clean_doc = " ".join(str(doc).split())
        if clean_doc:
            snippets.append(clean_doc[:650])

    evidence = "\n\n".join(f"- {snippet}" for snippet in snippets)
    question_lower = question.lower()

    if any(term in question_lower for term in ("crc", "fcs", "input error")):
        explanation = (
            "CRC/FCS errors are usually caused by physical-layer or link "
            "stability problems such as bad cabling, failing optics, dirty "
            "connectors, speed or duplex negotiation issues, or an unstable "
            "switch port."
        )
        actions = [
            "Inspect and reseat the cable or fiber pair on the affected interface.",
            "Check optics, transceivers, patch panels, and connectors for faults or contamination.",
            "Clear interface counters, then monitor whether CRC/FCS errors return.",
            "Move the link to a known-good cable, optic, or port if errors continue.",
            "Escalate to switch or hardware replacement if errors follow the port.",
        ]
    elif any(term in question_lower for term in ("temperature", "temp", "thermal", "hot")):
        explanation = (
            "Temperature alerts usually point to airflow, cooling, rack load, "
            "or environmental problems around the affected equipment."
        )
        actions = [
            "Check rack inlet temperature and compare it with the warning and critical thresholds.",
            "Inspect airflow direction, blanking panels, blocked vents, and fan status.",
            "Validate CRAC or cooling output near the affected rack.",
            "Reduce local load or move noncritical systems if redundancy is constrained.",
            "Continue monitoring until temperatures return to the normal operating range.",
        ]
    elif any(term in question_lower for term in ("power", "pdu", "draw", "kw", "load")):
        explanation = (
            "Power alerts usually indicate rack load, PDU capacity, redundancy, "
            "or unexpected draw changes that can affect availability."
        )
        actions = [
            "Compare current draw against expected operating envelope and PDU capacity.",
            "Check whether redundant feeds still have safe headroom.",
            "Move noncritical load if redundancy or capacity is constrained.",
            "Look for recent hardware additions or workload changes.",
            "Keep monitoring peak draw after mitigation.",
        ]
    else:
        explanation = (
            "RackMind found related local runbook material and summarized it "
            "without calling the cloud AI service."
        )
        actions = [
            "Review the matching runbook evidence below.",
            "Validate the affected device, interface, rack, and timestamps.",
            "Apply the safest low-risk checks first, then monitor for recurrence.",
            "Escalate if the condition persists after the documented procedure.",
        ]

    action_text = "\n".join(f"- {action}" for action in actions)

    return f"""
### Answer

RackMind found matching local runbook guidance for:
**{question}**

### Explanation

{explanation}

### Recommended Actions

{action_text}

### Local Runbook Evidence

{evidence}

_Local fallback mode was used because the cloud AI service was unavailable._
"""


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
