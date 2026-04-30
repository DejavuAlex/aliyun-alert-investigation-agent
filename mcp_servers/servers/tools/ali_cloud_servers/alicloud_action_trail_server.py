from alibabacloud_actiontrail20200706.models import LookupEventsRequestLookupAttribute
from alibabacloud_actiontrail20200706.client import Client as Actiontrail20200706Client
from alibabacloud_credentials.client import Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_actiontrail20200706 import models as actiontrail_20200706_models
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any


from mcp_servers.base_server import BaseServer
from fastmcp.utilities import logging


logger = logging.get_logger(__name__)

class ALI_CLOUD_ACTION_TRAIL(BaseServer):
    def __init__(self,cmd_config):
        super().__init__(cmd_config,"ali_cloud_actiontrail_mcp_server", prefix="ali_cloud_actiontrail_mcp_server")
        self.setup_server()


    def initialize_client_4_specific_region(self,access_key_id:str,region_id:str) -> Actiontrail20200706Client:
        actiontrail_client = None
        """初始化 Aliyun action trail Client for specific region under specific account"""
        for config in self.alicloud_client_configs:
            if config.access_key_id == access_key_id:
                selected_config = config.config
                cred = Client(selected_config)
                config = open_api_models.Config(
                    credential=cred
                )
                config.endpoint = f'actiontrail.{region_id}.aliyuncs.com'
                actiontrail_client = Actiontrail20200706Client(config)
                break
        if actiontrail_client is None:
            raise ValueError(f"No valid Aliyun client config found for account_key_id: {access_key_id}, region_id: {region_id}")
        else:
            logger.info("Successfully initialized Aliyun Action Trail client for account_key_id: {}, region_id: {}".format(access_key_id, region_id))
            return actiontrail_client

    def setup_server(self):

        @self.mcp_instance.tool
        async def get_access_key_last_used_ips(
                access_key_id: str,
                region_id: str,
                next_token: Optional[str] = None,
                service_name: str = "Ecs",
                page_size: int = 20
        ) -> Dict[str, Any]:
            """
            查询指定AccessKey在阿里云服务上的最后使用的IP地址记录

            Args:
                access_key_id: AccessKey ID (例如: LTAI****************)
                region_id: region id (例如: cn-shanghai)
                ServiceName: 阿里云服务名称 (例如: Ecs, Oss, Rds等)
                next_token: 分页令牌，用于获取下一页结果
                page_size: 每页返回的最大结果数量 (1-100，默认20)
                service_name: 阿里云服务名称 (例如: Ecs, Oss, Rds等)

            Returns:
            ```json
            {
                "Ips": [ // IP地址列表
                    {
                        "IpAddress": "String", // IP地址
                        "LastUsedTime": "String", // 最后使用时间（UTC格式）
                        "ServiceName": "String" // 服务名称
                        "Source": "String" // 来源
                    }
                ],
                "NextToken": "String", // 用于获取后续更多结果的令牌
                "RequestId": "String" // 本次请求的唯一ID
            }
            ```
            """
            try:
                logger.info(f"Querying last used IPs for AccessKey: {access_key_id}")
                actiontrail_client = self.initialize_client_4_specific_region(access_key_id,region_id)
                request = actiontrail_20200706_models.GetAccessKeyLastUsedIpsRequest(
                    access_key=access_key_id,
                    page_size=str(page_size),
                    service_name=service_name,
                    next_token=next_token if next_token else None
                )

                response:actiontrail_20200706_models.GetAccessKeyLastUsedIpsResponse = actiontrail_client.get_access_key_last_used_ips(request)
                return response.body.to_map()


            except Exception as e:
                logger.error(f"Error querying last used IPs: {str(e)}")
                return {"error": f"查询失败: {str(e)}"}

        @self.mcp_instance.tool
        async def get_access_key_last_used_info(
                access_key_id: str,
                region_id: str,
        ) -> Dict[str, Any]:
            """
            查询该AK最后使用的信息
            Args:
                access_key_id: AccessKey ID (例如: LTAI****************)
                region_id: region id (例如: cn-shanghai)
            Returns:
            ```json
            {
                "AccessKeyId": "String", // AccessKey ID
                "AccountId": "String", // 账号ID
                "AccountType": "String", // 账号类型
                "Detail": "String", // 详细信息
                "OwnerId": "String", // 所有者ID
                "RequestId": "String", // 本次请求的唯一ID
                "ServiceName": "String", // 服务名称
                "UserName": "String", // 用户名
                "Source": "String" // 来源
                "ServiceNameCn": "String" // 服务中文名称
                "ServiceNameEn": "String" // 服务英文名称
                "UsedTimestamp": "String" // 最后使用时间戳
            }
            ```
            """
            try:
                logger.info(f"Querying last used info for AccessKey: {access_key_id}")
                actiontrail_client = self.initialize_client_4_specific_region(access_key_id,region_id)
                request:actiontrail_20200706_models.GetAccessKeyLastUsedInfoRequest = actiontrail_20200706_models.GetAccessKeyLastUsedInfoRequest(
                    access_key=access_key_id,

                )
                response:actiontrail_20200706_models.GetAccessKeyLastUsedInfoResponse = actiontrail_client.get_access_key_last_used_info(request)
                return response.body.to_map()
            except Exception as e:
                logger.error(f"Error querying last used info: {str(e)}")
                return {"error": f"查询失败: {str(e)}"}



        @self.mcp_instance.tool
        async def get_access_key_last_used_events(
                access_key_id: str,
                region_id: str,
                service_name: str,
                next_token: Optional[str] = None,
                page_size: int = 20
        ) -> Dict[str, Any]:
            """
                        查询指定AccessKey在阿里云服务上的最后使用的日志记录

                        Args:
                            access_key_id: AccessKey ID (例如: LTAI****************)
                            region_id: region id (例如: cn-shanghai)
                            service_name: 阿里云服务名称 (例如: Ecs, Oss, Rds等)
                            next_token: 分页令牌，用于获取下一页结果
                            page_size: 每页返回的最大结果数量 (1-100，默认20)

                        Returns:
                        ```json
                        {
                            "Events": [ // 事件列表
                                {
                                    "Detail": "String", // 事件详情
                                    "EventName": "String", // 事件名称
                                    "Source": "String", // 最后使用记录来源,like ManagementEvent
                                    "UsedTimestamp": "String", // 最后使用时间戳
                                }
                            ],
                            "NextToken": "String", // 用于获取后续更多结果的令牌
                            "RequestId": "String" // 本次请求的唯一ID
                        }
                        ```
                        """
            return await _get_access_key_last_used_events(access_key_id=access_key_id,region_id=region_id,service_name=service_name,next_token=next_token,page_size=page_size)

        async def _get_access_key_last_used_events(
                access_key_id: str,
                region_id: str,
                service_name: str,
                next_token: Optional[str] = None,
                page_size: int = 20
        ) -> Dict[str, Any]:
            try:
                logger.info(f"Querying last used events for AccessKey: {access_key_id} on service: {service_name}")
                actiontrail_client = self.initialize_client_4_specific_region(access_key_id, region_id)
                request:actiontrail_20200706_models.GetAccessKeyLastUsedEventsRequest = actiontrail_20200706_models.GetAccessKeyLastUsedEventsRequest(
                    access_key=access_key_id,
                    page_size=str(page_size),
                    service_name=service_name,
                    next_token=next_token if next_token else None
                )


                response:actiontrail_20200706_models.GetAccessKeyLastUsedEventsResponse = actiontrail_client.get_access_key_last_used_events(request)
                return response.body.to_map()

            except Exception as e:
                logger.error(f"Error querying last used events: {str(e)}")
                return {"error": f"查询失败: {str(e)}"}

        # @self.mcp_instance.tool
        # def describe_regions() -> Dict[str, Any]:
        #     """
        #     获取可用区域列表
        #
        #     Returns: for example
        #         ```json
        #         [
        #             {"RegionId": "cn-hangzhou"},
        #         ]
        #     """
        #     try:
        #         logger.info("find out all accessible regions for aliyun action trail")
        #         request = actiontrail_20200706_models.DescribeRegionsRequest()
        #         response:actiontrail_20200706_models.DescribeRegionsResponse = self.client.describe_regions(request)
        #         return response.body.to_map()
        #
        #     except Exception as e:
        #         return {"error": f"查询失败: {str(e)}"}

        @self.mcp_instance.tool
        def lookup_events(
                access_key_id: str,
                region_id: str,

                start_time: Optional[str] = None,
                end_time: Optional[str] = None,
                direction: Optional[str] = None,
                next_token: Optional[str] = None,
                max_results: int = 50,
                service_name: Optional[str] = None, # ServiceName只能与以下任意一个组合：EventName、User、PrincipalId、RoleName、ResourceName、EventRW、SensitiveAction 或 EventType。
                event_name: Optional[str] = None,
                user: Optional[str] = None,
                event_id: Optional[str] = None, #EventType 和 EventName 可组合查询。
                resource_type: Optional[str] = None,
                resource_name: Optional[str] = None, # ResourceName 只能与以下任意一个组合：ResourceType、EventName、User、RoleName 或 ServiceName。
                event_access_key_id: Optional[str] = None,
                source_ip: Optional[str] = None,
                event_type: Optional[str] = None, #EventType 和 EventName 可组合查询。
                role_name: Optional[str] = None
        ) -> List[Dict[str, Any]]:
            """
            查询ActionTrail日志，action trail是阿里云的审计日志，这里不是搜索安全事件的。
            如果超过max_results, 需要记忆并使用next_token进行分页查询
            严格遵守以下限制:
            1,在设置检索条件时，您可以选择设定单个 AttributeItem 检索条件或同时设置两个 AttributeItem 检索条件进行查询。需要注意的是，检索键（Key）和检索值（Value）的匹配必须精确，并且区分大小写。
            2,当同时设置两个 AttributeItem 检索条件时，系统将返回同时满足这两个条件的结果。
            3,若两个检索条件的 Key 值相同，则仅返回符合第二个检索条件的结果。
            4,如果设置了超过两个检索条件，系统只会考虑并返回符合前两个条件的结果。
            5,对于同时设置两个 AttributeItem 检索条件的情况，以下是支持的 Key 组合：
                - ServiceName 可与以下任意一个组合：EventName、User、PrincipalId、RoleName、ResourceName、EventRW、SensitiveAction 或 EventType。
                - ResourceName 可与以下任意一个组合：ResourceType、EventName、User、RoleName 或 ServiceName。
                - EventType 和 EventName 可组合查询。


            Args:
                access_key_id: AccessKey ID (例如: LTAI****************)
                region_id: region id (例如: cn-shanghai)

                start_time: 开始时间，格式：YYYY-MM-DDTHH:MM:SSZ (UTC时间)
                end_time: 结束时间，格式：YYYY-MM-DDTHH:MM:SSZ (UTC时间)
                direction: 查询方向 (Forward/Backward)
                max_results: 最大返回结果数 (1-50)
                next_token: 用于请求下一页检索的结果，请求参数必须保证和上次请求一致。

                service_name: 事件来源服务名称, like Ecs, Rds, Oss
                event_name: 事件名称, like CreateInstance, DeleteInstance
                user: 事件发起用户, like admin
                event_id: 事件ID, like 12345678-1234-1234-1234-123456789012
                resource_type: 资源类型, like Instance, Bucket
                resource_name: 资源名称, like my-instance, my-bucket
                event_access_key_id: 事件关联的AccessKey ID, like LTAI****************
                source_ip: 事件发起源IP地址, like 211.31.20.1
                event_type: 事件类型 (Read/Write) , like Read, Write
                role_name: 事件关联的RAM角色名称，like AliyunServiceRoleForActionTrail

            Returns:
                安全事件列表
            """
            return _lookup_events(
                  access_key_id=access_key_id,region_id=region_id,
                  start_time=start_time, end_time=end_time, event_name=event_name,user=user,
                  event_id=event_id,resource_type=resource_type,resource_name=resource_name,
                  event_access_key_id=event_access_key_id,source_ip=source_ip,
                  event_type=event_type,role_name=role_name,
                  max_results=max_results,direction=direction,next_token=next_token,
                  service_name=service_name)


        def _lookup_events(
                access_key_id: str,
                region_id: str,

                start_time: Optional[str] = None,
                end_time: Optional[str] = None,
                direction: Optional[str] = None,
                next_token: Optional[str] = None,
                max_results: int = 50,
                service_name: Optional[str] = None,
                event_name: Optional[str] = None,
                user: Optional[str] = None,
                event_id: Optional[str] = None,
                resource_type: Optional[str] = None,
                resource_name: Optional[str] = None,
                event_access_key_id: Optional[str] = None,
                source_ip: Optional[str] = None,
                event_type: Optional[str] = None,
                role_name: Optional[str] = None,
                event_rw: Optional[str] = None,
        ) -> List[Dict[str, Any]]:
            """
            查询ActionTrail审计日志, 如果超过max_results, 需要记忆并使用next_token进行分页查询

            Args:
                access_key_id: AccessKey ID (例如: LTAI****************)
                region_id: region id (例如: cn-shanghai)

                start_time: 开始时间，格式：YYYY-MM-DDTHH:MM:SSZ (UTC时间)
                end_time: 结束时间，格式：YYYY-MM-DDTHH:MM:SSZ (UTC时间)
                direction: 查询方向 (FORWARD/BACKWARD)
                max_results: 最大返回结果数 (1-50)
                next_token: 用于请求下一页检索的结果，请求参数必须保证和上次请求一致。

                service_name: 事件来源服务名称, like Ecs, Rds, Oss
                event_name: 事件名称, like CreateInstance, DeleteInstance
                user: 事件发起用户, like admin
                event_id: 事件ID, like 12345678-1234-1234-1234-123456789012
                resource_type: 资源类型, like Instance, Bucket
                resource_name: 资源名称, like my-instance, my-bucket
                event_rw: 事件类型 (Read/Write) , like Read, Write
                event_access_key_id: 事件关联的AccessKey ID, like LTAI****************
                source_ip: 事件发起源IP地址, like 211.31.20.1
                event_type: 事件类型 (Read/Write) , like Read, Write
                role_name: 事件关联的RAM角色名称，like AliyunServiceRoleForActionTrail

            Returns:
                安全事件列表
            """
            try:
                logger.info("Beginning to run lookup_events for aliyun action trail")
                actiontrail_client = self.initialize_client_4_specific_region(access_key_id=access_key_id,region_id=region_id)
                # 设置默认时间范围（最近1小时）
                if not start_time:
                    start_time = (datetime.utcnow() - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
                if not end_time:
                    end_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

                request = actiontrail_20200706_models.LookupEventsRequest(
                    start_time=start_time,
                    end_time=end_time,
                    max_results=str(max_results),
                    direction=direction,
                    next_token=next_token if next_token else None,

                )

                # 设置过滤条件
                filter_params = {}
                if service_name:
                    filter_params['ServiceName'] = service_name
                if event_name:
                    filter_params['EventName'] = event_name
                if user:
                    filter_params['User'] = user
                if event_id:
                    filter_params['EventId'] = event_id
                if resource_name:
                    filter_params['ResourceName'] = resource_name
                if event_access_key_id:
                    filter_params['EventAccessKeyId'] = event_access_key_id
                if source_ip:
                    filter_params['SourceIpAddress'] = source_ip
                if event_type:
                    filter_params['EventType'] = event_type
                if role_name:
                    filter_params['RoleName'] = role_name
                if resource_type:
                    filter_params['ResourceType'] = resource_type
                if event_rw:
                    filter_params['EventRW'] = event_rw

                if filter_params:
                    request.lookup_attribute = [
                        LookupEventsRequestLookupAttribute(key=key, value=value) for key, value in filter_params.items()

                    ]

                    # request.lookup_attribute = [{"Key": k, "Value": v} for k, v in filter_params.items()]
                logger.info("lookup action trail events with request: {}".format(request))
                response:actiontrail_20200706_models.LookupEventsResponse = actiontrail_client.lookup_events(request)
                logger.info("lookup action trail events with response: {}".format(response))
                response_body:actiontrail_20200706_models.LookupEventsResponseBody = response.body
                """
                {
                  "headers": {
                    "date": "Thu, 25 Sep 2025 13:28:08 GMT",
                    "content-type": "application/json;charset=utf-8",
                    "content-length": "1201",
                    "connection": "keep-alive",
                    "keep-alive": "timeout=25",
                    "vary": "Accept-Encoding",
                    "access-control-allow-origin": "*",
                    "access-control-expose-headers": "*",
                    "x-acs-request-id": "0D371542-0BC2-5DC2-9570-0299BEE7288D",
                    "x-acs-trace-id": "d9f7c3703058df3c761e62f492e5f7df",
                    "etag": "1rjFg8gfOfBCkYjaQCcoFOg1"
                  },
                  "statusCode": 200,
                  "body": {
                    "EndTime": "2025-09-25T23:59:59Z",
                    "Events": [
                      {
                        "eventId": "68D4BC64B29A8D36369698D9",
                        "eventVersion": 1,
                        "eventSource": "oss-cn-hangzhou-internal.aliyuncs.com",
                        "requestParameters": {
                          "stsTokenPlayerUid": "1803023858759084"
                        },
                        "sourceIpAddress": "211.144.221.1",
                        "userAgent": "aliyun-oss-console",
                        "eventRW": "Read",
                        "eventType": "ConsoleOperation",
                        "userIdentity": {
                          "accessKeyId": "STS.9jMtu5186zsezCML8QsdkLUedGwzfEEBnTNrrNQrTxeXGH9vGtBymR",
                          "sessionContext": {
                            "attributes": {
                              "mfaAuthenticated": "false"
                            }
                          },
                          "accountId": "1219234893152666",
                          "principalId": "347354551678227529:fum9",
                          "type": "assumed-role",
                          "userName": "GLOCHNALI-Cloud-Contributor:fum9"
                        },
                        "serviceName": "Oss",
                        "additionalEventData": {
                          "CallerBid": "26842"
                        },
                        "apiVersion": "2019-05-17",
                        "requestId": "68D4BC64B29A8D36369698D9",
                        "eventTime": "2025-09-25T03:52:04Z",
                        "isGlobal": false,
                        "acsRegion": "cn-hangzhou",
                        "eventName": "ListUserRegions"
                      }
                    ],
                    "NextToken": "CAESCQoHCgUKAXQQARgBIqEBCgkAoOb/fpkBAAAKkwEDjgAAADFTMzIzMDJkMzEzMjMxMzkzMjMzMzQzODM5MzMzMTM1MzIzNjM2MzYuUzMxMzIzMTM5MzIzMzM0MzgzOTMzMzEzNTMyMzYzNjM2Lkw4MDAwMDE5OTdlZmZlNmEwLlMzNjM4NDQzNDQyNDMzNjM0NDIzMjM5NDEzODQ0MzMzNjMzNjM5MzYzOTM4NDQzOQ==",
                    "RequestId": "0D371542-0BC2-5DC2-9570-0299BEE7288D",
                    "StartTime": "2025-08-01T00:00:00Z"
                  }
                }
                """
                # events_info = [
                #     {
                #         "eventId": event.event_id,
                #         "eventName": event.event_name,
                #         "eventTime": event.event_time,
                #         "serviceName": event.service_name,
                #         "acsRegion": event.region_id,
                #         "sourceIpAddress": event.source_ip_address,
                #         "eventType": event.event_type,
                #         "eventRW": event.event_rw,
                #         "userIdentity": {
                #             "accessKeyId": event.event_access_key_id,
                #             "userName": event.user,
                #             "type": "assumed-role" if event.role_name else "user",
                #             **({"sessionContext": {
                #                 "attributes": {"mfaAuthenticated": "false"}}} if event.role_name else {})
                #         },
                #         **({"requestParameters": {"resourceType": event.resource_type}} if event.resource_type else {}),
                #         **({"additionalEventData": event.event_data} if event.event_data else {}),
                #         "requestId": event.request_id,
                #         "eventVersion": event.event_version
                #     } for event in response_body.events
                # ]
                # events_info = [
                #     {
                #         "eventId": event.eventId,
                #         "eventVersion": event.eventVersion,
                #         "eventSource": event.eventSource,
                #         "requestParameters": event.requestParameters,
                #         "sourceIpAddress": event.sourceIpAddress,
                #         "userAgent": event.userAgent,
                #         "eventRW": event.eventRW,
                #         "eventType": event.eventType,
                #         "userIdentity": {
                #             "accessKeyId": event.accessKeyId,
                #             "sessionContext": {
                #                 "attributes": {
                #                     "mfaAuthenticated": event.mfaAuthenticated
                #                 }
                #             },
                #             "accountId": event.accountId,
                #             "principalId": event.principalId,
                #             "type": event.identityType,
                #             "userName": event.userName
                #         },
                #         "serviceName": event.serviceName,
                #         "additionalEventData": event.additionalEventData,
                #         "apiVersion": event.apiVersion,
                #         "requestId": event.requestId,
                #         "eventTime": event.eventTime,
                #         "isGlobal": event.isGlobal,
                #         "acsRegion": event.acsRegion,
                #         "eventName": event.eventName
                #     } for event in response_body.events
                # ]
                return response_body.events

            except Exception as e:
                return [{"error": f"查询失败: {str(e)}"}]

        # @self.mcp_instance.tool
        # def search_user_events(
        #         username: str,
        #         hours: int = 24,
        #         max_results: int = 50
        # ) -> List[Dict[str, Any]]:
        #     """
        #     查询特定用户的ActionTrail事件
        #
        #     Args:
        #         username: 用户名
        #         hours: 查询时间范围（小时）
        #         max_results: 最大返回结果数
        #
        #     Returns:
        #         用户事件列表
        #     """
        #     end_time = datetime.utcnow()
        #     start_time = end_time - timedelta(hours=hours)
        #
        #     return _lookup_events(
        #         start_time=start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        #         end_time=end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
        #         max_results=max_results
        #     )