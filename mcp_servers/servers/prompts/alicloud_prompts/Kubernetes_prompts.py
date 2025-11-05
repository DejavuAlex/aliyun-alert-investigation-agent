from mcp.types import PromptMessage, TextContent

from mcp_servers.base_server import BaseServer
from mcp_servers.servers.prompts.prompt_mixin import PromptMixin


class ALICLOUD_KUBERNETES_PROMPTS(BaseServer,PromptMixin):
    def __init__(self,cmd_config):
        BaseServer.__init__(self,cmd_config,"alicloud_k8s_prompt_Server", prefix="alicloud_k8s_prompt")
        PromptMixin.__init__(self)
        self.setup_server()

    def setup_server(self):
        return
        @self.mcp_instance.tool
        def api_server_investigation_prompt() -> PromptMessage:
            """
            本prompt是用来调查某个Kubernetes集群的API server的安全审计日志，用来分析该Kubernetes集群的安全状态，输出该Kubernetes集群的风险评估结论
            Args:
                cluster_id: str, the kubernetes cluster id to investigate
                region_id: str, the region id where the kubernetes cluster is located
            Returns:
                security assessment prompt
             """
            STEPS = f"""
            1, 分析Source IP分布与外网来源，重点关注是否有外网IP访问API Server，如果有外网IP，则调用IP分析工具，分析IP相关信息，如地理位置、是否为已知恶意IP等
            2, 分析批量删除或删除敏感资源行为，检索 pods、deployments、jobs、daemonsets、statefulsets 的 delete/deletecollection 行为
            3，分析Secrets的读取行为，排除掉系统用户如system:serviceaccount:kube-system:namespace-controller，system:serviceaccount:kube-system:prometheus，system:node:worker-node-01，system:kube-proxy等，关注人类用户，如zhangsan@company.com，ci-cd-bot等，
               需要关注的异常指标:
                - 非工作时间的大量访问
                - 高频的list secrets操作
                - 跨命名空间的Secrets访问
                - 从未见过的主体访问Secrets
                - 来自异常地理位置的访问
            4, 分析RBAC变更活动，监控 roles/clusterroles/rolebindings/clusterrolebindings 的 create/update/patch/delete 行为，该些行为是否为人类用户的操作行为。
            5，分析非法认证与未授权访问活动，检索 401/403 认证/授权失败的审计事件（stage=ResponseComplete, level=Metadata），是否存在暴力破解或越权尝试。
            3, 综合以上信息，评估该Kubernetes集群的安全状态，给出风险评估结论
            """
            TEMPLATE = f"""
            输出格式：
            {{
                "操作日志分析": string, // 对操作日志的分析结果，重点关注高危操作
                "安全事件分析": string, // 对安全事件的分析结果，重点关注异常登录、异常网络连接、异常容器行为等
                "风险评估结论": string, // 综合以上信息，给出风险评估结论
            }}
            
            """
            prompt = f"""
                        请按以下思维步骤（Chain-of-Thought）逐步推理：
                        {STEPS.strip()}
                        输出必须严格遵循以下模板：
                        {TEMPLATE.strip()}
                        强制规则：
                        {self.mandatory_rules.strip()}
                        约束条件：
                        {self.constraints.strip()}
                        """

            return PromptMessage(
                role="assistant",
                content=TextContent(
                    type="text",
                    text=prompt)
            )
