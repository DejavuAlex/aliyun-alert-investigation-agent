
from alibabacloud_credentials.client import Client
from alibabacloud_ram20150501.client import Client as Ram20150501Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ram20150501 import models as ram_20150501_models
from alibabacloud_tea_util import models as util_models
from typing import List, Optional, Dict, Any

from mcp_servers.base_server import BaseServer
from fastmcp.utilities import logging

logger = logging.get_logger(__name__)

"""
Ali cloud account related MCP server, including RAM user, RAM role, RAM policy, AK, etc.
"""
class ALI_CLOUD_ACCOUNT(BaseServer):
    def __init__(self, cmd_config):
        super().__init__(cmd_config, "ali_cloud_account_mcp_server", prefix="ali_cloud_account_mcp_server")
        self.setup_server()


    def initialize_client(self,access_key_id:str) -> Ram20150501Client:
        """初始化 Aliyun AcsClient for specific region under specific account"""
        client = None
        for config in self.alicloud_client_configs:
            if config.access_key_id == access_key_id:
                selected_config = config.config
                cred = Client(selected_config)
                config = open_api_models.Config(
                    credential=cred
                )
                config.endpoint = f'ram.aliyuncs.com'
                client = Ram20150501Client(config)
                break
        if client is None:
            raise ValueError(f"No valid Aliyun client config found for account_key_id: {access_key_id}")
        else:
            logger.info(f"Successfully initialized Aliyun RAM client for account_key_id: {access_key_id}")
            return client



    def setup_server(self):

        @self.mcp_instance.tool
        async def get_aliyun_all_accounts_info() -> list[list]:
            """获取本智能体所管理的所有的阿里云账号，以及对应的access_key_id
            :return
                [
                    [
                        <account_id>,<access_key_id>
                    ]
                ]

            """
            return [[config.account_id,config.access_key_id] for config in self.alicloud_client_configs]

        @self.mcp_instance.tool
        async def get_info_detail_of_RAM_role(access_key_id:str,ram_role_name: str) -> dict[str,str]:
            """
            `获取RAM角色的详细信息,也用来判断这个ram_role_name是否是一个RAM角色，如果本方法不会报错，则返回的是一个RAM角色`
            :param
                ram_role_name: str
                access_key_id: str
            :return:
            ```json
            {
              "Role": {
                "RoleId": "222748924538****",
                "RoleName": "role1",
                "Arn": "acs:ram::1234567890123456:role/role1",
                "Description": "这是一位云计算工程师",
                "AssumeRolePolicyDocument": "{\n  \"Statement\": [\n    {\n      \"Action\": \"sts:AssumeRole\",\n      \"Effect\": \"Allow\",\n      \"Principal\": {\n        \"Service\": [\n          \"ecs.aliyuncs.com\"\n        ]\n      }\n    }\n  ],\n  \"Version\": \"1\"\n}",
                "CreateDate": "2015-01-23T12:33:18Z",
                "UpdateDate": "2015-02-11T03:15:21Z",
                "MaxSessionDuration": 3600
              },
              "RequestId": "2D69A58F-345C-4FDE-88E4-BF5189484043"
            }
            ```
            """
            account_client = self.initialize_client(access_key_id)
            get_role_request = ram_20150501_models.GetRoleRequest(ram_role_name)
            runtime = util_models.RuntimeOptions()
            try:
                response:ram_20150501_models.GetRoleResponse = await account_client.get_role_with_options_async(get_role_request, runtime)
                role_info = {
                    'role_id': response.body.role.role_id,
                    'role_name': response.body.role.role_name,
                    'arn': response.body.role.arn,
                    'description': response.body.role.description,
                    'assume_role_policy_document': response.body.role.assume_role_policy_document,
                    'create_date': response.body.role.create_date,
                    'update_date': response.body.role.update_date,
                    'max_session_duration': str(response.body.role.max_session_duration)
                }
                return role_info
            except Exception as error:
                logger.error(f"GetRAMRoleDetail failed: {str(error)}")
                logger.error(error.data.get("Recommend"))
                return {"error": str(error)}

        @self.mcp_instance.tool
        async def get_info_detail_of_RAM_user(access_key_id:str,ram_user_name:str)-> Dict[str,str]:
            """
            获取RAM用户的详细信息,也用来判断这个ram_user_name是否是一个RAM用户，如果本方法不会报错，则返回的是一个RAM用户
            :param ram_user_name:
            :return:
            ```json
            {
              "User": {
                "DisplayName": "alice",
                "Email": "alice@example.com",
                "UpdateDate": "2015-02-11T03:15:21Z",
                "MobilePhone": "86-1860000****",
                "UserId": "222748924538****",
                "Comments": "这是一位云计算工程师",
                "LastLoginDate": "2015-01-23T12:33:18Z",
                "CreateDate": "2015-01-23T12:33:18Z",
                "UserName": "alice"
              },
              "RequestId": "2D69A58F-345C-4FDE-88E4-BF5189484043"
            }
            """
            account_client = self.initialize_client(access_key_id)
            get_user_request = ram_20150501_models.GetUserRequest(ram_user_name)
            runtime = util_models.RuntimeOptions()
            try:
                response:ram_20150501_models.GetUserResponse = await account_client.get_user_with_options_async(get_user_request, runtime)
                user_info = {
                    'display_name': response.body.user.display_name,
                    'email': response.body.user.email,
                    'update_date': response.body.user.update_date,
                    'mobile_phone': response.body.user.mobile_phone,
                    'user_id': response.body.user.user_id,
                    'comments': response.body.user.comments,
                    'last_login_date': response.body.user.last_login_date,
                    'create_date': response.body.user.create_date,
                    'user_name': response.body.user.user_name
                }
                return user_info
            #'{'error': "Error: EntityNotExist.User code: 404, account not exists request id: FC9D48BC-B0C8-5E33-9722-06D4D2FF7507 Response: {'RequestId': 'FC9D48BC-B0C8-5E33-9722-06D4D2FF7507', 'HostId': 'ram.aliyuncs.com', 'Code': 'EntityNotExist.User', 'Message': 'account not exists', 'Recommend': 'https://api.aliyun.com/troubleshoot?q=EntityNotExist.User&product=Ram&requestId=FC9D48BC-B0C8-5E33-9722-06D4D2FF7507\', 'statusCode': 404}'
            except Exception as error:
                logger.error(f"GetRAMUserDetail failed: {str(error)}")
                logger.error(error.data.get("error"))
                return [{"error": str(error)}]

        @self.mcp_instance.tool
        async def list_policies_for_user(
                access_key_id:str,
                user_name: str,
        ) -> Dict[str, Any]:
            """
            列出用户关联的权限策略

            Args:
                user_name: RAM用户名称


            Returns:
            ```json
            {
                "Policies": [
                    {
                        "PolicyName": "String", // 策略名称
                        "PolicyType": "String", // 策略类型
                        "Description": "String", // 策略描述
                        "DefaultVersion": "String", // 默认版本
                        "AttachDate": "String", // 关联时间
                    }
                ],
                "RequestId": "String" // 本次请求的唯一ID
            }
            ```
            """
            try:
                account_client = self.initialize_client(access_key_id)
                logger.info(f"Listing policies for user: {user_name}")
                request = ram_20150501_models.ListPoliciesForUserRequest(user_name)
                response = await account_client.list_policies_for_user_with_options_async(request, util_models.RuntimeOptions())
                result = response.to_map()

                return {
                    "Policies": result.get("Policies", []),
                    "RequestId": result.get("RequestId")
                }

            except Exception as e:
                logger.error(f"Error listing policies for user: {str(e)}")
                return {"error": f"查询失败: {str(e)}"}

        @self.mcp_instance.tool
        async def list_policies_for_role(
                access_key_id:str,
                role_name: str,
        ) -> Dict[str, Any]:
            """
            列出角色关联的权限策略

            Args:
                role_name: RAM角色名称

            Returns:
            ```json
            {
                "Policies": [
                    {
                        "PolicyName": "String", // 策略名称
                        "PolicyType": "String", // 策略类型
                        "Description": "String", // 策略描述
                        "DefaultVersion": "String", // 默认版本
                        "AttachDate": "String", // 关联时间
                        "Description_en": "String" // 英文描述（如有）
                    }
                ],
                "RequestId": "String" // 本次请求的唯一ID
            }
            ```
            """
            try:
                account_client = self.initialize_client(access_key_id)
                logger.info(f"Listing policies for role: {role_name}")
                request = ram_20150501_models.ListPoliciesForRoleRequest(role_name)
                response:ram_20150501_models.ListPoliciesForRoleResponse = await account_client.list_policies_for_role_with_options_async(request, util_models.RuntimeOptions())
                policies_info = {
                    "Policies": {
                        "Policy": [
                            {
                                "PolicyName": policy.policy_name,
                                "PolicyType": policy.policy_type,
                                "Description": policy.description,
                                "DefaultVersion": policy.default_version,
                                "AttachDate": policy.attach_date,
                                "Description_en": getattr(policy, 'description_en', '')
                            } for policy in response.body.policies.policy
                        ]
                    },
                    "RequestId": response.body.request_id
                }
                return policies_info


            except Exception as e:
                logger.error(f"Error listing policies for role: {str(e)}")
                return {"error": f"查询失败: {str(e)}"}

        # @self.mcp_instance.tool
        # async def get_role_info(
        #         role_name: str
        # ) -> Dict[str, Any]:
        #     """
        #     获取RAM角色详细信息
        #
        #     Args:
        #         role_name: RAM角色名称
        #
        #     Returns:
        #     ```json
        #     {
        #         "Role": {
        #             "RoleId": "String", // 角色ID
        #             "RoleName": "String", // 角色名称
        #             "Arn": "String", // 角色ARN
        #             "Description": "String", // 角色描述
        #             "AssumeRolePolicyDocument": "String", // 信任策略文档
        #             "CreateDate": "String", // 创建时间
        #             "UpdateDate": "String", // 更新时间
        #             "MaxSessionDuration": "Number" // 最大会话时长
        #         },
        #         "RequestId": "String" // 本次请求的唯一ID
        #     }
        #     ```
        #     """
        #     try:
        #         logger.info(f"Getting role info for: {role_name}")
        #
        #         request = GetRoleRequest.GetRoleRequest()
        #         request.set_RoleName(role_name)
        #
        #         response = self.client.do_action_with_exception(request)
        #         result = json.loads(response.decode('utf-8'))
        #
        #         return {
        #             "Role": result.get("Role", {}),
        #             "RequestId": result.get("RequestId")
        #         }
        #
        #     except Exception as e:
        #         logger.error(f"Error getting role info: {str(e)}")
        #         return {"error": f"查询失败: {str(e)}"}

        @self.mcp_instance.tool
        async def list_roles(
                access_key_id:str,
                marker: Optional[str] = None,
                max_items: int = 100
        ) -> Dict[str, Any]:
            """
            列出所有RAM角色

            Args:
                marker: 分页标记
                max_items: 每页最大数量 (1-1000，默认100)

            Returns:
            ```json
            {
                "Roles": {
                    "Role": [
                        {
                            "RoleId": "String",
                            "RoleName": "String",
                            "Arn": "String",
                            "Description": "String",
                            "CreateDate": "String",
                            "UpdateDate": "String"
                        }
                    ]
                },
                "IsTruncated": "Boolean", // 是否还有更多结果
                "Marker": "String", // 分页标记
                "RequestId": "String" // 本次请求的唯一ID
            }
            ```
            """
            try:
                logger.info("Listing all RAM roles")
                account_client = self.initialize_client(access_key_id)
                request = ram_20150501_models.ListRolesRequest(marker, max_items)
                response:ram_20150501_models.ListRolesResponse = account_client.list_roles_with_options(request, util_models.RuntimeOptions())
                return {
                    "Roles": {
                        "Role": [
                            {
                                "RoleId": role.role_id,
                                "RoleName": role.role_name,
                                "Arn": role.arn,
                                "Description": role.description,
                                "CreateDate": role.create_date,
                                "UpdateDate": role.update_date
                            } for role in response.body.roles.role
                        ]
                    },
                    "IsTruncated": response.body.is_truncated,
                    "Marker": response.body.marker,
                    "RequestId": response.body.request_id
                }


            except Exception as e:
                logger.error(f"Error listing roles: {str(e)}")
                return {"error": f"查询失败: {str(e)}"}


