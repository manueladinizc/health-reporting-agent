import os
import json
import requests
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_summary_metrics(metrics, news_analysis):
    """
    Generate a structured summary of the srag epidemiological metrics and news context.
    Uses LLM if available, otherwise produces a simple summary.
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    news_summary = news_analysis.get('summary', 'Nenhuma notícia analisada') if news_analysis else ''
    prompt = (
        "Gere um relatório automatizado sobre Síndrome Respiratória Aguda Grave (SRAG) para gestores brasileiros, usando os dados e notícias abaixo.\n"
        "Estruture a resposta assim:\n"
        "1. Resumo executivo do cenário atual (máx. 5 linhas).\n"
        "2. Para cada métrica, apresente o valor, explique o significado e comente tendências ou anomalias:\n"
        "   - Taxa de aumento de casos\n"
        "   - Taxa de mortalidade\n"
        "   - Taxa de ocupação de UTI\n"
        "   - Taxa de vacinação\n"
        "3. Relacione as métricas com as notícias recentes, explicando possíveis causas para tendências observadas.\n"
        "4. Cite as fontes de dados e notícias utilizadas.\n"
        "\nMÉTRICAS:\n"
        f"{json.dumps(metrics, ensure_ascii=False, indent=2)}\n"
        "NOTÍCIAS:\n"
        f"{news_summary}\n"
        "Responda em português, de forma clara, objetiva e profissional, com no máximo 20 linhas."
    )
    if openai_api_key:
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "Você é um especialista em saúde pública, com foco em doenças respiratórias agudas graves (SRAG)."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                logger.error(f"OpenAI response error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
    # fallback
    return (
        "Resumo das métricas:\n"
        f"Métricas: {metrics}\n"
        f"Notícias: {news_summary}"
    )

def generate_summary_charts(news_analysis, charts):
    """
    Generate a summary relating the dates/content of the news with trends in the charts (daily and monthly).
    Uses LLM if available, otherwise produces a simple summary.
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    news_summary = news_analysis.get('summary', 'Nenhuma notícia analisada') if news_analysis else ''
    daily_desc = charts.get('daily_cases_chart', {}).get('description', '') if charts else ''
    monthly_desc = charts.get('monthly_cases_chart', {}).get('description', '') if charts else ''
    prompt = (
        "Analise as datas e conteúdos das notícias abaixo e compare com as tendências descritas nos gráficos diários e mensais.\n"
        "1. Diga se as tendências dos gráficos coincidem com o que está sendo relatado nas notícias (ex: aumento ou queda de casos em determinado mês/ano).\n"
        "2. Destaque convergências ou divergências relevantes para o relatório epidemiológico.\n"
        "3. Cite as fontes de dados e notícias utilizadas.\n"
        "\nNOTÍCIAS:\n"
        f"{news_summary}\n"
        "GRÁFICO DIÁRIO:\n"
        f"{daily_desc}\n"
        "GRÁFICO MENSAL:\n"
        f"{monthly_desc}\n"
        "Responda em português, de forma clara, objetiva e profissional, com no máximo 20 linhas."
    )
    if openai_api_key:
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "Você é um especialista em saúde pública, com foco em doenças respiratórias agudas graves (SRAG)."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                logger.error(f"OpenAI response error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
    # fallback
    return (
        "Resumo de gráficos e notícias:\n"
        f"Notícias: {news_summary}\n"
        f"Gráficos: Diário: {daily_desc} | Mensal: {monthly_desc}"
    )

def generate_executive_summary(summary_metrics, summary_charts):
    """
    Generate a final executive summary using the two previous summaries.
    Uses LLM if available, otherwise produces a simple summary.
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    prompt = (
        "Com base nos dois resumos abaixo (um sobre métricas e notícias, outro sobre análise de gráficos e notícias), escreva um resumo executivo final, comentando sobre o todo, destacando riscos e alertas para gestores públicos.\n"
        "1. Destaque os principais pontos de atenção e tendências.\n"
        "2. Comente sobre tendências dos gráficos.\n"
        "3. Seja conciso, objetivo e profissional.\n"
        "\nRESUMO MÉTRICAS/NOTÍCIAS:\n"
        f"{summary_metrics}\n"
        "RESUMO GRÁFICOS/NOTÍCIAS:\n"
        f"{summary_charts}\n"
        "Responda em português, em formato de texto corrido (sem tópicos ou listas), com no máximo 12 linhas."
    )
    if openai_api_key:
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "Você é um especialista em saúde pública, com foco em doenças respiratórias agudas graves (SRAG)."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"].strip()
            else:
                logger.error(f"OpenAI response error: {response.status_code} - {response.text}")
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
    # fallback
    return (
        "Resumo executivo:\n"
        f"Resumo métricas/notícias: {summary_metrics}\n"
        f"Resumo gráficos/notícias: {summary_charts}"
    )

def assemble_report(state):
    """
    Assemble the final report from the graph state, including summary_metrics, summary_charts, and executive_summary.
    The generated JSON follows the pattern of the mock provided by the user.
    """
    report = {
        "report_metadata": {
            "generation_date": datetime.now().isoformat(),
            "report_type": "SRAG Report",
            "generated_by": "SRAG Report Agent System"
        },
        "metrics": state.get("metrics"),
        "news_analysis": state.get("news_analysis"),
        "charts": state.get("charts"),
    }
    # Generate summaries
    summary_metrics = generate_summary_metrics(state.get("metrics"), state.get("news_analysis"))
    summary_charts = generate_summary_charts(state.get("news_analysis"), state.get("charts"))
    executive_summary = generate_executive_summary(summary_metrics, summary_charts)
    report["summary_metrics"] = summary_metrics
    report["summary_charts"] = summary_charts
    report["executive_summary"] = executive_summary

    report_path = f"resources/json/srag_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    report["report_path"] = report_path
    return report