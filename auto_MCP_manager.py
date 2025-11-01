import asyncio
import inspect
from typing import List, Coroutine

from invoke import Promise
from pydantic import Field
from starlette.requests import Request
from fastmcp import FastMCP
from starlette.responses import JSONResponse
from mcp_servers.base_server import BaseServer
import pkgutil
import importlib
from fastmcp.utilities import logging


logger = logging.get_logger(__name__)

class AutoMCPManager:
    def __init__(self,cmd_config):
        self.cmd_config = cmd_config
        if hasattr(self.cmd_config,"mcp_debug") and self.cmd_config.mcp_debug is True:
            self.main_mcp = FastMCP("AutoMCPManager",debug=True)
        else:
            self.main_mcp = FastMCP("AutoMCPManager")
        self.mcp_servers_instances = []

    def discovery_servers(self,package_name: str = "mcp_servers.servers") -> List[type[BaseServer]] | None:
        return self._discovery_servers(package_name)


    def _discovery_servers(self, package_name:str) -> List[type[BaseServer]] | None:
        servers = []
        try:
            package = importlib.import_module(package_name)
            for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
                if is_pkg:
                    servers.extend(self._discovery_servers(f"{package_name}.{module_name}"))
                else:
                    try:
                        module = importlib.import_module(f"{package_name}.{module_name}")
                        for name, obj in inspect.getmembers(module):
                            if inspect.isclass(obj) and issubclass(obj, BaseServer) and name is not BaseServer.__name__:
                                print(f"Discovered MCP server class: {module.__name__}")
                                servers.append(obj)
                        # return servers
                    except ImportError as err:
                        raise ImportError(f"Failed to import {package_name}.{module_name}: {err}")
            return servers
        except ImportError as err:
            raise ImportError(f"Failed to import package {package_name}: {err}")


    def create_server_instances(self,server_classes: List[type[BaseServer]]) -> List[type(BaseServer)]:
        instances = []
        try:
            for server_class in server_classes:
                server_instance = server_class(self.cmd_config)
                instances.append(server_instance)
            return instances
        except Exception as err:
            raise RuntimeError(f"Failed to create server instance: {err}")

    def auto_register_servers(self):
        """ 自动注册MCP服务器"""
        self.mcp_servers_instances = self.create_server_instances(self.discovery_servers())
        for server_instance in self.mcp_servers_instances:
            try:
                self.main_mcp.mount(server_instance.get_mcp_instance(), prefix=server_instance.prefix)
            except Exception as err:
                print(f"Failed to mount {server_instance.name}: {err}")

    async def _fetch_all_tools(self):
        server_instances = [server.get_mcp_instance() for server in self.mcp_servers_instances]
        return await asyncio.gather(*[server.get_tools() for server in server_instances])



    def setup_main_server(self):
        """ 设置主MCP服务器"""
        @self.main_mcp.custom_route("/health", methods=["GET"])
        async def health_check(request:Request):
            logger.info("Health check")
            return JSONResponse(
                {
                "status": "ok",
                "MCP_servers": [{"MCP_server":server.name,"prefix":server.prefix} for server in self.mcp_servers_instances],
                "total_servers": len(self.mcp_servers_instances)
                }
            )

        # @self.main_mcp.tool
        # def list_all_tools():
        #     """ 列出所有注册的MCP工具"""
        #     return asyncio.ensure_future(self._fetch_all_tools())

        @self.main_mcp.tool
        def list_all_tools():
            """ 列出所有注册的MCP工具"""
            loop = asyncio.get_event_loop()
            return loop.create_task(self._fetch_all_tools())
            # server_instances = [server.get_mcp_instance() for server in self.mcp_servers_instances]
            # return asyncio.ensure_future(*[instance.get_tools() for instance in server_instances])




        @self.main_mcp.custom_route("/server/{server_name}/info", methods=["GET"])
        async def server_info(request:Request):
            server_name = request.path_params.get("server_name")
            for server in self.mcp_servers_instances:
                logger.info(f"here server_name: {server.name}")
                if server.name.lower() == server_name.lower():
                    return JSONResponse(
                        {
                            "MCP_server": server.name,
                            "prefix": server.prefix,
                            "status":"active"

                        }
                    )
            return JSONResponse({"error": "Server not found"}, status_code=404)

