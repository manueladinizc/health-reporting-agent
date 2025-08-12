from src.tools.news_search_tools import NewsSearchTool

class NewsSearchAgent:
    """
    Agente de busca de notícias: utiliza NewsSearchTool para buscar notícias sobre SRAG.
    Pode ser usado como nó em um grafo LangGraph ou isoladamente.
    """
    def __init__(self):
        self.news_tool = NewsSearchTool()

    def run(self, max_results: int = 5) -> dict:
        """
        Busca notícias e retorna uma lista de artigos.
        """
        articles = self.news_tool.search_srag_news(max_results=max_results)
        return {"articles": articles}


def run_news_search_agent(max_results: int = 5) -> dict:
    """
    Executa o agente de busca de notícias e retorna os resultados.
    """
    agent = NewsSearchAgent()
    return agent.run(max_results=max_results)


if __name__ == "__main__":
    output = run_news_search_agent()
    print("Resultado do NewsSearchAgent:\n", output)
