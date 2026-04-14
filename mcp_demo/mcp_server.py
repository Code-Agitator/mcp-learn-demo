import os

from langchain_community.tools import TavilySearchResults
from mcp.server.fastmcp import FastMCP

server = FastMCP(
    name="My Server",
    instructions="A simple server",
    port=8000
)

@server.tool('my_search_tool', description='专门搜索互联网中的内容')
def my_search(query: str) -> str:
    """搜索互联网上的内容"""
    try:
        web_search_tool = TavilySearchResults(max_results=2, tavily_api_key=os.environ.get('TAVILY_API_KEY'))
        docs = web_search_tool.invoke({"query": query})  # 调用网络搜索工具
        if docs:
            return "\n".join([d["content"] for d in docs])
    except Exception as e:
        print(e)
        return '没有搜索到任何内容！'



@server.resource("datas://users/{user_id}/email", name='get_user_email')
async def get_user_email(user_id: str) -> str:
    """检索给定用户ID的电子邮件地址。"""
    emails = {"123": "alice@example.com", "456": "bob@example.com"}
    return emails.get(user_id, "not_found@example.com")


@server.resource("data://product-categories")
async def get_categories() -> list[str]:
    """返回一个类型的列表."""
    return ["Electronics", "Books", "Home Goods"]