import json
import base64
import os
import logging
from alibabacloud_ecs20140526.client import Client as Ecs20140526Client
from alibabacloud_credentials.client import Client as CredentialClient, Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_ecs20140526 import models as ecs_20140526_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient

from mcp_servers.base_server import BaseServer

from fastmcp.utilities import logging
logger = logging.get_logger(__name__)

# 命令执行状态描述
COMMAND_INVOCATION_STATUS_DESCRIPTIONS = {
    "Pending": "系统正在校验或发送命令",
    "Invalid": "命令类型或参数有误",
    "Aborted": "向实例发送命令失败（实例需运行且命令需1分钟内发送完成）",
    "Running": "命令正在实例上执行",
    "Success": "执行成功：退出码为0（或定时任务上一次成功且已结束）",
    "Failed": "执行失败：退出码非0（或定时任务上一次失败且将中止）",
    "Error": "执行异常无法继续",
    "Timeout": "命令执行超时",
    "Cancelled": "执行动作取消，命令未启动",
    "Stopping": "正在停止执行的命令",
    "Terminated": "命令执行中被终止",
    "Scheduled": "定时任务等待执行",
}

class ALI_CLOUD_ECS(BaseServer):

    ecs_client = None

    def __init__(self, cmd_config):
        super().__init__(cmd_config, "ali_cloud_ecs_mcp_server", prefix="ali_cloud_ecs_mcp_server")
        self.setup_server()
        #self.initialize_client()


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

    def initialize_client_4_specific_region(self,access_key_id:str,region_id:str) -> Ecs20140526Client:
        client = None
        """初始化 Aliyun action trail Client for specific region under specific account"""
        for config in self.alicloud_client_configs:
            if config.access_key_id == access_key_id:
                selected_config = config.config
                cred = Client(selected_config)
                config = open_api_models.Config(
                    credential=cred
                )
                config.endpoint = f'ecs.{region_id}.aliyuncs.com'
                client = Ecs20140526Client(config)
                break
        if client is None:
            raise ValueError(f"No valid Aliyun ECS client config found for account_id: {access_key_id}, region_id: {region_id}")
        else:
            logger.info(f"Successfully initialized Aliyun ECS client for account_id: {access_key_id}, region_id: {region_id}")
            return client


    def setup_server(self):
        @self.mcp_instance.tool
        async def describe_instances(
                access_key_id: str,
                region_id: str,
                # 分页参数
                page_number: int = 1,
                page_size: int = 10,
                next_token: str = None,
                max_results: int = None,

                # 实例标识参数 - 改为字符串类型
                instance_ids: str = None,  # JSON字符串格式：'["i-123", "i-456"]'
                instance_name: str = None,

                # 网络参数
                vpc_id: str = None,
                vswitch_id: str = None,
                security_group_id: str = None,
                instance_network_type: str = None,

                # IP地址参数 - 改为字符串类型
                inner_ip_addresses: str = None,  # JSON字符串格式
                private_ip_addresses: str = None,  # JSON字符串格式
                public_ip_addresses: str = None,  # JSON字符串格式
                eip_addresses: str = None,  # JSON字符串格式
                ipv6_addresses: str = None,  # JSON字符串格式

                # 实例配置参数
                instance_type: str = None,
                instance_type_family: str = None,
                image_id: str = None,
                zone_id: str = None,

                # 状态参数
                status: str = None,
                instance_charge_type: str = None,
                lock_reason: str = None,
                io_optimized: bool = None,

                # 其他参数
                key_pair_name: str = None,
                resource_group_id: str = None,
                hpc_cluster_id: str = None,
                rdma_ip_addresses: str = None,
                dry_run: bool = False,

                # 时间筛选参数
                creation_start_time: str = None,
                creation_end_time: str = None,
                expired_start_time: str = None,
                expired_end_time: str = None,

                # 元数据服务参数
                http_endpoint: str = None,
                http_tokens: str = None,
                http_put_response_hop_limit: int = None,

                # 标签和属性 - 改为字符串类型
                tags: str = None,  # JSON字符串格式
                additional_attributes: str = None,  # JSON字符串格式

        ) -> dict:
            """
            查询ECS实例列表,如果返回的信息中存在next_token，表示存在分页控制，如果寻找的资产不在此次返回的实例列表中，可以通过分页参数next_token继续查询

            Args:
                region_id: 实例所属的地域ID，如cn-hangzhou
                access_key_id: 使用哪个账号下的access_key_id来调用接口

                # 分页参数
                page_number: 页码（推荐使用next_token和max_results）
                page_size: 每页大小（<=100）
                next_token: 查询凭证，用于分页
                max_results: 每页行数（<=100）

                # 实例标识
                instance_ids: JSON字符串格式的实例ID列表，如：'["i-123", "i-456"]'
                instance_name: 实例名称，支持通配符*

                # 网络配置
                vpc_id: 专有网络VPC ID
                vswitch_id: 交换机ID
                security_group_id: 安全组ID
                instance_network_type: 实例网络类型（vpc/classic）

                # IP地址筛选（JSON字符串格式）
                inner_ip_addresses: 经典网络内网IP列表，如：'["10.1.1.1", "10.1.2.1"]'
                private_ip_addresses: VPC私有IP列表
                public_ip_addresses: 公网IP列表
                eip_addresses: 弹性公网IP列表
                ipv6_addresses: IPv6地址列表

                # 实例配置
                instance_type: 实例规格
                instance_type_family: 实例规格族
                image_id: 镜像ID
                zone_id: 可用区ID

                # 状态筛选
                status: 实例状态（Running/Stopped等）
                instance_charge_type: 计费方式（PostPaid/PrePaid）
                lock_reason: 锁定原因
                io_optimized: 是否I/O优化实例

                # 其他配置
                key_pair_name: SSH密钥对名称
                resource_group_id: 资源组ID
                hpc_cluster_id: HPC集群ID
                rdma_ip_addresses: RDMA网络IP
                dry_run: 是否只预检请求

                # 时间筛选
                creation_start_time: 创建开始时间（yyyy-MM-ddTHH:mmZ）
                creation_end_time: 创建结束时间
                expired_start_time: 过期开始时间
                expired_end_time: 过期结束时间

                # 元数据服务
                http_endpoint: 实例元数据访问通道（enabled/disabled）
                http_tokens: 元数据访问模式（optional/required）
                http_put_response_hop_limit: 跳数限制

                # 标签和属性（JSON字符串格式）
                tags: 标签列表，如：'[{"Key": "env", "Value": "prod"}]'
                additional_attributes: 其他属性列表，如：'["META_OPTIONS"]'

            Returns:
                dict: 包含ECS实例信息的字典
            """
            ecs_client = self.initialize_client_4_specific_region(access_key_id,region_id)

            def parse_json_string(json_str: str, param_name: str):
                """解析JSON字符串，处理解析错误"""
                if not json_str:
                    return None
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    raise ValueError(f"{param_name}必须是有效的JSON字符串: {e}")

            # 构建请求参数
            request_params = {
                "region_id": region_id,
                "page_number": page_number,
                "page_size": min(page_size, 100)  # 确保不超过限制
            }

            # 解析JSON字符串参数
            instance_ids_list = parse_json_string(instance_ids, "instance_ids")
            inner_ip_list = parse_json_string(inner_ip_addresses, "inner_ip_addresses")
            private_ip_list = parse_json_string(private_ip_addresses, "private_ip_addresses")
            public_ip_list = parse_json_string(public_ip_addresses, "public_ip_addresses")
            eip_list = parse_json_string(eip_addresses, "eip_addresses")
            ipv6_list = parse_json_string(ipv6_addresses, "ipv6_addresses")
            tags_list = parse_json_string(tags, "tags")
            additional_attrs_list = parse_json_string(additional_attributes, "additional_attributes")

            # 添加可选参数
            optional_params = {
                "next_token": next_token,
                "max_results": max_results,
                "instance_ids": instance_ids_list,
                "instance_name": instance_name,
                "vpc_id": vpc_id,
                "vswitch_id": vswitch_id,
                "security_group_id": security_group_id,
                "instance_network_type": instance_network_type,
                "instance_type": instance_type,
                "instance_type_family": instance_type_family,
                "image_id": image_id,
                "zone_id": zone_id,
                "status": status,
                "instance_charge_type": instance_charge_type,
                "lock_reason": lock_reason,
                "key_pair_name": key_pair_name,
                "resource_group_id": resource_group_id,
                "hpc_cluster_id": hpc_cluster_id,
                "rdma_ip_addresses": rdma_ip_addresses,
                "dry_run": dry_run,
                "http_endpoint": http_endpoint,
                "http_tokens": http_tokens,
                "http_put_response_hop_limit": http_put_response_hop_limit,
                "tag": tags_list,
                "additional_attributes": additional_attrs_list,
            }

            # 只添加非None的参数
            for key, value in optional_params.items():
                if value is not None:
                    request_params[key] = value

            # 处理布尔参数
            if io_optimized is not None:
                request_params["io_optimized"] = io_optimized

            # 处理IP地址列表参数（需要转换为JSON字符串传递给阿里云SDK）
            ip_params = {
                "inner_ip_addresses": inner_ip_list,
                "private_ip_addresses": private_ip_list,
                "public_ip_addresses": public_ip_list,
                "eip_addresses": eip_list,
                "ipv6_address": ipv6_list,
            }

            for key, value in ip_params.items():
                if value:
                    request_params[key] = json.dumps(value)

            # 处理时间筛选参数
            time_filters = {
                "creation_start_time": ("Filter.1.Key", "CreationStartTime", "Filter.1.Value"),
                "creation_end_time": ("Filter.2.Key", "CreationEndTime", "Filter.2.Value"),
                "expired_start_time": ("Filter.3.Key", "ExpiredStartTime", "Filter.3.Value"),
                "expired_end_time": ("Filter.4.Key", "ExpiredEndTime", "Filter.4.Value"),
            }

            filter_index = 1
            for param_name, (key_field, key_value, value_field) in time_filters.items():
                param_value = locals().get(param_name)
                if param_value:
                    request_params[key_field] = key_value
                    request_params[value_field] = param_value
                    filter_index += 1

            try:
                request = ecs_20140526_models.DescribeInstancesRequest(
                    **request_params
                )
                response = await ecs_client.describe_instances_with_options_async(
                    request,
                    util_models.RuntimeOptions()
                )
                return response.to_map()
            except Exception as e:
                raise RuntimeError(f"Failed to describe ECS instances: {e}")

        @self.mcp_instance.tool
        async def describe_security_group_attribute(
                access_key_id:str,
                region_id: str,

                security_group_id: str,
                nic_type: str = None,
                direction: str = "all",
                next_token: str = None,
                max_results: int = None,
                attribute: str = None
        ) -> dict:
            """
            查询安全组属性和规则详情

            Args:
                region_id: 安全组所属地域ID，如cn-hangzhou
                access_key_id: 使用哪个账号下的access_key_id来调用接口
                security_group_id: 安全组ID

                # 筛选参数
                nic_type: 安全组规则的网卡类型（intranet/internet）
                direction: 安全组规则授权方向（ingress/egress/all）
                attribute: 安全组属性（snapshotPolicyIds等）

                # 分页参数
                next_token: 查询凭证，用于分页
                max_results: 每页最大条目数（<=1000）

            Returns:
                dict: 包含安全组属性和规则信息的字典，包含以下字段：
                    - VpcId: VPC ID
                    - RequestId: 请求ID
                    - InnerAccessPolicy: 安全组内网络连通策略
                    - Description: 安全组描述信息
                    - SecurityGroupId: 安全组ID
                    - SecurityGroupName: 安全组名称
                    - RegionId: 地域ID
                    - Permissions: 安全组规则权限列表
                    - NextToken: 查询凭证
                    - SnapshotPolicyIds: 快照策略ID列表

            Example:
                >>> describe_security_group_attribute(
                ...     region_id="cn-hangzhou",
                ...     security_group_id="sg-bp1gxw6bznjjvhu3****",
                ...     direction="ingress",
                ...     nic_type="intranet"
                ... )
            """
            ecs_client = self.initialize_client_4_specific_region(access_key_id,region_id)

            # 构建请求参数
            request_params = {
                "region_id": region_id,
                "security_group_id": security_group_id
            }

            # 添加可选参数
            optional_params = {
                "nic_type": nic_type,
                "direction": direction,
                "next_token": next_token,
                "max_results": max_results,
                "attribute": attribute,
            }

            # 只添加非None的参数
            for key, value in optional_params.items():
                if value is not None:
                    request_params[key] = value

            # 验证max_results范围
            if max_results is not None and max_results > 1000:
                max_results = 1000
                request_params["max_results"] = str(max_results)

            try:
                request = ecs_20140526_models.DescribeSecurityGroupAttributeRequest(**request_params)
                response = await ecs_client.describe_security_group_attribute_with_options_async(
                    request,
                    util_models.RuntimeOptions()
                )
                return response.to_map()
            except Exception as e:
                raise RuntimeError(f"Failed to describe security group attribute: {e}")

        @self.mcp_instance.tool
        async def describe_regions(access_key_id,instance_charge_type=None,resource_type=None,accept_language="zh-CN") -> dict:
            """
            查询可用地域列表, 原则上任何阿里云账号下可能使用多个地域，都需要先到这里查询下可用地域
            Args:
                access_key_id: 使用哪个账号下的access_key_id来调用接口

                InstanceChargeType: str #实例的计费方式，取值：PrePaid（包年包月）、PostPaid（按量付费）。如果不指定，默认返回所有计费方式的地域。
                ResourceType: str #资源类型，取值：Instance（ECS实例）、Disk（云盘）、Snapshot（快照）、Image（镜像）、SecurityGroup（安全组）、KeyPair（密钥对）。如果不指定，默认返回所有资源类型的地域。
                AcceptLanguage: str #语言类型，取值：zh-CN（中文）、en-US（英文）。如果不指定，默认返回中文地域名称。

            Returns:
                dict: 包含地域信息的字典，包含以下字段：
                    - Regions: 地域列表
                    - RequestId: 请求ID

            Example:
                >>> describe_regions()
            """

            ecs_client = self.initialize_client_4_specific_region(access_key_id,"cn-hangzhou") #区域随便指定一个，因为DescribeRegions接口不区分区域

            try:
                request = ecs_20140526_models.DescribeRegionsRequest(
                    instance_charge_type=instance_charge_type,
                    resource_type=resource_type,
                    accept_language=accept_language,
                )
                response = await ecs_client.describe_regions_with_options_async(
                    request,
                    util_models.RuntimeOptions()
                )
                return response.to_map()
            except Exception as e:
                raise RuntimeError(f"Failed to describe regions: {e}")

        @self.mcp_instance.tool
        async def run_command_async(
                access_key_id: str,
                region_id: str,
                command_request:str,
                instance_id_list:list[str],
                os:str
        ) -> dict:
            """
            在指定ECS实例上运行命令

            Args:
                access_key_id: 使用哪个账号下的access_key_id来调用接口
                region_id: 实例所属的地域ID，如cn-hangzhou
                command_request: Base64格式的RunCommand请求参数
                instance_id_list: 执行命令所在的ECS实例ID列表
                os: 目标实例操作系统类型，取值：Linux、Windows
            Returns:
                commandId: 命令ID
                invokeId: 命令执行ID
            """
            ecs_client = self.initialize_client_4_specific_region(access_key_id,region_id)

            try:
                request = ecs_20140526_models.RunCommandRequest()
                request.instance_id = instance_id_list
                request.command_content = command_request
                request.region_id = region_id
                request.content_encoding = "Base64"
                request.keep_command = True
                if os == "Linux":
                    request.type = "RunShellScript"
                elif os == "Windows":
                    request.type = "RunPowerShellScript"
                else:
                    raise ValueError("Unsupported OS type. Must be 'Linux' or 'Windows'.")
                response:ecs_20140526_models.RunCommandResponse = await ecs_client.run_command_with_options_async(
                    request,
                    util_models.RuntimeOptions()
                )
                return {"commandId":response.body.command_id,"invokeId":response.body.invoke_id}
            except Exception as e:
                raise RuntimeError(f"Failed to run command on ECS instance: {e}")

        @self.mcp_instance.tool
        async def run_script_content_async(
                access_key_id: str,
                region_id: str,
                instance_id_list: list[str],
                os: str,
                script_content: str = None,
                local_script_path: str = None,
        ) -> dict:
            """
            在ECS实例上安全运行脚本。
            - 支持直接传入脚本内容(script_content)或提供本地脚本路径(local_script_path)读取。
            - 自动处理编码(BOM/UTF-8/GBK等)和换行(CRLF->LF)以避免内容截断或未闭合引号问题。
            - Linux: 使用单引号heredoc写入临时文件；若脚本包含shebang则直接执行该文件，否则使用bash执行。
            - Windows: 使用PowerShell单引号Here-String写入临时ps1文件并执行。
            """
            # 读入脚本内容（如果提供了本地路径）
            if local_script_path and not script_content:
                if not os.path.isfile(local_script_path):
                    raise FileNotFoundError(f"本地脚本不存在: {local_script_path}")
                raw = None
                with open(local_script_path, "rb") as f:
                    raw = f.read()
                decoded = None
                for enc in ("utf-8", "utf-8-sig", "gbk", "latin-1"):
                    try:
                        decoded = raw.decode(enc)
                        break
                    except Exception:
                        continue
                if decoded is None:
                    decoded = raw.decode("utf-8", errors="replace")
                # 规范换行，避免在Linux上出现CRLF导致解析异常
                script_content = decoded.replace("\r\n", "\n").replace("\r", "\n")
            if script_content is None:
                raise ValueError("必须提供脚本内容(script_content)或本地脚本路径(local_script_path)之一。")

            # 确保脚本末尾以换行结束，以避免heredoc/Here-String末行被吞导致内容不完整
            if not script_content.endswith("\n"):
                script_content = script_content + "\n"

            ecs_client = self.initialize_client_4_specific_region(access_key_id, region_id)

            try:
                if os == "Linux":
                    # 选择一个不与脚本内容冲突的heredoc分隔符
                    delim = "MCP_EOF"
                    while delim in script_content:
                        delim += "_X"

                    has_shebang = script_content.lstrip().startswith("#!")
                    # 构造不含缩进的脚本，确保heredoc分隔符在列首，避免未终止引号错误
                    bootstrap = (
                        "#!/bin/bash\n"
                        + "set -euo pipefail\n"
                        + "tmp=\"$(mktemp /tmp/aliyun_run_XXXXXX.sh)\"\n"
                        + f"cat <<'{delim}' > \"$tmp\"\n"
                        + f"{script_content}"
                        + f"{delim}\n"
                        + "chmod +x \"$tmp\"\n"
                        + ("\"$tmp\"\n" if has_shebang else "bash \"$tmp\"\n")
                    )
                    payload_b64 = base64.b64encode(bootstrap.encode("utf-8")).decode("utf-8")
                    request_type = "RunShellScript"

                elif os == "Windows":
                    # 使用单引号Here-String，防止插值；将脚本写入临时ps1文件后执行；确保Here-String定界符在列首
                    bootstrap = (
                        "$ErrorActionPreference = 'Stop'\n"
                        + "$tmp = [System.IO.Path]::GetTempFileName() + '.ps1'\n"
                        + "@'\n"
                        + f"{script_content}\n"
                        + "'@ | Set-Content -Path $tmp -Encoding UTF8\n"
                        + "powershell -ExecutionPolicy Bypass -File $tmp\n"
                    )
                    payload_b64 = base64.b64encode(bootstrap.encode("utf-8")).decode("utf-8")
                    request_type = "RunPowerShellScript"

                else:
                    raise ValueError("Unsupported OS type. Must be 'Linux' or 'Windows'.")

                request = ecs_20140526_models.RunCommandRequest()
                request.instance_id = instance_id_list
                request.command_content = payload_b64
                request.region_id = region_id
                request.content_encoding = "Base64"
                request.keep_command = True
                request.type = request_type

                response: ecs_20140526_models.RunCommandResponse = await ecs_client.run_command_with_options_async(
                    request,
                    util_models.RuntimeOptions()
                )
                return {"commandId": response.body.command_id, "invokeId": response.body.invoke_id}
            except Exception as e:
                raise RuntimeError(f"Failed to run script content on ECS instance: {e}")

        @self.mcp_instance.tool
        async def describe_invocation_results(
                access_key_id: str,
                region_id: str,
                command_id: str,
                instance_id: str,
                invoke_id: str,
                nextToken: str = None,
                maxResults: int = 50,
                include_output_on_error: bool = True,
                max_output_chars: int = 4000,
        ) -> str:
            """
            查询命令执行结果
            当执行命令后，不代表命令一定成功执行，并且一定有预期的命令效果。您需要通过本接口查看实际的具体执行结果，以实际输出结果为准。
            可以查询最近 4 周的执行信息，执行信息的保留上限为 10 万条。
            可以通过云助手任务状态事件订阅的方式，通过事件获取任务结果，避免频繁轮询，用以提升效率。
            分页查询首页时，仅需设置MaxResults以限制返回信息的条目数，返回结果中的NextToken将作为查询后续页的凭证。查询后续页时，将NextToken参数设置为上一次返回结果中获取到的NextToken作为查询凭证，并设置MaxResults限制返回条目数。
            DescribeInvocations和DescribeInvocationResults差异点：
            当一次RunCommand/InvokeCommand调用指定有多个实例时：
            使用DescribeInvocations可以获得任务在各个实例上的执行状态、多个实例任务状态的聚合状态；
            使用DescribeInvocationResults仅能获得各个实例上的单独的执行状态，不包含多实例的聚合状态；
            当一次RunCommand/InvokeCommand调用指定有一个实例时：
            DescribeInvocations与DescribeInvocationResults区别不大，完全可以互相替换。
            当需要查看定时性（周期性）任务、开机自动执行任务（RepeatMode=Period, EveryReboot）的每一次执行情况时，仅能用DescribeInvocationResults可以查询获得执行的过往历史记录（需指定IncludeHistory=true），而DescribeInvocations仅支持返回最新的任务状态。
            当需要查看命令的内容、参数时，仅有DescribeInvocations返回CommandContent

            Args:
                access_key_id: 使用哪个账号下的access_key_id来调用接口
                region_id: 实例所属的地域ID，如cn-hangzhou
                command_id: 运行命令时返回的commandId
                instance_id: ECS实例ID
                invoke_id: 运行命令时返回的invokeId
                nextToken: 分页查询时的查询凭证
                maxResults: 每页最大条目数（<=50）
                include_output_on_error: 当命令失败或退出码非0时，是否在错误信息中附带解码后的输出片段（默认 True）
                max_output_chars: 错误信息中输出片段的最大长度（默认 4000）

            Returns:
                str: 返回的是命令执行结果，用Base64编码，需要解码后查看
            """
            ecs_client = self.initialize_client_4_specific_region(access_key_id,region_id)
            try:
                request = ecs_20140526_models.DescribeInvocationResultsRequest(
                    command_id=command_id,
                    instance_id=instance_id,
                    region_id=region_id,
                    content_encoding="Base64",
                    invoke_id=invoke_id,
                    max_results=maxResults,
                    next_token=nextToken,
                )
                response: ecs_20140526_models.DescribeInvocationResultsResponse = await ecs_client.describe_invocation_results_with_options_async(
                    request,
                    util_models.RuntimeOptions()
                )

                # 安全获取结果列表
                inv_container = response.body.invocation if response and response.body else None
                inv_results_container = inv_container.invocation_results if inv_container else None
                inv_list = inv_results_container.invocation_result if inv_results_container else None
                if not inv_list or len(inv_list) == 0:
                    raise RuntimeError(f"未找到命令执行结果；instance_id={instance_id}, command_id={command_id}, invoke_id={invoke_id}")

                invocation_result = inv_list[0]
                status = invocation_result.invocation_status
                exit_code = invocation_result.exit_code
                error_code = invocation_result.error_code
                error_info = invocation_result.error_info
                output_b64 = invocation_result.output or ""

                logger.debug(f"Invocation status={status} exit_code={exit_code} error_code={error_code} instance={instance_id}")

                # 构建输出片段（仅在错误时附带）
                def build_output_snippet():
                    if not include_output_on_error or not output_b64:
                        return ""
                    try:
                        decoded = base64.b64decode(output_b64).decode("utf-8", errors="replace")
                    except Exception as de:
                        return f"\n输出解码失败: {de}"
                    if len(decoded) > max_output_chars:
                        return f"\n输出片段(截断为{max_output_chars}字节):\n{decoded[:max_output_chars]}"
                    return f"\n输出片段:\n{decoded}"

                # 按状态分类处理
                if status in ("Pending", "Running", "Scheduled", "Stopping"):
                    desc = COMMAND_INVOCATION_STATUS_DESCRIPTIONS.get(status, "进行中")
                    raise RuntimeError(f"命令状态[{status}]：{desc}，请稍后重试；instance_id={instance_id}, command_id={command_id}, invoke_id={invoke_id}")

                if status in ("Invalid", "Aborted", "Error", "Timeout", "Cancelled", "Terminated"):
                    desc = COMMAND_INVOCATION_STATUS_DESCRIPTIONS.get(status, "失败")
                    raise RuntimeError(
                        f"命令状态[{status}]失败：{desc}；exit_code={exit_code}；error_code={error_code or '无'}；错误信息: {error_info or '无'}；"
                        f"instance_id={instance_id}, command_id={command_id}, invoke_id={invoke_id}"
                        + build_output_snippet()
                    )

                if status == "Failed":
                    msg = (
                        f"命令执行失败，退出码: {exit_code}；error_code={error_code or '无'}；错误: {error_info or '无'}；"
                        f"instance_id={instance_id}, command_id={command_id}, invoke_id={invoke_id}"
                        + build_output_snippet()
                    )
                    # 针对常见的引号未闭合错误提供更具体的诊断与修复建议
                    if include_output_on_error and output_b64:
                        try:
                            _decoded = base64.b64decode(output_b64).decode("utf-8", errors="replace")
                            if "Unterminated quoted string" in _decoded:
                                msg += "\n诊断: 检测到Shell报错“Unterminated quoted string”。这通常是由于将脚本内容用引号包裹导致的字符串未闭合。\n修复建议: 使用工具 run_script_content_async 传入原始脚本内容，或在构建命令内容时使用 heredoc（例如 <<'EOF' ... EOF）避免转义问题。"
                        except Exception:
                            pass
                    raise RuntimeError(msg)

                if status == "Success":
                    if UtilClient.equal_string(f"{exit_code}", "0"):
                        return output_b64  # Base64 编码输出
                    else:
                        raise RuntimeError(
                            f"命令标记成功但退出码非0({exit_code})；error_code={error_code or '无'}；错误: {error_info or '无'}；"
                            f"instance_id={instance_id}, command_id={command_id}, invoke_id={invoke_id}"
                            + build_output_snippet()
                        )

                # 未知状态兜底
                raise RuntimeError(
                    f"未识别的命令状态[{status}]；error_code={error_code or '无'}；请检查：{error_info or '无'}；"
                    f"instance_id={instance_id}, command_id={command_id}, invoke_id={invoke_id}"
                    + build_output_snippet()
                )
            except Exception as e:
                raise RuntimeError(f"Failed to describe invocation results: {e}")

        @self.mcp_instance.tool
        async def upload_file_async(
            access_key_id: str,
            region_id: str,
            instance_id_list: list[str],
            local_file_path: str,
            remote_file_path: str,
            os_type: str,
            run_after_upload: bool = False
        ) -> dict:
            """
            上传本地文件到指定 ECS 实例，并可选择上传后执行

            Args:
                access_key_id: 使用哪个账号下的access_key_id来调用接口
                region_id: 实例所属的地域ID，如cn-hangzhou
                instance_id_list: ECS实例ID列表
                local_file_path: 本地待上传文件路径
                remote_file_path: ECS上目标文件路径
                os_type: Linux 或 Windows
                run_after_upload: 是否在上传后执行文件
            Returns:
                dict: 包含上传命令ID和执行命令ID（如果执行了）
            """
            if not os.path.isfile(local_file_path):
                raise FileNotFoundError(f"本地文件不存在: {local_file_path}")

            # 读取文件并Base64编码
            with open(local_file_path, "rb") as f:
                file_content_b64 = base64.b64encode(f.read()).decode("utf-8")

            ecs_client = self.initialize_client_4_specific_region(access_key_id, region_id)

            try:
                # 生成上传命令内容
                if os_type == "Linux":
                    # 使用echo + base64解码写入目标文件
                    # 使用printf避免echo将以'-'开头的Base64误判为选项；并保持严格单引号包裹内容
                    command_content = f"printf '%s' '{file_content_b64}' | base64 -d > {remote_file_path}"
                    command_type = "RunShellScript"
                    run_command = f"chmod +x {remote_file_path} && {remote_file_path}" if run_after_upload else None
                elif os_type == "Windows":
                    # Windows PowerShell上传
                    command_content = (
                        f"$content = '{file_content_b64}'; "
                        f"[System.IO.File]::WriteAllBytes('{remote_file_path}', [Convert]::FromBase64String($content))"
                    )
                    command_type = "RunPowerShellScript"
                    run_command = remote_file_path if run_after_upload else None
                else:
                    raise ValueError("Unsupported OS type. Must be 'Linux' or 'Windows'.")

                # 上传文件命令
                upload_request = ecs_20140526_models.RunCommandRequest()
                upload_request.instance_id = instance_id_list
                upload_request.command_content = base64.b64encode(command_content.encode("utf-8")).decode("utf-8")
                upload_request.region_id = region_id
                upload_request.content_encoding = "Base64"
                upload_request.keep_command = True
                upload_request.type = command_type

                upload_response: ecs_20140526_models.RunCommandResponse = await ecs_client.run_command_with_options_async(
                    upload_request,
                    util_models.RuntimeOptions()
                )

                result = {"uploadCommandId": upload_response.body.command_id, "uploadInvokeId": upload_response.body.invoke_id}

                # 如果需要执行
                if run_command:
                    exec_request = ecs_20140526_models.RunCommandRequest()
                    exec_request.instance_id = instance_id_list
                    exec_request.region_id = region_id
                    exec_request.content_encoding = "Base64"
                    exec_request.keep_command = True
                    exec_request.type = command_type
                    # 设置要执行的命令内容
                    exec_request.command_content = base64.b64encode(run_command.encode("utf-8")).decode("utf-8")

                    exec_response: ecs_20140526_models.RunCommandResponse = await ecs_client.run_command_with_options_async(
                        exec_request,
                        util_models.RuntimeOptions()
                    )
                    result.update({"execCommandId": exec_response.body.command_id, "execInvokeId": exec_response.body.invoke_id})

                return result

            except Exception as e:
                raise RuntimeError(f"Failed to upload or execute file on ECS instance: {e}")
