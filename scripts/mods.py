#!/usr/bin/env python3
"""Resolve a lista de mods (mods.txt) no Modrinth e baixa os arquivos.

Uso:
  mods.py verificar                 # so confere se todos os mods existem para a versao
  mods.py servidor <pasta>          # baixa o Fabric e os mods de servidor para <pasta>
  mods.py modpack <arquivo.mrpack>  # gera o modpack dos jogadores e a lista para o Aternos (.md)

So usa a biblioteca padrao do Python.
"""
import hashlib
import json
import os
import shutil
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODRINTH = "https://api.modrinth.com/v2"
FABRIC = "https://meta.fabricmc.net/v2"
USER_AGENT = "PedroASenna/Servidor-de-Minecraft (github.com/PedroASenna/Servidor-de-Minecraft)"


def ler_config():
    config = {}
    with open(os.path.join(RAIZ, "config.env"), encoding="utf-8") as f:
        for linha in f:
            linha = linha.split("#", 1)[0].strip()
            if "=" in linha:
                chave, valor = linha.split("=", 1)
                config[chave.strip()] = valor.strip().strip('"')
    return config


def ler_mods():
    mods = []
    with open(os.path.join(RAIZ, "mods.txt"), encoding="utf-8") as f:
        for linha in f:
            linha = linha.split("#", 1)[0].strip()
            if not linha:
                continue
            # Aceita o link inteiro do Modrinth ou so o nome (slug).
            if "modrinth.com/" in linha:
                partes = [p for p in urllib.parse.urlparse(linha).path.split("/") if p]
                linha = partes[1] if len(partes) > 1 else partes[-1]
            mods.append(linha.lower())
    return mods


def baixar_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def baixar_arquivo(url, destino, sha512=None):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=300) as r, open(destino, "wb") as f:
        shutil.copyfileobj(r, f)
    if sha512:
        with open(destino, "rb") as f:
            if hashlib.sha512(f.read()).hexdigest() != sha512:
                raise RuntimeError(f"arquivo corrompido: {url}")


def resolver(versao_mc):
    """Retorna (lista de mods resolvidos, lista de erros)."""
    pedidos = ler_mods()
    resolvidos = {}
    erros = []
    fila = [(slug, None) for slug in pedidos]
    while fila:
        ident, pedido_por = fila.pop(0)
        try:
            projeto = baixar_json(f"{MODRINTH}/project/{urllib.parse.quote(ident)}")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                erros.append(f"'{ident}' nao existe no Modrinth (confira o nome no link do mod)")
                continue
            raise
        if projeto["id"] in resolvidos:
            continue
        params = urllib.parse.urlencode({
            "loaders": json.dumps(["fabric"]),
            "game_versions": json.dumps([versao_mc]),
        })
        versoes = baixar_json(f"{MODRINTH}/project/{projeto['id']}/version?{params}")
        if not versoes:
            origem = f" (dependencia de {pedido_por})" if pedido_por else ""
            erros.append(f"'{projeto['slug']}'{origem} nao tem versao Fabric para o Minecraft {versao_mc}")
            continue
        estaveis = [v for v in versoes if v["version_type"] == "release"]
        versao = (estaveis or versoes)[0]
        arquivo = next((a for a in versao["files"] if a["primary"]), versao["files"][0])
        resolvidos[projeto["id"]] = {
            "slug": projeto["slug"],
            "nome": projeto["title"],
            "versao": versao["version_number"],
            "server_side": projeto["server_side"],
            "client_side": projeto["client_side"],
            "arquivo": arquivo,
        }
        for dep in versao["dependencies"]:
            if dep["dependency_type"] == "required" and dep.get("project_id"):
                if dep["project_id"] not in resolvidos:
                    fila.append((dep["project_id"], projeto["slug"]))
    return list(resolvidos.values()), erros


def no_servidor(mod):
    return mod["server_side"] != "unsupported"


def no_cliente(mod):
    return mod["client_side"] != "unsupported"


def versao_fabric(versao_mc):
    loaders = baixar_json(f"{FABRIC}/versions/loader/{versao_mc}")
    if not loaders:
        raise RuntimeError(f"o Fabric nao suporta o Minecraft {versao_mc}")
    loader = next((l["loader"]["version"] for l in loaders if l["loader"]["stable"]), loaders[0]["loader"]["version"])
    instaladores = baixar_json(f"{FABRIC}/versions/installer")
    instalador = next(i["version"] for i in instaladores if i["stable"])
    return loader, instalador


def mostrar(mods, erros):
    for mod in mods:
        onde = []
        if no_servidor(mod):
            onde.append("servidor")
        if no_cliente(mod):
            onde.append("jogadores")
        print(f"  OK  {mod['nome']} {mod['versao']}  ({' + '.join(onde)})")
    for erro in erros:
        print(f"  ERRO  {erro}")


def cmd_verificar(config):
    mods, erros = resolver(config["VERSAO_MINECRAFT"])
    mostrar(mods, erros)
    return 1 if erros else 0


def cmd_servidor(config, pasta):
    versao_mc = config["VERSAO_MINECRAFT"]
    mods, erros = resolver(versao_mc)
    mostrar(mods, erros)
    if erros:
        return 1
    os.makedirs(pasta, exist_ok=True)

    loader, instalador = versao_fabric(versao_mc)
    print(f"Fabric loader {loader} para Minecraft {versao_mc}")
    baixar_arquivo(
        f"{FABRIC}/versions/loader/{versao_mc}/{loader}/{instalador}/server/jar",
        os.path.join(pasta, "fabric-server-launch.jar"),
    )

    # Baixa tudo numa pasta nova e so depois troca, para nao deixar o servidor pela metade.
    nova = os.path.join(pasta, "mods.novo")
    shutil.rmtree(nova, ignore_errors=True)
    os.makedirs(nova)
    for mod in mods:
        if not no_servidor(mod):
            print(f"  pulando {mod['nome']} (so funciona no jogo dos jogadores)")
            continue
        a = mod["arquivo"]
        baixar_arquivo(a["url"], os.path.join(nova, a["filename"]), a["hashes"]["sha512"])
    antiga = os.path.join(pasta, "mods")
    shutil.rmtree(antiga, ignore_errors=True)
    os.rename(nova, antiga)
    return 0


def cmd_modpack(config, destino):
    versao_mc = config["VERSAO_MINECRAFT"]
    mods, erros = resolver(versao_mc)
    mostrar(mods, erros)
    if erros:
        return 1
    loader, _ = versao_fabric(versao_mc)
    arquivos = []
    for mod in mods:
        if not no_cliente(mod):
            continue
        a = mod["arquivo"]
        arquivos.append({
            "path": f"mods/{a['filename']}",
            "hashes": {"sha1": a["hashes"]["sha1"], "sha512": a["hashes"]["sha512"]},
            "env": {
                "client": "required",
                "server": "unsupported" if not no_servidor(mod) else "required",
            },
            "downloads": [a["url"]],
            "fileSize": a["size"],
        })
    indice = {
        "formatVersion": 1,
        "game": "minecraft",
        "versionId": os.environ.get("VERSAO_MODPACK", "1"),
        "name": config.get("NOME_MODPACK", "Servidor dos Amigos"),
        "files": arquivos,
        "dependencies": {"minecraft": versao_mc, "fabric-loader": loader},
    }
    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("modrinth.index.json", json.dumps(indice, indent=2))
    print(f"Modpack gerado: {destino}")

    # Lista do que instalar no servidor do Aternos (aba Mods), com as dependencias.
    linhas = [
        f"## Mods para instalar no Aternos (Fabric {versao_mc})",
        "",
        "No Aternos, abra **Mods**, pesquise cada nome abaixo e clique em **Install**.",
        "",
    ]
    for mod in mods:
        if no_servidor(mod):
            linhas.append(f"- [ ] **{mod['nome']}** (versão {mod['versao']}): https://modrinth.com/mod/{mod['slug']}")
    so_jogo = [m for m in mods if not no_servidor(m)]
    if so_jogo:
        linhas += ["", "Estes ficam só no jogo, não instale no Aternos:", ""]
        linhas += [f"- {m['nome']}" for m in so_jogo]
    linhas += [
        "",
        "## Jogadores",
        "",
        "Baixe `modpack.mrpack` abaixo e importe no Modrinth App (**+ → Import from file**).",
    ]
    lista = os.path.splitext(destino)[0] + "-aternos.md"
    with open(lista, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas) + "\n")
    print(f"Lista para o Aternos: {lista}")
    return 0


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    config = ler_config()
    comando = sys.argv[1]
    if comando == "verificar":
        return cmd_verificar(config)
    if comando == "servidor" and len(sys.argv) == 3:
        return cmd_servidor(config, sys.argv[2])
    if comando == "modpack" and len(sys.argv) == 3:
        return cmd_modpack(config, sys.argv[2])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
