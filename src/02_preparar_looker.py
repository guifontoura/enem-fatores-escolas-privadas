"""Gera as tabelas do dashboard (Looker Studio) a partir dos resultados do notebook.

Saídas em outputs/: looker_escolas.csv (uma linha por escola), looker_cidades.csv (página 4),
looker_coeficientes.csv e looker_metricas.csv (página 2), looker_grupos.csv (página 3).
Entrada: arquivos gerados pelo notebook. Uso: python src/02_preparar_looker.py
"""
from pathlib import Path

import unicodedata

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

RAIZ = Path(__file__).resolve().parent.parent
REGIAO_POR_UF = {
    "AC": "Norte", "AM": "Norte", "AP": "Norte", "PA": "Norte", "RO": "Norte", "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste", "PB": "Nordeste", "PE": "Nordeste",
    "PI": "Nordeste", "RN": "Nordeste", "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MS": "Centro-Oeste", "MT": "Centro-Oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul",
}

# Página 4: bairro de renda alta = renda mediana 20% acima da mediana da própria cidade (R$ 8 mil não serve para
# cidades médias). Só cidades com 5+ escolas, para haver o que comparar dentro da cidade.
MIN_ESCOLAS_CIDADE = 5
RENDA_RELATIVA_ALTA = 1.2
PCT_RENDA_ALTA_MINIMA = 10  # % da população em domicílios com mais de 3 salários mínimos per capita
LIMIAR_COBERTURA = 0.75  # em desvios-padrão da diferença entre cobertura real e esperada


def carregar_resultados() -> pd.DataFrame:
    """Lê a tabela de escolas gerada pelo notebook."""
    caminho = RAIZ / "outputs" / "escolas_resultados.csv"
    try:
        return pd.read_csv(caminho)
    except FileNotFoundError:
        raise SystemExit(f"ERRO: {caminho} não existe. Execute o notebook 01_eda_modelagem.ipynb antes.")


def formatar_nome(nome: str) -> str:
    """'COLEGIO MARISTA E MUNICIPAL' -> 'Colegio Marista e Municipal' (INEP entrega tudo em maiúsculas e sem acento)."""
    minusculas = {"e", "de", "da", "do", "das", "dos"}
    romanos = {"Ii", "Iii", "Iv", "Vi", "Vii", "Viii", "Ix"}
    palavras = str(nome).title().split()
    return " ".join(p.upper() if p in romanos else p.lower() if p.lower() in minusculas and i > 0 else p
                    for i, p in enumerate(palavras))


def adicionar_colunas_de_filtro(df: pd.DataFrame) -> pd.DataFrame:
    """Região, faixas de renda/porte e rótulos legíveis para usar como filtros no painel."""
    df = df.copy()
    df["nome_escola"] = df["nome_escola"].map(formatar_nome)
    df["regiao"] = df["uf"].map(REGIAO_POR_UF)
    df["faixa_renda"] = pd.cut(df["renda_mediana_responsavel"], [0, 2500, 4000, 6000, 1e9],
                               labels=["1. Até R$ 2,5 mil", "2. R$ 2,5 a 4 mil", "3. R$ 4 a 6 mil", "4. Mais de R$ 6 mil"])
    df["faixa_porte"] = pd.cut(df["matriculas_medio"], [0, 75, 150, 300, 10_000],
                               labels=["1. Até 75 alunos", "2. 76 a 150", "3. 151 a 300", "4. Mais de 300"])
    df["seletividade"] = df["exame_selecao"].map({1.0: "Seleciona alunos", 0.0: "Não seleciona"})
    df["bairro"] = df["bairro"].fillna("Não informado")
    return df  # situacao_vs_esperado (dois anos, ±30 pts) já vem pronta do notebook


def gerar_tabelas_modelo() -> None:
    """Coeficientes em unidades legíveis (pontos de ENEM) e métricas com nomes de coluna simples, para a página 2."""
    coef = pd.read_csv(RAIZ / "outputs" / "coeficientes.csv")
    # fator de conversão: renda vem por R$ 1 (vira por R$ 1.000); porte vem por unidade de log (vira "dobrar os alunos")
    escala = {
        "Renda do responsável": (1000, "pontos a cada R$ 1.000 a mais de renda do bairro"),
        "Porte (log matrículas)": (0.6931, "pontos ao dobrar o número de alunos"),
        "Exame de seleção": (1, "pontos para escolas que selecionam alunos"),
        "Infraestrutura": (1, "pontos por nível de infraestrutura (0 a 5)"),
    }
    linhas = []
    for _, r in coef.iterrows():
        k, texto = escala[r["variavel"]]
        linhas.append({
            "fator": r["variavel"].replace(" (log matrículas)", " (alunos)"),
            "peso_relativo": round(r["coef_padronizado"], 2),
            "efeito_pontos": round(r["coef_bruto_pontos"] * k, 1),
            "ic_inferior": round(r["ic95_inf"] * k, 1),
            "ic_superior": round(r["ic95_sup"] * k, 1),
            "interpretacao": texto,
        })
    tabela = pd.DataFrame(linhas)
    # colunas em texto (vírgula decimal, sinal de +) para a tabela do Looker sair pronta, sem formatação manual
    br = lambda x, casas=1: f"{x:.{casas}f}".replace(".", ",")
    rotulo = {
        "Exame de seleção": "Passa a selecionar alunos na entrada",
        "Porte (alunos)": "Dobra o número de alunos (ex.: 100 → 200)",
        "Renda do responsável": "Bairro com R$ 1.000 a mais de renda",
        "Infraestrutura": "Sobe 1 nível de infraestrutura (0 a 5)",
    }
    tabela["o_que_muda"] = tabela["fator"].map(rotulo)
    # o sufixo " pts" impede o Looker de ler o texto como número ("+15,8" virava 158 com a vírgula de milhar)
    tabela["pontos_txt"] = "+" + tabela["efeito_pontos"].map(br) + " pts"
    tabela["faixa_txt"] = tabela["ic_inferior"].map(br) + " a " + tabela["ic_superior"].map(br)
    tabela["fator_exibicao"] = tabela["fator"].replace({"Renda do responsável": "Renda do bairro", "Porte (alunos)": "Porte da escola",
                                                        "Exame de seleção": "Seleciona alunos"})
    tabela["grupo_fator"] = tabela["fator"].map(lambda f: "Infraestrutura" if f == "Infraestrutura" else "Outros fatores")
    tabela.sort_values("efeito_pontos", ascending=False).to_csv(RAIZ / "outputs" / "looker_coeficientes.csv", index=False)

    met = pd.read_csv(RAIZ / "outputs" / "metricas_modelos.csv")
    met.columns = ["modelo", "r2", "rmse", "mae", "r2_validacao_aleatoria"]
    met["modelo_exibicao"] = met["modelo"].replace({"Regressão linear": "Regressão linear (usado)", "Baseline (média)": "Chutar sempre a média"})
    met["r2_txt"] = met["r2"].map(lambda x: br(x, 3).replace("-", "−"))
    met["mae_txt"] = met["mae"].map(br) + " pts"
    met.to_csv(RAIZ / "outputs" / "looker_metricas.csv", index=False)
    print("[ok] looker_coeficientes.csv e looker_metricas.csv gerados")


def copiar_grupos() -> None:
    """Tabela da página 3 (tipo de instituição x situação), calculada no notebook."""
    origem = RAIZ / "outputs" / "grupos_instituicao.csv"
    try:
        pd.read_csv(origem).to_csv(RAIZ / "outputs" / "looker_grupos.csv", index=False)
    except FileNotFoundError:
        raise SystemExit(f"ERRO: {origem} não existe. Execute o notebook 01_eda_modelagem.ipynb antes.")
    print("[ok] looker_grupos.csv gerado")


def marcar_bairros_de_renda_alta(escolas: pd.DataFrame) -> pd.DataFrame:
    """Junta município e participantes do ENEM; marca as escolas em bairro de renda alta (relativa à cidade)."""
    modelo = pd.read_csv(RAIZ / "data" / "escolas_modelo.csv",
                         usecols=["codigo_escola", "codigo_municipio", "participantes_2025", "participantes_2024"])
    d = escolas.merge(modelo, on="codigo_escola", how="left", validate="1:1")
    # tamanho do público: média dos dois anos de alunos que fizeram o ENEM na escola (só 2025 quando falta 2024)
    d["alunos_enem_ano"] = d[["participantes_2025", "participantes_2024"]].mean(axis=1).round(1)
    por_cidade = d.groupby("codigo_municipio")
    d["escolas_na_cidade"] = por_cidade["codigo_escola"].transform("size")
    d["renda_relativa"] = d["renda_mediana_responsavel"] / por_cidade["renda_mediana_responsavel"].transform("median")
    alta = (d["escolas_na_cidade"] >= MIN_ESCOLAS_CIDADE) & (d["renda_relativa"] >= RENDA_RELATIVA_ALTA)
    d["bairro_renda_alta"] = np.where(alta, "Sim", "Não")
    return d.drop(columns=["participantes_2025", "participantes_2024"])


def calcular_mercado(mercado: pd.DataFrame, populacao: pd.DataFrame, regioes: pd.DataFrame) -> pd.DataFrame:
    """Mercado por município: jovens de 15 a 17 anos, renda alta, vagas privadas e se a cidade é polo ou vizinha de um polo."""
    m = mercado.merge(populacao, on="codigo_municipio", how="left", validate="1:1")
    m = m.merge(regioes[["codigo_municipio", "regiao_imediata_id", "regiao_imediata"]], on="codigo_municipio",
                how="left", validate="1:1")
    m["pct_renda_alta"] = m["pessoas_renda_alta"] / m["populacao_total"] * 100
    # vagas privadas no ensino médio para cada 100 jovens de 15 a 17 anos (aproximação: a matrícula inclui quem tem 18+)
    m["cobertura_privada"] = m["matriculas_privadas_em"] / m["jovens_15_17"] * 100
    m["faixa_cidade"] = pd.cut(m["populacao_total"], [0, 150_000, 300_000, 1_000_000, 1e9],
                               labels=["1. Até 150 mil hab.", "2. 150 a 300 mil", "3. 300 mil a 1 milhão", "4. Mais de 1 milhão"])
    return m


def carregar_mercado() -> pd.DataFrame:
    """Lê vagas/renda por município (01_preparar_dados.py), população e regiões (00_baixar_populacao.py)."""
    try:
        mercado = pd.read_csv(RAIZ / "data" / "mercado_municipio.csv")
        populacao = pd.read_csv(RAIZ / "data" / "populacao_municipios.csv")
        regioes = pd.read_csv(RAIZ / "data" / "regioes_imediatas.csv")
    except FileNotFoundError as e:
        raise SystemExit(f"ERRO: {e.filename} não existe. Rode src/00_baixar_populacao.py e src/01_preparar_dados.py antes.")
    return calcular_mercado(mercado, populacao, regioes)


def sem_acento(texto: str) -> str:
    """'São José' -> 'sao jose', para comparar nomes."""
    return unicodedata.normalize("NFKD", str(texto)).encode("ascii", "ignore").decode().lower().strip()


def marcar_polos(cidades: pd.DataFrame) -> pd.Series:
    """Polo = cidade que dá nome à sua Região Geográfica Imediata (o IBGE nomeia a região pelo polo).

    Quando nenhuma cidade do estudo tem esse nome, vale a maior da região. As demais são vizinhas: parte dos alunos
    delas estuda no polo, então a conta de vagas por jovem da cidade vizinha engana."""
    nome_polo = cidades["regiao_imediata"].map(sem_acento)
    partes = nome_polo.map(lambda r: {r, *[p.strip() for p in r.split(" - ")]})
    pelo_nome = pd.Series([sem_acento(c) in p for c, p in zip(cidades["cidade"], partes)], index=cidades.index)
    tem_polo = pelo_nome.groupby(cidades["regiao_imediata_id"]).transform("any")
    maior = cidades["populacao_total"] == cidades.groupby("regiao_imediata_id")["populacao_total"].transform("max")
    eh_polo = pelo_nome | (~tem_polo & maior)
    return pd.Series(np.where(eh_polo, "Polo", "Vizinha de um polo"), index=cidades.index)


def adicionar_cobertura_esperada(cidades: pd.DataFrame) -> pd.DataFrame:
    """Vagas privadas esperadas para cidades-polo parecidas (mesma região do país e mesma % de moradores de renda alta)."""
    cidades["perfil_cidade"] = marcar_polos(cidades)
    polos = cidades[cidades["perfil_cidade"] == "Polo"]
    ajuste = smf.ols("cobertura_privada ~ pct_renda_alta + C(regiao)", polos).fit()
    print(f"[mercado] {len(polos)} cidades-polo de {len(cidades)}; cobertura privada ~ % renda alta + região: "
          f"R² {ajuste.rsquared:.2f}, +{ajuste.params['pct_renda_alta']:.2f} ponto de cobertura por ponto de renda alta")
    cidades["cobertura_esperada"] = ajuste.predict(cidades)
    cidades["dif_cobertura"] = cidades["cobertura_privada"] - cidades["cobertura_esperada"]
    cidades["vagas_vs_esperado"] = cidades["dif_cobertura"] / 100 * cidades["jovens_15_17"]
    vizinha = cidades["perfil_cidade"] != "Polo"  # para vizinhas a comparação não faz sentido
    cidades.loc[vizinha, ["cobertura_esperada", "dif_cobertura", "vagas_vs_esperado"]] = np.nan
    limiar = LIMIAR_COBERTURA * cidades["dif_cobertura"].std()  # mesma lógica das escolas: 0,75 desvio-padrão
    cidades["cobertura_vs_esperado"] = np.select(
        [vizinha, cidades["dif_cobertura"] <= -limiar, cidades["dif_cobertura"] >= limiar],
        ["Sem comparação (vizinha de polo)", "Abaixo do esperado", "Acima do esperado"], default="Dentro do esperado")
    # decisão de negócio: só vale olhar primeiro onde há moradores de renda alta suficientes para pagar mensalidade
    cidades["prioridade"] = np.where((cidades["cobertura_vs_esperado"] == "Abaixo do esperado")
                                     & (cidades["pct_renda_alta"] >= PCT_RENDA_ALTA_MINIMA), "Olhar primeiro", "-")
    print(f"[mercado] limiar de cobertura: {limiar:.1f} pontos | {cidades['cobertura_vs_esperado'].value_counts().to_dict()}")
    return cidades


def gerar_cidades(d: pd.DataFrame, mercado: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por cidade: mercado (jovens, renda alta, vagas privadas) e, onde existe, os bairros de renda mais alta."""
    todas = d.groupby("codigo_municipio")
    cidades = todas.agg(cidade=("cidade", "first"), uf=("uf", "first"), regiao=("regiao", "first"),
                        escolas_cidade=("codigo_escola", "size"), enem_cidade=("enem_media_2anos", "mean"))
    alta = d[d["bairro_renda_alta"] == "Sim"]
    por_cidade = alta.groupby("codigo_municipio")
    cidades = cidades.join(por_cidade.agg(
        escolas_bairro_alto=("codigo_escola", "size"), alunos_enem_ano=("alunos_enem_ano", "sum"),
        renda_bairro_alto=("renda_mediana_responsavel", "median"), enem_bairro_alto=("enem_media_2anos", "mean"),
        bairros=("bairro", lambda s: ", ".join(s.value_counts().index[:2]))))
    maior = alta.loc[por_cidade["matriculas_medio"].idxmax()].set_index("codigo_municipio")
    cidades["maior_escola"] = maior["nome_escola"]
    cidades["maior_escola_alunos_em"] = maior["matriculas_medio"]
    cidades["maior_escola_enem"] = maior["enem_media_2anos"]
    cidades["dif_enem"] = cidades["enem_bairro_alto"] - cidades["enem_cidade"]
    cidades["bairro_renda_alta"] = np.where(cidades["escolas_bairro_alto"].notna(), "Sim", "Não")
    cidades = cidades.join(mercado.set_index("codigo_municipio"), how="left")
    cidades = adicionar_cobertura_esperada(cidades)
    return cidades.reset_index(drop=True).round(1)


def main() -> None:
    gerar_tabelas_modelo()
    copiar_grupos()
    df = marcar_bairros_de_renda_alta(adicionar_colunas_de_filtro(carregar_resultados()))
    cidades = gerar_cidades(df, carregar_mercado())
    cidades.to_csv(RAIZ / "outputs" / "looker_cidades.csv", index=False)
    escolas = df.drop(columns=["codigo_municipio", "escolas_na_cidade", "renda_relativa"])
    escolas.round(2).to_csv(RAIZ / "outputs" / "looker_escolas.csv", index=False)
    print(f"[ok] {len(escolas)} escolas -> looker_escolas.csv | {len(cidades)} cidades -> looker_cidades.csv")
    print("nulos (escolas):", escolas.isna().sum()[escolas.isna().sum() > 0].to_dict())
    for col in ["regiao", "faixa_renda", "faixa_porte", "seletividade", "situacao_vs_esperado", "bairro_renda_alta"]:
        print(f"{col}:", escolas[col].value_counts().sort_index().to_dict())
    print("cidades: escolas em bairro alto", int(cidades["escolas_bairro_alto"].sum()),
          "| alunos no ENEM/ano", int(cidades["alunos_enem_ano"].sum()),
          "| cidades com nota do bairro acima da cidade:", int((cidades["dif_enem"] > 0).sum()),
          "| cobertura (polos):", cidades["cobertura_vs_esperado"].value_counts().to_dict())


if __name__ == "__main__":
    main()
