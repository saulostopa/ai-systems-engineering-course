# Area Copilot — contexto de negócio para agentes
# (planilhas, documentos e dados da área; motor: rag_harness)

import os
import sys

# O motor vive em ../rag-harness (irmão de diretório)
_RAG_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "rag-harness"))
if _RAG_ROOT not in sys.path:
    sys.path.insert(0, _RAG_ROOT)