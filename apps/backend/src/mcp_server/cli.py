"""Command-line interface to start the Politiklar MCP Server."""

import argparse
import sys

from core.settings import Settings
from .server import create_mcp_server


def main() -> None:
    parser = argparse.ArgumentParser(description="Politiklar Model Context Protocol (MCP) Server")
    parser.add_argument(
        "transport",
        nargs="?",
        default="stdio",
        choices=["stdio", "sse", "streamable-http"],
        help="Transport protocol to use (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind for SSE or HTTP transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port to bind for SSE or HTTP transport (default: 8001)",
    )

    arguments = parser.parse_args()
    settings = Settings()
    server = create_mcp_server(settings=settings)

    if arguments.transport == "stdio":
        server.run(transport="stdio")
    elif arguments.transport in ("sse", "streamable-http"):
        print(f"Starting Politiklar MCP Server on {arguments.host}:{arguments.port} ({arguments.transport})...", file=sys.stderr)
        server.run(transport=arguments.transport, host=arguments.host, port=arguments.port)


if __name__ == "__main__":
    main()
