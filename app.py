import os
from flask import Flask, jsonify
from flask_cors import CORS
from banco import inicializar_banco, buscar_ultima_leitura

app = Flask(__name__)
CORS(
    app,
    resources={
        r"/api/.*": {
            "origins": ["http://127.0.0.1:8000", "http://localhost:8000", "https://estacao-meteorologica-front.onrender.com"],
            "methods": ["GET"],
        }
    },
)
inicializar_banco()


@app.get("/api/status")
def consultar_status():
    return jsonify({"status": "ok", "servico": "backend-estacao-meteorologica"})


@app.get("/api/leituras/ultima")
def consultar_ultima_leitura():
    registro = buscar_ultima_leitura()

    if registro is None:
        return (
            jsonify({"erro": "Ainda não existem registros de leitura armazenados."}),
            404,
        )

    return jsonify(registro)

@app.get("/api/estacao")
def consultar_estacao():
    try:
        latitude = float(os.environ["ESTACAO_LATITUDE"])
        longitude = float(os.environ["ESTACAO_LONGITUDE"])

        if not (-90 <= latitude <= 90):
            raise ValueError("Latitude inválida.")

        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude inválida.")

    except (KeyError, ValueError):
        return jsonify({
            "erro": "Localização da estação ausente ou inválida."
        }), 503

    return jsonify({
        "estacao_id": "estacao-01",
        "nome": os.environ.get(
            "ESTACAO_NOME",
            "Estação meteorológica"
        ),
        "latitude": latitude,
        "longitude": longitude,
        "origem_localizacao": "cadastro_manual"
    })
