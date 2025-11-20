from mcp.types import PromptMessage, TextContent

from mcp_servers.base_server import BaseServer
from mcp_servers.servers.prompts.prompt_mixin import PromptMixin

"""
按照 https://help.aliyun.com/zh/security-center/user-guide/faq-about-detection-and-response?spm=a2c4g.11186623.0.0.1a0f5fbf0PffsD#section-faf-irm-az9 异常登录大类中各个子类进行编排
"""
class AliCLOUD_ABNORMAL_LOGIN_PROMPT(BaseServer,PromptMixin):
    def __init__(self,cmd_config):
        BaseServer.__init__(self,cmd_config,"alicloud_abnormal_login_prompt_Server", prefix="alicloud_abnormal_login_prompt")
        PromptMixin.__init__(self)
        self.setup_server()

    def setup_server(self):

        @self.mcp_instance.tool
        def analyze_weak_password_prompt() -> PromptMessage:
            """  这是一个专门调查阿里云通过弱密码登录阿里云资源(e.g. ECS, RDS)安全事件的模版prompt

            :return
                alicloud_abnormal_login_investigation_prompt:str , the prompt used by investigate alicloud abnormal login security event

            """
            FUNCTION = """
            你是一个云安全智能体（Cloud Security Agent），专门负责对阿里云'弱密码登录'事件进行调查。
            """

            AUDIENCE = """
            - 云安全工程师
            """

            TEMPLATE = """
            # 🛡️ 阿里云安全事件中心 - 异常登录安全事件调查报告

            ## 📋 事件摘要
            
            **🔹 基本信息**
            - 🚨 告警名称: {event_name}
            - ⚠️ 紧急程度: {event_level}
            - 🆔 告警ID: {event_id}
            - 📊 告警类型: {event_type}
            - 📍 状态: {event_status}
            - 🎯 攻击阶段: {attacking_phase}
            - 🔍 检测模式: {detection_mode}
            
            **🔹 登录信息**
            - ⏰ 登录时间: {login_time}  # 2025-09-26 17:57:36
            - 🌐 登录IP: {login_ip} # 112.124.56.78
            - 📍 登录来源地区: {login_region} # 中国-浙江-杭州
            - 🔑 登录方式: {login_method}  # 密码登录/密钥登录/控制台登录
            - ✅ 登录结果: {login_result}  # 成功/失败
            - 👤 登录用户名: {user_name}  # root/admin
            - ❌ 失败次数: {failed_attempts} # 5
            - ⏱️ 会话持续时间: {session_duration} # 2小时35分钟
            - 📝 操作记录: {operation_records} # 执行了whoami, ls, cat /etc/passwd等命令
            
            **🔹 资产信息**
            - 💻 受影响资产: {instance_id} # i-uf6j3z1z1zxxxxxx
            - 🏷️ 资产名称: {instance_name} # prod-web-01
            - 🌐 资产内网IP: {private_ip} # 10.10.30.2
            - 🌍 资产公网IP: {public_ip} # 47.96.123.45
            - 💾 资产操作系统: {os_name} # CentOS 7.9 64位
            - 📍 资产区域: {region} # cn-shanghai
            - 🛡️ 资产安全组: {security_group} # sg-uf6j3z1z1zxxxxxx
            - 🏷️ 资产标签: {instance_tags} # env:prod,app:web,business:algosuite
            
            **🔹 业务上下文**
            - 📦 所属产品线: {product_name}
            - 🌿 所属环境: {env}
            
            ## 🔎 调查过程
            
            **1️⃣ 步骤1：分析受影响资产属性**
            - 📝 分析描述: {step1_description}
            - 🛠️ 使用工具: {step1_tool_status}
            
            **2️⃣ 步骤2：分析登录后操作**
            - 📝 分析描述: {step2_description}
            - 🛠️ 使用工具: {step2_tool_status}
            
            **3️⃣ 步骤3：来源IP所在资产安全分析**
            - 📝 分析描述: {step3_description}
            - 🛠️ 使用工具: {step3_tool_status}
            
            **4️⃣ 步骤4：关联分析**
            - 📝 分析描述: {step4_description}
            - 🛠️ 使用工具: {step4_tool_status}
            
            **5️⃣ 步骤5：综合风险评估**
            - 📝 分析描述: {step5_description}
            
            **6️⃣ 步骤6：制定处置建议**
            - 📝 分析描述: {step6_description}
            
            **7️⃣ 步骤7：识别工具改进需求**
            - 📝 分析描述: {step7_description}
            
            ## 🔍 关键发现
            {key_findings}
            
            ## ⚠️ 风险评估
            {risk_indicators}
            
            **📊 综合结论**
            - 🎯 风险等级: {risk_level}
            - 📌 风险原因: {risk_reason}
            
            ## 🚀 处置建议
            {action_items}
            
            ## 🛠️ 待建立的工具
            {to_be_setup_tools}
            """

            Mandatory_RULES = self.mandatory_rules

            CONSTRAINTS = self.constraints

            STEPS = """
            请严格按以下步骤执行调查分析，并将每个步骤的输出写入对应的模板变量：

            步骤1：分析受影响资产属性
            
            - 分析关键信息：实例ID、IP地址、端口、资产标签等
            
            - 识别产品线归属：基于instance_tags判断属于algosuite、remix等哪个产品线
            
            - 识别环境分类：基于env标签判断是prod、staging、dev还是test环境
            
            - 检查安全组策略：开放的高危端口（如22、3389、445、135等）、允许访问的网段
            
            - 评估资产重要性：基于业务上下文判断资产关键程度
            
            - 将分析结果写入：{step1_description}
            
            - 将使用的工具名称写入：{step1_tool_status}
            
            - 将关键发现摘要写入：{key_findings}
            
            步骤2：分析登录后操作
            
            - 查询阿里云安全中心告警：分析弱密码登录后该受影响资产上是否存在其他安全事件，分析他们之间的关联性
            
            - 查询ActionTrail审计日志：分析登录后的操作行为
            
            - 检查K8S集群API Server访问日志（如适用）
            
            - 分析会话期间的操作记录：命令执行、文件访问等
            
            - 评估是否存在后续攻击行为（如木马植入、权限提升）
            
            - 将完整的分析过程和执行结果写入：{step2_description}
            
            - 将实际使用的工具名称或未使用工具的原因写入：{step2_tool_status}
            
            - 将关键发现摘要写入：{key_findings}
            
            步骤3：来源IP所在资产安全分析
            - 调用工具查询源IP是否是阿里云某个资产的IP地址？如果是，则需要分析这个资产是否已被安全攻击，分析方法:
              - 根据该资产类别，查找本地工具库中相应的资产安全检查工具，比如ECS调查相关的prompt，并执行，如果没找到，则按照你的调查经验执行调查
              - 如果该资产也属于Kubernetes集群的node，则需要调用工具查询该集群的API server的访问日志，如果没找到，则按照你的调查经验执行调查。如果不是K8S的node，则在结果中说明'因为不是K8S的node,所以不需要执行K8S相关的安全检查'
              - 源IP若是公网IP，则调取工具库中相关的IP调查工具prompt，并执行，如果没找到，则按照你的调查经验执行调查
            
            - 将完整的分析过程和执行结果写入：{step3_description}
            
            - 将实际使用的工具名称或未使用工具的原因写入：{step3_tool_status}
            
            - 将关键发现摘要写入：{key_findings}
            
            步骤4：关联分析
            - 调取工具查询阿里云安全中心的网络安全事件，是否有相同账号存在于其他资产上
            
            - 调取工具查询若有相同账号，则是否同样存在弱密码的告警
            
            - 调取工具查询源IP所在的资产是否也有其他涉及安全威胁到其他资产的网络安全事件告警
            
            - 识别攻击模式和横向移动迹象
            
            - 将完整的分析过程和执行结果写入：{step4_description}
            
            - 将实际使用的工具名称或未使用工具的原因写入：{step4_tool_status}
            
            - 将关键发现摘要写入：{key_findings}
            
            步骤5：综合风险评估
            
            - 整合所有步骤的分析发现
            
            - 评估整体风险等级：低、中、高、严重
            
            - 明确风险评级的关键依据和证据
            
            - 将完整的风险评估过程写入：{step5_description}
            
            - 将风险等级写入：{risk_level}
            
            - 将风险原因写入：{risk_reason}
            
            - 将风险指标写入：{risk_indicators}
            
            步骤6：制定处置建议
            
            - 基于风险评估制定具体处置措施
            
            - 建议包括：立即阻断IP、重置用户密码、吊销会话令牌、增强监控等
            
            - 提供优先级和操作步骤
            
            - 将完整的处置建议制定过程写入：{step6_description}
            
            - 将最终的处置建议列表写入：{action_items}
            
            步骤7：识别工具改进需求
            
            - 分析调查过程中缺失的工具能力
            
            - 描述需要建立的工具名称、功能、输入输出参数
            
            - 将完整的工具需求分析写入：{step7_description}
            
            - 将具体的工具规格要求写入：{to_be_setup_tools}
            """

            prompt = f"""
            {FUNCTION.strip()}
            目标受众：
            {AUDIENCE.strip()}
            请按以下思维步骤（Chain-of-Thought）逐步推理：
            {STEPS.strip()}
            输出必须严格遵循以下模板：
            {TEMPLATE.strip()}
            强制规则：
            {Mandatory_RULES.strip()}
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
        def analyze_process_exception_prompt() -> PromptMessage:
            """  这是一个专门调查阿里云进程异常行为安全事件的模版prompt
            :arg
                mandatory_rules: str, the mandatory rules prompt, 本地工具库中提供了该prompt
                constraints: str, the constraints prompt, 本地工具库中提供了该prompt
            :return
                alicloud_abonormal_process_behavior_prompt:str , the prompt used by investigate alicloud process exception security event

            """
            FUNCTION = """
            你是一个云安全智能体（Cloud Security Agent），专门负责对阿里云'进程异常行为'进行调查与响应。
            你需要基于安全告警原始数据（如异常登录、可疑进程、恶意文件、端口扫描、C2通信等），执行系统性分析，判断是否为真实攻击行为，并输出结构化调查报告与应急处置建议。
            """

            AUDIENCE = """
            - 云安全工程师
            """

            # TEMPLATE = """
            # # 🛡️ 阿里云安全事件中心 - 进程异常行为安全事件调查报告
            #
            # ## 📋 事件摘要
            #
            # **🔹 基本信息**
            # - 🚨 告警名称: {event_name}
            # - ⚠️ 紧急程度: {event_level}
            # - 🆔 告警ID: {event_id}
            # - 📊 告警类型: {event_type}
            # - 📍 状态: {event_status}
            # - 🎯 攻击阶段: {attacking_phase}
            # - 🔍 检测模式: {detection_mode}
            #
            # **🔹 进程信息**
            # - 🔧 进程ID: {process_id}
            # - ⏰ 进程启动时间: {process_start_time}
            # - 📁 进程路径: {process_path}
            # - 💻 命令行: {cmd_line}
            # - 👤 用户名: {user_name}
            #
            # **🔹 父进程信息**
            # - 🔗 父进程ID: {parent_process_id}
            # - 📂 父进程路径: {parent_process_path}
            # - ⌨️ 父进程命令行: {parent_cmd_line}
            #
            # **🔹 Kubernetes环境**
            # - 🏷️ K8s命名空间: {kubernetes_namespace}
            # - 🖥️ K8s节点名称: {kubernetes_node}
            # - 📦 K8s Pod: {kubernetes_pod}
            # - 🐳 容器名: {pod_name}
            # - 🆔 容器ID: {pod_id}
            # - 🖼️ 镜像名: {image_name}
            # - 🆔 镜像ID: {image_id}
            #
            # **🔹 进程链**
            # - ⛓️ 进程链: {process_chain}
            #
            # **🔹 资产信息**
            # - 💻 受影响资产: {instance_id}
            # - 🏷️ 资产名称: {instance_name}
            # - 🌐 资产内网IP: {private_ip}
            # - 🌍 资产公网IP: {public_ip}
            # - 💾 资产操作系统: {os_name}
            # - 📍 资产区域: {region}
            # - 🛡️ 资产安全组: {security_group}
            # - 🏷️ 资产标签: {instance_tags}
            #
            # **🔹 业务上下文**
            # - 📦 所属产品线: {product_name}
            # - 🌿 所属环境: {env}
            #
            # ## 🔎 调查过程
            #
            # **1️⃣ 步骤1：解析告警上下文**
            # - 📝 分析描述: {step1_description}
            # - 🛠️ 使用工具: {step1_tool_status}
            #
            # **2️⃣ 步骤2：分析来源IP威胁情报**
            # - 📝 分析描述: {step2_description}
            # - 🛠️ 使用工具: {step2_tool_status}
            #
            # **3️⃣ 步骤3：检查ECS实例暴露面**
            # - 📝 分析描述: {step3_description}
            # - 🛠️ 使用工具: {step3_tool_status}
            #
            # **4️⃣ 步骤4：检查ECS实例异常活动**
            # - 📝 分析描述: {step4_description}
            # - 🛠️ 使用工具: {step4_tool_status}
            #
            # **5️⃣ 步骤5：分析可疑进程行为**
            # - 📝 分析描述: {step5_description}
            # - 🛠️ 使用工具: {step5_tool_status}
            #
            # **6️⃣ 步骤6：综合风险评估**
            # - 📝 分析描述: {step6_description}
            #
            # **7️⃣ 步骤7：制定处置建议**
            # - 📝 分析描述: {step7_description}
            #
            # **8️⃣ 步骤8：识别工具改进需求**
            # - 📝 分析描述: {step8_description}
            #
            # ## 🔍 关键发现
            # {key_findings}
            #
            # ## ⚠️ 风险评估
            # {risk_indicators}
            #
            # **📊 综合结论**
            # - 🎯 风险等级: {risk_level}
            # - 📌 风险原因: {risk_reason}
            #
            # ## 🚀 处置建议
            # {action_items}
            #
            # ## 🛠️ 待建立的工具
            # {to_be_setup_tools}
            #
            # """
            # Mandatory_RULES = self.mandatory_rules
            # CONSTRAINTS = self.constraints
            #
            # STEPS = """
            # 请严格按以下步骤执行调查分析，并将每个步骤的输出写入对应的模板变量：
            #
            # 1. 步骤1：解析告警上下文
            #    - 分析关键信息：实例ID、IP地址、端口、文件路径、资产标签等
            #    - 识别产品线归属：基于instance_tags判断属于algosuite、remix等哪个产品线
            #    - 识别环境分类：基于env标签判断是prod、staging、dev还是test环境
            #    - 将分析结果写入：{step1_description}
            #    - 将使用的工具名称写入：{step1_tool_status}
            #    - 将关键发现摘要写入：{key_findings}
            #
            # 2. 步骤2：分析来源IP的威胁
            #    - 搜索IP调查工具分析源IP的威胁等级
            #    - 检查IP的信誉度、历史恶意行为、地理位置风险
            #    - 评估该IP是否在已知威胁情报库中
            #    - 将分析结果写入：{step2_description}
            #    - 将使用的工具名称写入：{step2_tool_status}
            #    - 将关键发现摘要写入：{key_findings}
            #
            # 3. 步骤3：检查受影响的ECS实例暴露面
            #    - 检查实例是否绑定公网IP及暴露程度
            #    - 分析安全组策略：开放的高危端口、允许访问的网段
            #    - 评估安全组设置是否存在风险（如允许任意来源访问）
            #    - 输出具体的安全组策略ID和规则内容
            #    - 将分析结果写入：{step3_description}
            #    - 将使用的工具名称写入：{step3_tool_status}
            #    - 将关键发现摘要写入：{key_findings}
            #
            # 4. 步骤4：检查ECS实例异常活动
            #    - 如果是容器内的进程异常，需要考虑是否发生容器逃逸，导致宿主机被侵入，所以要检查宿主机相关的异常活动
            #    - 分析通过workbench/VNC等阿里云支持的浏览器登录ECS的方式做异常登录：通过actiontrail检查ConsoleConnect、VNC登录事件
            #      * 执行结果：必须明确说明是否执行了检查，检查结果如何，如未执行需说明原因
            #    - 分析通过SSH/RDP等系统方式做的异常登录：检查SSH/RDP登录日志中的异常模式
            #      * 执行结果：必须明确说明是否执行了检查，检查结果如何，如未执行需说明原因
            #    - 检查堡垒机日志：分析登录时间、IP、失败次数等异常
            #      * 执行结果：必须明确说明是否执行了检查，检查结果如何，如未执行需说明原因
            #    - 关联其他安全事件：检查是否有其他事件关联到此资产
            #      * 执行结果：必须明确说明是否执行了检查，检查结果如何，如未执行需说明原因
            #    - 将完整的分析过程和执行结果写入：{step4_description}
            #    - 将实际使用的工具名称或未使用工具的原因写入：{step4_tool_status}
            #    - 将关键发现摘要写入：{key_findings}
            #
            # 5. 步骤5：分析可疑进程行为
            #    - 分析进程执行上下文：执行用户、权限级别、运行目的
            #      * 执行结果：必须明确说明是否执行了检查，检查结果如何，如未执行需说明原因
            #    - 检测异常行为模式：CPU/内存占用、网络连接、文件操作
            #      * 执行结果：必须明确说明是否执行了检查，检查结果如何，如未执行需说明原因
            #    - 评估进程的合法性和潜在风险
            #      * 执行结果：必须明确说明是否执行了检查，检查结果如何，如未执行需说明原因
            #    - 将完整的分析过程和执行结果写入：{step5_description}
            #    - 将实际使用的工具名称或未使用工具的原因写入：{step5_tool_status}
            #    - 将关键发现摘要写入：{key_findings}
            #
            # 6. 步骤6：综合风险评估
            #    - 整合所有步骤的分析发现
            #      * 执行结果：必须基于前5个步骤的实际执行情况进行整合
            #    - 评估整体风险等级：低、中、高、严重
            #      * 执行结果：必须给出明确的风险等级判断
            #    - 明确风险评级的关键依据和证据
            #      * 执行结果：必须列出具体的评估依据
            #    - 将完整的风险评估过程写入：{step6_description}
            #    - 将风险等级写入：{risk_level}
            #    - 将风险原因写入：{risk_reason}
            #    - 将风险指标写入：{risk_indicators}
            #
            # 7. 步骤7：制定处置建议
            #    - 基于风险评估制定具体处置措施
            #      * 执行结果：必须给出具体的处置建议
            #    - 建议包括：网络隔离、访问阻断、密码重置、补丁更新等
            #      * 执行结果：必须列出具体的处置措施
            #    - 提供优先级和操作步骤
            #      * 执行结果：必须明确处置的优先级顺序
            #    - 将完整的处置建议制定过程写入：{step7_description}
            #    - 将最终的处置建议列表写入：{action_items}
            #
            # 8. 步骤8：识别工具改进需求
            #    - 分析调查过程中缺失的工具能力
            #      * 执行结果：必须明确说明哪些工具能力缺失
            #    - 描述需要建立的工具名称、功能、输入输出参数
            #      * 执行结果：必须详细描述待建立工具的具体规格
            #    - 将完整的工具需求分析写入：{step8_description}
            #    - 将具体的工具规格要求写入：{to_be_setup_tools}
            # """
            TEMPLATE = """
            # 🛡️ 阿里云安全事件中心 - 进程异常行为安全事件调查报告

            ## 📋 事件摘要

            **🔹 基本信息**
            - 🚨 告警名称: {event_name}
            - ⚠️ 紧急程度: {event_level}
            - 🆔 告警ID: {event_id}
            - 📊 告警类型: {event_type}
            - 📍 状态: {event_status}
            - 🎯 攻击阶段: {attacking_phase}
            - 🔍 检测模式: {detection_mode}

            **🔹 进程行为特征**
            - 🔧 进程ID: {process_id}
            - ⏰ 进程启动时间: {process_start_time}
            - 📁 进程路径: {process_path}
            - 💻 命令行: {cmd_line}
            - 👤 用户名: {user_name}
            - 🔐 执行权限: {process_privileges}
            - 📊 资源占用: {resource_usage}

            **🔹 进程关系分析**
            - 🔗 父进程ID: {parent_process_id}
            - 📂 父进程路径: {parent_process_path}
            - ⌨️ 父进程命令行: {parent_cmd_line}
            - ⛓️ 完整进程链: {process_chain}
            - 🔍 进程树分析: {process_tree_analysis}

            **🔹 行为异常指标**
            - 🎯 异常行为模式: {suspicious_patterns}
            - 🌐 网络连接: {network_connections}
            - 📁 文件操作: {file_operations}
            - ⚡ 系统调用: {system_calls}

            **🔹 Kubernetes环境**
            - 🏷️ K8s命名空间: {kubernetes_namespace}
            - 🖥️ K8s节点名称: {kubernetes_node}
            - 📦 K8s Pod: {kubernetes_pod}
            - 🐳 容器名: {pod_name}
            - 🆔 容器ID: {pod_id}
            - 🖼️ 镜像名: {image_name}
            - 🆔 镜像ID: {image_id}
            - 🔒 容器安全上下文: {security_context}

            **🔹 资产信息**
            - 💻 受影响资产: {instance_id}
            - 🏷️ 资产名称: {instance_name}
            - 🌐 资产内网IP: {private_ip}
            - 🌍 资产公网IP: {public_ip}
            - 💾 资产操作系统: {os_name}
            - 📍 资产区域: {region}
            - 🛡️ 资产安全组: {security_group}
            - 🏷️ 资产标签: {instance_tags}

            **🔹 业务上下文**
            - 📦 所属产品线: {product_name}
            - 🌿 所属环境: {env}
            - 🎯 业务关键性: {business_criticality}

            ## 🔎 调查过程

            **1️⃣ 步骤1：告警上下文深度解析**
            - 📝 分析描述: {step1_description}
            - 🛠️ 使用工具: {step1_tool_status}
            - 🔍 关键发现: {step1_findings}

            **2️⃣ 步骤2：进程行为深度分析**
            - 📝 分析描述: {step2_description}
            - 🛠️ 使用工具: {step2_tool_status}
            - 🔍 关键发现: {step2_findings}

            **3️⃣ 步骤3：威胁情报关联分析**
            - 📝 分析描述: {step3_description}
            - 🛠️ 使用工具: {step3_tool_status}
            - 🔍 关键发现: {step3_findings}

            **4️⃣ 步骤4：安全暴露面评估**
            - 📝 分析描述: {step4_description}
            - 🛠️ 使用工具: {step4_tool_status}
            - 🔍 关键发现: {step4_findings}

            **5️⃣ 步骤5：异常活动调查**
            - 📝 分析描述: {step5_description}
            - 🛠️ 使用工具: {step5_tool_status}
            - 🔍 关键发现: {step5_findings}

            **6️⃣ 步骤6：关联事件分析**
            - 📝 分析描述: {step6_description}
            - 🛠️ 使用工具: {step6_tool_status}
            - 🔍 关键发现: {step6_findings}

            **7️⃣ 步骤7：攻击链重建**
            - 📝 分析描述: {step7_description}
            - 🛠️ 使用工具: {step7_tool_status}
            - 🔍 关键发现: {step7_findings}

            **8️⃣ 步骤8：综合风险评估**
            - 📝 分析描述: {step8_description}

            **9️⃣ 步骤9：应急处置建议**
            - 📝 分析描述: {step9_description}

            **🔟 步骤10：改进措施识别**
            - 📝 分析描述: {step10_description}

            ## 🔍 关键发现汇总
            {key_findings}

            ## ⚠️ 风险评估矩阵
            {risk_indicators}

            **📊 综合风险结论**
            - 🎯 风险等级: {risk_level}
            - 📌 风险评分: {risk_score}/100
            - 🔥 影响程度: {impact_level}
            - 📈 置信度: {confidence_level}
            - 📌 风险原因: {risk_reason}

            ## 🚀 处置行动计划
            {action_items}

            ## 🛠️ 能力提升建议
            {to_be_setup_tools}

            ## 📋 证据链摘要
            {evidence_chain}
            """

            Mandatory_RULES = self.mandatory_rules
            CONSTRAINTS = self.constraints

            STEPS = """
            请严格按以下步骤执行调查分析，并将每个步骤的输出写入对应的模板变量：

            1. 步骤1：告警上下文深度解析
               - 分析进程异常的具体行为特征：命令行参数、执行参数、参数异常
               - 检查进程执行环境：容器内/宿主机、执行用户权限、工作目录
               - 分析进程启动时机：系统启动时、定时任务、服务启动时、用户交互时
               - 识别产品线归属和业务关键性：基于instance_tags和业务上下文
               - 将分析结果写入：{step1_description}
               - 将使用的工具名称写入：{step1_tool_status}
               - 将关键发现写入：{step1_findings}和{key_findings}

            2. 步骤2：进程行为深度分析
               - 分析进程行为模式：文件操作、网络连接、系统调用序列
               - 检查进程血缘关系：父进程合法性、子进程派生、进程树异常
               - 评估进程资源使用：异常CPU/内存占用、文件描述符、网络连接数
               - 检测进程隐藏行为：进程伪装、注入、隐藏技术
               - 将分析结果写入：{step2_description}
               - 将使用的工具名称写入：{step2_tool_status}
               - 将关键发现写入：{step2_findings}和{key_findings}

            3. 步骤3：威胁情报关联分析
               - 多维度威胁情报分析：进程哈希、文件路径、命令行特征
               - 检查进程相关IOC在威胁情报库中的匹配情况
               - 分析网络连接的目的地IP/域名的信誉度
               - 评估进程行为与已知攻击模式的匹配度
               - 将分析结果写入：{step3_description}
               - 将使用的工具名称写入：{step3_tool_status}
               - 将关键发现写入：{step3_findings}和{key_findings}

            4. 步骤4：安全暴露面评估
               - 异常进程是否暴露宿主机某个端口，如果有，该端口涉及的安全组权限是否收敛
               - 评估实例网络暴露程度：公网IP、NAT映射、负载均衡配置
               - 宿主机是否开放了其他端口，如果有，端口涉及的安全组权限是否收敛
               - 检查容器运行时安全配置：特权模式、挂载敏感目录、capabilities
               - 评估身份认证和访问控制风险
               - 将分析结果写入：{step4_description}
               - 将使用的工具名称写入：{step4_tool_status}
               - 将关键发现写入：{step4_findings}和{key_findings}

            5. 步骤5：异常活动调查
               - 检查登录异常：成功/失败登录、异常时间、异常地理位置
               - 分析用户行为异常：权限提升、sudo使用、敏感命令执行
               - 检查系统日志异常：服务异常启动、配置变更、审计日志
               - 调查容器逃逸迹象：挂载docker.sock、特权容器、内核漏洞利用
               - 将分析结果写入：{step5_description}
               - 将使用的工具名称写入：{step5_tool_status}
               - 将关键发现写入：{step5_findings}和{key_findings}

            6. 步骤6：关联事件分析
               - 时间关联分析：同一时间段内的其他安全事件
               - 资产关联分析：同一资产的其他告警和异常
               - 行为关联分析：相似攻击手法的其他事件
               - 威胁情报关联：同一IOC出现的其他事件
               - 将分析结果写入：{step6_description}
               - 将使用的工具名称写入：{step6_tool_status}
               - 将关键发现写入：{step6_findings}和{key_findings}

            7. 步骤7：攻击链重建
               - 重构攻击时间线：从初始访问到目标达成
               - 识别攻击技术：基于MITRE ATT&CK框架分类
               - 评估攻击成功率：已达成目标和未达成的攻击步骤
               - 分析攻击者意图：数据窃取、持久化、横向移动等
               - 将分析结果写入：{step7_description}
               - 将使用的工具名称写入：{step7_tool_status}
               - 将关键发现写入：{step7_findings}和{key_findings}

            8. 步骤8：综合风险评估
               - 量化风险评估：基于CVSS或类似框架评分
               - 评估业务影响：数据泄露风险、服务中断风险、合规风险
               - 评估攻击复杂性：攻击者技能要求、利用难度
               - 确定风险等级和置信度
               - 将完整的风险评估过程写入：{step8_description}
               - 将风险等级写入：{risk_level}，风险评分写入：{risk_score}
               - 将影响程度写入：{impact_level}，置信度写入：{confidence_level}
               - 将风险原因写入：{risk_reason}，风险指标写入：{risk_indicators}

            9. 步骤9：应急处置建议
               - 制定优先级处置措施：立即阻断、调查取证、恢复加固
               - 提供具体操作命令和步骤
               - 考虑业务影响最小化的处置方案
               - 制定验证处置效果的方法
               - 将完整的处置建议制定过程写入：{step9_description}
               - 将最终的处置建议列表写入：{action_items}

            10. 步骤10：改进措施识别
                - 识别检测能力缺口：未能检测的攻击技术和行为
                - 提出防护措施改进：配置加固、策略优化
                - 建议监控能力提升：新的检测规则、监控覆盖
                - 规划自动化响应能力
                - 将完整的改进需求分析写入：{step10_description}
                - 将具体的工具和能力要求写入：{to_be_setup_tools}
                - 将证据链摘要写入：{evidence_chain}

            【关键执行要求】
            1. 每个步骤必须明确说明是否执行了检查，检查结果如何，如未执行需说明原因
            2. 所有发现必须基于可验证的证据和数据
            3. 风险评估必须基于实际发现，避免主观臆断
            4. 处置建议必须具体可行，包含操作步骤
            5. 工具使用情况必须真实反映调查过程
            """

            prompt = f"""
            {FUNCTION.strip()}
            目标受众：
            {AUDIENCE.strip()}
            请按以下思维步骤（Chain-of-Thought）逐步推理：
            {STEPS.strip()}
            输出必须严格遵循以下模板：
            {TEMPLATE.strip()}
            强制规则：
            {Mandatory_RULES.strip()}
            约束条件：
            {CONSTRAINTS.strip()}
            """
            return PromptMessage(
                role="assistant",
                content=TextContent(
                    type="text",
                    text=prompt)
            )

        #
        #
        # @self.mcp_instance.tool
        # def analyze_alicloud_OSS_event_prompt() -> SyncPromptResult:
        #     """ this is a prompt used by investigate alicloud OSS security event, not audit event or config event """
        #     FUNCTION = """
        #     你是一个云安全智能体（Cloud Security Agent），专门负责对阿里云OSS相关的安全事件(不是审计事件)行为告警进行自动化调查与响应。
        #     你需要基于告警原始数据，执行系统性分析，识别是否为真实攻击或误报，并输出结构化调查报告与处置建议。
        #     """
        #
        #     AUDIENCE = """
        #     - 云安全工程师
        #     """
        #
        #     TEMPLATE = """
        #     # OSS可疑访问事件调查报告
        #
        #     ## 事件摘要
        #     - 事件ID: {event_id}
        #     - 事件名称: {event_name}
        #     - 事件等级: {event_level}
        #     - 事件状态: {event_status}
        #     - 告警原因: {alert_reason}
        #     - 实体类型: {entity_type}
        #     - 实体名称: {entity_name}
        #     - AK: {AK_name}
        #     - 来源IP: {source_ip}
        #     - User-Agent: {user_agent}
        #     - API: {api_name}
        #     - 时间: {event_time}
        #
        #     ## 调查过程
        #     {step1_description}
        #     {step1_tool_status}
        #
        #     {step2_description}
        #     {step2_tool_status}
        #
        #     {step3_description}
        #     {step3_tool_status}
        #
        #     {step4_description}
        #     {step4_tool_status}
        #
        #     {step5_description}
        #     {step5_tool_status}
        #
        #     {step6_description}
        #     {step6_tool_status}
        #
        #     {step7_description}
        #     {step7_tool_status}
        #
        #     {step8_description}
        #     {step8_tool_status}
        #
        #     ## 关键发现
        #     {key_findings}
        #
        #     ## 风险评估
        #     {risk_indicators}
        #     📊 综合结论：{risk_level} + {risk_reason}
        #
        #     ## 处置建议
        #     {action_items}
        #
        #     ## 后续跟踪（Checklist）
        #     {checklist}
        #     """
        #
        #     MANDATORY_RULES = """
        #     ✅ 必须遵守：
        #     - 只有实际调用了工具的步骤才需要记录工具信息
        #     - 工具调用格式：工具名称 | 状态：成功/失败 | 失败原因（如失败）
        #     - 无工具调用的步骤只需记录分析结果，不需写工具信息
        #     - 工具调用失败的必须写明具体失败原因和对分析的影响
        #     - 不得虚构不存在的工具调用记录
        #     - 所有分析必须基于实际可用的信息源
        #     """
        #
        #     CONSTRAINTS = """
        #     ⛔ 不允许：
        #     - 在无工具调用的步骤中虚构工具信息
        #     - 使用模糊的工具状态描述（如"可能成功"）
        #     - 忽略工具调用失败对分析的影响
        #     - 假设存在未在告警中提及的安全工具
        #
        #     ✅ 必须做到：
        #     - 真实反映每个步骤的工具调用情况
        #     - 工具调用成功时清晰说明获得的信息
        #     - 工具调用失败时说明限制和替代分析方法
        #     - 保持工具调用记录的准确性和真实性
        #     """
        #
        #     STEPS = f"""
        #     请按以下逻辑链逐步推理并记录中间判断：
        #
        #     对于每个调查步骤，请按以下格式记录：
        #     1. 步骤描述和分析结果
        #     2. 工具调用情况（如有）：
        #        - 调用的工具名称
        #        - 调用状态：成功/失败
        #        - 如失败，说明失败原因
        #
        #     具体步骤内容：
        #
        #     1. 【解析告警上下文】
        #        - 分析结果：基于告警字段进行初步分析
        #        - 工具调用：此步骤为内部分析，无需调用外部工具
        #
        #     2. 【分析来源IP风险】
        #        - 调用IP_common_prompts，按照prompt执行调查并写回结果
        #        - 要求将工具返回的字段（国家/城市、ASN、是否企业出口、是否命中黑名单、证据链接）写入step2_description，并同步汇总到“关键发现”和“风险评估”段。
        #
        #
        #     3. 【RAM账户溯源及权限合理性判断】
        #        - 请按照RAM_check_prompts来溯源
        #        - 要求将工具返回的字段（溯源路径，停止理由，需人工补充的内容，调用者身份类型、调用者身份ID、信任策略、关联权限策略）写入step3_description
        #        - 分析信任策略和关联权限策略，评估权限合理性
        #        - 如无工具则基于现有信息分析权限合理性
        #        - 记录工具调用情况（如有）
        #
        #     4. 【评估AK泄露可能性】
        #        - 如有ActionTrail查询工具则调用
        #        - 如果涉及IP分析，请调用IP_common_prompts，按照prompt执行调查并写回结果
        #        - 分析AK使用模式，评估泄露风险
        #        - 记录工具调用状态和结果
        #
        #     5. 【分析User-Agent行为模式】
        #        - 分析User-Agent字符串特征
        #        - 如有行为分析工具则调用
        #        - 记录分析结果和工具状态
        #
        #     6. 【关联其他事件】
        #        - 如有事件关联分析工具则调用
        #        - 分析同一AK/IP的历史活动
        #        - 记录工具调用情况
        #
        #     7. 【综合风险评级】
        #        - 综合各维度分析结果进行评级
        #        - 无需调用外部工具
        #
        #     8. 【输出处置建议】
        #        - 基于风险评估给出具体建议
        #        - 无需调用外部工具
        #     """
        #
        #     TO_BE_SETUP_TOOLS = """
        #     此次调查过程中，大模型需要调用的工具库，但目前还没有，有待后期建设，内容包括:
        #     - {具体名称}
        #    - {入参}
        #    - {出参}
        #    - {功能描述}
        #     """
        #     prompt = f"""
        #     {FUNCTION.strip()}
        #
        #     目标受众：
        #     {AUDIENCE.strip()}
        #
        #     请按以下思维步骤（Chain-of-Thought）逐步推理：
        #     {STEPS.strip()}
        #
        #     输出必须严格遵循以下模板：
        #     {TEMPLATE.strip()}
        #
        #     强制规则：
        #     {MANDATORY_RULES.strip()}
        #
        #     约束条件：
        #     {CONSTRAINTS.strip()}
        #
        #     待建立的工具：
        #     {TO_BE_SETUP_TOOLS.strip()}
        #     """
        #
        #     return  PromptMessage(
        #             role="assistant",
        #             content=TextContent(
        #                 type="text",
        #                 text=prompt)
        #         )
        #
        # @self.mcp_instance.tool
        # def analyze_alicloud_ECS_event_prompt() -> SyncPromptResult:
        #     """ this is a prompt used by investigate alicloud ECS security event,not audit event  or config event"""
        #     FUNCTION = """
        #     你是一个云安全智能体（Cloud Security Agent），专门负责对阿里云ECS实例相关的安全事件（非配置变更或审计日志事件）进行自动化调查与响应。
        #     你需要基于安全告警原始数据（如异常登录、可疑进程、恶意文件、端口扫描、C2通信等），执行系统性分析，判断是否为真实攻击行为，并输出结构化调查报告与应急处置建议。
        #     """
        #
        #     AUDIENCE = """
        #     - 云安全工程师
        #     """
        #
        #     TEMPLATE = """
        #     # ECS可疑安全事件调查报告
        #
        #     ## 事件摘要
        #     告警名称: {event_name}
        #     紧急程度: {event_level}
        #     告警ID: {event_id}
        #     告警类型: {event_type}
        #     状态: {event_status}
        #     攻击阶段: {attacking_phase}
        #     检测模式: {detection_mode}
        #     进程ID: {process_id}
        #     进程启动时间: {process_start_time}  # 2025-09-26 17:57:36
        #     进程路径: {process_path} # /usr/local/bin/dockerd
        #     命令行: {cmd_line}  #dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2375 --tls=false --insecure-registry=harbor-core.harbor.svc.cluster.local
        #     用户名: {user_name}  # root
        #     父进程ID: {parent_process_id} # 3095027
        #     父进程路径: {parent_process_path} #/usr/local/bin/docker-init
        #     父进程命令行:{parent_cmd_line} # docker-init -- dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2375 --tls=false --insecure-registry=harbor-core.harbor.svc.cluster.local
        #     K8s命名空间: {kubernetes_namespace} #gitlab-runner
        #     K8s节点名称: {kubernetes_node} #cn-shanghai.10.151.224.147
        #     K8s Pod: {kubernetes_pod} #runner-gvx8xbr8p-project-186448-concurrent-0-ji4n8uxn
        #     容器名: {pod_name} #svc-0
        #     容器ID: {pod_id} #b95e9831ba4165e0a2ffcf96d190d62c8eb050a65df56d1110547058125f1726
        #     镜像名: {image_name} #artifact.roche.com.cn/common-dockerhub-docker-r/docker@sha256:96637a2755acf4eaea3f15da24c03d88b86468a691a640c51a527b27622c2b58
        #     镜像ID: {image_id} #artifact.roche.com.cn/common-dockerhub-docker-r/docker:25.0.4
        #     进程链: {process_chain} #-[3095027]  docker-init -- dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2375 --tls=false --insecure-registry=harbor-core.harbor.svc.cluster.local
        #     受影响资产: {instance_id} #i-uf6j3z1z1xxxxxx
        #     资产名称: {instance_name} #test-ecs
        #     资产内网IP: {private_ip} #
        #     资产公网IP: {public_ip} #
        #     资产操作系统: {os_name} #CentOS 7.9 64位
        #     资产区域: {region} #cn-shanghai
        #     资产安全组: {security_group} #sg-uf6j3z1z1zxxxxxx
        #     资产标签: {instance_tags} #env:prod,app:web
        #
        #
        #     ## 调查过程
        #     {step1_description}
        #     {step1_tool_status}
        #
        #     {step2_description}
        #     {step2_tool_status}
        #
        #     {step3_description}
        #     {step3_tool_status}
        #
        #     {step4_description}
        #     {step4_tool_status}
        #
        #     {step5_description}
        #     {step5_tool_status}
        #
        #     {step6_description}
        #     {step6_tool_status}
        #
        #     {step7_description}
        #     {step7_tool_status}
        #
        #     {step8_description}
        #     {step8_tool_status}
        #
        #     {step9_description}
        #     {step9_tool_status}
        #
        #     ## 关键发现
        #     {key_findings}
        #
        #     ## 风险评估
        #     {risk_indicators}
        #     📊 综合结论：{risk_level} + {risk_reason}
        #
        #     ## 处置建议
        #     {action_items}
        #
        #     ## 后续跟踪（Checklist）
        #     {checklist}
        #     """
        #
        #     MANDATORY_RULES = """
        #     ✅ 必须遵守：
        #     - 仅当实际调用了工具时才记录工具信息
        #     - 工具调用格式：工具名称 | 状态：成功/失败 | 失败原因（如失败）
        #     - 无工具调用的步骤只需记录分析结果，不得虚构工具调用
        #     - 工具调用失败时必须说明具体原因及其对分析的影响
        #     - 所有判断必须基于告警中提供的或可通过工具获取的真实数据
        #     - 不得假设存在未明确提供的安全产品（如未启用云防火墙则不可引用其日志）
        #     """
        #
        #     CONSTRAINTS = """
        #     ⛔ 不允许：
        #     - 在未调用工具的步骤中编造工具名称或状态
        #     - 使用“可能”“大概”等模糊状态描述
        #     - 忽略工具失败对结论的影响
        #     - 引用未在环境中部署的安全能力（如未安装云安全中心Agent则不可获取进程快照）
        #
        #     ✅ 必须做到：
        #     - 如实反映每一步是否依赖工具及结果
        #     - 工具成功时清晰列出获取的关键信息
        #     - 工具失败时说明限制并尝试基于已有信息推断
        #     - 保持调查逻辑的可追溯性和真实性
        #     """
        #
        #     STEPS = """
        #     请按以下逻辑链逐步推理并记录中间判断：
        #
        #     1. 【解析告警上下文】
        #        - 分析结果：识别告警类型（如暴力破解、Webshell上传、C2外联、可疑进程等），提取关键实体（实例ID、IP、端口、文件路径，instance标签等），描述ECS的label，判断所属哪个产品，哪个环境(生产环境或者非生产环境)，将结果写入step1_description，并汇总至“关键发现”
        #
        #     2. 【分析来源IP威胁情报】
        #        - 调用本地工具：ip_common_prompts，并按照prompt执行调查
        #        - 将结果写入step2_description，并汇总至“关键发现”
        #
        #     3. 【检查ECS实例暴露面】
        #        - 调用工具：ECS_exposure_analyzer
        #        - 检查内容：该实例是否绑定公网IP、安全组是否开放高危端口（如22、3389、445、135等）、是否允许0.0.0.0/0访问
        #        - 输出：暴露的端口列表及对应安全组规则ID
        #        - 若工具不可用，则基于告警中的安全组ID和端口信息做推断
        #        - 将结果写入step3_description，并汇总至“关键发现”
        #
        #     4, [检查ECS实例登录异常]
        #         - 调用工具：查询本地工具库中action trail相关工具，搜索该实例在告警前后30分钟内的登录事件(ConnectInstance),得到登录IP，登录成功或者失败结果
        #         - 调用本地工具：ip_common_prompts，并按照prompt执行调查
        #         - 将结果写入step4_description，并汇总至“关键发现”
        #
        #     5. 【获取主机层上下文（如Agent可用）】
        #        - 调用工具：CloudSecurityCenter_host_snapshot
        #        - 获取：可疑进程树、启动命令、父进程、文件哈希、网络连接（lsof/netstat）
        #        - 若未安装Agent或调用失败，注明“无法获取主机层上下文”，并基于网络层告警推断
        #        - 将结果写入step5_description，并汇总至“关键发现”
        #
        #     6. 【文件/进程恶意性判定】
        #        - 调用工具：File_malware_scan（如提供文件路径或哈希）
        #        - 或调用：Process_behavior_analyzer（如提供进程名/PID）
        #        - 返回：是否为已知恶意软件、家族类型、IOC（如C2域名、IP）
        #        - 若无可调用工具，则基于文件路径（如/tmp/.X11-unix）或进程名（如xmrig）做启发式判断
        #        - 将结果写入step6_description，并汇总至“关键发现”
        #
        #     7. 【关联横向移动或内网扫描行为】
        #        - 调用工具：VPC_flow_log_correlator
        #        - 分析：该实例在告警前后5分钟内是否对其他内网IP发起连接（尤其是高危端口）
        #        - 输出：可疑内网目标列表及协议
        #        - 若无流日志权限，则跳过并注明限制
        #        - 将结果写入step7_description，并汇总至“关键发现”
        #
        #     8. 【综合风险评级】
        #        - 综合IP威胁、暴露面、主机行为、横向活动等维度
        #        - 判定：真实攻击 / 误报 / 需人工确认
        #        - 无需调用工具
        #
        #     9. 【输出处置建议】
        #        - 基于风险等级给出具体操作：隔离实例、回收AK、更新安全组、查杀病毒、重装系统等
        #        - 无需调用工具
        #     """
        #
        #     TO_BE_SETUP_TOOLS = """
        #     此次调查过程中，大模型需要调用的工具库（当前为占位，后续需对接真实API）：
        #     - IP_threat_intel_lookup
        #       - 入参：source_ip
        #       - 出参：country, asn, is_malicious, threat_type, intel_source_url
        #       - 功能：查询IP在阿里云威胁情报中的风险评级
        #
        #     - ECS_exposure_analyzer
        #       - 入参：instance_id
        #       - 出参：public_ip, security_groups, exposed_ports, allow_anywhere_rules
        #       - 功能：分析ECS实例的公网暴露面和安全组风险配置
        #
        #     - CloudSecurityCenter_host_snapshot
        #       - 入参：instance_id, event_time_window
        #       - 出参：suspicious_processes, network_connections, file_hashes
        #       - 功能：获取云安全中心采集的主机进程与网络快照
        #
        #     - File_malware_scan
        #       - 入参：file_path 或 file_hash
        #       - 出参：is_malicious, malware_family, confidence_score
        #       - 功能：调用病毒引擎扫描文件
        #
        #     - VPC_flow_log_correlator
        #       - 入参：instance_id, start_time, end_time
        #       - 出参：internal_connections, target_ips, ports, protocols
        #       - 功能：分析VPC流日志中的内网横向行为
        #     """
        #
        #     prompt = f"""
        #     {FUNCTION.strip()}
        #
        #     目标受众：
        #     {AUDIENCE.strip()}
        #
        #     请按以下思维步骤（Chain-of-Thought）逐步推理：
        #     {STEPS.strip()}
        #
        #     输出必须严格遵循以下模板：
        #     {TEMPLATE.strip()}
        #
        #     强制规则：
        #     {MANDATORY_RULES.strip()}
        #
        #     约束条件：
        #     {CONSTRAINTS.strip()}
        #
        #     待建立的工具：
        #     {TO_BE_SETUP_TOOLS.strip()}
        #     """
        #
        #     return PromptMessage(
        #         role="assistant",
        #         content=TextContent(
        #             type="text",
        #             text=prompt
        #         )
        #     )
        #
        #



