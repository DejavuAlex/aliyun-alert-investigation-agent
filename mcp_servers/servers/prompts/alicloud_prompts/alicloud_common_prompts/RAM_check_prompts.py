from fastmcp.prompts.prompt import PromptResult, Message, SyncPromptResult
from mcp.types import PromptMessage, TextContent

from mcp_servers.base_server import BaseServer


class ALICLOUD_RAM_CHECK_PROMPT(BaseServer):
    def __init__(self,cmd_config):
        super().__init__(cmd_config,"alicloud_RAM_check_Server", prefix="alicloud_RAM_check_prompt")
        self.setup_server()

    def setup_server(self):

        @self.mcp_instance.tool
        def AK_leak_check(
                AK:str
        ):
            """
                本prompt需要输入AK，查询该AK是否泄露
            """
            FUNCTION = f"""
                        你是一个安全智能体,分析AK是否泄露。
                        """

            AUDIENCE = """
                        - 安全工程师
                        """
            STEPS = f"""
                        请按以下逻辑链逐步推理并记录中间判断,每一步先判断本地库中是否有相关prompt，如果有，按照相关prompt执行调查，并回写结果在这里，若没有则自行分析，并回写结果在这里：
                        1, 查询AK相关信息:
                            1.1 AK 创建时间；
                            1.2 AK 最近使用时间及频率及IP分布，并按照IP相关prompt进行调查；
                            1.3 AK 使用的地域（Region）和产品（如 ECS、OSS、RDS 等）；
                            1.4 是否绑定 RAM 用户？该用户权限范围（如是否具备高危权限：Delete、CreateAccessKey、AttachPolicy 等）；
                            1.5 是否启用了多因素认证（MFA）？
                            1.6 是否配置了 AK 轮换策略？
                        2，查询该AK是否在情报库中出现过
            """
            TEMPLATE = f"""            
                            输出分析结果，包含以下内容:
                            - 是否泄露: 是/否
                            - 泄露时间点: 如果泄露，则给出泄露的时间点
                            - 泄露频率: 如果泄露，则给出泄露的频率
                            - 泄露IP地址: 如果泄露，则给出泄露的IP地址
                            - 泄露User-Agent: 如果泄露，则给出泄露的User-Agent
                            - 需人工补充: 如果无法判断是否泄露，则标注需要人工补充的信息
            
                        """
            MANDATORY_RULES = """
                        ✅ 必须遵守：

                        所有判断必须基于提供的告警字段或可查询的公开情报（如IP地理位置）
                        不得虚构不存在的数据（如“该IP曾攻击过Google”除非有证据）
                        风险等级必须有明确依据支撑
                        处置建议必须具体、可执行、分优先级
                        输出必须严格遵循上述 Template 格式
                        若信息不足，需明确标注“需人工补充：XXX”
                        """
            CONSTRAINTS = """
                        ⛔ 不允许：

                        使用模糊语言如“可能有问题”、“大概率是攻击” → 必须量化或引用依据
                        推荐超出权限的操作（如“删除主账号”）
                        忽略失败状态（GetService失败 ≠ 无害）
                        假设企业已有某安全产品（如WAF/SIEM），除非告警中提及
                        ⏱ 时间约束：

                        分析过程应在 30 秒内完成（模拟实时响应）
                        输出长度控制在 800 字以内（适合告警工单嵌入）
                        """
            prompt = f"""
                        {FUNCTION.strip()}

                        目标受众：
                        {AUDIENCE.strip()}

                        请按以下思维步骤（Chain-of-Thought）逐步推理：
                        {STEPS.strip()}

                        请按照template输出内容
                        {TEMPLATE.strip()}

                        强制规则：
                        {MANDATORY_RULES.strip()}

                        约束条件：
                        {CONSTRAINTS.strip()}
                        """

            return PromptMessage(
                role="assistant",
                content=TextContent(
                    type="text",
                    text=prompt)
            )




        @self.mcp_instance.tool
        def who_assume_ram_role(
                event_trigger_time:str,
                ram_name:str,
                ip_address:str

        ) -> SyncPromptResult:
            """ 本prompt用来根据action_trail日志里面提供的ram_name和event_trigger_time，查询ram_nem是一个RAM用户，还是RAM角色，如果是RAM角色，则溯源该RAM角色的调用者，调用者调用{ram_name}的时间点必须早于{event_trigger_time},并且IP地址要和{ip_address}相同
                Args:
                    event_trigger_time
                Returns:
                    investigation report
             """
            FUNCTION = f"""
            你是一个安全智能体,这是在action trail日志分析中用来溯源RAM实体的prompt。
            """

            AUDIENCE = """
            - 安全工程师
            """

            STEPS = f"""
            请按以下逻辑链逐步推理并记录中间判断：
            请使用本地工具库中的工具:
            1，查询{ram_name}是RAM用户还是RAM角色，如果是RAM用户，则停止溯源，输出“该RAM实体是一个RAM用户，用户名为***，无需继续溯源”，如果是RAM角色，则继续下一步
            2, 如果是RAM角色，则查询该RAM角色的AssumeRole事件，AssumeRole事件的时间必须早于{event_trigger_time}，如果有多个AssumeRole事件，则选择时间最接近{event_trigger_time}的AssumeRole事件
            3, 分析AssumeRole事件的调用者身份，判断调用者身份类型，调用者身份类型有以下几种:
                - RAMUser: 代表是一个RAM用户，直接停止溯源，输出“该RAM角色的调用者是一个RAM用户，用户名为***，无需继续溯源”
                - Federation: 代表是一个联合身份用户，直接停止溯源，输出“该RAM角色的调用者是一个联合身份用户，联合身份用户ID为***，无需继续溯源”
                - OIDCUser: 代表是一个OIDC用户，直接停止溯源，输出“该RAM角色的调用者是一个OIDC用户，OIDC用户ID为***，无需继续溯源”
                - STSUser: 代表是一个临时用户，直接停止溯源，输出“该RAM角色的调用者是一个临时用户，临时用户ID为***，无需继续溯源
                - AssumedRole: 代表是一个RAM角色，表示是另一个RAM角色assume了该RAM角色，继续溯源该RAM角色的AssumeRole事件，AssumeRole事件的时间必须早于上一级AssumeRole事件的时间，并且{ip_address}相同。如果有多个AssumeRole事件，则选择时间最接近上一级AssumeRole事件的AssumeRole事件
            4，重复步骤3，直到满足以下任一停止条件:
                - 到达可信的“根身份”（Root Identity）
                - 进入阿里云服务代入角色（Service-Linked Role）
                - 遇到外部身份联合（Federated Identity）且已验证可信
                - 超过合理递归深度（防无限循环）
                - 时间超出调查窗口或日志不可用
            5，输出溯源结果，包含以下内容:
                - 溯源路径: 从{ram_name}开始，逐级列出每一级调用者的身份类型、ID、名称、AssumeRole时间、源IP、User-Agent等信息
                - 停止理由: 说明溯源停止的原因
                - 需人工补充: 如果溯源过程中遇到无法判断的情况，则标注需要人工补充的信息
            

            """

            TEMPLATE = """
            溯源路径: {trace_path}
            停止理由: {stop_reason}
            需人工补充: {need_manual}
            示例:
            1. RAM角色: GLOCHNALI-Cloud-Contributor
                - ARN: acs:ram::1219234893152666:role/glochnali-cloud-contributor
                - AssumeRole时间: 2024-10-01T12:00:00Z
                - 源IP: 192.168.1.2
                - User-Agent: aliyun-cli/3.0.0
                - 调用者身份类型: AssumedRole
                - 调用者身份ID: acs:ram::1803023858759084:role/glochnali-cloud-contributor
                - 信任策略
                - 关联权限策略
            2. RAM角色: glochnali-cloud-contributor
                - ARN: acs:ram::1803023858759084:role/glochnali-cloud-contributor
                - AssumeRole时间: 2024-10-01T11:50:00Z
                - 源IP: 192.168.1.2
                - User-Agent: aliyun-cli/3.0.0
                - 调用者身份类型: RAMUser
                - 调用者身份ID: user12345
                - 信任策略
                - 关联权限策略
            
            """

            MANDATORY_RULES = """
            ✅ 必须遵守：

            所有判断必须基于提供的告警字段或可查询的公开情报（如IP地理位置）
            不得虚构不存在的数据（如“该IP曾攻击过Google”除非有证据）
            风险等级必须有明确依据支撑
            处置建议必须具体、可执行、分优先级
            输出必须严格遵循上述 Template 格式
            若信息不足，需明确标注“需人工补充：XXX”
            """
            CONSTRAINTS = """
            ⛔ 不允许：

            使用模糊语言如“可能有问题”、“大概率是攻击” → 必须量化或引用依据
            推荐超出权限的操作（如“删除主账号”）
            忽略失败状态（GetService失败 ≠ 无害）
            假设企业已有某安全产品（如WAF/SIEM），除非告警中提及
            ⏱ 时间约束：

            分析过程应在 30 秒内完成（模拟实时响应）
            输出长度控制在 800 字以内（适合告警工单嵌入）
            """
            prompt = f"""
            {FUNCTION.strip()}

            目标受众：
            {AUDIENCE.strip()}

            请按以下思维步骤（Chain-of-Thought）逐步推理：
            {STEPS.strip()}
            
            请按照template输出内容
            {TEMPLATE.strip()}

            强制规则：
            {MANDATORY_RULES.strip()}

            约束条件：
            {CONSTRAINTS.strip()}
            """

            return  PromptMessage(
                    role="assistant",
                    content=TextContent(
                        type="text",
                        text=prompt)
                )

        # 实体类型与信任策略
        #     角色: GLOCHNALI-Cloud-Contributor
        #
        #     ARN: acs:ram::1219234893152666:role/glochnali-cloud-contributor
        #
        #     信任策略:
        #
        #     允许来自账号 1803023858759084 的角色：
        #
        #     acs:ram::1803023858759084:role/glochnali-cloud-contributor
        #
        #     acs:ram::1803023858759084:role/glochnali-cidevops-contributor
        #
        #
        #     允许服务 dataworks.aliyuncs.com 代入
        #
        #
        #     最大会话时长: 14400 秒
        #
        #
        #     关联权限策略（已绑定）
        #
        #
        #     AdministratorAccess（系统策略，管理所有阿里云资源）
        #
        #     AliyunOSSFullAccess（系统策略，OSS完全权限）
        #
        #     AliyunYundunCertFullAccess（云盾证书）
        #
        #     AliyunDataWorksFullAccess
        #
        #     AliyunMaxComputeFullAccess
        #