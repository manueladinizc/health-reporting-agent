from src.tools.news_search_tools import NewsSearchTool

class NewsSearchAgent:
    """
    News Search Agent: uses NewsSearchTool to search for news about SRAG.
    Can be used as a node in a LangGraph or standalone.
    """
    def __init__(self):
        self.news_tool = NewsSearchTool()

    def run(self, max_results: int = 5) -> dict:
        """
        Searches for news and returns a list of articles.
        """
        articles = self.news_tool.search_srag_news(max_results=max_results)
        return {"articles": articles}


def run_news_search_agent(max_results: int = 5) -> dict:
    """
    Runs the news search agent and returns the results.
    """
    agent = NewsSearchAgent()
    return agent.run(max_results=max_results)
