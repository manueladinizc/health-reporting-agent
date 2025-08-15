# Health Reporting Agent — Indicium HealthCare

## Recursos

1. [Link para o Diagrama Conceitual](resources/diagram/conceptual_diagram.png)

## Sumário

1. [Visão Geral](#visão-geral)
2. [Detalhes do Projeto](#detalhes-do-projeto)
3. [Tratamento dos Dados](#tratamento-dos-dados)
4. [Estrutura do Projeto](#estrutura-do-projeto)
5. [Como Configurar](#como-configurar)

## Visão Geral

Este projeto é uma solução automatizada para geração de relatórios epidemiológicos sobre Síndrome Respiratória Aguda Grave (SRAG), integrando dados reais do Open DATASUS, análise de notícias em tempo real e explicações geradas por IA. O sistema foi desenvolvido como parte da certificação AI Engineer by Indicium.

O pipeline realiza:
- Extração e tratamento de dados SRAG do DATASUS.
- Cálculo de métricas epidemiológicas mensais (taxa de aumento de casos, mortalidade, ocupação de UTI, vacinação).
- Busca de notícias recentes sobre SRAG.
- Geração de gráficos com o históricos dos casos de 30 dias e 12 meses.
- Síntese e explicação do cenário por IA generativa.
- Geração automática de relatório em HTML e PDF.


## Detalhes do Projeto

Os dados utilizados neste projeto são provenientes do DATASUS ([link para o dataset](https://opendatasus.saude.gov.br/dataset/srag-2021-a-2024)), abrangendo internações por Síndrome Respiratória Aguda Grave (SRAG) nos anos de 2024 e 2025 (até 04/08/2025). Os arquivos CSV podem ser baixados diretamente pelos links:

- [INFLUD25-04-08-2025.csv (2025)](https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2025/INFLUD25-04-08-2025.csv)
- [INFLUD24-26-06-2025.csv (2024)](https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2024/INFLUD24-26-06-2025.csv)

Por padrão, ao executar o arquivo `main.py`, a pipeline verifica se os arquivos CSV já estão presentes na pasta `data/`. O usuário pode optar por baixar manualmente esses arquivos e adicioná-los a essa pasta. Caso contrário, se os arquivos não estiverem presentes, a pipeline fará o download automaticamente das URLs acima. Após o download, os dados são processados e armazenados em um banco SQLite local.

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

## Como Configurar

Para configurar este projeto, você precisará das seguintes chaves de API:

- **OpenAI API Key**: Necessária para utilizar os modelos de linguagem da OpenAI.
- **SERPER API Key**: Necessária para realizar buscas de notícias em tempo real.

Você pode obter suas chaves nos seguintes urls:

- [SERPER API](https://serper.dev/)
- [OpenAI API](https://platform.openai.com)

1. **Clone o repositório:**
	```bash
	git clone https://github.com/seu-usuario/health-reporting-agent.git
	cd health-reporting-agent
	```


## Como rodar com Docker

1. **Configure as variáveis de ambiente:**
	- Copie `.env.example` para `.env` e preencha com suas chaves:
	  ```bash
	  cp .env.example .env
	  ```

2. **Construa a imagem Docker:**
	```bash
	docker compose build
	```

3. **Suba o container em background:**
	```bash
	docker compose up -d
	```

4. **Acesse o terminal do container:**
	```bash
	docker compose exec report-agent bash
	```

5. **Dentro do container, execute o pipeline manualmente:**
	```bash
	python main.py
	```
	Todas as mensagens de logger aparecerão no terminal do container.

6. **Acesse o relatório:**
	- O relatório PDF será gerado em `resources/reports/srag_report.pdf`.

7. **Para parar e remover o container:**
	```bash
	exit
	docker compose down
	```

---


## Como rodar localmente

> ⚠️ É necessário ter Python 3.11 ou superior instalado.

2. **Crie e ative um ambiente virtual:**
	```bash
	python3 -m venv .venv
	source .venv/bin/activate
	```

3. **Instale as dependências:**
	```bash
	pip install -r requirements.txt
	python -m playwright install
	```

4. **Configure as variáveis de ambiente:**
	- Copie `.env.example` para `.env` e preencha com suas chaves:
	  ```bash
	  cp .env.example .env
	  ```

5. **Execute o pipeline:**
	```bash
	python main.py
	```

6. **Acesse o relatório:**
	- O relatório PDF será gerado em `resources/reports/srag_report.pdf`.
