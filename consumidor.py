import json
import sqlite3
import paho.mqtt.client as mqtt

from banco import inicializar_banco, salvar_leitura
from validacao import validar_mensagem
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

        validar_mensagem(dados)
        salvar_leitura(dados)

    except (UnicodeDecodeError, ValueError) as erro:
        print("Mensagem descartada:", erro)
        return

    except sqlite3.Error as erro:
        print("Falha ao salvar no banco:", erro)
        return

    print("Leitura salva:", dados["estacao_id"], "sequência", dados["sequencia"])


def main():
    inicializar_banco()

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
