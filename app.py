from flask import Flask, jsonify

from banco import inicializar_banco, buscar_ultima_leitura

app = Flask(__name__)
inicializar_banco()


@app.get("/api/status")
def consultar_status():
    return jsonify({"status": "ok", "servico": "backend-estacao-meteorologica"})


@app.get("/api/leituras/ultima")
def consultar_ultima_leitura():
    registro = buscar_ultima_leitura()

    if registro is None:
        return jsonify({"erro": "Ainda não existem leituras válidas armazenadas."}), 404

    return jsonify(
        {
            "id": registro["id"],
            "estacao_id": registro["estacao_id"],
            "sequencia": registro["sequencia"],
            "leituras": {
                "temperatura_c": registro["temperatura_c"],
                "umidade_pct": registro["umidade_pct"],
            },
            "estado_dht22": "ok",
            "recebido_em": registro["recebido_em"],
        }
    )
