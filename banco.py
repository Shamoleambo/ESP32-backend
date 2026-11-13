import json
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

CAMINHO_BANCO = Path(
    os.environ.get(
        "CAMINHO_BANCO",
        str(Path(__file__).resolve().parent / "estacao.sqlite3"),
    )
)

CAMINHO_BANCO.parent.mkdir(parents=True, exist_ok=True)

CAMPOS = (
    "temperatura_c",
    "umidade_pct",
    "pressao_hpa",
    "mq135_adc",
    "luminosidade_adc",
    "luminosidade_digital",
)

ESQUEMA = """
    CREATE TABLE {tabela} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        estacao_id TEXT NOT NULL,
        sequencia INTEGER NOT NULL,
        temperatura_c REAL
            CHECK (temperatura_c BETWEEN -40 AND 80),
        umidade_pct REAL
            CHECK (umidade_pct BETWEEN 0 AND 100),
        pressao_hpa REAL
            CHECK (pressao_hpa BETWEEN 300 AND 1100),
        mq135_adc INTEGER
            CHECK (mq135_adc BETWEEN 0 AND 4095),
        luminosidade_adc INTEGER
            CHECK (luminosidade_adc BETWEEN 0 AND 4095),
        luminosidade_digital INTEGER
            CHECK (luminosidade_digital IN (0, 1)),
        estado_sensores TEXT NOT NULL,
        recebido_em TEXT NOT NULL
    )
"""


def inicializar_banco():
    with closing(sqlite3.connect(CAMINHO_BANCO, timeout=10)) as conexao:
        colunas = {linha[1] for linha in conexao.execute("PRAGMA table_info(leituras)")}

        if colunas and "estado_sensores" not in colunas:
            backup = CAMINHO_BANCO.with_name("estacao-antes-v2.sqlite3")

            if backup.exists():
                raise RuntimeError(
                    "Backup já existe. Confira antes de migrar novamente."
                )

            with closing(sqlite3.connect(backup)) as destino:
                conexao.backup(destino)

            print("Backup criado:", backup)

        with conexao:
            conexao.execute("BEGIN IMMEDIATE")

            if not colunas:
                conexao.execute(ESQUEMA.format(tabela="leituras"))

            elif "estado_sensores" not in colunas:
                conexao.execute(ESQUEMA.format(tabela="leituras_nova"))

                estados_antigos = json.dumps(
                    {
                        "dht22": "ok",
                        "bmp280": "nao_configurado",
                        "mq135": "nao_configurado",
                        "ldr": "nao_configurado",
                    }
                )

                conexao.execute(
                    """
                    INSERT INTO leituras_nova (
                        id, estacao_id, sequencia, temperatura_c,
                        umidade_pct, estado_sensores, recebido_em
                    )
                    SELECT
                        id, estacao_id, sequencia, temperatura_c,
                        umidade_pct, ?, recebido_em
                    FROM leituras
                """,
                    (estados_antigos,),
                )

                conexao.execute("DROP TABLE leituras")
                conexao.execute("ALTER TABLE leituras_nova RENAME TO leituras")

                print("Histórico migrado para o formato 2.")

            colunas_atuais = {
                linha[1] for linha in conexao.execute("PRAGMA table_info(leituras)")
            }

            if "luminosidade_digital" not in colunas_atuais:
                conexao.execute("""
                    ALTER TABLE leituras
                    ADD COLUMN luminosidade_digital INTEGER
                    CHECK (luminosidade_digital IN (0, 1))
                """)

                print("Coluna de luminosidade digital adicionada.")


def salvar_leitura(dados):
    valores = [dados["leituras"][campo] for campo in CAMPOS]

    with closing(sqlite3.connect(CAMINHO_BANCO, timeout=10)) as conexao:
        with conexao:
            conexao.execute(
                """
                INSERT INTO leituras (
                    estacao_id, sequencia, temperatura_c, umidade_pct,
                    pressao_hpa, mq135_adc, luminosidade_adc,
                    luminosidade_digital, estado_sensores, recebido_em
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    dados["estacao_id"],
                    dados["sequencia"],
                    *valores,
                    json.dumps(dados["estado_sensores"]),
                    datetime.now(timezone.utc).isoformat(),
                ),
            )


def buscar_ultima_leitura():
    with closing(sqlite3.connect(CAMINHO_BANCO, timeout=10)) as conexao:
        conexao.row_factory = sqlite3.Row

        linha = conexao.execute("""
            SELECT *
            FROM leituras
            ORDER BY id DESC
            LIMIT 1
        """).fetchone()

        if linha is None:
            return None

        registro = dict(linha)

        return {
            "versao": 3,
            "id": registro["id"],
            "estacao_id": registro["estacao_id"],
            "sequencia": registro["sequencia"],
            "leituras": {campo: registro[campo] for campo in CAMPOS},
            "estado_sensores": json.loads(registro["estado_sensores"]),
            "recebido_em": registro["recebido_em"],
        }


if __name__ == "__main__":
    inicializar_banco()
    print("Banco preparado em:", CAMINHO_BANCO)
