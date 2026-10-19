"""Baixa do IBGE os dados por município usados na página de cidades. Cada arquivo só é baixado se ainda não existir.

1. data/populacao_municipios.csv: população total e de 15 a 17 anos (Censo 2022, SIDRA, tabela 9514).
2. data/regioes_imediatas.csv: Região Geográfica Imediata de cada município (API de localidades). Serve para
   separar cidades-polo de cidades vizinhas, cujos alunos estudam no polo e distorcem a conta de vagas.
Uso: python src/00_baixar_populacao.py   (precisa de data/escolas_modelo.csv para saber quais municípios buscar)
"""
import time
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "data" / "populacao_municipios.csv"
SAIDA_REGIOES = RAIZ / "data" / "regioes_imediatas.csv"
URL_MUNICIPIOS = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
# Códigos conferidos nos metadados da tabela 9514 (classificação 287 = Idade; variável 93 = população residente):
# 100362 = Total, 6572 = 15 anos, 6573 = 16 anos, 6574 = 17 anos.
IDADES = {"100362": "populacao_total", "6572": "idade_15", "6573": "idade_16", "6574": "idade_17"}
LOTE = 40  # municípios por chamada, para a URL não ficar longa demais


def baixar_lote(codigos: list) -> pd.DataFrame:
    """Uma chamada à API do SIDRA para um lote de municípios; devolve linhas município x idade."""
    url = (f"https://apisidra.ibge.gov.br/values/t/9514/n6/{','.join(codigos)}/v/93/p/2022/"
           f"c2/6794/c287/{','.join(IDADES)}")
    try:
        resposta = requests.get(url, timeout=90)
        resposta.raise_for_status()
        dados = resposta.json()
    except (requests.RequestException, ValueError) as erro:
        raise SystemExit(f"ERRO ao consultar o SIDRA ({type(erro).__name__}): {erro}\nURL: {url}")
    return pd.DataFrame(dados[1:])  # a primeira linha é o cabeçalho descritivo da API


def baixar_regioes_imediatas(codigos_estudo: set) -> None:
    """Região Geográfica Imediata (área de influência de uma cidade-polo) dos municípios do estudo."""
    if SAIDA_REGIOES.exists():
        print(f"[cache] {SAIDA_REGIOES.name} já existe, nada a baixar.")
        return
    try:
        resposta = requests.get(URL_MUNICIPIOS, timeout=120)
        resposta.raise_for_status()
        municipios = resposta.json()
    except (requests.RequestException, ValueError) as erro:
        raise SystemExit(f"ERRO ao consultar a API de localidades ({type(erro).__name__}): {erro}")
    if "regiao-imediata" not in municipios[0]:
        raise SystemExit(f"ERRO: campo 'regiao-imediata' ausente na resposta. Campos recebidos: {list(municipios[0])}")
    linhas = [{"codigo_municipio": m["id"], "regiao_imediata_id": m["regiao-imediata"]["id"],
               "regiao_imediata": m["regiao-imediata"]["nome"]} for m in municipios if m["id"] in codigos_estudo]
    saida = pd.DataFrame(linhas)
    saida.to_csv(SAIDA_REGIOES, index=False)
    print(f"[ok] {len(saida)} municípios -> {SAIDA_REGIOES.name} ({saida['regiao_imediata_id'].nunique()} regiões imediatas)")


def baixar_populacao(codigos: list) -> None:
    """População total e de 15 a 17 anos, via SIDRA."""
    if SAIDA.exists():
        print(f"[cache] {SAIDA.name} já existe, nada a baixar.")
        return
    partes = []
    for i in range(0, len(codigos), LOTE):
        partes.append(baixar_lote(codigos[i:i + LOTE]))
        print(f"  lote {i // LOTE + 1}: {len(partes[-1])} linhas")
        time.sleep(0.3)
    bruto = pd.concat(partes, ignore_index=True)
    bruto["valor"] = pd.to_numeric(bruto["V"], errors="coerce")
    larga = bruto.pivot_table(index="D1C", columns="D5C", values="valor", aggfunc="first").rename(columns=IDADES)
    larga["jovens_15_17"] = larga["idade_15"] + larga["idade_16"] + larga["idade_17"]
    saida = larga[["populacao_total", "jovens_15_17"]].reset_index().rename(columns={"D1C": "codigo_municipio"})
    saida["codigo_municipio"] = saida["codigo_municipio"].astype(int)
    saida.to_csv(SAIDA, index=False)
    print(f"[ok] {len(saida)} municípios -> {SAIDA.name}")
    print(saida.describe().round(0).loc[["min", "mean", "max"]])
    faltam = set(int(c) for c in codigos) - set(saida["codigo_municipio"])
    print("municípios sem dado:", sorted(faltam) if faltam else "nenhum")


def main() -> None:
    municipios = pd.read_csv(RAIZ / "data" / "escolas_modelo.csv", usecols=["codigo_municipio"])["codigo_municipio"]
    codigos = sorted({str(int(c)) for c in municipios})
    baixar_populacao(codigos)
    baixar_regioes_imediatas({int(c) for c in codigos})


if __name__ == "__main__":
    main()
