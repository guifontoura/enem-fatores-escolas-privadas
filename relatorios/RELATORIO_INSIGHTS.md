# Relatório de Insights — O que se associa ao ENEM em escolas privadas?

*Projeto de Parceria EBAC/Semantix — Guilherme Julião Fontoura*

**Base:** 4.396 escolas privadas, 311 municípios, 27 UFs. **Alvo:** nota média no ENEM (2024 e 2025 combinados). **Fatores:** infraestrutura (índice 0–5), renda do bairro da escola, porte (alunos no ensino médio) e seleção de alunos na admissão. Definições em [METODOLOGIA.md](METODOLOGIA.md); detalhes técnicos em `notebooks/01_eda_modelagem.ipynb`.

## Resumo executivo

1. **O contexto pesa mais do que a escola controla.** Renda do bairro e porte da escola se associam mais à nota do ENEM do que a infraestrutura. Quem investe só em estrutura física espera mais do que os dados sustentam.
2. **Infraestrutura importa, em escala modesta.** Cada nível a mais no índice se associa a cerca de +4 pontos; dois níveis, a +8 pontos (IC 95%: 6 a 10), contra um desvio-padrão de 45 pontos entre escolas.
3. **Selecionar alunos na entrada "vale" cerca de +16 pontos**, mas isso mede o filtro de quem entra, não o quanto a escola ensina.
4. **O modelo explica ~23% da variação.** Serve para priorizar e comparar, não para prever a nota de uma escola específica (erro típico de ~40 pontos).
5. **Estar muito acima ou muito abaixo do esperado é um traço persistente da escola.** O desvio de 2024 e o de 2025 têm correlação de 0,85; 647 escolas ficam muito abaixo do esperado nos dois anos e 667, muito acima. Essas escolas têm o mesmo perfil medido (infraestrutura, porte, renda, seleção); a diferença está no que as bases públicas não medem.
6. **Na escala da cidade, as vagas privadas acompanham a renda.** Nas cidades-polo, a parcela de moradores de renda alta explica boa parte das vagas privadas no ensino médio (R² 0,61). 14 cidades têm renda alta e menos vagas do que o esperado; onde a cidade já está no esperado, como Santos, o que há é espaço para comprar ou fazer parceria com uma escola grande. Sem mensalidade e concorrência, é um mapa de onde olhar.

**O que os dados mostram × o que isso sugere.** Os dados mostram associação entre nota e bairro, porte e infraestrutura. Sugerem, como hipótese de negócio, que quem começa uma escola ganha mais escolhendo o bairro e planejando escala (construir grande, expandir ou comprar uma escola grande) do que gastando primeiro em estrutura. Isso não foi testado: os dados não têm retorno financeiro nem mensalidade.

## Insight 1 — Renda e porte à frente da infraestrutura

| Fator | Peso relativo (coef. padronizado) | Efeito em pontos de ENEM |
|---|---|---|
| Renda do bairro | 0,27 | +5,7 pts a cada R$ 1.000 a mais de renda mediana |
| Porte (alunos no ensino médio) | 0,25 | +11,6 pts quando o número de alunos dobra (ex.: 100 → 200) |
| Seleção de alunos | 0,14 | +15,8 pts (escolas que selecionam vs. não) |
| Infraestrutura | 0,12 | +4,1 pts por nível (0 a 5) |

Todos os efeitos são estatisticamente significativos (p < 0,001). A ordem foi confirmada por um segundo método independente (importância por permutação no Random Forest): renda > porte > infraestrutura ≈ seleção.

**O que isso significa:** a variação da nota entre escolas privadas acompanha, antes de tudo, onde a escola está e o tamanho que tem, fatores que a gestão muda devagar ou não muda.

## Insight 2 — O ganho de infraestrutura é real, mas não é a alavanca principal

A diferença bruta entre escolas com infraestrutura máxima (nível 5, média 619) e as de nível 0–2 (média ~591) é de cerca de 27 pontos, e a nota só começa a subir a partir do nível 3. Descontados renda, porte e seleção, o efeito de ir de 0 a 5 cai para ~20 pontos: parte da vantagem aparente vem de as escolas com mais estrutura também estarem em bairros mais ricos e serem maiores.

Uma simulação com o modelo: elevar a infraestrutura em dois níveis, mantendo o resto constante, projeta **+8 pontos** (IC 95%: 6,3 a 9,9). É um efeito consistente, porém pequeno diante da dispersão de 45 pontos entre escolas. É **associação**, não promessa de retorno causal.

## Insight 3 — Seleção de alunos: cuidado com a leitura

Escolas que selecionam alunos têm média bruta 25 pontos maior (622,7 contra 598,1). Com controle de renda, porte e infraestrutura, a diferença cai para ~16 pontos. Parte vem de a seleção filtrar alunos que já chegam mais preparados, o que não indica melhor ensino. Para comparar escolas "por valor agregado", este indicador sozinho não basta.

## Insight 4 — A relação é linear e o teto está nos dados

O Random Forest (R² 0,214) não superou a regressão linear (R² 0,229) na validação agrupada por município. Se um modelo mais flexível não ajuda, o limite está nos fatores **não medidos** (qualidade docente, perfil do aluno que ingressa, tradição da escola), e não na técnica. Para avançar, o caminho é trazer dados novos, não complicar o modelo.

## Insight 5 — O "abaixo do esperado" é persistente, não é acaso de um ano

Comparei a nota real de cada escola com a prevista por um modelo que não viu aquela cidade, separadamente para 2024 e para 2025. Os desvios dos dois anos são **muito parecidos (correlação 0,85)**: das 949 escolas que ficaram 30 ou mais pontos abaixo do esperado em 2024, 68% seguem 30 ou mais abaixo em 2025, e 96% seguem abaixo de zero. Só 4 escolas trocaram de lado (muito acima num ano, muito abaixo no outro).

Com isso, 647 escolas ficam **muito abaixo do esperado nos dois anos**, 667 **muito acima**, 2.646 dentro do esperado ou sem padrão consistente e 436 têm dado de só um ano.

**Leitura prudente:** o desvio mostra onde olhar, não o diagnóstico. Escolas "abaixo do esperado" não são "escolas ruins": o modelo explica ~23% da variação e não vê características importantes. Por isso o painel fala em "esperado para o perfil", e não em qualidade.

## Insight 6 — O que as escolas fora do padrão têm em comum

**No que foi medido, nada.** Escolas muito abaixo e muito acima do esperado são praticamente iguais em infraestrutura (3,4 e 3,3), mediana de alunos no ensino médio (133 e 127), renda do bairro (R$ 2.500 nos dois grupos) e seleção na entrada (24% nos dois). Era esperado, porque o "esperado" é calculado com esses fatores; a diferença de ~114 pontos de ENEM entre os grupos vem de algo que o modelo não vê.

**O tipo de instituição dá pistas.** Entre os 9 grupos com 15 ou mais escolas (identificados pelo nome), os Adventistas (137 escolas) ficam muito abaixo em 36% dos casos e nunca muito acima, as escolas técnicas/profissionalizantes (41) em 37% e os colégios de aplicação (19) em 53%, contra 16% na média geral. Vinci (15) fica muito acima em 80% dos casos e Anglo (32) em 34%. Maristas, Salesianos e Objetivo ficam perto da média. O padrão é coerente: instituições com missão além do ENEM tendem a ficar abaixo, e redes com foco em vestibular, acima.

**Leitura prudente:** é uma hipótese. Os grupos foram definidos pelo nome, foram testados 9 de uma vez (alguns padrões podem ser acaso) e alguns têm poucas escolas. Confirmar exige dados que as bases públicas não têm (corpo docente, projeto pedagógico, perfil dos alunos).

## Insight 7 — A variação de um ano para o outro é pequena e não é explicada pelos fatores

A nota média caiu cerca de 5 pontos de 2024 para 2025 em todo o conjunto (desvio-padrão da variação por escola: 22,5 pontos). A variação praticamente não se relaciona com infraestrutura, renda, porte ou seleção (correlações abaixo de 0,07). Como a infraestrutura é uma foto de 2025, os dados não permitem estimar o efeito da infraestrutura sobre a *mudança* de nota. Essa é uma limitação dos dados, e não um indício de que o efeito não exista.

## Insight 8 — Por cidade: renda alta, vagas privadas e escola de referência

**Vagas seguem a renda.** Para os 311 municípios, juntei a renda domiciliar per capita (IBGE) com as vagas privadas no ensino médio (Censo Escolar). Nas cidades-polo (aquelas que dão nome à sua região de influência), a parcela de moradores em famílias de renda alta, junto com a região do país, explica 61% da diferença de vagas privadas por 100 jovens de 15 a 17 anos. Com essa reta defini o "esperado" de cada cidade.

**Cidades abaixo do esperado.** Das 186 cidades-polo, 40 têm vagas abaixo do esperado, 105 estão dentro e 41 acima. Se exijo também que ao menos 10% da população viva em famílias de renda alta, sobram **14 cidades para olhar primeiro**: São Paulo, Brasília, Porto Alegre, Campinas, Vitória, Blumenau, Chapecó, Uberaba, Pelotas, Passo Fundo, Macaé, São Leopoldo, Bento Gonçalves e Erechim. Juntas têm 3,7 milhões de pessoas de renda alta, 720 mil jovens de 15 a 17 anos e 36,8 mil vagas a menos do que o esperado (28,8 mil em São Paulo e Brasília).

**Um cuidado que mudou o resultado.** Sem separar cidades-polo das vizinhas, as maiores faltas de vagas apareciam em cidades como Barueri, Santana de Parnaíba e Carapicuíba, cujos alunos estudam na capital. Por isso a comparação só vale para polos.

**Dentro da cidade.** Para 100 cidades com 5 ou mais escolas, identifiquei os bairros com renda 20% acima da mediana da própria cidade (1.056 escolas, cerca de 53 mil alunos no ENEM por ano). Em 72 dessas cidades as escolas desses bairros tiram nota maior que a média da cidade, como o Insight 1 prevê; em 28, tiram menos. Santos é um exemplo: vagas no esperado (33,8 contra 33,5 por 100 jovens), mas só uma escola grande nos bairros Gonzaga e Pompeia (Liceu Santista, 316 alunos no ensino médio, nota 611 contra 592 da cidade) e quatro pequenas.

**Leitura prudente:** é um mapa de onde olhar. Oito das 14 cidades estão no Sul, onde uma rede pública forte pode explicar parte da diferença. A conta de vagas é aproximada (a matrícula inclui alunos de 18 anos ou mais), o bairro é só uma aproximação da área de captação da escola e não há mensalidade nem concorrentes.

## Robustez

O resultado se manteve em quatro checagens: sem São Paulo e Rio, as duas maiores cidades (R² 0,215); só escolas com os dois anos de ENEM (0,216); sem as escolas filantrópicas (R² 0,216; infraestrutura +3,9 por nível); e dando mais peso às escolas com mais participantes (R² 0,223; infraestrutura +3,6). Comparando apenas escolas da mesma cidade (efeitos fixos de município), infraestrutura (4,1 → 3,8 pts por nível), porte e seleção mudam pouco e a renda segue positiva (+5,7 → +6,6 pts por R$ 1.000). Ou seja, não é só "cidade rica contra cidade pobre".

## Limitações

- **Observacional:** a análise mostra associações, não causas.
- **A renda é da vizinhança, não da família:** é a mediana do responsável no bairro (ou distrito) da escola. Não mede o perfil dos alunos que de fato estudam lá.
- **Escolas com poucos participantes** (mínimo de 10) têm média mais ruidosa, e as com menos de 10 ficam de fora, o que subestima o público por cidade.
- **Infraestrutura é um índice resumido (0–5),** sem separar tipos de investimento (laboratório, biblioteca, quadra).
- **Recortes aplicados:** excluídas escolas de educação especial, de alternância, Sistema S, Fundação Bradesco (ensino gratuito) e as "salas vitrine" (turmas pequenas que concentram os melhores alunos). As "salas vitrine" são um problema reconhecido: o filtro removeu 4 casos e unidades fora do critério podem ainda distorcer a média de uma escola. Filantrópicas com mensalidade foram mantidas.
- **Tipo de instituição pelo nome:** é uma aproximação; nomes diferentes podem esconder a mesma rede.
- **Análise por cidade:** as vagas são aproximadas, o corte de 10% de renda alta é critério de negócio, e a comparação só vale para cidades-polo. O bairro não é a área de captação da escola, e a nota do bairro soma poucas escolas (de 2 a 8 na maioria das cidades).
- **Seleção de alunos:** o código "não se aplica" do INEP foi tratado como dado ausente (11 escolas fora do modelo).

## Próximos passos sugeridos

1. Incluir dados de corpo docente (Censo Escolar) para testar o principal fator não medido.
2. Incluir mais edições do ENEM (2022 e 2023) para estimar *valor agregado* (evolução da mesma escola) com mais de uma variação anual, o que separa melhor o efeito da escola do efeito do público.
3. Cruzar o mapa por cidade com mensalidades, concorrentes e a rede pública, para chegar a uma decisão de investimento.
