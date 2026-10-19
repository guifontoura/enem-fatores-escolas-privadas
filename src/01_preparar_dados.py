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
# O pipeline do Poliedro já tira o Sistema S pela marcação oficial do Censo (IN_MANT_ESCOLA_PRIVADA_SIST_S).
# Aqui pegamos o que o Censo deixou sem marcar (nome com SESI/SENAI/SESC/SENAC) e a Fundação Bradesco (gratuita).
PADRAO_FORA_DO_MERCADO = r"\b(?:SESI|SENAI|SESC|SENAC)\b|FUNDACAO BRADESCO"


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


def remover_fora_do_mercado_pago(df: pd.DataFrame) -> pd.DataFrame:
    """Exclui escolas gratuitas ou de rede paraestatal (Fundação Bradesco, Sistema S que o Censo não marcou)."""
    marca = df["NO_ENTIDADE"].str.upper().str.contains(PADRAO_FORA_DO_MERCADO, regex=True, na=False)
    print(f"[filtro] fora do mercado pago removidas: {marca.sum()} -> {df.loc[marca, 'NO_ENTIDADE'].tolist()}")
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
    out["bairro"] = out["bairro"].str.title()
    cols = ["codigo_escola", "nome_escola", "codigo_municipio", "cidade", "bairro", "uf", "enem_media_2anos", "enem_2025",
            "enem_2024", "participantes_2025", "participantes_2024", "matriculas_medio", "indice_infra",
            "exame_selecao", "renda_mediana_responsavel", "categoria_privada"]
    return out[cols]


def exportar_mercado_municipio(df: pd.DataFrame, origem: Path) -> None:
    """Por município: vagas no ensino médio em escolas privadas pagas e pessoas em domicílios de renda alta (IBGE 2022)."""
    try:
        todas = pd.read_csv(origem / "data/raw/escolas_privadas_elegiveis_2025_ampliado.csv")
        renda = pd.read_excel(origem / "data/raw/Tabela_10296__1_.xlsx", header=None, skiprows=6,
                              names=["municipio", "classe", "pessoas"])
        correspondencia = pd.read_csv(origem / "data/raw/correspondencia_municipios_ibge.csv")
    except FileNotFoundError as e:
        sys.exit(f"ERRO: arquivo de origem não encontrado ({e.filename}). Rode o pipeline do repo Poliedro antes.")
    # mesmo escopo da base: sem Sistema S, sem escolas gratuitas e sem educação especial; só quem oferece ensino médio
    nomes = todas["NO_ENTIDADE"].str.upper()
    fora = nomes.str.contains(PADRAO_ESPECIAL + "|" + PADRAO_FORA_DO_MERCADO, regex=True, na=False)
    em = todas[(todas["IN_MANT_ESCOLA_PRIVADA_SIST_S"] != 1) & (todas["QT_TUR_MED"] > 0) & ~fora]
    vagas = em.groupby("codigo_municipio").agg(escolas_privadas_em=("CO_ENTIDADE", "size"),
                                               matriculas_privadas_em=("QT_MAT_MED", "sum"))
    # Tabela 10296 (Censo 2022): moradores por classe de renda domiciliar per capita em salários mínimos.
    # "Renda alta" = mais de 3 salários mínimos per capita (a tabela de origem só traz classes acima de 1 salário).
    renda = renda[renda["classe"].notna()].assign(municipio=lambda x: x["municipio"].ffill())
    renda["pessoas"] = pd.to_numeric(renda["pessoas"], errors="coerce").fillna(0)
    alta = renda[renda["classe"].str.contains(r"Mais de (?:3 a 5|5 a 10|10 a 15|15 a 20|20 salários)", regex=True)]
    alta = alta.groupby("municipio")["pessoas"].sum().rename("pessoas_renda_alta").reset_index()
    alta = alta.merge(correspondencia[["codigo_municipio", "chave_nome_uf"]], left_on="municipio", right_on="chave_nome_uf")
    saida = pd.DataFrame({"codigo_municipio": df["codigo_municipio"].unique()}).merge(
        vagas.reset_index(), on="codigo_municipio", how="left").merge(
        alta[["codigo_municipio", "pessoas_renda_alta"]], on="codigo_municipio", how="left")
    destino = Path(__file__).resolve().parent.parent / "data" / "mercado_municipio.csv"
    saida.to_csv(destino, index=False)
    print(f"[ok] {len(saida)} municípios -> {destino.name} | nulos: {saida.isna().sum()[saida.isna().sum() > 0].to_dict()}")


def main(origem: Path) -> None:
    df = carregar_tabela_base(origem)
    print(f"[base] {len(df)} escolas na tabela consolidada")
    df = remover_salas_vitrine(df, origem)
    df = remover_ensino_atipico(df)
    df = remover_fora_do_mercado_pago(df)
    df = selecionar_colunas(df)
    destino = Path(__file__).resolve().parent.parent / "data" / "escolas_modelo.csv"
    df.to_csv(destino, index=False)
    print(f"[ok] {len(df)} escolas salvas em {destino}")
    print(df[["enem_media_2anos", "indice_infra", "matriculas_medio", "renda_mediana_responsavel"]].describe().round(1).T[["min", "mean", "max"]])
    print("nulos por coluna:", df.isna().sum()[df.isna().sum() > 0].to_dict())
    print("exame_selecao:", df["exame_selecao"].value_counts().to_dict())
    exportar_mercado_municipio(df, origem)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
