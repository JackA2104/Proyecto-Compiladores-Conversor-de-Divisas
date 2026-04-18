"""
parser.py
Analizador sintáctico (PLY) + construcción del árbol (Lark) + motor de conversión.
"""
import ply.yacc as yacc
from lark import Lark
from lark.exceptions import UnexpectedInput
import pathlib
import json

from lexer import tokens, lexer, analizar_tokens, DIVISAS

# ─── TASAS DE CAMBIO (base USD) ───────────────────────────────────────────────
TASAS_USD = {
    "USD": 1.0,
    "EUR": 0.92,
    "HNL": 24.70,
    "MXN": 17.15,
    "GBP": 0.79,
    "JPY": 149.50,
    "CRC": 510.50,
}


def obtener_tasa(origen: str, destino: str) -> float:
    """
    Retorna el factor de conversión entre dos divisas.
    Convierte primero a USD y luego al destino.
    """
    codigo_origen  = DIVISAS[origen]
    codigo_destino = DIVISAS[destino]
    tasa_origen    = TASAS_USD[codigo_origen]
    tasa_destino   = TASAS_USD[codigo_destino]
    return tasa_destino / tasa_origen


def conversor_origen_destino(cantidad: float, origen: str, destino: str) -> float:
    """
    Regla semántica principal.
    Aplica la tasa de cambio y retorna el resultado redondeado a 4 decimales.
    """
    tasa = obtener_tasa(origen, destino)
    return round(cantidad * tasa, 4)


# ─── REGLAS SINTÁCTICAS PLY ───────────────────────────────────────────────────
resultado_global = {}


def p_expresion(p):
    """expresion : NUMERO MONEDA A MONEDA FIN"""
    cantidad = p[1]
    origen   = p[2]
    destino  = p[4]
    convertido = conversor_origen_destino(cantidad, origen, destino)
    resultado_global["cantidad"]   = cantidad
    resultado_global["origen"]     = origen
    resultado_global["destino"]    = destino
    resultado_global["resultado"]  = convertido
    resultado_global["cod_origen"] = DIVISAS[origen]
    resultado_global["cod_destino"]= DIVISAS[destino]
    resultado_global["tasa"]       = obtener_tasa(origen, destino)
    p[0] = convertido


def p_error(p):
    if p:
        raise SyntaxError(
            f"Error sintáctico en token '{p.value}' (tipo: {p.type}) — posición {p.lexpos}"
        )
    else:
        raise SyntaxError("Error sintáctico: fin de cadena inesperado.")


parser = yacc.yacc()


# ─── CONSTRUCCIÓN DEL ÁRBOL CON LARK ─────────────────────────────────────────
_grammar_path = pathlib.Path(__file__).parent / "grammar.lark"
_lark_parser  = Lark(_grammar_path.read_text(encoding="utf-8"), parser="lalr")


def construir_arbol(cadena: str) -> dict:
    """
    Usa Lark para construir el árbol de análisis sintáctico.
    Retorna un dict anidado apto para JSON / renderizado en frontend.
    """
    tree = _lark_parser.parse(cadena)
    return _tree_to_dict(tree)


def _tree_to_dict(node) -> dict:
    """Convierte el árbol Lark a dict recursivamente."""
    from lark import Tree, Token
    if isinstance(node, Tree):
        return {
            "tipo":  "regla",
            "nombre": node.data,
            "hijos": [_tree_to_dict(c) for c in node.children],
        }
    elif isinstance(node, Token):
        return {
            "tipo":   "token",
            "nombre": str(node.type),
            "valor":  str(node),
        }
    return {"tipo": "desconocido", "valor": str(node)}


# ─── FUNCIÓN PRINCIPAL ────────────────────────────────────────────────────────
def procesar(cadena: str) -> dict:
    """
    Punto de entrada principal.
    Recibe la cadena cruda y retorna todo el análisis.
    """
    resultado_global.clear()

    # 1) Análisis léxico
    try:
        tokens_encontrados = analizar_tokens(cadena)
    except ValueError as e:
        return {"error": f"Error léxico: {e}"}

    # 2) Análisis sintáctico (PLY)
    try:
        lexer.input(cadena)
        parser.parse(cadena, lexer=lexer)
    except SyntaxError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Error inesperado: {e}"}

    # 3) Árbol (Lark)
    try:
        arbol = construir_arbol(cadena)
    except UnexpectedInput as e:
        arbol = {"error": str(e)}

    return {
        "tokens":   tokens_encontrados,
        "semantica": resultado_global.copy(),
        "arbol":     arbol,
    }
