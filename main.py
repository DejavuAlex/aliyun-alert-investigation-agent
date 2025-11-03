
import sys




from auto_MCP_manager import AutoMCPManager
from config import parse_cmd_config
from fastmcp.utilities import logging

logger = logging.get_logger(__name__)






def main():
    # Config now sourced from K8S env vars / optional secret file (see config.parse_cmd_config)
    argvs = sys.argv[1:]
    cmd_config = parse_cmd_config(argvs)
    #auto register MCP servers
    auto_mcp_manager = AutoMCPManager(cmd_config)
    auto_mcp_manager.auto_register_servers()
    # setup main MCP server
    auto_mcp_manager.setup_main_server()

    # start MCP servers
    print(f"Starting MCP server on {cmd_config.host}:{cmd_config.port}")
    print("Available endpoints:")
    for server_instance in auto_mcp_manager.mcp_servers_instances:
        print(f"   • /{server_instance.prefix} - {server_instance.name}")
        print("   • /health - Health check")
        print("   • /server/{name}/info - Server info")

    auto_mcp_manager.main_mcp.run(
        transport="streamable-http",
        host=cmd_config.host,
        port=cmd_config.port,
        log_level="DEBUG",
    )


if __name__ == "__main__":
    main()
