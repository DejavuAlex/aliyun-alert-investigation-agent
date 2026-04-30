from mcp_servers.base_server import BaseServer
from alibabacloud_rds20140815.client import Client as Rds20140815Client
from alibabacloud_credentials.client import Client as CredentialClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_rds20140815 import models as rds_20140815_models
from fastmcp.utilities import logging
logger = logging.get_logger(__name__)

class ALI_CLOUD_RDS(BaseServer):
    def __init__(self, cmd_config):
        super().__init__(cmd_config, "ali_cloud_rds_mcp_server", prefix="ali_cloud_rds_mcp_server")
        self.setup_server()

    def initialize_client_4_specific_region(self,access_key_id:str,access_key_secret:str) -> Rds20140815Client:
        client = None
        """初始化 Aliyun RDS Client for specific region under specific account"""
        for config in self.alicloud_client_configs:
            if config.access_key_id == access_key_id:
                selected_config = config.config
                cred = CredentialClient(selected_config)
                config = open_api_models.Config(
                    credential=cred
                )
                config.endpoint = f'slb.aliyuncs.com'
                client = Rds20140815Client(config)
                break
        if client is None:
            raise ValueError(
                f"No valid Aliyun RDS client config found for account_id: {access_key_id}")
        else:
            logger.info(
                f"Successfully initialized Aliyun RDS client for account_id: {access_key_id}")
            return client

    def setup_server(self):
        @self.mcp_instance.tool
        async def describe_db_instance_net_info(
                access_key_id: str,
                region_id: str,
                db_instance_id: str,
                client_token: str = None,
                flag: int = None,
                db_instance_net_rw_split_type: str = None,
                general_group_name: str = None
        ):
            """
            查询阿里云RDS实例的连接地址信息, 从这里可以查看到数据库内网连接及外网连接域名地址

            参数:
            - access_key_id: 访问密钥ID
            - region_id: 地域ID
            - db_instance_id: 实例ID
            - client_token: 客户端令牌，用于保证请求的幂等性
            - flag: 备用参数，无需配置
            - db_instance_net_rw_split_type: 连接地址类型
            - general_group_name: 专属集群MySQL通用版实例所属的组名

            返回:
            - result: 包含连接地址信息的字典

            """
            rds_client:Rds20140815Client = self.initialize_client_4_specific_region(access_key_id, region_id)
            request = rds_20140815_models.DescribeDBInstanceNetInfoRequest(
                dbinstance_id=db_instance_id,
                client_token=client_token,
                flag=flag,
                dbinstance_net_rwsplit_type=db_instance_net_rw_split_type,
                general_group_name=general_group_name

            )
            try:
                response = await rds_client.describe_dbinstance_net_info_async(request)
                result = response.to_map()
                return result
            except Exception as error:
                print(error.message)
                # 诊断地址
                print(error.data.get("Recommend"))