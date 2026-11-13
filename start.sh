#!/bin/sh
set -eu

export PYTHONUNBUFFERED=1

# Inicializa o banco antes de iniciar os dois processos.
python -c 'from banco import inicializar_banco; inicializar_banco()'

exec supervisord -c supervisord.conf