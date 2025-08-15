
# Health Reporting Agent — Indicium HealthCare


Geração de relatórios epidemiológicos sobre SRAG com dados do Open DATASUS, análise de notícias em tempo real (SERPER API) e explicações por IA (OpenAI). Pipeline modular, geração de gráficos, HTML e PDF.

**Principais recursos:** download e tratamento de dados, métricas mensais, busca de notícias, relatórios automáticos, orquestração por agentes (LangGraph).

- [Diagrama Conceitual](resources/diagram/conceptual_diagram.png)


## Sumário
1. [Visão Geral e Funcionalidades](#visão-geral-e-funcionalidades)
2. [Detalhes do Projeto](#detalhes-do-projeto)
3. [Tratamento dos Dados](#tratamento-dos-dados)
4. [Estrutura do Projeto](#estrutura-do-projeto)
5. [Configuração e Execução](#configuração-e-execução)


## Visão Geral e Funcionalidades

- Download e tratamento de dados do Open DATASUS
- Cálculo de métricas mensais (casos, óbitos, UTI, vacinação)
- Busca de notícias em tempo real (SERPER API)
- Explicações com auxílio por IA (OpenAI)
- Geração de gráficos, HTML e PDF


## Detalhes do Projeto

Os dados utilizados neste projeto são provenientes do DATASUS ([link para o dataset](https://opendatasus.saude.gov.br/dataset/srag-2021-a-2024)), abrangendo internações por Síndrome Respiratória Aguda Grave (SRAG) nos anos de 2024 e 2025 (até 04/08/2025). Os arquivos CSV podem ser baixados diretamente pelos links:

- [INFLUD25-04-08-2025.csv (2025)](https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2025/INFLUD25-04-08-2025.csv)
- [INFLUD24-26-06-2025.csv (2024)](https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2024/INFLUD24-26-06-2025.csv)

Ao executar o arquivo `main.py`, a pipeline verifica automaticamente se os arquivos CSV já existem na pasta `data/`. Caso não estejam presentes, o download será feito das URLs acima. Se preferir, você pode baixar manualmente os arquivos e colocá-los na pasta `data/` para agilizar a primeira execução e evitar o tempo de download. Após essa etapa, os dados são processados e armazenados em um banco SQLite local.

A execução do `main.py` aciona toda a pipeline, que é orquestrada por um grafo de agentes (LangGraph). Cada agente é responsável por uma etapa específica: cálculo de métricas, geração de gráficos, busca de notícias e elaboração do resumo do relatório. Para a busca de notícias, foi utilizada a SERPER API, que se mostrou uma solução eficiente e prática para atender à necessidade de obtenção de notícias em tempo real nesta prova de conceito (PoC). O agente `ReportSummaryAgent` utiliza modelos de linguagem para interpretar os dados e as notícias, gerando explicações automáticas para o relatório.

Ao final do processamento, os resultados são salvos em arquivos JSON, que alimentam um template HTML. Este HTML é então convertido automaticamente em PDF, gerando o relatório final.


## Tratamento dos dados

Para esta análise, foram selecionadas as seguintes colunas do dataset SRAG:

- **DT_SIN_PRI**: Data dos primeiros sintomas.
- **EVOLUCAO**: Desfecho do caso (1 - Cura, 2 - Óbito, 3 - Óbito por outras causas, 9 - Ignorado).
- **UTI**: Internação em UTI (1 - Sim, 2 - Não, 9 - Ignorado).
- **VACINA_COV**: Recebeu vacina contra COVID-19 (1 - Sim, 2 - Não, 9 - Ignorado).
- **VACINA**: Recebeu qualquer vacina (1 - Sim, 2 - Não, 9 - Ignorado).
- **CLASSI_FIN**: Classificação final do caso (1 - SRAG por Influenza, 2 - SRAG por outro vírus respiratório, 3 - SRAG por outro agente etiológico, 4 - SRAG não especificado, 5 - Em investigação, 9 - Ignorado).
- **SEM_PRI**: Semana epidemiológica do início dos sintomas.

Valores ausentes nessas colunas foram preenchidos com o valor 9, que segundo o dicionário de dados significa "Ignorado". Isso garante consistência no tratamento dos dados e facilita a análise.

Para o cálculo das métricas:
- **Taxa de Evolução de Casos**: Comparando o número de casos do mês atual da análise (julho) com o mês anterior (junho) de 2025.
- **Óbitos**: Considera-se EVOLUCAO = 2.
- **Ocupação de UTI**: Considera-se UTI = 1.
- **Vacinação COVID-19**: Considera-se VACINA_COV = 1.


## Estrutura do Projeto

```
health-reporting-agent/
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── src/
│   ├── agents/           # Agentes para métricas, visualização, notícias, resumo
│   ├── tools/            # Ferramentas para cálculo, busca, visualização
│   ├── utils/            # Utilitários (logs, renderização de relatório)
│   ├── template/         # Template HTML do relatório
│   ├── data_loader.py    # Download e ingestão dos dados
│   ├── graph_workflow.py # Orquestrador LangGraph
├── resources/
│   ├── charts/           # Gráficos gerados
│   ├── json/             # Relatórios JSON gerados
│   ├── reports/          # Relatórios HTML e PDF gerados
│   └── diagram/          # Diagramas conceituais
```


## Configuração e Execução

**Pré-requisitos:**
- Python 3.11+
- OpenAI API Key ([crie aqui](https://platform.openai.com))
- SERPER API Key ([crie aqui](https://serper.dev/))
- (Recomandado) Docker e Docker Compose

**1. Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/health-reporting-agent.git
cd health-reporting-agent
```

**2. Configure as variáveis de ambiente:**
Copie `.env.example` para `.env` e preencha com suas chaves:
```bash
cp .env.example .env
# Edite o arquivo .env com suas chaves
```

**3. Execute o pipeline:**

- **Com Docker:**
	```bash
	docker compose build
	docker compose up -d
	docker compose exec report-agent bash
	python main.py
	```
	
**Para parar e remover o container:**
	```bash
	exit
	docker compose down
	```

OU

- **Localmente:**
	```bash
	python3 -m venv .venv
	source .venv/bin/activate
	pip install -r requirements.txt
	python -m playwright install
	python main.py
	```

O relatório PDF será gerado em `resources/reports/srag_report.pdf`.
