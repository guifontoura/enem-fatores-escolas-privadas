"""Gera outputs/looker_escolas.csv: a tabela de escolas com colunas prontas para filtros e gráficos no Looker Studio.

Entrada: outputs/escolas_resultados.csv (gerado pelo notebook). Uso: python src/02_preparar_looker.py
"""
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
REGIAO_POR_UF = {
    "AC": "Norte", "AM": "Norte", "AP": "Norte", "PA": "Norte", "RO": "Norte", "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste", "PB": "Nordeste", "PE": "Nordeste",
    "PI": "Nordeste", "RN": "Nordeste", "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MS": "Centro-Oeste", "MT": "Centro-Oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul",
}


def carregar_resultados() -> pd.DataFrame:
    """Lê a tabela de escolas gerada pelo notebook."""
    caminho = RAIZ / "outputs" / "escolas_resultados.csv"
    try:
        return pd.read_csv(caminho)
    except FileNotFoundError:
        raise SystemExit(f"ERRO: {caminho} não existe. Execute o notebook 01_eda_modelagem.ipynb antes.")


def adicionar_colunas_de_filtro(df: pd.DataFrame) -> pd.DataFrame:
    """Região, faixas de renda/porte e rótulos legíveis para usar como filtros no painel."""
    df = df.copy()
    df["regiao"] = df["uf"].map(REGIAO_POR_UF)
    df["faixa_renda"] = pd.qcut(df["renda_mediana_responsavel"], 4, duplicates="drop",
                                labels=["1. Renda mais baixa", "2. Média-baixa", "3. Média-alta", "4. Renda mais alta"])
    df["faixa_porte"] = pd.cut(df["matriculas_medio"], [0, 75, 150, 300, 10_000],
                               labels=["1. Até 75 matrículas", "2. 76 a 150", "3. 151 a 300", "4. Mais de 300"])
    df["seletividade"] = df["exame_selecao"].map({1.0: "Seleciona alunos", 0.0: "Não seleciona"})
    df["situacao_vs_esperado"] = pd.cut(df["residuo_cv"], [-1000, -40, 40, 1000],
                                        labels=["Abaixo do esperado (> 40 pts)", "Dentro do esperado", "Acima do esperado (> 40 pts)"])
    return df


def main() -> None:
    df = adicionar_colunas_de_filtro(carregar_resultados())
    destino = RAIZ / "outputs" / "looker_escolas.csv"
    df.round(2).to_csv(destino, index=False)
    print(f"[ok] {len(df)} escolas -> {destino}")
    print("nulos:", df.isna().sum()[df.isna().sum() > 0].to_dict())
    for col in ["regiao", "faixa_renda", "faixa_porte", "seletividade", "situacao_vs_esperado"]:
        print(f"{col}:", df[col].value_counts().sort_index().to_dict())


if __name__ == "__main__":
    main()
