
from alibabacloud_vpc20160428.client import Client as Vpc20160428Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_vpc20160428 import models as vpc_20160428_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_vpc20160428.models import DescribeEipAddressesRequestFilter

from mcp_servers.base_server import BaseServer

from fastmcp.utilities import logging
logger = logging.get_logger(__name__)

class ALI_CLOUD_VPC(BaseServer):

    ecs_client = None

    def __init__(self, cmd_config):
        super().__init__(cmd_config, "ali_cloud_vpc_mcp_server", prefix="ali_cloud_vpc_mcp_server")
        self.setup_server()

    def initialize_client_4_specific_region(self,access_key_id:str,region_id:str) -> Vpc20160428Client:
        client = None
        """初始化 Aliyun action trail Client for specific region under specific account"""
        for config in self.alicloud_client_configs:
            if config.access_key_id == access_key_id:
                selected_config = config.config
                cred = CredentialClient(selected_config)
                config = open_api_models.Config(
                    credential=cred
                )
                config.endpoint = f'vpc.{region_id}.aliyuncs.com'
                client = Vpc20160428Client(config)
                break
        if client is None:
            raise ValueError(f"No valid Aliyun VPC client config found for account_id: {access_key_id}, region_id: {region_id}")
        else:
            logger.info(f"Successfully initialized Aliyun VPC client for account_id: {access_key_id}, region_id: {region_id}")
            return client


    def setup_server(self):
        @self.mcp_instance.tool
        async def describe_eip_addresses(
                access_key_id: str,
                region_id: str,
                include_reservation_data: bool = None,
                status: str = None,
                eip_address: str = None,
                allocation_id: str = None,
                segment_instance_id: str = None,
                resource_group_id: str = None,
                page_number: int = 1,
                page_size: int = 10,
                isp: str = None,
                lock_reason: str = None,
                associated_instance_type: str = None,
                associated_instance_id: str = None,
                charge_type: str = None,
                dry_run: bool = None,
                eip_name: str = None,
                security_protection_enabled: bool = None,
                public_ip_address_pool_id: str = None,
                service_managed: bool = None,
                creation_start_time: str = None,
                creation_end_time: str = None
        ):
            """
            提供查询阿里云上是否有公网IP的功能。具体来说，就是查询指定地域已创建的EIP,EIP是阿里云的外网IP资源。可以绑定实例，类型如 ECS、NAT 网关、SLB 等

            参数:
            - access_key_id: 访问密钥ID
            - region_id: 地域ID
            - include_reservation_data: 是否包含未生效的订购数据
            - status: EIP状态
            - eip_address: EIP的IP地址
            - allocation_id: EIP实例ID
            - segment_instance_id: 连续EIP的实例ID
            - resource_group_id: 资源组ID
            - page_number: 页码
            - page_size: 每页行数
            - isp: 线路类型
            - lock_reason: 锁定类型
            - associated_instance_type: 绑定的云产品实例类型
            - associated_instance_id: 云产品实例ID
            - charge_type: 付费模式
            - dry_run: 是否只预检
            - eip_name: EIP名称
            - security_protection_enabled: 是否开启DDoS防护
            - public_ip_address_pool_id: IP地址池ID
            - service_managed: 是否为托管实例
            - creation_start_time: 创建开始时间(UTC格式: YYYY-MM-DDThh:mmZ)
            - creation_end_time: 创建结束时间(UTC格式: YYYY-MM-DDThh:mmZ)
            :return:
            - result: 包含EIP信息的字典
            - example:
            {
                "EipAddresses": {
                    "EipAddress": [
                        {
                            "AllocationId": "eip-1234567890abcdefg",
                            "IpAddress": "10.142.23.30",
                            "Status": "Available",
                            "InstanceId": "",
                            "Bandwidth": 5,
                            "InternetChargeType": "PayByTraffic",
                            "AllocationTime": "2023-10-01T12:00:00Z",
                            "RegionId": "cn-hangzhou",
                            "EipName": "MyEIP",
                            "Description": "My first EIP",
                            "ChargeType": "PostPaid",
                            "ExpiredTime": "2024-10-01T12:00:00Z",
                            "InstanceType": "",
                            "InstanceRegionId": "",
                            "OperationLocks": {
                                "LockReason": []
                            },
                            "Tags": {
                                "Tag": []
                            },
                            "SecurityProtectionEnabled": false,
                            "ServiceManaged": false
                        }
                    ]
                },
                "PageNumber": 1,
                "PageSize": 10,
                "TotalCount": 1,
                "RequestId": "ABCDEF12-3456-7890-ABCD-EF1234567890"
            }
            以上示例展示了一个包含单个EIP信息的响应结构。实际返回结果会根据查询条件和账户下的EIP数量有所不同。
            具体字段说明请参考官方文档:
            https://next.api.aliyun.com/api/VPC/2016-04-28/DescribeEipAddresses?params={}


            """
            vpc_client = self.initialize_client_4_specific_region(access_key_id, region_id)
            filter = []
            if creation_start_time:
                create_start_time = DescribeEipAddressesRequestFilter(
                    "CreationStartTime",
                    creation_start_time
                )
                filter.append(create_start_time)
            if creation_end_time:
                create_end_time = DescribeEipAddressesRequestFilter(
                    "CreationEndTime",
                    creation_end_time
                )
                filter.append(create_end_time)

            request = vpc_20160428_models.DescribeEipAddressesRequest(
                region_id=region_id,
                page_number=page_number,
                page_size=page_size,
                include_reservation_data=include_reservation_data,
                status=status,
                eip_address=eip_address,
                allocation_id=allocation_id,
                segment_instance_id=segment_instance_id,
                resource_group_id=resource_group_id,
                isp=isp,
                lock_reason=lock_reason,
                associated_instance_type=associated_instance_type,
                associated_instance_id=associated_instance_id,
                charge_type=charge_type,
                dry_run=dry_run,
                eip_name=eip_name,
                security_protection_enabled=security_protection_enabled,
                public_ip_address_pool_id=public_ip_address_pool_id,
                service_managed=service_managed,
                filter = filter
            )
            runtime = util_models.RuntimeOptions()
            try:
                response = await vpc_client.describe_eip_addresses_with_options_async(request, runtime)
                result = response.to_map()
                return result


            except Exception as error:
                print(error.message)
                # 诊断地址
                print(error.data.get("Recommend"))


        @self.mcp_instance.tool
        async def describe_vpcs(
                access_key_id: str,
                region_id: str,
                vpc_id: str = None,
                vpc_name: str = None,
                is_default: bool = None,
                dry_run: bool = None,
                resource_group_id: str = None,
                page_number: int = 1,
                page_size: int = 10,
                vpc_owner_id: int = None,
                dhcp_options_set_id: str = None,
                enable_ipv6: bool = None
        ):
            """
            查询指定地域的VPC列表，通过region_id查询到可访问的VPC列表，通过VPC列表查询比如已使用的内网IP地址段等信息。从而可以通过输入一个内网IP，而知道他所在哪个账号下的哪个region的哪个VPC中。

            参数:
            - access_key_id: 访问密钥ID
            - region_id: 地域ID
            - vpc_id: VPC的ID
            - vpc_name: VPC的名称
            - is_default: 是否查询默认VPC
            - dry_run: 是否只预检此次请求
            - resource_group_id: 资源组ID
            - page_number: 列表页码，默认值为1
            - page_size: 每页行数，最大值为50，默认值为10
            - vpc_owner_id: VPC所属的阿里云账号ID
            - dhcp_options_set_id: DHCP选项集的ID
            - enable_ipv6: 是否查询开启IPv6网段的VPC

            :return:
            - result: 包含VPC信息的字典
            - example:
            {
                "Vpcs": {
                    "Vpc": [
                        {
                            "VpcId": "vpc-1234567890abcdefg",
                            "RegionId": "cn-hangzhou",
                            "Status": "Available",
                            "VpcName": "MyVPC",
                            "CidrBlock": "sfsfssd133"
                            "IsDefault": false,
                            "Description": "My first VPC",
                            "CreationTime": "2023-10-01T12:00:00Z",
                            "VSwitchIds": {
                                "VSwitchId": [
                                    "vsw-1234567890abcdefg",
                                    "vsw-abcdefg1234567890"
                                ]
                            },
                            "RouterTableIds": {
                                "RouterTableId": [
                                    "rtb-1234567890abcdefg"
                                ]
                            },
                            "ResourceGroupId": "rg-1234567890abcdefg",
                            "DhcpOptionsSetId": "dopt-1234567890abcdefg",
                            "Ipv6CidrBlock": "2001:0db8:85a3:0000:0000:8a2e:0370:7334/64",
                            "Ipv6CidrBlocks": {
                                "Ipv6CidrBlock": [
                                    "2001:0db8:85a3:0000:0000:8a2e:0370:7334/64"
                                ]
                            }
                        }
                    ]
                },
                "PageNumber": 1,
                "PageSize": 10,
                "TotalCount": 1,
                "RequestId": "ABCDEF12-3456-7890-ABCD-EF1234567890"
            }
            """
            vpc_client = self.initialize_client_4_specific_region(access_key_id, region_id)
            request = vpc_20160428_models.DescribeVpcsRequest(
                region_id=region_id,
                page_number=page_number,
                page_size=page_size,
                vpc_id=vpc_id,
                vpc_name=vpc_name,
                is_default=is_default,
                dry_run=dry_run,
                resource_group_id=resource_group_id,
                vpc_owner_id=vpc_owner_id,
                dhcp_options_set_id=dhcp_options_set_id,
                enable_ipv_6=enable_ipv6

            )
            runtime = util_models.RuntimeOptions()
            try:
                response = await vpc_client.describe_vpcs_with_options_async(request, runtime)
                result = response.to_map()
                return result

            except Exception as error:
                print(error.message)
                # 诊断地址
                print(error.data.get("Recommend"))