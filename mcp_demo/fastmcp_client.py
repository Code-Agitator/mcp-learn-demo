import asyncio

from fastmcp import Client
from fastmcp.client import SSETransport


async def fastmcp_client():
    async  with Client(SSETransport("http://127.0.0.1:8000/sse")) as client:
        tools = await client.list_tools()
        print(tools)
        email = await client.read_resource("datas://users/123/email")
        print(email)

        result = await client.call_tool('add', arguments={"a": 23, "b": 11})
        print(result)


if __name__ == '__main__':
    asyncio.run(fastmcp_client())
