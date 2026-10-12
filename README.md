# Servidor de Minecraft com mods

Servidor de Minecraft **Java 1.21.1 com Fabric**, ligado 24 horas numa máquina grátis da Oracle Cloud.
Você controla tudo por este repositório:

- **`mods.txt`**: a lista de mods. Adicionou uma linha, o servidor instala sozinho.
- **`config.env`**: versão do Minecraft e memória.
- **`server.properties`**: nome do servidor, dificuldade, número de jogadores etc.
- **`reiniciar.txt`**: mude qualquer coisa nele para reiniciar o servidor.

A máquina confere o GitHub a cada 2 minutos. Quando algum desses arquivos muda, ela baixa os mods do
[Modrinth](https://modrinth.com), reinicia o servidor e pronto. O endereço (IP) nunca muda.

> **Por que não rodar o servidor no GitHub Actions?** Os
> [termos do GitHub](https://docs.github.com/en/site-policy/github-terms/github-terms-for-additional-products-and-features#actions)
> proíbem usar o Actions para algo que não seja testar, compilar ou publicar o projeto, e cada execução
> morre em no máximo 6 horas. Aqui o Actions só **testa** a lista de mods e **publica** o modpack; o
> servidor roda na Oracle, que é grátis para sempre.

## Primeira vez (uns 20 minutos, só uma vez)

### 1. Criar a conta grátis da Oracle

1. Entre em <https://www.oracle.com/br/cloud/free/> e clique em **Comece gratuitamente**.
2. Na região, escolha **Brazil East (Sao Paulo)** (não dá para trocar depois).
3. Ela pede um cartão de crédito só para confirmar quem você é. A conta "Always Free" não cobra nada.

### 2. Criar a máquina

1. No painel da Oracle: **Compute → Instances → Create instance**.
2. **Image**: troque para **Canonical Ubuntu 24.04**.
3. **Shape**: **Ampere → VM.Standard.A1.Flex**, com **2 OCPUs** e **12 GB** de memória (é o limite grátis).
4. Em **Add SSH keys**, clique em **Save private key** (guarde o arquivo).
5. Clique em **Create**. Se aparecer *Out of capacity*, tente de novo mais tarde ou troque o
   *Availability domain*.

### 3. Abrir a porta do Minecraft

1. Na página da máquina, clique no nome da **Subnet** → **Security Lists** → **Default Security List**.
2. **Add Ingress Rules**: Source CIDR `0.0.0.0/0`, IP Protocol **TCP**, Destination Port Range **25565**. Salve.

### 4. Instalar o servidor

No seu computador, abra o **PowerShell** (Windows) ou o **Terminal** (Mac/Linux) e entre na máquina,
trocando o caminho da chave e o **Public IP** que aparece na página dela:

```bash
ssh -i C:\Users\SEU-USUARIO\Downloads\ssh-key.key ubuntu@IP-DA-MAQUINA
```

Já dentro da máquina, cole este comando:

```bash
curl -fsSL https://raw.githubusercontent.com/PedroASenna/Servidor-de-Minecraft/Pedro/scripts/instalar.sh | sudo bash
```

No fim aparece: **`Pronto! Endereço para colocar no Minecraft: 123.45.67.89`**. É o mesmo
**Public IP** que aparece na página da máquina.

## Entrar no servidor

Você e seus amigos precisam do Minecraft **1.21.1 com Fabric** e dos mesmos mods. O jeito fácil:

1. Instale o [Modrinth App](https://modrinth.com/app).
2. Baixe o modpack: <https://github.com/PedroASenna/Servidor-de-Minecraft/releases/latest/download/modpack.mrpack>
3. No Modrinth App: **+ (Create instance) → Import from file** e escolha o arquivo baixado.
4. Jogue essa instância → **Multiplayer → Add Server** → cole o IP do servidor.

## Adicionar um mod

1. Ache o mod no [Modrinth](https://modrinth.com/mods) e confira se ele tem versão **Fabric 1.21.1**.
2. Aqui no GitHub, abra **`mods.txt`**, clique no lápis ✏️, cole o link do mod numa linha nova
   (ex.: `https://modrinth.com/mod/waystones`) e clique em **Commit changes**.
3. Em até 2 minutos o servidor reinicia com o mod. Na aba **Actions** aparece um ✅ quando o teste passa
   (se der ❌, abra para ver qual mod deu erro).
4. Seus amigos baixam o modpack de novo (mesmo link) e importam por cima.

Para **remover** um mod, apague a linha. Mods só de visual (ex.: `sodium`, `iris`) podem ir na lista:
eles vão só para o modpack dos jogadores, não para o servidor.

## Problemas comuns

- **Não conecta**: confira a regra da porta 25565 (passo 3) e se a versão do jogo é a 1.21.1 com Fabric.
- **Ver o log do servidor**: no terminal da máquina, `sudo journalctl -u minecraft -f`.
- **Ver se atualizou**: `sudo journalctl -u minecraft-atualizar -n 50`.
- **Mundo**: fica em `/opt/minecraft/server/world` na máquina.
- A Oracle pode desligar máquinas grátis que ficam paradas por 7 dias. Com o servidor ligado usando
  8 GB de memória isso não acontece; se acontecer, é só ligar a máquina de novo no painel.
