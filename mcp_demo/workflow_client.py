import asyncio
import os
from typing import TypedDict, Annotated

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.sessions import SSEConnection
from langchain_openai import ChatOpenAI
from langgraph.constants import START, END
from langgraph.graph import add_messages, StateGraph

mcp_server_config: SSEConnection = {
    "url": "http://127.0.0.1:8000/sse",
    "transport": "sse"
}
model = ChatOpenAI(
    model='deepseek-ai/DeepSeek-V3.2',
    base_url=os.environ.get('OPENAI_BASE_URL'),
    api_key=os.environ.get('OPENAI_API_KEY')
)
client = MultiServerMCPClient({"personal": mcp_server_config})


class WorkflowState(TypedDict):
    email: str
    messages: Annotated[list, add_messages]


async def async_tools(state: WorkflowState):
    """加载MCP工具"""
    print(state.get('email'))
    agent = create_agent(model, tools=await client.get_tools(), debug=True)
    resp = await agent.ainvoke(state)
    return resp


async def async_resource(state: WorkflowState):
    """加载MCP资源"""
    resource = await client.get_resources("personal", uris="datas://users/123/email")

    return {"email": resource[0].model_dump().get('data')}


workflow = StateGraph(WorkflowState)
workflow.add_node("resource", async_resource)
workflow.add_node("node", async_tools)

workflow.set_entry_point("resource")
workflow.add_edge("resource", "node")
workflow.add_edge("node", END)

graph = workflow.compile()

_printed = set()


def _print_event(event: dict, _printed: set, max_length=1500):
    """
    打印事件信息，特别是对话状态和消息内容。如果消息内容过长，会进行截断处理以保证输出的可读性。

    参数:
        event (dict): 事件字典，包含对话状态和消息。
        _printed (set): 已打印消息的集合，用于避免重复打印。
        max_length (int): 消息的最大长度，超过此长度将被截断。默认值为1500。
    """
    current_state = event.get("dialog_state")
    if current_state:
        print("当前处于: ", current_state[-1])  # 输出当前的对话状态
    message = event.get("messages")
    if message:
        if isinstance(message, list):
            message = message[-1]  # 如果消息是列表，则取最后一个
        if message.id not in _printed:
            msg_repr = message.pretty_repr(html=True)
            if len(msg_repr) > max_length:
                msg_repr = msg_repr[:max_length] + " ... （已截断）"  # 超过最大长度则截断
            print(msg_repr)  # 输出消息的表示形式
            _printed.add(message.id)  # 将消息ID添加到已打印集合中


async def execute_graph():
    while True:
        user_input = input("用户：")
        if user_input.lower() in ["exit", "quit", 'q']:
            print('对话结束')
            break
        else:
            async for event in graph.astream({"messages": [("user", user_input)]}, stream_mode="values"):
                _print_event(event, _printed)


if __name__ == '__main__':
    asyncio.run(execute_graph())
