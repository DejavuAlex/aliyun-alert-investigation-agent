from dataclasses import dataclass
from typing import Optional, List

from alibabacloud_credentials.models import Config
from fastmcp import FastMCP
from abc import ABC,abstractmethod

from fastmcp.server.auth import StaticTokenVerifier

@dataclass
class AliyunClientConfig:
    config: Config
    account_id:str
    access_key_id:str

class BaseServer(ABC):

    """ 所有MCP Server 的基类"""
    def __init__(self, cmd_config,name: str,prefix:Optional[str] = None):
        self.cmd_config = cmd_config
        self.name = name
        self.alicloud_client_configs:List[AliyunClientConfig] = []
        self.initialize_alicloud_clients_configs()
        self.prefix = prefix or self._get_prefix()
        if hasattr(self.cmd_config,"mcp_debug") and self.cmd_config.mcp_debug is True:
            self.mcp_instance = FastMCP(self.name,debug=True)
        else:
            self.mcp_instance = FastMCP(self.name)
        self.mcp_instance = FastMCP(self.name)
        super().__init__()

    def initialize_alicloud_clients_configs(self):
        """初始化各个账号的阿里云客户端"""
        for config in self.cmd_config.alicloud_configs:
            ali_config = Config(
                type='access_key',
                access_key_id=config["access_key_id"],
                access_key_secret=config["access_key_secret"],
            )
            self.alicloud_client_configs.append(AliyunClientConfig(
                config=ali_config,
                account_id=config["account_id"],
                access_key_id=config["access_key_id"],
            ))


    def _get_prefix(self):
        class_name = self.__class__.__name__
        if class_name.endswith("Server"):
            return class_name[:-6].lower()
        else:
            return class_name
    @abstractmethod
    def setup_server(self):
        pass

    def get_mcp_instance(self) -> FastMCP:
        return self.mcp_instance

    def __str__(self):
        return f"{self.name} (prefix:{self.prefix})"


