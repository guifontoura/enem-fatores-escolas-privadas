# Relatório de Insights — O que se associa ao ENEM em escolas privadas?

*Projeto de Parceria EBAC/Semantix — Guilherme Julião Fontoura*

**Base:** 4.422 escolas privadas, 311 municípios, 27 UFs. **Alvo:** nota média no ENEM (2024 e 2025 combinados). **Fatores:** infraestrutura (índice 0–5), renda do responsável, porte (matrículas) e exame de seleção na admissão. Detalhes técnicos em `notebooks/01_eda_modelagem.ipynb`.

## Resumo executivo

1. **O contexto pesa mais do que a escola controla.** Renda das famílias e porte da escola se associam mais ao ENEM do que infraestrutura. Quem investe só em estrutura física espera mais do que os dados sustentam.
2. **Infraestrutura importa, em escala modesta.** Cada nível a mais no índice se associa a cerca de +4 pontos; dois níveis, a +8 pontos (IC 95%: 6 a 10), contra um desvio-padrão de 45 pontos entre escolas.
3. **Selecionar alunos na entrada "vale" cerca de +15 pontos**, mas isso mede o filtro de quem entra, não o quanto a escola ensina.
4. **O modelo explica ~22% da variação.** Serve para priorizar e comparar, não para prever a nota de uma escola específica (erro típico de ~40 pontos).

## Insight 1 — Renda e porte à frente da infraestrutura

| Fator | Peso relativo (coef. padronizado) | Efeito em pontos de ENEM |
|---|---|---|
| Renda do responsável | 0,28 | +5,8 pts a cada R$ 1.000 de renda mediana |
| Porte (matrículas) | 0,24 | +11 pts a cada vez que as matrículas dobram |
| Exame de seleção | 0,13 | +14,7 pts (escolas que selecionam vs. não) |
| Infraestrutura | 0,12 | +4,1 pts por nível (0 a 5) |

Todos os efeitos são estatisticamente significativos (p < 0,001). A ordem foi confirmada por um segundo método independente (importância por permutação no Random Forest): renda > porte > infraestrutura ≈ exame.

**O que isso significa:** a variação do ENEM entre escolas privadas acompanha, antes de tudo, quem as escolas atendem e o tamanho que têm, fatores que a gestão muda devagar ou não muda.

## Insight 2 — O ganho de infraestrutura é real, mas não é a alavanca principal

A diferença bruta entre escolas com infraestrutura máxima (nível 5, média 619) e as de nível 0–2 (média ~591) é de cerca de 28 pontos. Descontados renda, porte e seletividade, o efeito de ir de 0 a 5 cai para ~20 pontos. Parte da vantagem aparente vem de as escolas com mais estrutura também atenderem famílias mais ricas.

Uma simulação com o modelo: elevar a infraestrutura em dois níveis, mantendo o resto constante, projeta **+8 pontos** (IC 95%: 6,4 a 9,9). É um efeito consistente, porém pequeno diante de uma dispersão de 45 pontos entre escolas. É **associação**, não promessa de retorno causal.

## Insight 3 — Seletividade: cuidado com a leitura

Escolas que selecionam alunos têm média bruta 24 pontos maior (621,7 contra 598,0). Com controle de renda, porte e infraestrutura, a diferença cai para ~15 pontos. Parte vem de a seleção filtrar alunos que já chegam mais preparados, o que não indica melhor ensino. Para comparar escolas "por valor agregado", este indicador sozinho não basta.

## Insight 4 — A relação é linear e o teto está nos dados

O Random Forest (R² 0,205) não superou a regressão linear (R² 0,224) na validação agrupada por município. Se um modelo mais flexível não ajuda, o limite está nos fatores **não medidos** (qualidade docente, perfil do aluno que ingressa, tradição da escola), e não na técnica. Para avançar, o caminho é trazer dados novos, não complicar o modelo.

## Insight 5 — Escolas abaixo do esperado: pontos de partida para investigar

Comparando a nota real com a prevista por um modelo que não viu aquela cidade, algumas escolas com infraestrutura baixa (nível ≤ 2) e porte médio rendem bem abaixo do perfil: Col. Vital Brasil (Niterói, −130 pts), Paulicéia Colégio (São Paulo, −117), Colégio Objetiva Ramili (Alagoinhas, −99), Colégio Pinheiro Guimarães (Rio de Janeiro, −90) e Externato Pinheiro (Rio de Janeiro, −88).

**Leitura prudente:** o resíduo mostra onde olhar, não o diagnóstico. Como o modelo cobre só ~22% da variação, resíduos grandes também podem vir de fatores não medidos ou de amostra pequena de participantes.

## Robustez

O resultado se manteve em três checagens: sem São Paulo e Rio, as duas maiores cidades (R² 0,207); só escolas com os dois anos de ENEM (0,209); e comparando apenas escolas da mesma cidade (efeitos fixos de município), onde infraestrutura (4,1 → 3,7 pts por nível), porte e seletividade mudam pouco e a renda segue positiva (+5,8 → +6,7 pts por R$ 1.000). Ou seja, não é só "cidade rica contra cidade pobre".

## Limitações

- **Observacional:** a análise mostra associações, não causas.
- **A renda é da vizinhança, não da família:** é a mediana do responsável no bairro (ou distrito) da escola. Não mede o perfil dos alunos que de fato estudam lá.
- **Escolas com poucos participantes** (mínimo de 10) têm média mais ruidosa.
- **Infraestrutura é um índice resumido (0–5),** sem separar tipos de investimento (laboratório, biblioteca, quadra).
- **Recortes aplicados:** excluídas escolas de educação especial, de alternância e as "salas vitrine" (turmas pequenas que concentram os melhores alunos).
- **Seletividade:** o código "não se aplica" do INEP foi tratado como dado ausente (11 escolas fora do modelo).

## Próximos passos sugeridos

1. Incluir dados de corpo docente (Censo Escolar) para testar o principal fator não medido.
2. Usar o ENEM de anos anteriores para estimar *valor agregado* (evolução da mesma escola), que separa melhor o efeito da escola do efeito do público.
3. Publicar o dashboard no Looker Studio com filtros por UF, faixa de infraestrutura e nível de renda.
