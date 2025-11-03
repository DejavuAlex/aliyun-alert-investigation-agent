from alibabacloud_credentials.client import Client
from alibabacloud_sls20201230.models import GetProjectLogsResponse, GetLogsResponse

from mcp_servers.base_server import BaseServer
from alibabacloud_sls20201230.client import Client as SLSClient
from alibabacloud_sls20201230 import models as sls_20201230_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_openapi import models as open_api_models
from fastmcp.utilities import logging
logger = logging.get_logger(__name__)

class ALI_CLOUD_SLS(BaseServer):
    def __init__(self, cmd_config):
        super().__init__(cmd_config, "ali_cloud_sls_mcp_server", prefix="ali_cloud_sls_mcp_server")
        self.client = None
        self.setup_server()

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
    #     config.endpoint = f"sls.{region_id}.aliyuncs.com"
    #     cred = Client(config)
    #     config = open_api_models.Config(
    #         credential=cred
    #     )
    #     return Client(config)

    def initialize_client_4_specific_region(self,access_key_id:str,region_id:str) -> SLSClient:
        client = None
        """初始化 Aliyun action trail Client for specific region under specific account"""
        for config in self.alicloud_client_configs:
            if config.access_key_id == access_key_id:
                selected_config = config.config
                cred = Client(selected_config)
                config = open_api_models.Config(
                    credential=cred
                )
                if region_id != "":
                    config.endpoint = f'{region_id}.log.aliyuncs.com'
                client = SLSClient(config)
                break
        if client is None:
            raise ValueError(f"No valid Aliyun client config found for account_id: {access_key_id}, region_id: {region_id}")
        else:
            logger.info(f"Successfully initialized Aliyun SLS Client for account_id: {access_key_id}, region_id: {region_id}")
            return client


    def setup_server(self):

        @self.mcp_instance.tool
        async def get_index(access_key_id:str, region_id:str,log_project_name: str,log_store_name:str):
            """
            生成sls查询语句前，需要了解指定Logstore的索引信息，并且了解哪些是全文索引，哪些是字段索引
            以及每个字段的类型，是否开启了日志聚类等信息
            :param
                access_key_id:str # 阿里云账号的Access Key ID
                region_id:str # 地域ID，例如 cn-hangzhou
                log_project_name: 日志项目名称
                log_store_name: 日志库名称
            :return:
                索引配置信息，包含以下字段：
                - ttl: integer<int32> # 索引文件生命周期
                - max_text_len: integer<int32> # 字段值的最大长度
                - log_reduce_white_list: array<string> # 日志聚类的聚类字段过滤白名单
                - log_reduce_black_list: array<string> # 日志聚类的聚类字段过滤黑名单
                - line: object # 全文索引配置
                - keys: map<IndexKey> # 字段索引配置
                - log_reduce: boolean # 是否开启日志聚类
                - lastModifyTime: integer<int64> # 索引最后更新时间
                - index_mode: string # 索引类型
                - storage: string # 存储类型

            """
            sls_client = self.initialize_client_4_specific_region(access_key_id, region_id)
            try:
                response = await sls_client.get_index_with_options_async(
                    log_project_name,
                    log_store_name,
                    {},
                    util_models.RuntimeOptions()
                )
                return response.to_map()
            except Exception as error:
                print(error.message)
                # 诊断地址
                print(error.data.get("Recommend"))

        """
        https://next.api.aliyun.com/api/Sls/2020-12-30/GetLogs?sdkStyle=dara&RegionId=cn-hangzhou&tab=DEMO&lang=PYTHON
        """

        @self.mcp_instance.tool
        async def search_sls_logs(
                access_key_id: str,
                region_id: str,
                log_project_name: str,
                query: str,
                from_time: int,
                to_time: int,
                log_store_name: str = None,
                topic: str = "",
                line: int = 100,
                offset: int = 0,
                reverse: bool = False,
                power_sql: bool = False
        ):
            """
            搜索阿里云SLS日志库中的日志数据。执行此命令前，确保已经了解当前logstore的index信息，可以通过get_index命令获取
            query知识: 使用前请搜索本地知识库中的阿里云SLS日志服务的query语句规则.md，了解query语法
            注意：query里面的JSON字段引用方式,要用双引号包裹，例如 "user.username": "system:serviceaccount:kube-system:alicloud-csi-provisioner" and "objectRef.resource": "leases" and "objectRef.namespace": "kube-system" and "objectRef.name": "snapshot-controller-leader" | select "requestReceivedTimestamp", "verb", "objectRef.resource", "objectRef.namespace", "objectRef.name", "responseStatus.code" limit 50， 这里面的"user.username"，"objectRef.name"等就是用双引号包裹的
            如下是logstore的字段信息，其中有些是index，有些不是，不是index的要搜索的话，就要采用类似* | set session mode=scan; SELECT * FROM log WHERE "userAgent" LIKE '%snapshot-controller%'进行搜索了
            ```json
            {
              "annotations": {},
              "authorization.k8s.io/decision": "allow",
              "authorization.k8s.io/reason": "RBAC: allowed by RoleBinding \"csi-provisioner-role-cfg/kube-system\" of Role \"alicloud-csi-provisioner\" to ServiceAccount \"alicloud-csi-provisioner/kube-system\"",
              "apiVersion": "audit.k8s.io/v1",
              "auditID": "47b102fb-1d72-466d-bbb7-c0b3cae73afe",
              "kind": "Event",
              "level": "Metadata",
              "objectRef": {
                "resource": "leases",
                "namespace": "kube-system",
                "name": "snapshot-controller-leader",
                "uid": "43baaa9d-49e8-46f1-9ea0-1222431f4375",
                "apiGroup": "coordination.k8s.io",
                "apiVersion": "v1",
                "resourceVersion": "858050559"
              },
              "requestReceivedTimestamp": "2025-10-03T12:51:53.948461Z",
              "requestURI": "/apis/coordination.k8s.io/v1/namespaces/kube-system/leases/snapshot-controller-leader",
              "responseStatus": {
                "metadata": {},
                "code": 200
              },
              "sourceIPs": ["10.151.224.118"],
              "stage": "ResponseComplete",
              "stageTimestamp": "2025-10-03T12:51:53.954878Z",
              "user": {
                "username": "system:serviceaccount:kube-system:alicloud-csi-provisioner",
                "uid": "7dd6a483-6217-4349-b578-248edad70687",
                "groups": [
                  "system:serviceaccounts",
                  "system:serviceaccounts:kube-system",
                  "system:authenticated"
                ],
                "extra": {
                  "authentication.kubernetes.io/credential-id": ["JTI=e5cc2810-ba79-41cc-9034-ebd1215a7941"],
                  "authentication.kubernetes.io/node-name": ["cn-shanghai.10.151.224.118"],
                  "authentication.kubernetes.io/node-uid": ["5f7f6941-1555-4f50-9c9b-5675a3f18937"],
                  "authentication.kubernetes.io/pod-name": ["csi-provisioner-848879758c-6xhks"],
                  "authentication.kubernetes.io/pod-uid": ["f867a87d-9a98-4cfe-903d-8594d214d1c1"]
                }
              },
              "userAgent": "snapshot-controller/v0.0.0 (linux/amd64) kubernetes/$Format",
              "verb": "update"
            }
            ```

            :Args:
                access_key_id: str # 阿里云账号的Access Key ID
                region_id: str # 地域ID，例如 cn-hangzhou
                log_project_name: str # log_project_name名称
                query: str # 查询语句或者分析语句，例如："status: 401 | SELECT remote_addr,COUNT(*) as pv GROUP by remote_addr"
                from_time: int # 查询开始时间点（Unix时间戳）
                to_time: int # 查询结束时间点（Unix时间戳）
                log_store_name: str = None # 日志库名称（可选）
                topic: str = "" # 日志主题，默认值为空字符串
                line: int = 100 # 返回的最大日志条数，最小值为0，最大值为100
                offset: int = 0 # 查询开始行，默认值为0
                reverse: bool = False # 是否按日志时间戳降序返回
                power_sql: bool = False # 是否使用SQL独享版

            :return:
                array # 查询到的日志数据
            """

            # 初始化SLS客户端
            sls_client = self.initialize_client_4_specific_region(access_key_id, region_id)

            try:

                # 如果有指定日志库名称，使用GetLogs接口
                if log_store_name:
                    request = sls_20201230_models.GetLogsRequest(
                        from_time,
                        line,
                        offset,
                        power_sql,
                        query,
                        reverse,
                        to_time,
                        topic
                    )
                    response:GetLogsResponse = await sls_client.get_logs_with_options_async(
                        log_project_name,
                        log_store_name,
                        request,
                        {},  # headers
                        util_models.RuntimeOptions()
                    )
                else:
                    # 如果没有指定日志库名称，使用GetProjectLogs接口
                    request = sls_20201230_models.GetProjectLogsRequest(
                        power_sql,
                        query
                    )
                    response:GetProjectLogsResponse = await sls_client.get_project_logs_with_options_async(
                        log_project_name,
                        request,
                        {},  # headers
                        util_models.RuntimeOptions()
                    )

                response_data = response.to_map()
                # response exmaple
                # {
                #     "apiVersion": "audit.k8s.io/v1",
                #     "kind": "Event",
                #     "level": "RequestResponse",
                #     "auditID": "954289ed-67d9-47da-9335-568bf24923d2",
                #     "stage": "ResponseComplete",
                #     "stageTimestamp": "2025-10-03T23:31:35.526131Z",
                #     "requestURI": "/apis/rbac.authorization.k8s.io/v1/clusterrolebindings/crd-controller-flux-system",
                #     "verb": "patch",
                #     "user": {
                #         "username": "system:serviceaccount:flux-system:kustomize-controller",
                #         "uid": "84bf18a2-1946-4c9e-998f-bd2501c1f4a4",
                #         "groups": [
                #             "system:serviceaccounts",
                #             "system:serviceaccounts:flux-system",
                #             "system:authenticated"
                #         ]
                #     },
                #     "objectRef": {
                #         "resource": "clusterrolebindings",
                #         "name": "crd-controller-flux-system",
                #         "apiGroup": "rbac.authorization.k8s.io",
                #         "apiVersion": "v1"
                #     },
                #     "responseStatus": {
                #         "metadata": {},
                #         "code": 200
                #     },
                #     "userAgent": "kustomize-controller/v0.0.0 (linux/amd64) kubernetes/$Format",
                #     "sourceIPs": ["10.151.224.118"],
                #     "annotations": {
                #         "authorization.k8s.io/decision": "allow",
                #         "authorization.k8s.io/reason": "RBAC: allowed by ClusterRoleBinding \"cluster-reconciler-flux-system\""
                #     }
                # }

                # 定义安全相关的字段列表
                security_fields = [
                    'auditID', 'level', 'requestReceivedTimestamp', 'requestURI',
                    'sourceIPs', 'stage', 'stageTimestamp', 'user', 'userAgent',
                    'verb', 'responseStatus', 'objectRef', 'annotations.authorization.k8s.io/decision',
                    'annotations.authorization.k8s.io/reason', 'apiVersion', 'kind'
                ]

                # 过滤日志数据，只保留安全相关字段
                if 'body' in response_data and isinstance(response_data['body'], list):
                    filtered_logs = []
                    for log_entry in response_data['body']:
                        filtered_entry = {}
                        for field in security_fields:
                            # 处理嵌套字段（如 user.username）
                            if '.' in field:
                                main_field, sub_field = field.split('.', 1)
                                if main_field in log_entry:
                                    if isinstance(log_entry[main_field], dict) and sub_field in log_entry[main_field]:
                                        if main_field not in filtered_entry:
                                            filtered_entry[main_field] = {}
                                        filtered_entry[main_field][sub_field] = log_entry[main_field][sub_field]
                            else:
                                if field in log_entry:
                                    filtered_entry[field] = log_entry[field]

                        # 添加时间戳字段（如果有）
                        for time_field in ['__time__', '__source__', '__topic__']:
                            if time_field in log_entry:
                                filtered_entry[time_field] = log_entry[time_field]
                        logger.info(f"For debug of SLS log, found one filtered log entry: {filtered_entry}")
                        filtered_logs.append(filtered_entry)

                    # 更新响应数据
                    response_data['body'] = filtered_logs

                return response_data

            except Exception as error:
                # 错误处理
                error_info = {
                    "error_message": error.message,
                    "recommend": getattr(error.data, "get", lambda x: None)("Recommend") if hasattr(error,
                                                                                                    'data') else None
                }
                print(f"搜索日志失败: {error.message}")
                if hasattr(error, 'data') and error.data.get("Recommend"):
                    print(f"建议: {error.data.get('Recommend')}")

                return error_info