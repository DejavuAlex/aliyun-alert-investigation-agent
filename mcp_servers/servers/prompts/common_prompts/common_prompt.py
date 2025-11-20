

from mcp_servers.base_server import BaseServer


class Ali_CLOUD_EVENT_PROMPT(BaseServer):
    def __init__(self,cmd_config):
        super().__init__(cmd_config,"common_prompt_Server", prefix="common_prompt")
        self.setup_server()

    def setup_server(self):
        @self.mcp_instance.tool
        async def describe_mandatory_rules_prompt():
            """
            这是一个通用的mandatory rules prompt，主要是为了分析过程中，遵循的通用准则

            :return
               mandatory_rules_prompt: str, the mandatory rules prompt
            """
            prompt = \
             """
            ✅ 必须遵守：
            - 仅当实际调用了工具时才记录工具信息
            - 工具调用格式：工具名称 | 状态：成功/失败 | 失败原因（如失败）
            - 无工具调用的步骤只需记录分析结果，不得虚构工具调用
            - 工具调用失败时必须说明具体原因及其对分析的影响
            - 工具调用成功时，在显示状态中加入✅ 
            - 工具调用失败时，在显示状态中加入❌
            - 所有判断必须基于告警中提供的或可通过工具获取的真实数据
            - 不得假设存在未明确提供的安全产品（如未启用云防火墙则不可引用其日志）
            - 调用和阿里云相关的工具时候，遇到API流控时采用节流与重试，而不是跳过
            - 调用和阿里云相关的工具的时候，常常需要指定region_id, access_key_id才能进行查询，如果未明确指定，则默认查询所有access_key_id下的所有region_id的资源
            - 遇到任何IP如果是外网IP，都需要执行本地工具库中IP调查相关的prompt
            
            """
            return prompt

        @self.mcp_instance.tool
        async def describe_constraints_prompt():
            """
            这是一个通用的constraints prompt，主要是为了约束输出内容

            :return
               constraints: str, the constraints prompt
            """
            prompt = \
            """
            ⛔ 不允许：
            - 在未调用工具的步骤中编造工具名称或状态
            - 使用“可能”“大概”等模糊状态描述
            - 忽略工具失败对结论的影响
            - 引用未在环境中部署的安全能力（如未安装云安全中心Agent则不可获取进程快照）
            ✅ 必须做到：
            - 如实反映每一步是否依赖工具及结果
            - 工具成功时清晰列出获取的关键信息
            - 工具失败时说明限制并尝试基于已有信息推断
            - 保持调查逻辑的可追溯性和真实性
            """
            return prompt

