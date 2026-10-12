# Servidor de Minecraft com mods

Servidor de Minecraft **Java 1.21.1 com Fabric** para jogar com os amigos.
Você controla os mods por este repositório, no arquivo **`mods.txt`**.

## Como funciona (Aternos)

O servidor roda no [Aternos](https://aternos.org), que é grátis e não pede cartão. Este repositório cuida do resto:
toda vez que você muda o `mods.txt`, o GitHub confere se os mods existem para a versão 1.21.1 e publica em
**[Releases → Modpack do servidor](https://github.com/PedroASenna/Servidor-de-Minecraft/releases/latest)**:

- a **lista de mods para instalar no Aternos**, já com as dependências;
- o **`modpack.mrpack`** para você e seus amigos importarem no Modrinth App.

### Criar o servidor (uma vez só)

1. Em <https://aternos.org>, crie a conta e clique em **Create server** (Java Edition). Escolha um nome, por exemplo `pedrocraft`.
   O endereço do servidor será **`pedrocraft.aternos.me`**.
2. Em **Software**, escolha **Fabric** na versão **1.21.1**.
3. Em **Mods**, instale cada mod da [lista do Release](https://github.com/PedroASenna/Servidor-de-Minecraft/releases/latest).
4. Clique em **Start**.

### Adicionar um mod

1. No GitHub, abra **`mods.txt`**, clique no lápis ✏️, cole o link do mod no Modrinth numa linha nova e clique em **Commit changes**.
2. Espere o ✅ na aba **Actions**. Se der ❌, abra o erro para ver qual mod não tem versão 1.21.1.
3. No Aternos, em **Mods**, instale o mod novo (a lista do Release mostra o que falta).
4. Todo mundo baixa o [modpack](https://github.com/PedroASenna/Servidor-de-Minecraft/releases/latest/download/modpack.mrpack) de novo e importa no Modrinth App.

### Jogar

1. Instale o [Modrinth App](https://modrinth.com/app) e importe o
   [modpack](https://github.com/PedroASenna/Servidor-de-Minecraft/releases/latest/download/modpack.mrpack) (**+ → Import from file**).
2. Alguém clica em **Start** no site do Aternos. O servidor desliga sozinho quando fica vazio.
   Em **Access** você dá esse acesso aos seus amigos.
3. No jogo: **Multiplayer → Add Server** → `pedrocraft.aternos.me`.

## Opção 2: servidor 24h na Oracle Cloud (automático)

Se um dia a Oracle aceitar seu cadastro, o servidor pode ficar ligado 24h e instalar os mods sozinho a partir do `mods.txt`.

### Primeira vez (uns 20 minutos, só uma vez)

#### 1. Criar a conta grátis da Oracle

1. Entre em <https://www.oracle.com/br/cloud/free/> e clique em **Comece gratuitamente**.
2. Na região, escolha **Brazil East (Sao Paulo)** (não dá para trocar depois).
3. Ela pede um cartão de crédito só para confirmar quem você é. A conta "Always Free" não cobra nada.

#### 2. Criar a máquina

1. No painel da Oracle: **Compute → Instances → Create instance**.
2. **Image**: troque para **Canonical Ubuntu 24.04**.
3. **Shape**: **Ampere → VM.Standard.A1.Flex**, com **2 OCPUs** e **12 GB** de memória (é o limite grátis).
4. Em **Add SSH keys**, clique em **Save private key** (guarde o arquivo).
5. Clique em **Create**. Se aparecer *Out of capacity*, tente de novo mais tarde ou troque o
   *Availability domain*.

#### 3. Abrir a porta do Minecraft

1. Na página da máquina, clique no nome da **Subnet** → **Security Lists** → **Default Security List**.
2. **Add Ingress Rules**: Source CIDR `0.0.0.0/0`, IP Protocol **TCP**, Destination Port Range **25565**. Salve.

#### 4. Instalar o servidor

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

### Entrar no servidor (Oracle)

Você e seus amigos precisam do Minecraft **1.21.1 com Fabric** e dos mesmos mods. O jeito fácil:

1. Instale o [Modrinth App](https://modrinth.com/app).
2. Baixe o modpack: <https://github.com/PedroASenna/Servidor-de-Minecraft/releases/latest/download/modpack.mrpack>
3. No Modrinth App: **+ (Create instance) → Import from file** e escolha o arquivo baixado.
4. Jogue essa instância → **Multiplayer → Add Server** → cole o IP do servidor.

### Adicionar um mod (Oracle)

1. Ache o mod no [Modrinth](https://modrinth.com/mods) e confira se ele tem versão **Fabric 1.21.1**.
2. Aqui no GitHub, abra **`mods.txt`**, clique no lápis ✏️, cole o link do mod numa linha nova
   (ex.: `https://modrinth.com/mod/waystones`) e clique em **Commit changes**.
3. Em até 2 minutos o servidor reinicia com o mod. Na aba **Actions** aparece um ✅ quando o teste passa
   (se der ❌, abra para ver qual mod deu erro).
4. Seus amigos baixam o modpack de novo (mesmo link) e importam por cima.

Para **remover** um mod, apague a linha. Mods só de visual (ex.: `sodium`, `iris`) podem ir na lista:
eles vão só para o modpack dos jogadores, não para o servidor.

### Problemas comuns (Oracle)

- **Não conecta**: confira a regra da porta 25565 (passo 3) e se a versão do jogo é a 1.21.1 com Fabric.
- **Ver o log do servidor**: no terminal da máquina, `sudo journalctl -u minecraft -f`.
- **Ver se atualizou**: `sudo journalctl -u minecraft-atualizar -n 50`.
- **Mundo**: fica em `/opt/minecraft/server/world` na máquina.
- A Oracle pode desligar máquinas grátis que ficam paradas por 7 dias. Com o servidor ligado usando
  8 GB de memória isso não acontece; se acontecer, é só ligar a máquina de novo no painel.
