"""
app.py
Servidor Flask — Conversor de Divisas
"""
from flask import Flask, render_template, request, jsonify
from parser import procesar, DIVISAS

app = Flask(__name__)


@app.route("/")
def index():
    divisas = list(DIVISAS.keys())
    return render_template("index.html", divisas=divisas)


@app.route("/convertir", methods=["POST"])
def convertir():
    datos = request.get_json()
    cantidad = datos.get("cantidad", "").strip()
    origen   = datos.get("origen", "").strip()
    destino  = datos.get("destino", "").strip()

    if not cantidad or not origen or not destino:
        return jsonify({"error": "Todos los campos son obligatorios."}), 400

    # Construir la cadena en el formato que espera el lexer/parser
    cadena = f"{cantidad}{origen}a{destino}$"

    resultado = procesar(cadena)
    resultado["cadena"] = cadena
    return jsonify(resultado)


if __name__ == "__main__":
    app.run(debug=True)
