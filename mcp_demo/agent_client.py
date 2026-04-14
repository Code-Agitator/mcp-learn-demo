import asyncio
import os

from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
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
prompt = ChatPromptTemplate.from_messages([
    ('system', '你是一个智能助手，尽可能的调用工具回答用户的问题'),
    MessagesPlaceholder(variable_name='chat_history', optional=True),
    ('human', '{input}'),
    MessagesPlaceholder(variable_name='agent_scratchpad', optional=True),
])


async def client_call():
    client = MultiServerMCPClient({"personal": mcp_server_config})
    tools = await client.get_tools()
    print(tools)
    resource = await client.get_resources('personal',
                                          uris="datas://users/123/email"
                                          )
    print(resource[0])

    agent = create_tool_calling_agent(model, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    resp = await agent_executor.ainvoke({'input': "今天，长沙天气情况"})
    print(resp)


if __name__ == '__main__':
    asyncio.run(client_call())
