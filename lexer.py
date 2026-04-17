"""
lexer.py
Analizador léxico del Conversor de Divisas — PLY
"""
import ply.lex as lex

# ─── DIVISAS SOPORTADAS ───────────────────────────────────────────────────────
DIVISAS = {
    "DólarEstadounidense": "USD",
    "EuroUnión":           "EUR",
    "LempiraHondureño":    "HNL",
    "PesoMexicano":        "MXN",
    "LibraEsterlina":      "GBP",
    "YenJaponés":          "JPY",
}

# ─── TOKENS ───────────────────────────────────────────────────────────────────
tokens = (
    "NUMERO",
    "MONEDA",
    "A",
    "FIN",
)

# Ignorar espacios y tabs
t_ignore = " \t"


def t_NUMERO(t):
    r"""\d+(\.\d+)?"""
    t.value = float(t.value)
    return t


def t_MONEDA(t):
    r"""DólarEstadounidense|EuroUnión|LempiraHondureño|PesoMexicano|LibraEsterlina|YenJaponés"""
    t.value = t.value  # string tal cual
    return t


def t_A(t):
    r"""a"""
    return t


def t_FIN(t):
    r"""\$"""
    return t


def t_error(t):
    raise ValueError(f"Carácter ilegal '{t.value[0]}' en posición {t.lexpos}")


# ─── CONSTRUCCIÓN DEL LEXER ───────────────────────────────────────────────────
lexer = lex.lex()


def analizar_tokens(cadena: str) -> list[dict]:
    """
    Recibe una cadena y retorna la lista de tokens encontrados.
    Cada elemento: { linea, tipo, valor, posicion }
    """
    lexer.input(cadena)
    resultado = []
    for tok in lexer:
        resultado.append({
            "linea":    tok.lineno,
            "tipo":     tok.type,
            "valor":    str(tok.value),
            "posicion": tok.lexpos,
        })
    return resultado
