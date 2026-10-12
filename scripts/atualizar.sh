#!/usr/bin/env bash
# Puxa o repositorio do GitHub. Se mods.txt, config.env, server.properties ou reiniciar.txt
# mudaram, baixa tudo de novo e reinicia o servidor. Roda sozinho a cada 2 minutos.
set -euo pipefail

BASE=/opt/minecraft
REPO="$BASE/repo"
SERVER="$BASE/server"
MARCA="$BASE/.ultima-versao"

cd "$REPO"
sudo -u minecraft git fetch -q origin
RAMO=${RAMO:-$(sudo -u minecraft git symbolic-ref --short refs/remotes/origin/HEAD | sed 's#^origin/##')}
sudo -u minecraft git reset -q --hard "origin/$RAMO"

ATUAL=$(cat mods.txt config.env server.properties reiniciar.txt scripts/mods.py | sha256sum | cut -d' ' -f1)
ANTERIOR=$(cat "$MARCA" 2>/dev/null || true)
if [ "$ATUAL" = "$ANTERIOR" ] && systemctl is-active -q minecraft; then
  exit 0
fi

echo "Mudancas encontradas, atualizando o servidor"
# Baixa primeiro; se algum mod der erro, o servidor continua rodando como estava.
sudo -u minecraft python3 "$REPO/scripts/mods.py" servidor "$SERVER"

systemctl stop minecraft || true
sudo -u minecraft cp "$REPO/server.properties" "$SERVER/server.properties"
. "$REPO/config.env"
if [ "${ACEITAR_EULA:-false}" = "true" ]; then
  echo "eula=true" | sudo -u minecraft tee "$SERVER/eula.txt" >/dev/null
fi
systemctl start minecraft
echo "$ATUAL" > "$MARCA"
echo "Servidor atualizado e ligado"
