from typing import Any

import anyio
from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
from slimconfig import build_output, output_schema, plain_output

from contract import TOOLS, Tool
from plugin import list_covenant_facts, read_covenant_fact

server = Server("financial-covenant-screener")
IMPLEMENTATIONS = {Tool.LIST_COVENANT_FACTS: list_covenant_facts, Tool.READ_COVENANT_FACT: read_covenant_fact}


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(name=t.value, inputSchema=output_schema(i), outputSchema=output_schema(o))
        for t, (i, o) in TOOLS.items()
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    tool = Tool(name)
    given, made = TOOLS[tool]
    output = IMPLEMENTATIONS[tool](build_output(arguments, given))
    if not isinstance(output, made):
        raise TypeError("wrong tool output type")
    return plain_output(output)


def main():
    async def run():
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())

    anyio.run(run)


if __name__ == "__main__":
    main()
