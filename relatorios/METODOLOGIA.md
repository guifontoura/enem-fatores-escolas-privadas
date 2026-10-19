# Metodologia: como ler o painel

*Projeto de Parceria EBAC/Semantix — Guilherme Julião Fontoura*

Este documento define os termos usados no painel e nos relatórios. Fontes e limitações dos dados: [RELATORIO_FONTES.md](RELATORIO_FONTES.md). Código: `notebooks/01_eda_modelagem.ipynb` e `src/`.

## Quais escolas entram

Escolas privadas com pelo menos 10 participantes no ENEM. Ficam de fora: educação especial, pedagogia da alternância, Sistema S (SESI, SENAI, SESC, SENAC), Fundação Bradesco (ensino gratuito) e "salas vitrine" (unidades pequenas que concentram os melhores alunos de uma rede). Escolas filantrópicas com mensalidade permanecem.

## Termos

**Nota no ENEM.** Média das notas dos participantes da escola, nos anos de 2024 e 2025 combinados (só 2025 quando falta 2024).

**Renda do bairro.** Renda mediana mensal do responsável pelo domicílio no bairro da escola (Censo 2022, IBGE); se o bairro não consta do cadastro do IBGE, usa-se o distrito. É a renda da vizinhança, não das famílias da escola.

**Alunos (porte).** Alunos matriculados no ensino médio (Censo Escolar 2025). "Dobrar o número de alunos" significa, por exemplo, ir de 100 para 200.

**Infraestrutura (0 a 5).** Quantos destes itens a escola tem: laboratório de ciências, laboratório de informática, biblioteca, quadra coberta e auditório. Todos pesam igual; o índice não mede a qualidade de cada item.

**Peso de cada fator.** Quanto a nota muda quando o fator varia um desvio-padrão, mantidos os outros três. Permite comparar fatores em unidades diferentes (reais, alunos, níveis).

**Faixa provável (IC 95%).** Intervalo em que o valor verdadeiro do efeito deve estar, com 95% de confiança.

**R².** Fração da diferença de nota entre escolas que o modelo explica, medida em escolas de cidades que ele não viu. 0,23 significa 23%.

**Nota esperada.** A nota que o modelo prevê para a escola a partir dos quatro fatores acima, calculada por validação cruzada agrupada por município (o modelo que prevê uma escola nunca viu as escolas da mesma cidade).

**Diferença (real − previsto).** Nota real menos nota esperada, em pontos de ENEM. A escola é "muito acima" ou "muito abaixo do esperado" quando a diferença é de 30 pontos ou mais, para cima ou para baixo, **nos dois anos** (2024 e 2025), calculada em cada ano separadamente. 30 pontos equivalem a cerca de 0,75 desvio-padrão da diferença (40 pontos). Escolas com dado de só um ano ficam em "Só um ano de dados".

**Tipo de instituição.** Identificado por palavras do nome da escola (por exemplo, "Adventista", "Anglo"). Só entram grupos com 15 ou mais escolas. É uma aproximação.

**Pessoas de renda alta.** Moradores de domicílios com mais de 3 salários mínimos de renda per capita (Censo 2022). Mede a cidade inteira, não só o bairro da escola.

**Vagas privadas e vagas por 100 jovens.** Matrículas no ensino médio em escolas privadas pagas da cidade (Censo Escolar 2025), divididas pela população de 15 a 17 anos e multiplicadas por 100. É aproximada: a matrícula inclui alunos com 18 anos ou mais e conta a cidade da escola, não a do aluno.

**Cidade-polo e vizinha de um polo.** Polo é a cidade que dá nome à sua Região Geográfica Imediata (IBGE). As demais são vizinhas: parte dos alunos delas estuda no polo, então a comparação de vagas só vale para polos.

**Esperado (vagas por 100 jovens).** Valor previsto para a cidade-polo a partir da parcela de moradores de renda alta e da região do país, com base nas outras cidades-polo. "Abaixo do esperado" = diferença de 0,75 desvio-padrão ou mais (cerca de 3,4 pontos), a mesma regra usada nas escolas.

**Olhar primeiro.** Cidade-polo abaixo do esperado com pelo menos 10% da população em famílias de renda alta. O corte de 10% é um critério de negócio.

**Bairro de renda mais alta.** Bairro cuja renda mediana é 20% maior que a mediana de renda das escolas da própria cidade. A régua é relativa porque o que é renda alta em São Paulo não é em uma cidade média. Só para cidades com 5 ou mais escolas.

**Alunos no ENEM por ano.** Média de 2024 e 2025 dos alunos que fizeram o ENEM nas escolas desses bairros. Indica o tamanho do público; não é o total de alunos das escolas.

**Maior escola.** A escola com mais alunos no ensino médio entre as dos bairros de renda mais alta da cidade.

## Limites

Os resultados são associações, não causas. A nota do ENEM depende de fatores que as bases públicas não medem (professores, gestão, perfil dos alunos). O painel não traz mensalidade nem concorrentes, então a página de cidades indica onde olhar, não onde investir. Oito das 14 cidades de "olhar primeiro" estão no Sul, onde uma rede pública forte pode explicar parte da diferença.
