"""
Indexes the sample runbook into ChromaDB.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from services.vector_service import add_runbook
from services.vector_service import collection

RUNBOOK = Path("sample_data/runbooks/sample_runbook.txt")


text = RUNBOOK.read_text(
    encoding="utf-8"
)

add_runbook(
    RUNBOOK.stem,
    text,
)

print("Documents in collection:")

print(collection.count())

print("Runbook indexed successfully.")