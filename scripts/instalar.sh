#!/usr/bin/env bash
# Instala o servidor numa maquina Ubuntu nova (rode uma vez so, como root).
#   curl -fsSL https://raw.githubusercontent.com/PedroASenna/Servidor-de-Minecraft/Pedro/scripts/instalar.sh | sudo bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/PedroASenna/Servidor-de-Minecraft.git}"
BASE=/opt/minecraft

echo "==> Instalando Java 21, git e python"
export DEBIAN_FRONTEND=noninteractive
apt-get update -q
apt-get install -y -q openjdk-21-jre-headless git python3 curl iptables-persistent

echo "==> Liberando a porta 25565 no firewall da maquina"
if ! iptables -C INPUT -p tcp --dport 25565 -j ACCEPT 2>/dev/null; then
  iptables -I INPUT -p tcp --dport 25565 -j ACCEPT
fi
netfilter-persistent save

echo "==> Criando usuario minecraft e baixando o repositorio"
id minecraft >/dev/null 2>&1 || useradd --system --home "$BASE" --shell /usr/sbin/nologin minecraft
mkdir -p "$BASE"
if [ ! -d "$BASE/repo/.git" ]; then
  git clone ${RAMO:+-b "$RAMO"} "$REPO_URL" "$BASE/repo"
fi
mkdir -p "$BASE/server"
# Ramo do GitHub que o servidor segue (padrao: o ramo principal do repositorio).
if [ -n "${RAMO:-}" ]; then echo "$RAMO" > "$BASE/ramo"; fi
chown -R minecraft:minecraft "$BASE"

JAVA="/usr/lib/jvm/java-21-openjdk-$(dpkg --print-architecture)/bin/java"

echo "==> Criando os servicos"
cat > /etc/systemd/system/minecraft.service <<UNIT
[Unit]
Description=Servidor de Minecraft (Fabric)
After=network-online.target
Wants=network-online.target

[Service]
User=minecraft
WorkingDirectory=$BASE/server
EnvironmentFile=$BASE/repo/config.env
ExecStart=$JAVA -Xms\${MEMORIA} -Xmx\${MEMORIA} -jar fabric-server-launch.jar nogui
Restart=on-failure
RestartSec=10
TimeoutStopSec=120

[Install]
WantedBy=multi-user.target
UNIT

cat > /etc/systemd/system/minecraft-atualizar.service <<UNIT
[Unit]
Description=Atualiza mods e configuracao do servidor a partir do GitHub

[Service]
Type=oneshot
ExecStart=/bin/bash $BASE/repo/scripts/atualizar.sh
UNIT

cat > /etc/systemd/system/minecraft-atualizar.timer <<UNIT
[Unit]
Description=Confere o GitHub a cada 2 minutos

[Timer]
OnBootSec=30s
OnUnitActiveSec=2min

[Install]
WantedBy=timers.target
UNIT

systemctl daemon-reload
systemctl enable minecraft.service minecraft-atualizar.timer

echo "==> Baixando Fabric e mods e ligando o servidor (pode levar alguns minutos)"
bash "$BASE/repo/scripts/atualizar.sh"
systemctl start minecraft-atualizar.timer

IP=$(curl -fsS https://api.ipify.org || echo "SEU-IP")
echo
echo "Pronto! Endereco para colocar no Minecraft: $IP"
