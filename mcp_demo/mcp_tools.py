from mcp_demo.mcp_server import server



@server.tool('add', description='计算两个数字的和')
def add(a: int, b: int) -> int:
    return a + b


@server.tool('subtract', description='计算两个数字的差')
def subtract(a: int, b: int) -> int:
    return a - b

