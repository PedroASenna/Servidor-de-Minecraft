#!/usr/bin/env python3
"""Pergunta a um servidor de Minecraft se ele esta online (igual a lista de servidores do jogo).

Uso: ping.py <endereco> [porta]
"""
import json
import socket
import struct
import sys


def varint(n):
    saida = b""
    while True:
        b = n & 0x7F
        n >>= 7
        saida += bytes([b | (0x80 if n else 0)])
        if not n:
            return saida


def ler_varint(sock):
    n = 0
    for i in range(5):
        b = sock.recv(1)[0]
        n |= (b & 0x7F) << (7 * i)
        if not b & 0x80:
            return n
    raise ValueError("varint invalido")


def status(host, porta=25565):
    with socket.create_connection((host, porta), timeout=10) as s:
        host_b = host.encode()
        handshake = varint(0) + varint(-1 & 0xFFFFFFFF) + varint(len(host_b)) + host_b + struct.pack(">H", porta) + varint(1)
        s.sendall(varint(len(handshake)) + handshake)
        s.sendall(varint(1) + varint(0))
        ler_varint(s)  # tamanho do pacote
        ler_varint(s)  # id do pacote
        tamanho = ler_varint(s)
        dados = b""
        while len(dados) < tamanho:
            parte = s.recv(tamanho - len(dados))
            if not parte:
                break
            dados += parte
        return json.loads(dados)


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "localhost"
    porta = int(sys.argv[2]) if len(sys.argv) > 2 else 25565
    resposta = status(host, porta)
    descricao = resposta.get("description")
    if isinstance(descricao, dict):
        descricao = descricao.get("text", "")
    print(f"Online: {resposta['version']['name']} | {descricao} | "
          f"{resposta['players']['online']}/{resposta['players']['max']} jogadores")
