"""Prepara a base do projeto: escolas privadas com ENEM confiável, só colunas relevantes à pergunta analítica.

Entrada: arquivos gerados pelo pipeline do repositório poliedro-inteligencia-mercado (dados públicos:
Censo Escolar INEP 2025, microdados ENEM 2024/2025, Censo IBGE 2022). Saída: data/escolas_modelo.csv.
Uso: python src/01_preparar_dados.py <pasta_do_repo_poliedro>
"""
import re
import sys
from pathlib import Path

import pandas as pd

PADRAO_ESPECIAL = r"FAMILIA AGRICOLA|SMALDONE|APAE|ESPECIAL|SURDO|CEGO|DEFICIENTE|ALTERNANCIA|AGROTECNIC"


def carregar_tabela_base(origem: Path) -> pd.DataFrame:
    """Tabela consolidada (4.444 escolas) + colunas do Censo que ela não traz."""
    try:
        base = pd.read_csv(origem / "data/outputs/29_universo_completo_powerbi.csv", sep=";", decimal=",")
        censo = pd.read_csv(origem / "data/raw/escolas_privadas_elegiveis_2025_ampliado.csv",
                            usecols=["CO_ENTIDADE", "TP_CATEGORIA_ESCOLA_PRIVADA", "IN_EXAME_SELECAO"])
    except FileNotFoundError as e:
        sys.exit(f"ERRO: arquivo de origem não encontrado ({e.filename}). Rode o pipeline do repo Poliedro antes.")
    censo = censo.rename(columns={"CO_ENTIDADE": "codigo_escola"})
    return base.merge(censo, on="codigo_escola", how="left", validate="1:1")


def remover_salas_vitrine(df: pd.DataFrame, origem: Path) -> pd.DataFrame:
    """Exclui unidades pequenas sinalizadas como 'sala vitrine' (casa por nome E município, não só nome)."""
    v = pd.read_csv(origem / "data/outputs/13_salas_vitrine_suspeitas.csv")
    chaves = set(zip(v["escola_pequena"].str.upper(), v["codigo_municipio"]))
    marca = [(n.upper(), m) in chaves for n, m in zip(df["NO_ENTIDADE"], df["codigo_municipio"])]
    print(f"[filtro] salas vitrine removidas: {sum(marca)}")
    return df[[not x for x in marca]]


def remover_ensino_atipico(df: pd.DataFrame) -> pd.DataFrame:
    """Exclui educação especial e pedagogia da alternância (ENEM não é comparável a escola regular)."""
    marca = df["NO_ENTIDADE"].str.upper().str.contains(PADRAO_ESPECIAL, regex=True, na=False)
    print(f"[filtro] ensino atípico removido: {marca.sum()} -> {df.loc[marca, 'NO_ENTIDADE'].tolist()}")
    return df[~marca]


def selecionar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    """Só o que responde à pergunta analítica; sem colunas comerciais."""
    out = df.rename(columns={
        "NO_ENTIDADE": "nome_escola", "UF": "uf", "enem_media_geral": "enem_2025",
        "enem_media_geral_2024": "enem_2024", "qtd_participantes_enem": "participantes_2025",
        "qtd_participantes_enem_2024": "participantes_2024", "QT_MAT_MED": "matriculas_medio",
        "IN_EXAME_SELECAO": "exame_selecao", "TP_CATEGORIA_ESCOLA_PRIVADA": "categoria_privada",
    })
    # INEP codifica "não se aplica/não informado" como 9 em IN_EXAME_SELECAO; tratar como número distorceria a análise
    out["exame_selecao"] = out["exame_selecao"].where(out["exame_selecao"].isin([0, 1]))
    # renda_mediana_responsavel: mediana da renda do responsável (IBGE, Censo 2022) no bairro da escola; se o bairro
    # não casa, no distrito. Não existe coluna confiável do nível usado em cada escola (granularidade_geo só rotula SP/RJ).
    cols = ["codigo_escola", "nome_escola", "codigo_municipio", "cidade", "uf", "enem_media_2anos", "enem_2025",
            "enem_2024", "participantes_2025", "participantes_2024", "matriculas_medio", "indice_infra",
            "exame_selecao", "renda_mediana_responsavel", "categoria_privada"]
    return out[cols]


def main(origem: Path) -> None:
    df = carregar_tabela_base(origem)
    print(f"[base] {len(df)} escolas na tabela consolidada")
    df = remover_salas_vitrine(df, origem)
    df = remover_ensino_atipico(df)
    df = selecionar_colunas(df)
    destino = Path(__file__).resolve().parent.parent / "data" / "escolas_modelo.csv"
    df.to_csv(destino, index=False)
    print(f"[ok] {len(df)} escolas salvas em {destino}")
    print(df[["enem_media_2anos", "indice_infra", "matriculas_medio", "renda_mediana_responsavel"]].describe().round(1).T[["min", "mean", "max"]])
    print("nulos por coluna:", df.isna().sum()[df.isna().sum() > 0].to_dict())
    print("exame_selecao:", df["exame_selecao"].value_counts().to_dict())


if __name__ == "__main__":
    main(Path(sys.argv[1]))
