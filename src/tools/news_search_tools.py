
import os
import json
import requests
from typing import List, Dict
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class NewsSearchTool:
    """Tool to search for news about SRAG (Severe Acute Respiratory Syndrome)."""

    def search_srag_news(self, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search for news about Severe Acute Respiratory Syndrome using the Serper API.
        Args:
            max_results (int): Maximum number of unique news articles to return.
        Returns:
            List[Dict[str, str]]: List of news articles with title, summary, source, date, and url.
        """
        serper_api_key = os.getenv("SERPER_API_KEY")
        if not serper_api_key:
            logger.error("SERPER_API_KEY not found in environment.")
            return []
        search_terms = [
            "Síndrome Respiratória Aguda Grave",
            "SRAG Brasil",
            "Surto respiratório Brasil",
            "Influenza Brasil",
            "COVID-19 Brasil",
            "Gripes no Brasil",
            "Mortes por síndrome respiratória aguda grave"
        ]
        headers = {
            "X-API-KEY": serper_api_key,
            "Content-Type": "application/json"
        }
        news_results = []
        for term in search_terms:
            payload = {"q": term, "type": "news"}
            try:
                response = requests.post(
                    "https://google.serper.dev/news",
                    headers=headers,
                    data=json.dumps(payload),
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("news", []):
                        news_results.append({
                            "title": item.get("title"),
                            "summary": item.get("snippet"),
                            "source": item.get("source"),
                            "date": item.get("date"),
                            "url": item.get("link")
                        })
                else:
                    logger.warning(f"Serper API returned status {response.status_code} for term '{term}'")
            except Exception as e:
                logger.error(f"Error fetching news for '{term}': {e}")
        # Remove duplicates based on URL
        seen = set()
        unique_news = []
        for news in news_results:
            if news["url"] not in seen:
                unique_news.append(news)
                seen.add(news["url"])
            if len(unique_news) >= max_results:
                break
        logger.info(f"Found {len(unique_news)} news articles about SRAG via Serper API")
        return unique_news