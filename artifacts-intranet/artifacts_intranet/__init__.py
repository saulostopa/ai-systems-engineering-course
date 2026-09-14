# Intranet de artefatos — busca RAG sobre o que o harness gerou.

import os
import sys

# Motor RAG: irmãos de diretório (rag-harness e area-copilot)
_REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))
for pkg in ("rag-harness", "area-copilot"):
    p = os.path.join(_REPO, pkg)
    if p not in sys.path:
        sys.path.insert(0, p)