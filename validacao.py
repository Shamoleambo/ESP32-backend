import math

CAMPOS = {
    "dht22": {"temperatura_c": (-40, 80), "umidade_pct": (0, 100)},
    "bmp280": {"pressao_hpa": (300, 1100)},
    "mq135": {"mq135_adc": (0, 4095)},
    "ldr": {"luminosidade_adc": (0, 4095)},
}

ESTADOS = {"ok", "erro_leitura", "aquecendo", "nao_configurado"}


def validar_mensagem(dados):
    if not isinstance(dados, dict):
        raise ValueError("A mensagem precisa ser um objeto JSON.")

    versao = dados.get("versao")

    if type(versao) is not int or versao not in (1, 2, 3):
        raise ValueError("Versão não suportada.")

    if dados.get("estacao_id") != "estacao-01":
        raise ValueError("Estação desconhecida.")

    sequencia = dados.get("sequencia")

    if type(sequencia) is not int or sequencia < 1:
        raise ValueError("Sequência inválida.")

    leituras = dados.get("leituras")

    if not isinstance(leituras, dict):
        raise ValueError("Campo leituras inválido.")

    grupos = {sensor: dict(campos) for sensor, campos in CAMPOS.items()}

    if versao == 3:
        grupos["ldr"] = {"luminosidade_digital": (0, 1)}

        if leituras.get("luminosidade_adc") is not None:
            raise ValueError("O módulo digital não fornece luminosidade_adc.")

    # Compatibilidade temporária com o firmware anterior.
    if versao == 1:
        estados = {sensor: "nao_configurado" for sensor in CAMPOS}
        estados["dht22"] = dados.get("estado_dht22")
        esperados = CAMPOS["dht22"]

    else:
        estados = dados.get("estado_sensores")

        if not isinstance(estados, dict):
            raise ValueError("Campo estado_sensores inválido.")

        esperados = {campo for grupo in grupos.values() for campo in grupo}

    if not all(campo in leituras for campo in esperados):
        raise ValueError("Campos de leitura obrigatórios ausentes.")

    resultado = {
        "versao": 3,
        "estacao_id": dados["estacao_id"],
        "sequencia": sequencia,
        "leituras": {"luminosidade_adc": None, "luminosidade_digital": None},
        "estado_sensores": {},
    }

    for sensor, campos in grupos.items():
        estado = estados.get(sensor)

        if not isinstance(estado, str) or estado not in ESTADOS:
            raise ValueError(f"Estado inválido para {sensor}.")

        if estado == "ok":
            for campo, (minimo, maximo) in campos.items():
                valor = leituras.get(campo)

                valido = (
                    type(valor) in (int, float)
                    and minimo <= valor <= maximo
                    and math.isfinite(valor)
                )

                if campo.endswith(("_adc", "_digital")):
                    valido = valido and type(valor) is int

                if not valido:
                    estado = "erro_leitura"
                    break

        resultado["estado_sensores"][sensor] = estado

        for campo in campos:
            resultado["leituras"][campo] = leituras[campo] if estado == "ok" else None

    return resultado
