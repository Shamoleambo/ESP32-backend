import math


def validar_mensagem(dados):
    if not isinstance(dados, dict):
        raise ValueError("A mensagem precisa ser um objeto JSON.")

    if type(dados.get("versao")) is not int or dados["versao"] != 1:
        raise ValueError("Versão da mensagem não suportada.")

    if dados.get("estacao_id") != "estacao-01":
        raise ValueError("Estação desconhecida.")

    sequencia = dados.get("sequencia")

    if type(sequencia) is not int or sequencia < 1:
        raise ValueError("Sequência inválida.")

    if dados.get("estado_dht22") != "ok":
        raise ValueError("Sensor informou falha de leitura.")

    leituras = dados.get("leituras")

    if not isinstance(leituras, dict):
        raise ValueError("Campo 'leituras' ausente ou inválido.")

    # Temperaturas fora da realidade não serão consideradas
    limites = {"temperatura_c": (-40, 80), "umidade_pct": (0, 100)}

    for campo, (minimo, maximo) in limites.items():
        valor = leituras.get(campo)

        if type(valor) not in (int, float):
            raise ValueError(f"{campo} precisa ser um número.")

        if not minimo <= valor <= maximo or not math.isfinite(valor):
            raise ValueError(f"{campo} fora do intervalo permitido.")
