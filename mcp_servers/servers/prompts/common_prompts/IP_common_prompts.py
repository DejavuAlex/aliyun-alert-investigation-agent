
from mcp.types import PromptMessage, TextContent


from mcp_servers.base_server import BaseServer
from mcp_servers.servers.prompts.prompt_mixin import PromptMixin


class IP_COMMON_PROMPT(BaseServer,PromptMixin):
    def __init__(self,cmd_config):
        BaseServer.__init__(self,cmd_config,"IP_common_prompt_Server", prefix="ip_common_prompt")
        PromptMixin.__init__(self)
        self.setup_server()

    def setup_server(self):
        return
        @self.mcp_instance.tool
        def ip_investigation_prompt(
                ip_list:str,
        ) -> PromptMessage:
            """ 本prompt是用来调查该IP的归属地，是否为内网IP，是否为企业出口IP等

                Args:
                    ip_list: str, the ip address to investigate，例如["38.179.66.175","211.144.221.1"]
                Returns:
                    investigation report
             """
            TEMPLATE = """
            输出格式：
            - "ip所属地": string, // 来源IP地理归属（国家/城市）。未知时填"需人工补充"
            - "是否为内网IP": "是"/"否", // 按RFC1918/100.64.0.0/10/127.0.0.0/8/169.254.0.0/16等判断
            - "是否为企业出口IP": "是"/"否", // 需对照本地Roche_knowledge_base；未匹配则"否"
            - "风险因素": array of string, // 示例值可包含["情报库风险","非中国IP","非内网IP","API调用失败","企业出口IP","来源IP变更","多UA混用"]，按实际取舍
            - "风险理由": string, // 简要合成结论，若信息缺失/工具失败需说明
            以上为单IP对象，若输入为多IP，则输出为数组样式，每个元素为上述对象
            例如:
            [
              {
                "ip所属地": "上海",
                "是否为内网IP": "是/否",
                "是否为企业出口IP": "是/否",
                "风险因素": ["..."],
                "风险理由": "..."
              },
              {
                "ip所属地": "北京",
                "是否为内网IP": "是/否",
                "是否为企业出口IP": "是/否",
                "风险因素": ["..."],
                "风险理由": "..."
              }
            ]
            以上为多IP输出示例
            
            
            """

            STEPS = f"""
            请按照以下步骤分析这些IP地址：:{ip_list}
            1,是否是内网IP
            2，调用工具搜索是否是企业出口IP
            3, 调用工具搜索IP是否在风险情报库中
            4, 综合以上信息，给出风险评估结论
            
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

            return  PromptMessage(
                    role="assistant",
                    content=TextContent(
                        type="text",
                        text=prompt)
                )