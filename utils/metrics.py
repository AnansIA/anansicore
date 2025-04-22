# utils/metrics.py

import tokenize
from io import BytesIO

def count_anansi_tokens(anansi_text: str) -> int:
    """Cuenta los tokens AnansiCore basados en líneas con etiqueta.ID:..."""
    return sum(1 for line in anansi_text.splitlines() if line.strip() and ':' in line)

def count_python_tokens(code_str: str) -> int:
    """Cuenta tokens reales de Python, excluyendo espacios, comentarios y estructura."""
    tokens = tokenize.tokenize(BytesIO(code_str.encode()).readline)
    return sum(1 for t in tokens if t.type not in {
        tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
        tokenize.ENCODING, tokenize.ENDMARKER,
        tokenize.INDENT, tokenize.DEDENT
    })

def estimate_apl_equivalent_tokens(anansi_count: int) -> int:
    """Estima cuántos tokens serían en APL, de forma aproximada."""
    return max(1, anansi_count // 3)

