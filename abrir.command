#!/bin/bash
# Duplo-clique neste arquivo para abrir a apostila no navegador.
# Sobe um pequeno servidor local (melhor experiência: busca, rotas e
# atualização das "Atualidades" funcionam plenamente) e abre o site.
cd "$(dirname "$0")"
PORT=8731
# Se já houver algo na porta, apenas abre o navegador.
if ! curl -s "http://localhost:$PORT" >/dev/null 2>&1; then
  python3 -m http.server "$PORT" >/dev/null 2>&1 &
  sleep 1
fi
open "http://localhost:$PORT"
