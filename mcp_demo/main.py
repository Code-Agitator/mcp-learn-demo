from mcp_demo.mcp_server import server
import mcp_demo.mcp_tools

if __name__ == '__main__':
    server.run(transport='sse')
