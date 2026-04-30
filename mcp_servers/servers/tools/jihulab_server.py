import requests
import json

from pydantic import Field

from mcp_servers.base_server import BaseServer
from fastmcp.utilities import logging

logger = logging.get_logger(__name__)

class JIHULAB_AUDIT_SERVER(BaseServer):
    def __init__(self, cmd_config):
        super().__init__(cmd_config, "jihulab_server", prefix="jihulab_server")
        self.token = Field(..., description="Jihulab PRIVATE-TOKEN",min_length=1)
        self.url = Field(..., description="Jihulab URL",min_length=1)
        self.roche_parent_group = Field(..., description="Roche Jihu lab parent group",min_length=1)
        self.roche_parent_group = self.cmd_config.jihulab["roche_parent_group"]
        self.token = self.cmd_config.jihulab["token"]
        self.url = self.cmd_config.jihulab["url"]
        self.setup_server()

    def setup_server(self):
        @self.mcp_instance.tool
        async def get_group_audit_events(
            group_full_path: str,
        ) -> dict:
            """
            查询指定 Jihulab Group 的审计事件

            Args:
                group_full_path: Group 的完整 path，斜杠用 %2F 替换
                private_token: Jihulab 的 PRIVATE-TOKEN

            Returns:
                审计事件列表响应
            """
            url = f"{self.url}/groups/{group_full_path}/audit_events"
            headers = {"PRIVATE-TOKEN": self.token}
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                events = response.json()
                result = []
                for event in events:
                    result.append({
                        "author_name": event["details"].get("author_name"),
                        "ip_address": event["details"].get("ip_address"),
                        "created_at": event["created_at"],
                        "details": event["details"]
                    })
                return {"events": result}
            except Exception as e:
                logger.error(f"get_group_audit_events failed: {str(e)}")
                return {"error": str(e)}

        @self.mcp_instance.tool
        async def get_project_audit_events(
            project_path_with_namespace: str,
        ) -> dict:
            """
            查询指定 Jihulab Project 的审计事件

            Args:
                project_path_with_namespace: 项目的完整 path，斜杠用 %2F 替换
                private_token: Jihulab 的 PRIVATE-TOKEN

            Returns:
                审计事件列表响应
            """
            url = f"{self.url}/projects/{project_path_with_namespace}/audit_events"
            headers = {"PRIVATE-TOKEN": self.token}
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                events = response.json()
                result = []
                for event in events:
                    result.append({
                        "author_name": event["details"].get("author_name"),
                        "ip_address": event["details"].get("ip_address"),
                        "created_at": event["created_at"],
                        "details": event["details"]
                    })
                return {"events": result}
            except Exception as e:
                logger.error(f"get_project_audit_events failed: {str(e)}")
                return {"error": str(e)}

        @self.mcp_instance.tool
        async def get_parent_group_path() -> str:
            """
            Query the root group of Jihulab. Starting from this root group, you can retrieve all its subgroups and projects, including those of its nested subgroups, allowing for recursive traversal throughout the entire hierarchy.

            Returns：
                Jihulab的 root group

            """
            return self.roche_parent_group

        @self.mcp_instance.tool
        async def get_all_subgroups(
            parent_group: str,
        ) -> dict:
            """
            查询指定 Jihulab Group 的所有子组（递归）

            Args:
                parent_group: 父 Group 的完整 path，斜杠用 %2F 替换

            Returns:
                子组信息列表响应，每项包含 id、name、web_url、full_path
            """
            headers = {"PRIVATE-TOKEN": self.token}
            groups = []

            def _retrieve_all_subgroups(group_path):
                url = f"{self.url}/groups/{group_path}/subgroups"
                response = requests.get(url, headers=headers)
                data = response.json()
                if response.status_code != 200:
                    logger.error(f"get_all_subgroups failed: {response.status_code}, {response.content}")
                    return
                for event in data:
                    full_path = event["full_path"].replace("/", "%2F")
                    groups.append({
                        "id": event["id"],
                        "name": event["name"],
                        "web_url": event["web_url"],
                        "full_path": full_path,
                    })
                    _retrieve_all_subgroups(full_path)

            try:
                _retrieve_all_subgroups(parent_group)
                return {"groups": groups}
            except Exception as e:
                logger.error(f"get_all_subgroups failed: {str(e)}")
                return {"error": str(e)}

        @self.mcp_instance.tool
        async def get_all_projects(
            groups: list,
        ) -> dict:
            """
            查询指定 Jihulab Groups 下的所有项目

            Args:
                groups: Group 信息列表，每项需包含 full_path 字段（斜杠用 %2F 替换）

            Returns:
                项目信息列表响应，每项包含 project_id、project_name、project_web_url、project_path_with_namespace
            """
            headers = {"PRIVATE-TOKEN": self.token}
            projects = []
            try:
                for group in groups:
                    group_path = group["full_path"]
                    url = f"{self.url}/groups/{group_path}/projects?with_shared=false"
                    response = requests.get(url, headers=headers)
                    data = response.json()
                    for project in data:
                        projects.append({
                            "project_id": project["id"],
                            "project_name": project["name"],
                            "project_web_url": project["web_url"],
                            "project_path_with_namespace": project["path_with_namespace"].replace("/", "%2F"),
                        })
                return {"projects": projects}
            except Exception as e:
                logger.error(f"get_all_projects failed: {str(e)}")
                return {"error": str(e)}
