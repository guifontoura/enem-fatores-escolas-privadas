# Relatório de Fontes de Dados Públicos

*Projeto de Parceria EBAC/Semantix — Guilherme Julião Fontoura*

Todos os dados usados são públicos e foram obtidos por mim diretamente nos portais oficiais. Nenhum dado pessoal de alunos entra na análise: o ENEM é agregado por escola e o Censo Escolar já é publicado por escola.

## Fontes

| # | Fonte | Órgão | Ano | Link oficial | O que foi usado |
|---|---|---|---|---|---|
| 1 | Microdados do Censo Escolar da Educação Básica | INEP | 2025 | [Página](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/censo-escolar) · [Arquivo](https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2025.zip) | Dependência administrativa (privada), categoria da escola privada, matrículas no ensino médio (`QT_MAT_MED`), infraestrutura, `IN_EXAME_SELECAO`, localização |
| 2 | Microdados do ENEM | INEP | 2024 | [Página](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem) · [Arquivo](https://download.inep.gov.br/microdados/microdados_enem_2024.zip) | Nota média por escola (arquivo `RESULTADOS`, que traz `CO_ESCOLA`) e número de participantes |
| 3 | Microdados do ENEM | INEP | 2025 | [Página](https://www.gov.br/inep/pt-br/acesso-a-informacao/dados-abertos/microdados/enem) · [Arquivo](https://download.inep.gov.br/microdados/microdados_enem_2025.zip) | Idem, ano mais recente |
| 4 | Censo Demográfico 2022 — Agregados por Setores Censitários, Rendimento do Responsável | IBGE | 2022 | [Portal do Censo 2022](https://censo2022.ibge.gov.br/) | Mediana mensal do rendimento do responsável pelo domicílio (`V06006`), agregada por bairro e por distrito |
| 5 | SIDRA, tabela 9514 — População residente por sexo e idade | IBGE | 2022 | [Tabela 9514](https://sidra.ibge.gov.br/tabela/9514) | População total e de 15, 16 e 17 anos por município |
| 6 | SIDRA, tabela 10296 — Moradores por classe de rendimento domiciliar per capita | IBGE | 2022 | [Tabela 10296](https://sidra.ibge.gov.br/tabela/10296) | Moradores em domicílios com mais de 3 salários mínimos per capita, por município (a extração usada só traz classes acima de 1 salário mínimo) |
| 7 | API de Localidades — Regiões Geográficas Imediatas | IBGE | 2017 | [API](https://servicodados.ibge.gov.br/api/v1/localidades/municipios) | Região Geográfica Imediata de cada município, para separar cidades-polo de vizinhas |

## Como as fontes se combinam

1. **Universo:** escolas privadas ativas no Censo Escolar 2025 (fonte 1).
2. **Desempenho:** média das notas do ENEM por escola, em 2024 e 2025 (fontes 2 e 3). A variável-alvo é a média dos dois anos; para 441 escolas só há 2025. Entram só escolas com pelo menos 10 participantes.
3. **Contexto:** cada escola recebe a renda mediana do responsável do seu bairro; se o bairro não casa com o cadastro do IBGE, usa-se o distrito (fonte 4). A junção é por nome normalizado do bairro/distrito dentro do município.
4. **Mercado da cidade:** vagas privadas do Censo Escolar (todas as escolas privadas pagas com ensino médio, não só as do estudo), população de 15 a 17 anos e renda domiciliar per capita (IBGE), por código de município.
5. **Chave:** código INEP da escola (`CO_ENTIDADE` / `CO_ESCOLA`) liga o Censo Escolar ao ENEM; código IBGE do município liga a escola à renda.

Resultado: 4.444 escolas na tabela consolidada (o Sistema S já foi excluído pela marcação oficial do Censo, `IN_MANT_ESCOLA_PRIVADA_SIST_S`), 4.407 após os filtros deste projeto (salas vitrine, educação especial e alternância, e escolas gratuitas ou do Sistema S sem marcação) e 4.396 na modelagem (11 sem informação válida de seletividade).

## Limitações conhecidas das fontes

- **Renda é da vizinhança, não do aluno.** A mediana é do responsável pelo domicílio no bairro ou distrito da escola. Uma escola pode atrair alunos de outras regiões.
- **O indicador do IBGE considera só responsáveis com algum rendimento.** O IBGE informa que a renda do responsável, em domicílios sem rendimento, e a renda domiciliar per capita serão divulgadas em etapas futuras. Os valores tendem a ser mais altos do que uma renda que inclua quem não tem rendimento.
- **A variável `V06006` (mediana) não consta no dicionário oficial** do arquivo, embora esteja preenchida em 99,5% das linhas. Usei a mediana por ser mais robusta a valores extremos; a média (`V06004`), documentada, ficou como referência.
- **Bairro não é unidade oficial do Censo.** Em municípios sem cadastro de bairros do IBGE, a renda vem do distrito, que é uma região maior.
- **Vagas privadas por cidade:** a matrícula do ensino médio (Censo Escolar) é contada na cidade da escola, não da residência do aluno, e inclui alunos com 18 anos ou mais. Por isso a conta "vagas por 100 jovens de 15 a 17 anos" é aproximada, e cidades vizinhas de um polo ficam de fora da comparação.
- **ENEM 2024 e 2025:** a participação é voluntária e o perfil de quem faz a prova varia entre escolas. Escolas com poucos participantes têm média instável, por isso o corte de 10.
- **`IN_EXAME_SELECAO`:** o INEP usa o código 9 para "não se aplica". Tratei como dado ausente.
- **Índice de infraestrutura:** não é um índice oficial. É a contagem (0 a 5) de itens presentes na escola segundo o Censo Escolar: laboratório de ciências, laboratório de informática, biblioteca, quadra de esportes coberta e auditório. Todos os itens têm o mesmo peso e o índice não mede a qualidade de cada item.

## Tratamento de dados pessoais

As bases usadas são agregadas por escola e por região, públicas e sem identificação de alunos, professores ou famílias. Nenhuma etapa do projeto reidentifica pessoas.

## Reprodutibilidade

O código que une as fontes está em `src/01_preparar_dados.py` (a partir do pipeline do repositório `poliedro-inteligencia-mercado`) e a base resultante é `data/escolas_modelo.csv`. Os arquivos brutos não são versionados por tamanho; os links acima levam aos originais.
