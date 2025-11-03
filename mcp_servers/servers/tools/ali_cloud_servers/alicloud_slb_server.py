from mcp_servers.base_server import BaseServer
from alibabacloud_slb20140515.client import Client as Slb20140515Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_slb20140515 import models as slb_20140515_models
from alibabacloud_tea_util import models as util_models
from fastmcp.utilities import logging
logger = logging.get_logger(__name__)

class ALI_CLOUD_SLB(BaseServer):

    ecs_client = None

    def __init__(self, cmd_config):
        super().__init__(cmd_config, "ali_cloud_slb_mcp_server", prefix="ali_cloud_slb_mcp_server")
        self.setup_server()

    def initialize_client_4_specific_region(self,access_key_id:str,region_id:str) -> Slb20140515Client:
        client = None
        """初始化 Aliyun SLB Client for specific region under specific account"""
        for config in self.alicloud_client_configs:
            if config.access_key_id == access_key_id:
                selected_config = config.config
                cred = CredentialClient(selected_config)
                config = open_api_models.Config(
                    credential=cred
                )
                config.endpoint = f'slb.aliyuncs.com'
                client = Slb20140515Client(config)
                break
        if client is None:
            raise ValueError(f"No valid Aliyun SLB client config found for account_id: {access_key_id}, region_id: {region_id}")
        else:
            logger.info(f"Successfully initialized Aliyun SLB client for account_id: {access_key_id}, region_id: {region_id}")
            return client


    def setup_server(self):
        @self.mcp_instance.tool
        async def describe_load_balancers(
                access_key_id: str,
                region_id: str,
                server_id: str = None,
                address_ip_version: str = None,
                load_balancer_status: str = None,
                load_balancer_id: str = None,
                load_balancer_name: str = None,
                server_intranet_address: str = None,
                address_type: str = None,
                internet_charge_type: str = None,
                vpc_id: str = None,
                vswitch_id: str = None,
                network_type: str = None,
                address: str = None,
                master_zone_id: str = None,
                slave_zone_id: str = None,
                pay_type: str = None,
                resource_group_id: str = None,
                page_number: int = 1,
                page_size: int = 50,
                tags: list = None
        ):
            """
            查询传统型负载均衡实例列表,通过返回的实例列表，可以查看例如分配的内网IP地址

            参数:
            - access_key_id: 访问密钥ID
            - region_id: 地域ID
            - server_id: 后端服务器ID
            - address_ip_version: IP版本，ipv4或ipv6
            - load_balancer_status: 实例状态
            - load_balancer_id: 负载均衡实例ID
            - load_balancer_name: 负载均衡实例名称
            - server_intranet_address: 后端服务器内网地址
            - address_type: 实例网络类型
            - internet_charge_type: 公网计费方式
            - vpc_id: VPC ID
            - vswitch_id: 交换机ID
            - network_type: 私网实例网络类型
            - address: 实例服务地址
            - master_zone_id: 主可用区ID
            - slave_zone_id: 备可用区ID
            - pay_type: 付费模式
            - resource_group_id: 资源组ID
            - page_number: 页码，<= 1000
            - page_size: 每页行数，<= 100
            - tags: 标签列表，格式 [{"Key": "tag1", "Value": "value1"}, ...]
            :return
            - result: DescribeLoadBalancersResponse,例如
            {
                "LoadBalancers": {
                    "LoadBalancer": [
                        {
                            "Address": "10.20.30.100",
                            "LoadBalancerId": "lb-1234567890abcdef",
                            "LoadBalancerName": "my-load-balancer",
                            "LoadBalancerStatus": "active",
                            "RegionId": "cn-hangzhou",
                            "VpcId": "vpc-1234567890abcdef",
                            "NetworkType": "vpc",
                            "AddressType": "intranet",
                            "InternetChargeType": "paybytraffic",
                            "CreateTime": "2023-01-01T12:00:00Z",
                            "PayType": "PostPaid",
                            "Tags": {
                                "Tag": [
                                    {"Key": "env", "Value": "production"},
                                    {"Key": "project", "Value": "website"}
                                ]
                            },
                            ...
                        },
                        ...
                    ]
                },
                "PageNumber": 1,
                "PageSize": 50,
                "TotalCount": 100
            }
            详细参数说明请参考官方文档:
            https://next.api.aliyun.com/api/Slb/2014-05-15/DescribeLoadBalancers?params={}
            通过返回的实例列表，可以查看例如分配

            """
            slb_client = self.initialize_client_4_specific_region(access_key_id, region_id)
            request = slb_20140515_models.DescribeLoadBalancersRequest(
                region_id=region_id,
                page_number=page_number,
                page_size=page_size,
                tags=None,  # 初始时不设置标签，稍后处理
                server_id=server_id,
                address_ipversion=address_ip_version,
                load_balancer_status=load_balancer_status,
                load_balancer_id=load_balancer_id,
                load_balancer_name=load_balancer_name,
                server_intranet_address=server_intranet_address,
                address_type=address_type,
                internet_charge_type=internet_charge_type,
                vpc_id=vpc_id,
                v_switch_id=vswitch_id,
                network_type=network_type,
                address=address,
                master_zone_id=master_zone_id,
                slave_zone_id=slave_zone_id,
                pay_type=pay_type,
                resource_group_id=resource_group_id,
            )

            # 处理标签筛选
            if tags and len(tags) <= 20:
                tag_objects = []
                for tag in tags:
                    if isinstance(tag, dict) and 'tagKey' in tag.keys() and 'tagValue' in tag.keys():
                        tag_objects.append(slb_20140515_models.DescribeLoadBalancersRequestTag(
                            tag['tagKey'],
                            tag['tagValue']
                        ))
                if tag_objects:
                    request.tags = tag_objects

            runtime = util_models.RuntimeOptions()
            try:
                response = await slb_client.describe_load_balancers_with_options_async(request, runtime)
                result = response.to_map()
                return result

            except Exception as error:
                print(error.message)
                print(error.data.get("Recommend"))