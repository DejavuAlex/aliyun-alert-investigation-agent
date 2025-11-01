from alibabacloud_credentials.client import Client
from alibabacloud_credentials.models import Config
from alibabacloud_cs20151215.client import Client as CSClient
from alibabacloud_cs20151215 import models as cs_20151215_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_openapi import models as open_api_models
from mcp_servers.base_server import BaseServer
from fastmcp.utilities import logging
logger = logging.get_logger(__name__)


class ALI_CLOUD_CONTAINERSERVISE(BaseServer):
    def __init__(self, cmd_config):
        super().__init__(cmd_config, "ali_cloud_cs_mcp_server", prefix="ali_cloud_cs_mcp_server")
        self.setup_server()
        #self.initialize_client(region_id)

    # def initialize_client(self,region_id):
    #
    #
    #     access_key_id = self.cmd_config.alicloud_config["access_key_id"]
    #     access_key_secret = self.cmd_config.alicloud_config["access_key_secret"]
    #     if not access_key_id or not access_key_secret:
    #         raise ValueError("alicloud access key id and secret must be provided in internal_config.yaml")
    #     config = Config(
    #         type='access_key',
    #         access_key_id=access_key_id,
    #         access_key_secret=access_key_secret,
    #     )
    #     config.endpoint = f"cs.{region_id}.aliyuncs.com"
    #     cred = Client(config)
    #     config = open_api_models.Config(
    #         credential=cred
    #     )
    #     return Client(config)

    def initialize_client_4_specific_region(self, access_key_id: str, region_id: str) -> CSClient:
        """初始化 Aliyun action trail Client for specific region under specific account"""
        cs_client = None
        for config in self.alicloud_client_configs:
            if config.access_key_id == access_key_id:
                selected_config = config.config
                cred = Client(selected_config)
                config = open_api_models.Config(
                    credential=cred
                )
                if region_id != "":
                    config.endpoint = f'cs.{region_id}.aliyuncs.com'
                cs_client = CSClient(config)
                break
        if cs_client is None:
            raise ValueError(
                f"No valid Aliyun client config found for account_id: {access_key_id}, region_id: {region_id}")
        else:
            logger.info("Successfully initialized Aliyun CS Client for account_id: {access_key_id}, region_id: {region_id}")
            return cs_client

    def setup_server(self):

        @self.mcp_instance.tool
        async def get_clusters(access_key_id:str, region_id:str):
            """
            得到当前AK的某个区域下的所有K8S集群列表


            :param access_key_id:
            :param region_id:
            :return:
              K8S 集群列表
            """
            cs_client = self.initialize_client_4_specific_region(access_key_id, region_id)
            headers = {}
            runtime = util_models.RuntimeOptions()
            request = cs_20151215_models.DescribeClustersV1Request()
            try:
                response: cs_20151215_models.DescribeClustersV1Response = await cs_client.describe_clusters_v1with_options_async(request, headers, runtime)
                return response.body.to_map()
            except Exception as error:
                # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
                # 错误 message
                print(error.message)
                # 诊断地址
                print(error.data.get("Recommend"))

        @self.mcp_instance.tool
        async def get_cluster_audit_project(access_key_id: str, region_id: str, cluster_id: str):
            """
            查看集群是否开启API Server安全审计功能以及API Server安全审计日志对应的SLS Project，注意这里是安全审计日志。Kubernetes cluster还有一个审计日志，是集群审计日志，他的sls project名字例如k8s-log-c9b2085d56ad5426381117b7cc7ef1d09，而API server的安全审计日志例如audit-c9b2085d56ad5426381117b7cc7ef1d09
            :Args:
                access_key_id: str #阿里云账号的Access Key ID
                region_id: str
                clusterid: str
            :return:
                sls_project_name:str
                audit_enabled: bool

            """

            cs_client = self.initialize_client_4_specific_region(access_key_id, region_id)
            headers = {}
            runtime = util_models.RuntimeOptions()
            try:
                response: cs_20151215_models.GetClusterAuditProjectResponse = await cs_client.get_cluster_audit_project_with_options_async(
                    cluster_id, headers, runtime)
                return response.body.to_map()
            except Exception as error:
                # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
                # 错误 message
                print(error.message)
                # 诊断地址
                print(error.data.get("Recommend"))

        @self.mcp_instance.tool
        async def describe_cluster_detail(
                access_key_id: str,
                cluster_id: str,
                region_id: str,
        ):
            """
            查询阿里云ACK集群详细信息

            参数:
            - access_key_id: 访问密钥ID
            - cluster_id: 集群ID
            - region_id: 地域ID

            返回:
            - dict: 集群详细信息，包含以下字段：
                - cluster_id: 集群ID
                - cluster_type: 集群类型
                - created: 集群创建时间
                - init_version: 集群初始化版本
                - current_version: 集群当前版本
                - next_version: 集群可升级版本
                - deletion_protection: 集群删除保护状态
                - docker_version: Docker版本（已废弃）
                - external_loadbalancer_id: 集群Ingress LB实例ID
                - meta_data: 集群元数据信息
                - name: 集群名称
                - network_mode: 集群网络类型
                - region_id: 集群所在地域ID
                - resource_group_id: 集群资源组ID
                - security_group_id: 集群安全组ID
                - size: 集群节点数
                - state: 集群运行状态
                - tags: 集群资源标签
                - updated: 集群更新时间
                - vpc_id: 集群专有网络ID
                - vswitch_id: 虚拟交换机ID（已废弃）
                - subnet_cidr: Pod网络地址段（已废弃）
                - zone_id: 集群可用区ID（已废弃）
                - master_url: 集群访问地址
                - private_zone: 是否启用PrivateZone
                - profile: 集群子类型
                - cluster_spec: 集群规格
                - worker_ram_role_name: Worker RAM角色名称
                - maintenance_window: 集群维护窗口
                - parameters: 集群ROS参数集合
                - container_cidr: Pod网络网段
                - service_cidr: 服务网络网段
                - proxy_mode: kube-proxy代理模式
                - timezone: 时区
                - node_cidr_mask: 节点CIDR掩码
                - ip_stack: IP协议栈
                - cluster_domain: 集群本地域名
                - extra_sans: 自定义API Server证书SAN
                - rrsa_config: RRSA配置
                - vswitch_ids: 集群控制面虚拟交换机
                - operation_policy: 集群自动运维策略
                - control_plane_config: 专有版集群控制面配置
                - auto_mode: 智能托管模式配置
            """
            cs_client = self.initialize_client_4_specific_region(access_key_id, region_id)  # CS服务通常使用固定端点

            try:
                # 使用CS客户端调用DescribeClusterDetail接口
                haaders = {}
                runtime = util_models.RuntimeOptions()
                logger.info("begin to query cluster detail for cluster_id: {} in region: {} ".format(cluster_id,region_id))
                response = await cs_client.describe_cluster_detail_with_options_async(cluster_id, haaders, runtime)
                result = response.to_map()

                # 格式化返回结果
                # formatted_result = {
                #     "cluster_id": result.get("cluster_id"),
                #     "cluster_type": result.get("cluster_type"),
                #     "created": result.get("created"),
                #     "init_version": result.get("init_version"),
                #     "current_version": result.get("current_version"),
                #     "next_version": result.get("next_version"),
                #     "deletion_protection": result.get("deletion_protection"),
                #     "docker_version": result.get("docker_version"),
                #     "external_loadbalancer_id": result.get("external_loadbalancer_id"),
                #     "meta_data": result.get("meta_data"),
                #     "name": result.get("name"),
                #     "network_mode": result.get("network_mode"),
                #     "region_id": result.get("region_id"),
                #     "resource_group_id": result.get("resource_group_id"),
                #     "security_group_id": result.get("security_group_id"),
                #     "size": result.get("size"),
                #     "state": result.get("state"),
                #     "tags": result.get("tags", []),
                #     "updated": result.get("updated"),
                #     "vpc_id": result.get("vpc_id"),
                #     "vswitch_id": result.get("vswitch_id"),
                #     "subnet_cidr": result.get("subnet_cidr"),
                #     "zone_id": result.get("zone_id"),
                #     "master_url": result.get("master_url"),
                #     "private_zone": result.get("private_zone"),
                #     "profile": result.get("profile"),
                #     "cluster_spec": result.get("cluster_spec"),
                #     "worker_ram_role_name": result.get("worker_ram_role_name"),
                #     "maintenance_window": result.get("maintenance_window"),
                #     "parameters": result.get("parameters"),
                #     "container_cidr": result.get("container_cidr"),
                #     "service_cidr": result.get("service_cidr"),
                #     "proxy_mode": result.get("proxy_mode"),
                #     "timezone": result.get("timezone"),
                #     "node_cidr_mask": result.get("node_cidr_mask"),
                #     "ip_stack": result.get("ip_stack"),
                #     "cluster_domain": result.get("cluster_domain"),
                #     "extra_sans": result.get("extra_sans", []),
                #     "rrsa_config": result.get("rrsa_config"),
                #     "vswitch_ids": result.get("vswitch_ids", []),
                #     "operation_policy": result.get("operation_policy"),
                #     "control_plane_config": result.get("control_plane_config"),
                #     "auto_mode": result.get("auto_mode")
                # }
                #
                # # 清理空值
                # formatted_result = {k: v for k, v in formatted_result.items() if v is not None}
                return result

            except Exception as error:
                print(error.message)
                # 诊断地址
                print(error.data.get("Recommend"))

        @self.mcp_instance.tool
        async def get_cluster_audit_logstore(cluster_id):
            """
            查看集群的API Server安全审计日志对应的SLS Logstore name
            默认值就是 audit + - + cluster_id
            :return:
                sls_logstore_name:str

            """
            return "audit" + "-" + cluster_id

        @self.mcp_instance.tool
        async def get_labels_4_cluster(access_key_id,region_id,cluster_id,resource_ids,resource_type="CLUSTER",next_token=None,tags=None):
            """
            查看集群的Labels,可能会有'环境'标签，和 ‘产品’标签
            :Args:
                access_key_id: str #阿里云账号的Access Key ID
                resource_ids: list(str) #要查询的资源 ID 列表
                region_id: str #地域 ID
                cluster_id: str #集群ID
                resource_type: str # 就是 ‘CLUSTER’
                next_token: str #分页查询的起始位置，由上一次调用返回，首次调用可不填
                tags: list(str) #标签过滤条件，[{\"key\":\"env\",\"value\",\"dev\"},{\"key\":\"dev\", \"value\":\"IT\"}]
            """
            cs_client = self.initialize_client_4_specific_region(access_key_id,region_id)
            headers = {}
            runtime = util_models.RuntimeOptions()
            request = cs_20151215_models.ListTagResourcesRequest(
                resource_ids=resource_ids,
                resource_type=resource_type,
                next_token=next_token,
                tags=tags
            )
            try:
                response:cs_20151215_models.ListTagResourcesResponse = await cs_client.list_tag_resources_with_options_async(request,headers,runtime)
                return response.body.to_map()
            except Exception as error:
                # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
                # 错误 message
                print(error.message)
                # 诊断地址
                print(error.data.get("Recommend"))




