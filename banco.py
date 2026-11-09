import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

CAMINHO_BANCO = Path(__file__).resolve().parent / "estacao.sqlite3"


def inicializar_banco():
    with closing(sqlite3.connect(CAMINHO_BANCO, timeout=10)) as conexao:
        with conexao:
            conexao.execute("""
                CREATE TABLE IF NOT EXISTS leituras (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    estacao_id TEXT NOT NULL,
                    sequencia INTEGER NOT NULL,
                    temperatura_c REAL NOT NULL
                        CHECK (temperatura_c BETWEEN -40 AND 80),
                    umidade_pct REAL NOT NULL
                        CHECK (umidade_pct BETWEEN 0 AND 100),
                    recebido_em TEXT NOT NULL
                )
            """)


def salvar_leitura(dados):
    recebido_em = datetime.now(timezone.utc).isoformat()
    leituras = dados["leituras"]

    with closing(sqlite3.connect(CAMINHO_BANCO, timeout=10)) as conexao:
        with conexao:
            conexao.execute(
                """
                INSERT INTO leituras (
                    estacao_id, sequencia, temperatura_c,
                    umidade_pct, recebido_em
                )
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    dados["estacao_id"],
                    dados["sequencia"],
                    leituras["temperatura_c"],
                    leituras["umidade_pct"],
                    recebido_em,
                ),
            )


def buscar_ultima_leitura():
    with closing(sqlite3.connect(CAMINHO_BANCO, timeout=10)) as conexao:
        conexao.row_factory = sqlite3.Row

        registro = conexao.execute("""
            SELECT *
            FROM leituras
            ORDER BY id DESC
            LIMIT 1
        """).fetchone()

        return dict(registro) if registro is not None else None


if __name__ == "__main__":
    inicializar_banco()
    print("Banco preparado em:", CAMINHO_BANCO)
