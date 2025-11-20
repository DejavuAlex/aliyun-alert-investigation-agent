from mcp.types import PromptMessage, TextContent

from mcp_servers.base_server import BaseServer
from mcp_servers.servers.prompts.prompt_mixin import PromptMixin

"""
按照 https://help.aliyun.com/zh/security-center/user-guide/overview-6 列举的安全告警类别进行prompt编排

"""
class Ali_CLOUD_ECS_PROMPT(BaseServer,PromptMixin):
    def __init__(self,cmd_config):
        BaseServer.__init__(self,cmd_config,"alicloud_ecs_prompt_Server", prefix="alicloud_ecs_prompt")
        PromptMixin.__init__(self)
        self.setup_server()

    def setup_server(self):
        @self.mcp_instance.tool
        def ecs_instance_investigation_prompt(
                instance_id:str,
                region_id:str,

        ) -> PromptMessage:
            """
            本prompt是用来调查某个ECS的安全状态，输出该ECS的风险评估结论
            Args:
                instance_id: str, the ecs instance id to investigate
                region_id: str, the region id where the ecs instance is located
            Returns:
                security assessment prompt
             """
            STEPS = f"""
            1, 在阿里云审计中心中查询该ECS {instance_id}的操作日志，日志开始时间由你根据上下文决定，查询多少时间也由你决定，重点关注高危操作，如安全组变更、密钥变更、用户变更等高风险操作，如RunInstances, AttachKeyPair, ModifyInstanceAttribute, CreateSnapshot, DeleteInstance 等高危操作，并记录操作者和来源IP
            2, 在阿里云网络安全中心中查询该ECS的相关的网络安全事件，日志开始时间由你根据上下文决定，查询多少时间也由你决定，重点关注异常登录、异常进程、异常网络连接等
            3, 综合以上信息，评估该ECS的安全状态，给出风险评估结论
            """
            TEMPLATE = f"""
            输出格式：
            {{
                "操作日志分析": string, // 对操作日志的分析结果，重点关注高危操作
                "网络安全事件分析": string, // 对网络安全事件的分析结果，重点关注异常登录、异常进程、异常网络连接等
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

