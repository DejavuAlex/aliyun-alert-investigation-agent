import json

from alibabacloud_credentials.client import Client

from mcp_servers.base_server import BaseServer
from fastmcp.utilities import logging

from alibabacloud_sas20181203.client import Client as SASClient
from alibabacloud_sas20181203 import models as sas_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as tea_models

logger = logging.get_logger(__name__)

class ALI_CLOUD_SECURITY_CENTER(BaseServer):
    def __init__(self,cmd_config):
        super().__init__(cmd_config,"ali_sas_mcp_server", prefix="ali_sas_mcp_server")
        self.setup_server()
        #self.initialize_client()

    # def initialize_client(self):
    #     """ initialize Aliyun AcsClient """
    #     from alibabacloud_sas20181203.client import Client
    #
    #     access_key_id = self.alicloud_client_configs
    #     access_key_secret = self.cmd_config.alicloud_configs["access_key_secret"]
    #     region_id = self.cmd_config.alicloud_configs["region_id"]
    #     from alibabacloud_tea_openapi import models as open_api_models
    #
    #     sas_client_config = open_api_models.Config(
    #         access_key_id=access_key_id,
    #         access_key_secret=access_key_secret,
    #         endpoint="tds.cn-shanghai.aliyuncs.com",
    #     )
    #     if not access_key_id or not access_key_secret or not region_id:
    #         raise ValueError("alicloud access key id,secret and region_id must be provided in internal_config.yaml")
    #
    #     self.client = Client(config=sas_client_config)

    def initialize_client_4_specific_region(self,access_key_id:str,region_id:str) -> SASClient:
        client = None
        """初始化 Aliyun action trail Client for specific region under specific account"""
        for config in self.alicloud_client_configs:
            if config.access_key_id == access_key_id:
                selected_config = config.config
                cred = Client(selected_config)
                config = open_api_models.Config(
                    credential=cred
                )
                # attention: always cn-shanghai !
                config.endpoint = f'tds.cn-shanghai.aliyuncs.com'
                client = SASClient(config)
                break
        if client is None:
            raise ValueError(f"No valid Aliyun client config found for account_id: {access_key_id}, region_id: {region_id}")
        else:
            logger.info(f"Successfully initialized Aliyun SAS client for account_id: {access_key_id}, region_id: {region_id}")
            return client

    def setup_server(self):
        @self.mcp_instance.tool
        async def describe_susp_events(

                # 必需参数
                access_key_id: str,
                region_id: str,
                time_start: str,
                time_end: str,

                # 分页参数
                page_size: int = 20,
                current_page: int = 1,

                # 事件基本信息参数
                name: str = None,
                levels: str =  "serious,suspicious,remind",
                dealed: str = None,
                status: str = None,
                remark: str = None,

                # 事件类型参数
                parent_event_types: str = None,
                event_names: str = None,
                strict_mode: str = None,
                tactic_id: str = None,

                # 资产相关参数
                uuids: str = None,
                group_id: int = None,
                assets_type_list: str = None,
                cluster_id: str = None,

                # 容器相关参数
                container_field_name: str = None,
                container_field_value: str = None,
                target_type: str = None,

                # 时间范围参数
                operate_time_start: str = None,
                operate_time_end: str = None,

                # 排序参数
                sort_column: str = "operateTime",
                sort_type: str = "desc",

                # 其他参数
                source_ip: str = None,
                lang: str = "zh",
                alarm_unique_info: str = None,
                unique_info: str = None,
                id: int = None,
                source: str = "sas",
                operate_error_code_list: str = None,
                resource_directory_account_id: int = None,
                multi_account_action_type: int = 0,
                source_ali_uids: str = None

        ) -> dict:
            """
            查询安全告警事件列表, 如果未指定时间区间，默认是查询最近30天的安全事件。
            当调用本工具时传入的事件相关名字时候，首先传入parent_event_types进行搜索，如果搜索不到，再传入event_names进行搜索。
            注意：执行本工具前，先要确定是否有相关的调查模版prompt工具，如果有请先拿到模版，再执行本工具

            Args:
                access_key_id: str, 阿里云访问密钥ID
                region_id: str, 阿里云地域ID
                time_start: 最新发生时间起始时间，格式：YYYY-MM-DD HH:MM:SS
                time_end: 最新发生时间结束时间，格式：YYYY-MM-DD HH:MM:SS

                # 分页参数
                page_size: 每页显示的告警事件数量（<=100），默认20
                current_page: 当前页码，默认1

                # 事件基本信息
                name: 受影响的资产名称
                levels: 告警事件紧急程度，多个用逗号分隔（serious,suspicious,remind）
                dealed: 是否已处理（Y/N）
                status: 告警事件状态
                remark: 告警名称或资产信息

                # 事件类型
                parent_event_types: 告警事件的告警类型
                event_names: 告警事件的子类型，多个用逗号分隔
                strict_mode: 是否严格模式告警（Y/N）
                tactic_id: ATT&CK战术ID

                # 资产相关
                uuids: 服务器UUID列表，JSON字符串格式，如：'["uuid1","uuid2"]'
                group_id: 资产分组ID
                assets_type_list: 资产类型集合，JSON字符串格式
                cluster_id: 集群ID

                # 容器相关
                container_field_name: 容器检索项（instanceId等）
                container_field_value: 容器检索项对应值
                target_type: 容器检索目标类型（containerId等）

                # 时间范围
                operate_time_start: 处理时间开始时间戳，格式：YYYY-MM-DD HH:MM:SS
                operate_time_end: 处理时间结束时间戳，格式：YYYY-MM-DD HH:MM:SS

                # 排序参数
                sort_column: 排序字段（operateTime等），默认operateTime
                sort_type: 排序类型（asc/desc），默认desc

                # 其他参数
                source_ip: 访问源IP地址
                lang: 语言类型（zh/en等），默认zh
                alarm_unique_info: 告警事件唯一标识ID
                unique_info: 安全告警的唯一key
                id: 告警事件唯一标识ID
                source: 告警来源，默认sas
                operate_error_code_list: 处理结果码集合，JSON字符串格式
                resource_directory_account_id: 资源目录成员账号ID
                multi_account_action_type: 多账号查询类型，默认0
                source_ali_uids: 产生告警的阿里云账号ID列表，JSON字符串格式

            Returns:
                dict: 包含告警事件信息的字典，包含以下字段：
                    - current_page: 当前页码
                    - page_size: 每页大小
                    - RequestId: 请求ID
                    - TotalCount: 告警事件总数
                    - Count: 当前页数据条数
                    - SuspEvents: 告警事件列表

            Example:
                >>> # 查询未处理的严重告警
                >>> describe_susp_events(
                ...     time_start="2023-07-05 00:00:00",
                ...     time_end="2023-07-06 23:59:59",
                ...     levels="serious",
                ...     dealed="N",
                ...     page_size=50
                ... )

                >>> # 按指定服务器查询
                >>> describe_susp_events(
                ...     time_start="2023-07-05 00:00:00",
                ...     time_end="2023-07-06 23:59:59",
                ...     uuids='["bb5d2484-f10e-450d-8917-3e79667e****"]',
                ...     levels="serious,suspicious"
                ... )

                >>> # 容器安全事件查询
                >>> describe_susp_events(
                ...     time_start="2023-07-05 00:00:00",
                ...     time_end="2023-07-06 23:59:59",
                ...     container_field_name="instanceId",
                ...     container_field_value="ccf9769c22b844ff9b8d57417683b****",
                ...     target_type="containerId"
                ... )
            """
            logger.info(f"for describe suspicisous events, the access_key_id: {access_key_id}, region_id: {region_id}")

            def parse_json_string(json_str: str, param_name: str):
                """解析JSON字符串"""
                if not json_str:
                    return None
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    raise ValueError(f"{param_name}必须是有效的JSON字符串: {e}")

            try:

                sc_client = self.initialize_client_4_specific_region(access_key_id, region_id)
                # 构建基础请求参数
                request_params = {
                    "time_start": time_start,
                    "time_end": time_end,
                    "page_size": min(page_size, 100),  # 确保不超过最大限制
                    "current_page": current_page,
                    "lang": lang,
                    "source": source,
                    "sort_column": sort_column,
                    "sort_type": sort_type,
                    "multi_account_action_type": multi_account_action_type
                }

                # 解析JSON字符串参数
                uuids_list = parse_json_string(uuids, "uuids")
                assets_type_list_parsed = parse_json_string(assets_type_list, "assets_type_list")
                operate_error_code_list_parsed = parse_json_string(operate_error_code_list, "operate_error_code_list")
                source_ali_uids_list = parse_json_string(source_ali_uids, "source_ali_uids")

                # 添加所有可选参数
                optional_params = {
                    "name": name,
                    "levels": levels,
                    "dealed": dealed,
                    "status": status,
                    "remark": remark,
                    "parent_event_types": parent_event_types,
                    "event_names": event_names,
                    "strict_mode": strict_mode,
                    "tactic_id": tactic_id,
                    "uuids": uuids_list,
                    "group_id": group_id,
                    "assets_type_list": assets_type_list_parsed,
                    "cluster_id": cluster_id,
                    "container_field_name": container_field_name,
                    "container_field_value": container_field_value,
                    "target_type": target_type,
                    "operate_time_start": operate_time_start,
                    "operate_time_end": operate_time_end,
                    "source_ip": source_ip,
                    "alarm_unique_info": alarm_unique_info,
                    "unique_info": unique_info,
                    "id": id,
                    "operate_error_code_list": operate_error_code_list_parsed,
                    "resource_directory_account_id": resource_directory_account_id,
                    "source_ali_uids": source_ali_uids_list,
                }

                # 只添加非None的参数
                for key, value in optional_params.items():
                    if value is not None:
                        request_params[key] = value

                # 创建请求对象
                request = sas_models.DescribeSuspEventsRequest(**request_params)
                runtime = tea_models.RuntimeOptions()

                response = await sc_client.describe_susp_events_with_options_async(request, runtime)
                return response.to_map()

            except Exception as e:
                logger.error(f"DescribeSuspEvents failed: {str(e)}")
                return {"error": str(e)}

        @self.mcp_instance.tool
        async def describe_susp_event_detail(
                access_key_id: str,
                region_id: str,

                suspicious_event_id: int,
                from_: str = "sas",
                lang: str = "zh",
                source_ip: str = None,
                resource_directory_account_id: int = None
        ) -> dict:
            """
            查询单个安全告警事件的详情

            Args:
                access_key_id (str): Aliyun access key id
                region_id (str): Aliyun region id

                suspicious_event_id: 告警事件ID（必填）
                from_: 告警事件数据的来源，固定为"sas"
                lang: 请求和接收消息的语言类型，默认"zh"（zh-中文/en-英文）
                source_ip: 访问源的IP地址
                resource_directory_account_id: 资源目录成员账号主账号ID

            Returns:
                dict: 包含安全事件详情的字典，包含以下字段：
                    - DataSource: 告警事件的数据来源
                    - EventName: 告警事件的名称
                    - InternetIp: 服务器的公网IP
                    - IntranetIp: 服务器的私网IP
                    - LastTime: 告警事件最新发生时间
                    - OperateMsg: 告警事件处理结果的说明
                    - Uuid: 服务器实例的UUID
                    - CanBeDealOnLine: 是否支持在线处理告警事件
                    - RequestId: 请求ID
                    - EventTypeDesc: 告警事件类型说明
                    - EventDesc: 告警事件的描述信息
                    - InstanceName: 服务器的名称
                    - EventStatus: 告警事件状态
                    - SaleVersion: 云安全中心版本
                    - OperateErrorCode: 告警事件的处理结果
                    - Level: 告警事件的危险等级（serious/suspicious/remind）
                    - Id: 记录告警事件的唯一标识ID
                    - Details: 告警事件的详情列表

            Example:
                >>> describe_susp_event_detail(
                ...     suspicious_event_id=32750999,
                ...     lang="zh",
                ...     source_ip="121.33.XX.XX"
                ... )
            """
            try:
                sc_client = self.initialize_client_4_specific_region(access_key_id, region_id)
                # 构建请求参数
                request_params = {
                    "suspicious_event_id": suspicious_event_id,
                    "from_": from_,
                    "lang": lang
                }

                # 添加可选参数
                if source_ip:
                    request_params["source_ip"] = source_ip
                if resource_directory_account_id:
                    request_params["resource_directory_account_id"] = resource_directory_account_id

                request = sas_models.DescribeSuspEventDetailRequest(**request_params)
                runtime = tea_models.RuntimeOptions()
                response = sc_client.describe_susp_event_detail_with_options(request, runtime)
                return response.to_map()
            except Exception as e:
                logger.error(f"DescribeSuspEventDetail failed: {str(e)}")
                return {"error": str(e)}
            
        @self.mcp_instance.tool
        async def list_check_item_warning_summary(
                access_key_id: str,
                region_id: str,

                # 分页参数
                page_size: int = 20,
                current_page: int = 1,

                check_item_type: str = None,
                lang: str = "zh",
                source_ip: str = None,
                resource_directory_account_id: int = None,
        ) -> dict:
            """
            查询云安全中心基线检测结果

            Args:
                access_key_id (str): Aliyun access key id
                region_id (str): Aliyun region id

                check_item_type (str): 检测项类型
                lang (str): 请求和接收消息的语言类型，默认"zh"（zh-中文/en-英文）
                source_ip (str): 访问源IP地址
                resource_directory_account_id (int): 资源目录成员主账号ID

            Returns:
                dict: 包含检测项告警汇总信息的字典，包含以下字段：
                    - RequestId: 请求ID
                    - CheckIdList: 检查项ID列表（用于调用 ListCheckItemWarningMachine）
                    - List: 检查项告警汇总列表，每个元素包含：
                        - check_id: 检查项ID
                        - CheckItem: 检查项名称
                        - CheckLevel: 风险等级（high / medium / low）
                        - CheckType: 检查项类型（如：入侵防范）
                        - ContainerCheckItem: 是否为容器相关检查项
                        - Status: 检测项状态（1-启用，0-禁用）
                        - WarningMachineCount: 存在告警的服务器数量
                        - Description: 检查项描述
                        - Advice: 修复建议
                        - EnableRisks: 关联的启用风险基线列表
                        - AffiliatedRisks: 所属风险基线列表
                        - AffiliatedRiskTypes: 所属风险类型列表

            Example:
                >>> result = await list_check_item_warning_summary(
                ...     check_id = 697 ,
                ...     CheckItem = "Redis弱口令"
                        CheckLevel = "high"
                        CheckType = "入侵防范"
                        WarningMachineCount = "1"
                ...     Advice = "xxx")
            """
            try:
                sc_client = self.initialize_client_4_specific_region(access_key_id, region_id)

                # 构建请求参数
                request_params = {
                    "lang": lang,
                    "current_page": current_page,
                    "page_size": min(page_size, 100),
                }

                # 添加可选参数
                if check_item_type:
                    request_params["CheckItemType"] = check_item_type

                if source_ip:
                    request_params["SourceIp"] = source_ip

                if resource_directory_account_id:
                    request_params["ResourceDirectoryAccountId"] = resource_directory_account_id

                request = sas_models.ListCheckItemWarningSummaryRequest(**request_params)
                runtime = tea_models.RuntimeOptions()

                response = sc_client.list_check_item_warning_summary_with_options(request, runtime)

                return response.to_map()

            except Exception as e:
                logger.error(f"ListCheckItemWarningSummary failed: {str(e)}")
                return {"error": str(e)}
            

        @self.mcp_instance.tool
        async def list_check_item_warning_machine(
                access_key_id: str,
                region_id: str,
                page_size: int = 20,
                current_page: int = 1,
                check_id: int = None,
                lang: str = "zh",
                source_ip: str = None,
                resource_directory_account_id: int = None,
        ) -> dict:
            """
            查询指定基线检测项下存在告警的服务器列表

            Args:
                access_key_id (str): Aliyun access key id
                region_id (str): Aliyun region id

                check_id (int): 检查项ID（必填）
                lang (str): 请求和返回语言，默认 zh（zh-中文 / en-英文）
                source_ip (str): 请求来源IP地址
                resource_directory_account_id (int): 资源目录成员主账号ID
                current_page (int): 当前页码，默认 1
                page_size (int): 每页条数，默认 10

            Returns:
                dict: 返回服务器告警列表，常见字段包括：
                    - RequestId: 请求ID
                    - PageInfo: 分页信息
                    - MachineList: 告警服务器列表
                        - InstanceId: 实例ID
                        - Uuid: 服务器UUID
                        - InternetIp: 公网IP
                        - IntranetIp: 内网IP
                        - InstanceName: 实例名称
                        - Status: 当前告警状态
                        - RiskLevel: 风险等级
                        - LastCheckTime: 最近检查时间
            """

            try:
                sc_client = self.initialize_client_4_specific_region(access_key_id, region_id)

                # 构建请求参数
                request_params = {
                    "check_id": check_id,
                    "lang": lang,
                    "current_page": current_page,
                    "page_size": min(page_size, 100),
                }

                # 添加可选参数
                if source_ip:
                    request_params["SourceIp"] = source_ip

                if resource_directory_account_id:
                    request_params["ResourceDirectoryAccountId"] = resource_directory_account_id

                request = sas_models.ListCheckItemWarningMachineRequest(**request_params)
                runtime = tea_models.RuntimeOptions()

                response = sc_client.list_check_item_warning_machine_with_options(request, runtime)

                return response.to_map()

            except Exception as e:
                logger.error(f"ListCheckItemWarningMachine failed: {str(e)}")
                return {"error": str(e)}

