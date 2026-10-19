# Fatores associados ao desempenho no ENEM em escolas privadas

Projeto de Parceria EBAC/Semantix (Programa Analista de Dados). Pergunta central: **entre infraestrutura, porte, seletividade e contexto socioeconômico, o que mais se associa à nota média do ENEM de uma escola privada — e o que a escola pode de fato mudar?**

## Resultado em uma frase

Renda das famílias e porte da escola pesam mais que infraestrutura. Dois níveis a mais de infraestrutura se associam a cerca de +8 pontos de ENEM (IC 95%: 6 a 10), contra 45 pontos de desvio-padrão entre escolas. O modelo explica ~23% da variação (R² validado fora da amostra).

**Painel (Looker Studio, 4 páginas):** [abrir o relatório](https://datastudio.google.com/reporting/d6297567-7624-41e2-858f-d8776f9d9713)

Leia o [relatório de insights](relatorios/RELATORIO_INSIGHTS.md) para as conclusões e o [notebook](notebooks/01_eda_modelagem.ipynb) para a análise completa.

## Decisão de negócio

Imagine uma rede de escolas privadas, ou uma consultoria que a assessora, com orçamento limitado de melhoria. A decisão é **onde investir primeiro: em infraestrutura física ou em outras frentes**, e como comparar cada unidade com o que o perfil dela prevê. O projeto responde a três perguntas dessa decisão: quanto da nota do ENEM se associa à infraestrutura em relação a renda, porte e seletividade; quantos pontos um nível a mais de infraestrutura costuma valer; e quais escolas ficam persistentemente acima ou abaixo do esperado para o perfil, para saber onde investigar com mais profundidade. A análise orienta a priorização. Ela não classifica a qualidade de escolas nem prova que investir em infraestrutura causa o ganho.

## Estrutura

```
data/escolas_modelo.csv          base final: 4.407 escolas (4.396 usadas no modelo)
data/mercado_municipio.csv       vagas privadas e renda alta por município
data/populacao_municipios.csv    população total e de 15 a 17 anos (IBGE)
data/regioes_imediatas.csv       região de influência de cada município (IBGE)
src/00_baixar_populacao.py       baixa população e regiões do IBGE (cache local)
src/01_preparar_dados.py         monta a base a partir do pipeline do projeto Poliedro
src/02_preparar_looker.py        gera as tabelas do dashboard (escolas, cidades, modelo)
notebooks/01_eda_modelagem.ipynb EDA, modelagem, validação, robustez e exportação
outputs/                         CSVs para o Looker Studio e figuras
relatorios/DISSERTACAO_PROBLEMA.md problema, relevância e como a análise ajuda
relatorios/RELATORIO_FONTES.md   fontes públicas, links e limitações
relatorios/RELATORIO_INSIGHTS.md conclusões em linguagem de negócio
relatorios/METODOLOGIA.md        definições usadas no painel (esperado, ±30 pontos, bairro de renda alta)
```

## Coleta de dados

Todos os dados são públicos e foram obtidos por mim nas fontes oficiais:

| Fonte | O que traz | Uso |
|---|---|---|
| Censo Escolar 2025 (INEP) | Infraestrutura, matrículas, categoria e exame de seleção | Fatores explicativos |
| Microdados do ENEM 2024 e 2025 (INEP) | Notas por participante, agregadas por escola | Variável-alvo (média dos dois anos) |
| Censo Demográfico 2022 (IBGE) | Renda mediana mensal do responsável pelo domicílio, no bairro (ou distrito) da escola | Contexto socioeconômico |

A base reúne escolas privadas com pelo menos 10 participantes no ENEM. Os dados são agregados por escola; não há dados pessoais de alunos.

A coleta e a integração das fontes vieram de outro projeto meu, o mapeamento comercial de escolas privadas (repositório `poliedro-inteligencia-mercado`). `src/01_preparar_dados.py` lê as saídas desse pipeline e gera `data/escolas_modelo.csv`, já sem as colunas comerciais. A base final está versionada aqui para o notebook rodar sem o outro repositório.

### Tratamentos e recortes aplicados

- **Seletividade:** o INEP usa o código 9 em `IN_EXAME_SELECAO` para "não se aplica". Tratei como dado ausente (11 escolas fora do modelo). Deixar o 9 como valor numérico distorcia o coeficiente: o efeito da seletividade aparecia em ~+6 pontos, e o correto é ~+16.
- **"Salas vitrine":** 4 escolas removidas por concentrarem poucos alunos de alto desempenho. A detecção casa nome e município.
- **Educação especial e alternância:** 7 escolas removidas por nome (APAE, escolas especiais, família agrícola etc.), por não serem comparáveis.
- **Sistema S e escolas gratuitas:** o pipeline de origem já exclui o Sistema S pela marcação oficial do Censo (`IN_MANT_ESCOLA_PRIVADA_SIST_S`). Aqui removi também 8 escolas com SESI/SENAI/SESC/SENAC no nome que o Censo não marcou e 18 da Fundação Bradesco (ensino gratuito): 26 escolas fora do mercado pago.
- **Filantrópicas com mensalidade:** mantidas (565 escolas). Removê-las em bloco tiraria também redes confessionais de mensalidade plena. O notebook mostra que tirá-las não muda as conclusões (R² 0,216; infraestrutura +3,9 pontos por nível).
- **Renda:** mediana da renda do responsável no bairro da escola; se o bairro não casa com o cadastro do IBGE, no distrito. É a renda da vizinhança, não das famílias da escola. Mais de 70% da variação da renda ocorre dentro dos municípios.

## Modelagem

- **Alvo:** `enem_media_2anos`.
- **Fatores:** índice de infraestrutura (0–5), renda mediana do responsável, log das matrículas e exame de seleção.
- **Modelos comparados:** baseline (média), regressão linear e Random Forest.
- **Validação:** `GroupKFold` (5 partições) por município. Escolas da mesma cidade compartilham contexto e muitas vezes o mesmo valor de renda; numa validação aleatória elas cairiam em treino e teste e o R² seria inflado.
- **Métricas:** R², RMSE e MAE.
- **Interpretação:** coeficientes padronizados com erros robustos (HC3), VIF (todos perto de 1,0), importância por permutação e efeitos fixos de município como checagem de robustez.

| Modelo | R² | RMSE | MAE |
|---|---|---|---|
| Baseline (média) | −0,004 | 45,4 | 36,9 |
| Regressão linear | 0,229 | 39,8 | 31,8 |
| Random Forest | 0,214 | 40,2 | 32,1 |

## Conclusões

1. Contexto socioeconômico e porte pesam mais que infraestrutura (coeficientes padronizados: renda 0,27, porte 0,25, exame de seleção 0,14, infraestrutura 0,12).
2. Infraestrutura tem efeito real e modesto: ~+4 pontos por nível.
3. A seletividade mede o filtro de entrada, não o quanto a escola ensina.
4. O Random Forest não supera a regressão linear: o teto de ~23% vem de fatores não medidos, não da técnica.
5. O desvio de cada escola em relação ao esperado é persistente entre 2024 e 2025 (correlação 0,85).
6. Escolas muito acima e muito abaixo do esperado têm o mesmo perfil medido (infraestrutura, porte, renda, seleção); a diferença está no que as bases públicas não medem, e o tipo de instituição dá pistas (hipótese, ver notebook).
7. Por cidade, as vagas privadas no ensino médio acompanham a parcela de moradores de renda alta (R² 0,61 entre cidades-polo). 14 cidades-polo têm renda alta e menos vagas que o esperado e ficam como "olhar primeiro"; onde a cidade já tem vagas no esperado, como Santos, o painel mostra se existe uma escola grande de referência (compra ou parceria).

## Limitações

Resultados associativos, não causais. **Escolas-vitrine** (unidades pequenas que concentram os melhores alunos de uma rede) são uma dificuldade reconhecida: o filtro de 10 participantes e a detecção por nome e município removeram 4 casos, mas unidades fora desse critério podem ainda distorcer a média de uma escola. Renda medida por bairro/distrito, não por família. Escolas com poucos participantes têm média ruidosa. O índice de infraestrutura é resumido e não separa tipos de investimento. Na página de cidades, as vagas são aproximadas (a matrícula inclui alunos de 18 anos ou mais), o bairro é só uma aproximação da área de captação da escola, o público dos bairros conta quem fez o ENEM em escolas com 10 ou mais participantes e não há dados de mensalidade nem de concorrentes. Lista completa no relatório de insights.

## Como reproduzir

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt     # Windows
jupyter nbconvert --to notebook --execute --inplace notebooks/01_eda_modelagem.ipynb
```

Para baixar a população e as regiões do IBGE (uma vez; fica em cache):

```bash
python src/00_baixar_populacao.py
```

Para regenerar `data/escolas_modelo.csv` a partir do pipeline original (opcional, exige o repositório do Poliedro com os dados processados):

```bash
python src/01_preparar_dados.py <caminho_da_pasta_do_poliedro>
```

## Dashboard

Painel no Looker Studio com quatro páginas, cada gráfico acompanhado de um "como ler":

1. **Panorama:** nota no ENEM por infraestrutura, renda do bairro, porte e seleção de alunos.
2. **O que pesa mais:** peso e efeito de cada fator, comparação dos modelos.
3. **Escolas acima e abaixo do esperado:** as escolas que fogem do perfil nos dois anos, o que têm em comum e por que a diferença não está nos quatro fatores.
4. **Onde investir:** cidades com muita gente de renda alta e menos vagas em escola privada do que cidades parecidas, e, em cada cidade, os bairros de renda mais alta e a maior escola de lá.

[Abrir o dashboard no Looker Studio](https://datastudio.google.com/reporting/d6297567-7624-41e2-858f-d8776f9d9713)

Um mockup navegável das quatro páginas está em [docs/mockup_dashboard.html](docs/mockup_dashboard.html). Os dados do painel vêm de `outputs/looker_escolas.csv`, `looker_cidades.csv`, `looker_grupos.csv`, `looker_coeficientes.csv` e `looker_metricas.csv`, gerados por `src/02_preparar_looker.py` a partir dos resultados do notebook.

### Como a página 4 é calculada

- **Cidades:** os 311 municípios do estudo (mais de 100 mil habitantes, com escola privada de ENEM confiável).
- **Pessoas de renda alta:** moradores de domicílios com mais de 3 salários mínimos de renda per capita (Censo 2022, IBGE, tabela 10296), em toda a cidade e não só no bairro da escola.
- **Vagas privadas:** matrículas no ensino médio em escolas privadas pagas da cidade (Censo Escolar 2025; sem Sistema S, escolas gratuitas e educação especial). **Vagas por 100 jovens** = vagas dividido pela população de 15 a 17 anos (Censo 2022, tabela 9514 do SIDRA). É uma aproximação, porque a matrícula inclui alunos de 18 anos ou mais.
- **Polo e vizinhas:** cidade-polo é a que dá nome à sua Região Geográfica Imediata (IBGE): 186 cidades. As outras 125 são vizinhas de um polo e ficam de fora da comparação, porque parte dos alunos delas estuda no polo (sem esse corte, as maiores "faltas de vagas" apareciam em cidades como Barueri e Santana de Parnaíba).
- **Esperado:** vagas por 100 jovens previstas por uma reta que usa só a parcela de moradores de renda alta e a região do país, ajustada nas cidades-polo (R² 0,61). A cidade está **abaixo do esperado** quando a diferença passa de 0,75 desvio-padrão (3,4 pontos), mesma regra das escolas na página 3: 40 cidades abaixo, 105 dentro, 41 acima.
- **Olhar primeiro:** cidade-polo abaixo do esperado e com pelo menos 10% da população em famílias de renda alta (critério de negócio, não estatístico). São 14 cidades, com 3,7 milhões de pessoas de renda alta e 36,8 mil vagas a menos do que o esperado; São Paulo e Brasília respondem por 28,8 mil dessas vagas.
- **Bairros de renda mais alta:** em 100 cidades com 5 ou mais escolas, bairros com renda mediana do responsável 20% acima da mediana da própria cidade (régua relativa). Mostram o público (alunos no ENEM por ano), a maior escola e a nota contra a cidade.

**Resultado e cuidados:** a página mostra onde olhar, não afirma que há oportunidade. Oito das 14 cidades estão no Sul, onde uma rede pública forte (como os institutos federais) pode explicar parte da diferença. Não há mensalidade nem concorrentes fora do ENEM.

## Autor

Guilherme Julião Fontoura
