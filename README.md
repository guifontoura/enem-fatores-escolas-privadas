# Fatores associados ao desempenho no ENEM em escolas privadas

Projeto de Parceria EBAC/Semantix (Programa Analista de Dados). Pergunta central: **entre infraestrutura, porte, seletividade e contexto socioeconômico, o que mais se associa à nota média do ENEM de uma escola privada — e o que a escola pode de fato mudar?**

## Resultado em uma frase

Renda das famílias e porte da escola pesam mais que infraestrutura. Dois níveis a mais de infraestrutura se associam a cerca de +8 pontos de ENEM (IC 95%: 6 a 10), contra 45 pontos de desvio-padrão entre escolas. O modelo explica ~22% da variação (R² validado fora da amostra).

Leia o [relatório de insights](relatorios/RELATORIO_INSIGHTS.md) para as conclusões e o [notebook](notebooks/01_eda_modelagem.ipynb) para a análise completa.

## Estrutura

```
data/escolas_modelo.csv          base final: 4.433 escolas (4.422 usadas no modelo)
src/01_preparar_dados.py         monta a base a partir do pipeline do projeto Poliedro
notebooks/01_eda_modelagem.ipynb EDA, modelagem, validação, robustez e exportação
outputs/                         CSVs para o Looker Studio e figuras
relatorios/DISSERTACAO_PROBLEMA.md problema, relevância e como a análise ajuda
relatorios/RELATORIO_FONTES.md   fontes públicas, links e limitações
relatorios/RELATORIO_INSIGHTS.md conclusões em linguagem de negócio
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

- **Seletividade:** o INEP usa o código 9 em `IN_EXAME_SELECAO` para "não se aplica". Tratei como dado ausente (11 escolas fora do modelo). Deixar o 9 como valor numérico distorcia o coeficiente: o efeito da seletividade aparecia em ~+6 pontos, e o correto é ~+15.
- **"Salas vitrine":** 4 escolas removidas por concentrarem poucos alunos de alto desempenho. A detecção casa nome e município.
- **Educação especial e alternância:** 7 escolas removidas por nome (APAE, escolas especiais, família agrícola etc.), por não serem comparáveis.
- **Filantrópicas:** mantidas. Removê-las em bloco tiraria também redes confessionais de mensalidade plena.
- **Renda:** mediana da renda do responsável no bairro da escola; se o bairro não casa com o cadastro do IBGE, no distrito. É a renda da vizinhança, não das famílias da escola. 71% da variação da renda ocorre dentro dos municípios.

## Modelagem

- **Alvo:** `enem_media_2anos`.
- **Fatores:** índice de infraestrutura (0–5), renda mediana do responsável, log das matrículas e exame de seleção.
- **Modelos comparados:** baseline (média), regressão linear e Random Forest.
- **Validação:** `GroupKFold` (5 partições) por município. Escolas da mesma cidade compartilham contexto e muitas vezes o mesmo valor de renda; numa validação aleatória elas cairiam em treino e teste e o R² seria inflado.
- **Métricas:** R², RMSE e MAE.
- **Interpretação:** coeficientes padronizados com erros robustos (HC3), VIF (todos perto de 1,0), importância por permutação e efeitos fixos de município como checagem de robustez.

| Modelo | R² | RMSE | MAE |
|---|---|---|---|
| Baseline (média) | −0,003 | 45,3 | 36,8 |
| Regressão linear | 0,224 | 39,9 | 31,9 |
| Random Forest | 0,205 | 40,3 | 32,2 |

## Conclusões

1. Contexto socioeconômico e porte pesam mais que infraestrutura (coeficientes padronizados: renda 0,28, porte 0,24, exame de seleção 0,13, infraestrutura 0,12).
2. Infraestrutura tem efeito real e modesto: ~+4 pontos por nível.
3. A seletividade mede o filtro de entrada, não o quanto a escola ensina.
4. O Random Forest não supera a regressão linear: o teto de ~22% vem de fatores não medidos, não da técnica.

## Limitações

Resultados associativos, não causais. Renda medida por bairro/distrito, não por família. Escolas com poucos participantes têm média ruidosa. O índice de infraestrutura é resumido e não separa tipos de investimento. Lista completa no relatório de insights.

## Como reproduzir

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt     # Windows
jupyter nbconvert --to notebook --execute --inplace notebooks/01_eda_modelagem.ipynb
```

Para regenerar `data/escolas_modelo.csv` a partir do pipeline original (opcional, exige o repositório do Poliedro com os dados processados):

```bash
python src/01_preparar_dados.py <caminho_da_pasta_do_poliedro>
```

## Dashboard

Painel no Looker Studio com filtros por UF, faixa de infraestrutura e nível de renda, alimentado por `outputs/escolas_resultados.csv`, `coeficientes.csv` e `metricas_modelos.csv`. Link: *a adicionar*.

## Autor

Guilherme Julião Fontoura
