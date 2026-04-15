import asyncio
import os
from contextlib import asynccontextmanager

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import SSEConnection
from langchain_openai import ChatOpenAI

mcp_server_config: SSEConnection = {
    "url": "http://127.0.0.1:8000/sse",
    "transport": "sse"
}
model = ChatOpenAI(
    model='deepseek-ai/DeepSeek-V3.2',
    base_url=os.environ.get('OPENAI_BASE_URL'),
    api_key=os.environ.get('OPENAI_API_KEY')
)


@asynccontextmanager
async def make_agent():
    client = MultiServerMCPClient({"personal": mcp_server_config})
    agent = create_agent(model, tools=await client.get_tools(), debug=True)
    yield agent


async def main():
    async with make_agent() as agent:
        print(await agent.ainvoke({'messages': '今天，长沙天气情况'}))


if __name__ == '__main__':
    asyncio.run(main())
