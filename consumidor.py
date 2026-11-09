import json

import paho.mqtt.client as mqtt

from config import MQTT_SERVIDOR, MQTT_PORTA, MQTT_TOPICO


def ao_conectar(cliente, dados_usuario, flags, codigo, propriedades):
    if codigo != 0:
        print("Conexão recusada pelo broker:", codigo)
        return

    print("Conectado ao broker!")
    cliente.subscribe(MQTT_TOPICO)
    print("Assinatura solicitada para:", MQTT_TOPICO)


def ao_receber_mensagem(cliente, dados_usuario, mensagem):
    try:
        texto = mensagem.payload.decode("utf-8")
        dados = json.loads(texto)

    except (UnicodeDecodeError, json.JSONDecodeError) as erro:
        print("Mensagem descartada: conteúdo inválido.", erro)
        return

    if not isinstance(dados, dict):
        print("Mensagem descartada: esperado um objeto JSON.")
        return

    print("\nMensagem recebida!")
    print("Tópico:", mensagem.topic)
    print(json.dumps(dados, indent=2, ensure_ascii=False))


def main():
    cliente = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

    cliente.on_connect = ao_conectar
    cliente.on_message = ao_receber_mensagem

    cliente.reconnect_delay_set(min_delay=1, max_delay=30)

    try:
        print("Conectando ao broker...")
        cliente.connect(MQTT_SERVIDOR, MQTT_PORTA, keepalive=60)
        cliente.loop_forever()

    except KeyboardInterrupt:
        print("\nEncerrando consumidor.")

    except OSError as erro:
        print("Falha de conexão:", erro)

    finally:
        cliente.disconnect()


if __name__ == "__main__":
    main()
