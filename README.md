# Health Reporting Agent — Indicium HealthCare

## Visão Geral

Este projeto é uma solução automatizada para geração de relatórios epidemiológicos sobre Síndrome Respiratória Aguda Grave (SRAG), integrando dados reais do Open DATASUS, análise de notícias em tempo real e explicações geradas por IA. O sistema foi desenvolvido como parte da certificação Artificial Intelligence Engineer by Indicium.

O pipeline realiza:
- Extração e tratamento de dados SRAG do DATASUS.
- Cálculo de métricas epidemiológicas mensais (taxa de aumento de casos, mortalidade, ocupação de UTI, vacinação).
- Busca de notícias recentes sobre SRAG.
- Geração de gráficos históricos.
- Síntese e explicação do cenário por IA generativa.
- Geração automática de relatório em HTML e JSON.

## Estrutura do Projeto

```
health-reporting-agent/
├── main.py
├── requirements.txt
├── .env.example
├── src/
│   ├── agents/           # Agentes para métricas, visualização, notícias, resumo
│   ├── tools/            # Ferramentas para cálculo, busca, visualização
│   ├── utils/            # Utilitários (logs, renderização de relatório)
│   ├── template/         # Template HTML do relatório
│   ├── data_loader.py    # Download e ingestão dos dados
│   ├── graph_workflow.py # Orquestrador LangGraph
├── reports/              # Relatórios gerados (não versionados)
```

## Como Configurar

1. **Clone o repositório:**
	```bash
	git clone https://github.com/seu-usuario/health-reporting-agent.git
	cd health-reporting-agent
	```

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
	  ```
	  OPENAI_API_KEY=...
	  SERPER_API_KEY=...
	  ```

5. **Execute o pipeline:**
	```bash
	python main.py
	```

6. **Acesse o relatório:**
	- O relatório HTML será gerado em `reports/srag_report.html`.

## O que o projeto faz?

- **Automação completa:** Da ingestão dos dados à geração do relatório final, tudo é orquestrado por agentes e ferramentas modulares.
- **Explicações por IA:** O relatório traz explicações automáticas, contextualizando as métricas com notícias recentes.
- **Visualização:** Gráficos diários e mensais são gerados automaticamente.
- **Fácil auditoria:** Logs detalhados de cada etapa do pipeline.

## Observações

- Os dados são baixados automaticamente do DATASUS.
- As chaves de API são necessárias para uso de IA e busca de notícias.
- A pasta `reports/` é criada automaticamente e não é versionada.
