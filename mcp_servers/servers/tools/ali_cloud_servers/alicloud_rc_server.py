import json
from typing import List

from alibabacloud_credentials.client import Client
from alibabacloud_resourcecenter20221201.models import SearchResourcesRequestFilter
from alibabacloud_tea_util.client import Client as UtilClient
from mcp_servers.base_server import BaseServer
from alibabacloud_resourcecenter20221201 import models as resource_center_20221201_models
from alibabacloud_resourcecenter20221201.client import Client as ResourceCenterClient
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_openapi import models as open_api_models
from fastmcp.utilities import logging
logger = logging.get_logger(__name__)

class ALI_CLOUD_RESOURCECENTER(BaseServer):
    def __init__(self, cmd_config):
        super().__init__(cmd_config, "ali_cloud_rc_mcp_server", prefix="ali_cloud_rc_mcp_server")
        self.client = None
        self.setup_server()
        # self.initialize_client()

    # def initialize_client(self,region_id):
    #     access_key_id = self.cmd_config.alicloud_config["access_key_id"]
    #     access_key_secret = self.cmd_config.alicloud_config["access_key_secret"]
    #     if not access_key_id or not access_key_secret:
    #         raise ValueError("alicloud access key id and secret must be provided in internal_config.yaml")
    #     config = Config(
    #         type='access_key',
    #         access_key_id=access_key_id,
    #         access_key_secret=access_key_secret,
    #     )
    #     if region_id:
    #         config.endpoint = f"ecs.{region_id}.aliyuncs.com"
    #     cred = Client(config)
    #     config = open_api_models.Config(
    #         credential=cred
    #     )
    #     return Ecs20140526Client(config)

    def initialize_client_4_specific_region(self, access_key_id: str, region_id: str):
        rs_client = None
        """初始化 Aliyun action trail Client for specific region under specific account"""
        for config in self.alicloud_client_configs:
            if config.access_key_id == access_key_id:
                selected_config = config.config
                cred = Client(selected_config)
                config = open_api_models.Config(
                    credential=cred
                )
                # always resourcecenter.aliyuncs.com
                config.endpoint = f'resourcecenter.aliyuncs.com'
                rs_client = ResourceCenterClient(config)
                break
        if rs_client is None:
            raise ValueError(
                f"No valid Aliyun client config found for account_id: {access_key_id}, region_id: {region_id}")
        else:
            logger.info("Sunncessfully initialized Aliyun Resource Center client")
            return rs_client


    def setup_server(self):
        @self.mcp_instance.tool
        async def search_resources(
                access_key_id: str,
                region_id: str,
                next_token: str = None,
                max_results: int = 10,
                resource_group_id: str = None,
                filters: list = None,
                sort_criterion: dict = None
        ) -> dict:
            """
            搜索阿里云资源
            仅能搜索当前账号下有权限访问的资源。
            仅能搜索支持资源中心的云服务及资源类型,具体查看本地Roche_knowledge_base中的'阿里云资源列表'。
            SearchResources 接口默认最多返回 20 条数据，您可以通过指定MaxResults参数调整最大返回条目数。
            如果返回结果中不存在NextToken，则表示没有更多数据。否则，则表示还有更多数据。如果想要查询后续页，需要将 SearchResources 接口的NextToken参数设置为上一次返回结果中获取到的NextToken 。如果未输入NextToken参数，查询时默认返回第一页的数据。
            通过设置一个或多个过滤条件，可以精确资源的搜索范围。支持的过滤参数以及匹配方式见下文。多个过滤条件之间是逻辑与AND的关系，只有同时满足所有过滤条件的资源才会被返回。每个过滤条件内部是逻辑或OR的关系，只要满足任意一个过滤条件值的资源都会被返回

            Args:
                access_key_id: 使用的阿里云账号AccessKey ID
                region_id: 地域ID

                next_token: 下一页的令牌，用于分页查询
                max_results: 每页最大数据条数，最大500
                resource_group_id: 资源组ID，like rg-acfmzawhxxc****
                filters:
                    filters是List[dict]类型，形如
                    [
                        {
                            "Key": "ResourceType",
                            "Value": ["ACS::ECS::Instance"],
                            "MatchType": "Equals"
                        }
                    ]

                    filters的过滤条件列表，支持的过滤字段包括：
                      [
                        {
                          "参数": "ResourceType",
                          "描述": "资源类型。",
                          "支持的匹配类型": ["Equals"]
                        },
                        {
                          "参数": "RegionId",
                          "描述": "地域 ID。",
                          "支持的匹配类型": ["Equals"]
                        },
                        {
                          "参数": "ResourceId",
                          "描述": "资源 ID。",
                          "支持的匹配类型": ["Equals", "Prefix"]
                        },
                        {
                          "参数": "ResourceGroupId",
                          "描述": "资源组 ID。",
                          "支持的匹配类型": ["Equals", "Exists", "NotExists"]
                        },
                        {
                          "参数": "ResourceName",
                          "描述": "资源名称。",
                          "支持的匹配类型": ["Equals", "Contains"]
                        },
                        {
                          "参数": "Tag",
                          "描述": "标签键值对。 JSON 格式为 { \"key\": $key, \"value\": $value } ，key 与 value 至少出现一个。例如：查询标签键foo和标签值bar，则传递{ \"key\": \"foo\", \"value\": \"bar\" } ；查询标签键foo，则传递{ \"key\": \"foo\" }。",
                          "支持的匹配类型": ["Contains", "NotContains", "NotExists"]
                        },
                        {
                          "参数": "VpcId",
                          "描述": "VPC ID。",
                          "支持的匹配类型": ["Equals"]
                        },
                        {
                          "参数": "VSwitchId",
                          "描述": "交换机 ID。",
                          "支持的匹配类型": ["Equals"]
                        },
                        {
                          "参数": "IpAddress",
                          "描述": "IP 地址。",
                          "支持的匹配类型": ["Equals", "Contains"]
                        }
                      ]

                sort_criterion: 排序参数

            Returns:
                dict: 包含资源搜索结果的字典，包含以下字段：
                    - Resources: 资源列表
                    - Filters: 过滤条件
                    - MaxResults: 每页最大数据条数
                    - NextToken: 下一页令牌
                    - RequestId: 请求ID

            Example:
                >>> # 搜索特定类型的资源
                >>> filters = [
                ...     {
                ...         "Key": "ResourceType",
                ...         "Values": ["ACS::ECS::Instance"],
                ...         "MatchType": "Equals"
                ...     }
                ... ]
                >>> search_resources(access_key_id, filters=filters)

                >>> # 搜索特定资源ID
                >>> filters = [
                ...     {
                ...         "Key": "ResourceId",
                ...         "Values": ["i-xxxxxx"],
                ...         "MatchType": "Equals"
                ...     }
                ... ]
                >>> search_resources(access_key_id, filters=filters)

                >>> # 搜索包含特定标签的资源
                >>> filters = [
                ...     {
                ...         "Key": "Tag",
                ...         "Values": ['{"key": "Environment", "value": "Production"}'],
                ...         "MatchType": "Contains"
                ...     }
                ... ]
                >>> search_resources(access_key_id, filters=filters)
            """
            try:
                # 初始化 Resource Center 客户端
                rs_client = self.initialize_client_4_specific_region(access_key_id, region_id)

                # 构建请求参数
                model_filters: List[SearchResourcesRequestFilter] = []
                if len(filters) > 0:
                    for filter in filters:
                        value = ""
                        key = ""
                        match_type = ""
                        for k,v in filter.items():
                            if k == "Value":
                                value = v
                            if k == "Key":
                                key = v
                            if k == "MatchType":
                                match_type = v
                        if value != "" and key != "" and match_type != "":
                            search_resources_request_filter = SearchResourcesRequestFilter(
                                key=key,
                                value=value,
                                match_type=match_type
                            )
                            model_filters.append(search_resources_request_filter)
                logger.info("set the resource center request filters to {}".format(model_filters))
                request = resource_center_20221201_models.SearchResourcesRequest(
                    next_token=next_token,
                    max_results=max_results,
                    resource_group_id=resource_group_id,
                    filter=model_filters,
                    sort_criterion=sort_criterion
                )

                # 调用 API
                UtilClient.validate_model(request)
                response = await rs_client.search_resources_with_options_async(
                    request,
                    util_models.RuntimeOptions()
                )

                return response.to_map()

            except Exception as error:

                print(error.message)

                # 诊断地址

                print(error.data.get("Recommend"))

        def create_filter(key: str, values: list, match_type: str) -> dict:
            """
            创建过滤条件辅助函数

            Args:
                key: 过滤字段名称
                values: 过滤值列表
                match_type: 匹配类型 (Equals, Prefix, Contains, NotContains, Exists, NotExists)

            Returns:
                dict: 过滤条件字典
            """
            return {
                "Key": key,
                "Values": values,
                "MatchType": match_type
            }

        def create_tag_filter(tag_key: str = None, tag_value: str = None, match_type: str = "Contains") -> dict:
            """
            创建标签过滤条件辅助函数

            Args:
                tag_key: 标签键
                tag_value: 标签值
                match_type: 匹配类型 (Contains, NotContains, NotExists)

            Returns:
                dict: 标签过滤条件字典
            """
            tag_filter = {}
            if tag_key:
                tag_filter["key"] = tag_key
            if tag_value:
                tag_filter["value"] = tag_value

            return create_filter("Tag", [json.dumps(tag_filter)], match_type)

        def create_sort_criterion(sort_key: str, sort_order: str = "Asc") -> dict:
            """
            创建排序参数辅助函数

            Args:
                sort_key: 排序字段
                sort_order: 排序顺序 (Asc, Desc)

            Returns:
                dict: 排序参数字典
            """
            return {
                "Key": sort_key,
                "Order": sort_order
            }



        # # 使用示例工具函数
        # @self.mcp_instance.tool
        # async def search_ecs_instances(
        #         access_key_id: str,
        #         region_id: str = "cn-hangzhou",
        #         instance_ids: list = None,
        #         instance_name: str = None,
        #         vpc_id: str = None,
        #         vswitch_id: str = None,
        #         ip_address: str = None,
        #         resource_group_id: str = None,
        #         max_results: int = 50
        # ) -> dict:
        #     """
        #     搜索ECS实例的便捷函数
        #
        #     Args:
        #         access_key_id: 使用的阿里云账号AccessKey ID
        #         region_id: 地域ID
        #         instance_ids: 实例ID列表
        #         instance_name: 实例名称（支持模糊匹配）
        #         vpc_id: VPC ID
        #         vswitch_id: 交换机ID
        #         ip_address: IP地址
        #         resource_group_id: 资源组ID
        #         max_results: 返回最大数量
        #
        #     Returns:
        #         dict: ECS实例搜索结果
        #     """
        #     filters = []
        #
        #     # 资源类型过滤
        #     filters.append(create_filter("ResourceType", ["ACS::ECS::Instance"], "Equals"))
        #
        #     # 地域过滤
        #     filters.append(create_filter("RegionId", [region_id], "Equals"))
        #
        #     # 实例ID过滤
        #     if instance_ids:
        #         for instance_id in instance_ids:
        #             filters.append(create_filter("ResourceId", [instance_id], "Equals"))
        #
        #     # 实例名称过滤
        #     if instance_name:
        #         filters.append(create_filter("ResourceName", [instance_name], "Contains"))
        #
        #     # 网络过滤
        #     if vpc_id:
        #         filters.append(create_filter("VpcId", [vpc_id], "Equals"))
        #
        #     if vswitch_id:
        #         filters.append(create_filter("VSwitchId", [vswitch_id], "Equals"))
        #
        #     if ip_address:
        #         filters.append(create_filter("IpAddress", [ip_address], "Contains"))
        #
        #     # 资源组过滤
        #     if resource_group_id:
        #         filters.append(create_filter("ResourceGroupId", [resource_group_id], "Equals"))
        #
        #     return await search_resources(
        #         access_key_id=access_key_id,
        #         region_id=region_id,
        #         max_results=max_results,
        #         resource_group_id=resource_group_id,
        #         filters=filters
        #     )
        #
        # @self.mcp_instance.tool
        # async def search_resources_by_tag(
        #         access_key_id: str,
        #         region_id: str = "cn-hangzhou",
        #         tag_key: str = None,
        #         tag_value: str = None,
        #         resource_type: str = None,
        #         match_type: str = "Contains",
        #         max_results: int = 50
        # ) -> dict:
        #     """
        #     根据标签搜索资源的便捷函数
        #
        #     Args:
        #         access_key_id: 使用的阿里云账号AccessKey ID
        #         region_id: 地域ID
        #         tag_key: 标签键
        #         tag_value: 标签值
        #         resource_type: 资源类型
        #         match_type: 匹配类型
        #         max_results: 返回最大数量
        #
        #     Returns:
        #         dict: 标签搜索结果
        #     """
        #     filters = []
        #
        #     # 标签过滤
        #     if tag_key or tag_value:
        #         filters.append(create_tag_filter(tag_key, tag_value, match_type))
        #
        #     # 资源类型过滤
        #     if resource_type:
        #         filters.append(create_filter("ResourceType", [resource_type], "Equals"))
        #
        #     # 地域过滤
        #     filters.append(create_filter("RegionId", [region_id], "Equals"))
        #
        #     return await search_resources(
        #         access_key_id=access_key_id,
        #         region_id=region_id,
        #         max_results=max_results,
        #         filters=filters
        #     )