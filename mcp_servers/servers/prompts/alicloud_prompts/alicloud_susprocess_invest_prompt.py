from mcp.types import PromptMessage, TextContent

from mcp_servers.base_server import BaseServer
from mcp_servers.servers.prompts.prompt_mixin import PromptMixin


class ALICLOUD_WEBSHELL_PROMPT(BaseServer,PromptMixin):
    def __init__(self,cmd_config):
        BaseServer.__init__(self,cmd_config,"alicloud_susprocess_invest_Server", prefix="alicloud_susprocess_invest_prompt")
        PromptMixin.__init__(self)
        self.setup_server()

    def setup_server(self):
        # return
        @self.mcp_instance.tool
        def analyze_susprocess_prompt() -> PromptMessage:
            """ 这是一个专门调查阿里云进程异常行为类安全事件的模版prompt

            :return
                alicloud_malicious_process_investigation_prompt:str , the prompt used by investigate alicloud malicious process security event
            """
            FUNCTION = """
                   你是一个云安全智能体（Cloud Security Agent），专门负责对阿里云'进程异常行为'事件进行调查与响应。
                   你需要基于安全告警原始数据（如异常登录、可疑进程名称、进程PID、可疑执行路径、关联用户、启动命令行、网络连接、父子进程链、文件哈希、行为特征、安全组关键配、横向移动风险等），执行系统性分析，判断该恶意进程的威胁性质、传播范围与风险等级，并输出结构化调查报告与应急处置建议。
                   你的目标包括但不限于：
                     - 确定恶意进程性质、来源、传播链条
                     - 分析是否存在横向移动行为及影响范围
                     - 分析同一实例内其他相关告警之间的关联关系
                     - 评估资产风险等级
                     - 输出结构化调查报告、可量化风险评估和完整处置建议集
                   """

            AUDIENCE = """
                   - 云安全工程师
                   """
            
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

            **🔹 横向移动与扩散分析**
            - 🔁 横向移动迹象: {lateral_movement_signs}
            - 🖧 内网扫描行为: {internal_scan_behavior}
            - 🔑 凭证访问/窃取: {credential_access_behavior}
            - 🧭 资产访问扩散路径: {lateral_movement_path}
            - 📡 关联受影响资产: {related_instances}

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

            ---

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

            **7️⃣ 步骤7：攻击链重建 + 横向移动分析**
            - 📝 分析描述: {step7_description}
            - 🛠️ 使用工具: {step7_tool_status}
            - 🔍 关键发现: {step7_findings}

            **8️⃣ 步骤8：综合风险评估**
            - 📝 分析描述: {step8_description}

            **9️⃣ 步骤9：应急处置建议**
            - 📝 分析描述: {step9_description}

            **🔟 步骤10：改进措施识别**
            - 📝 分析描述: {step10_description}

            ---

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
              - 分析异常进程的业务上下文，是否与业务逻辑、部署阶段、发布窗口冲突
              - 判断进程是否属于基线白名单进程
              - 分析启动来源：systemd / cron / k8s / 用户手动 / exploit chain
              - 将分析结果写入：{step1_description}

            2. 步骤2：进程行为深度分析
              - 重点分析是否存在：反弹 shell、挖矿计算、加壳通信、C2 心跳特征
              - 检查进程是否进行内存注入、DLL注入、LD_PRELOAD 劫持等行为
              - 判断是否存在进程伪装（例如伪装成 sshd、kubelet、systemd）
              - 将分析结果写入：{step2_description}

            3. 步骤3：威胁情报关联分析
              - 基于进程哈希、网络目的IP、命令参数进行多IOC交叉匹配
              - 引用企业本地情报库及第三方情报结果综合评估
              - 输出威胁置信等级：高/中/低
              - 将分析结果写入：{step3_description}

            4. 步骤4：安全暴露面评估
              - 分析实例是否开放异常端口供该进程使用
              - 检查是否有 SSH 暴露、Docker API 暴露、K8s API 未授权风险
              - 将分析结果写入：{step4_description}

            5. 步骤5：异常活动调查
              - 排查该进程是否触发异常账号行为：新建账户、提权、sudo 执行
              - 审查是否有文件批量修改或清除日志行为
              - 判断是否有持久化机制：Systemd 服务、自启动脚本、cron任务
              - 将分析结果写入：{step5_description}

            6. 步骤6：关联事件分析（实例&账号级）
              - 查询该实例在相同时间窗口：
                - 是否存在其他恶意进程相关告警
                - 是否存在 WebShell、暴力破解、提权、异常登录等相关告警
              - 查询该账号在其他资产上的异常行为
              - 形成时间关联和行为关联矩阵
              - 将分析结果写入：{step6_description}

            7. 步骤7：攻击链重建 + 横向移动分析
              - 分析是否存在横向移动迹象：
                - SSH横向登录
                - SMB/RDP/WMI连接
                - 内网端口扫描
              - 判断是否存在凭证获取行为（读取 /etc/shadow、LSASS 访问等）
              - 输出横向扩散路径图：起始资产 → 目标资产
              - 将分析结果写入：{step7_description}

            8. 步骤8：综合风险评估
              - 综合考虑是否存在横向扩散、数据窃取、持久化能力
              - 若存在横向行为，风险至少提升一个等级
              - 将分析结果写入：{step8_description}

            9. 步骤9：应急处置建议
              - 必须给出分级处置：
                - 立即处置（隔离进程/封禁IP）
                - 短期处置（修复漏洞/重置凭证）
                - 长期处置（加固基线/优化检测）
              - 提供应急命令与回滚预案
              - 将结果写入：{step9_description}

            10. 步骤10：改进措施识别
                - 输出未来防御重点：横向移动检测、异常进程行为检测、凭证保护
                - 建议新增检测规则与工具：
                  - 内网扫描检测
                  - 异常进程行为规则
                  - 跨资产异常登录关联分析
                - 将结果写入：{step10_description} 与 {to_be_setup_tools}

            【关键执行要求】
            1. 强制评估是否存在横向移动行为
            2. 强制分析该实例关联的其他告警
            3. 所有结论需来源于日志、告警、进程数据或取证信息，不允许凭空结论
            4. 输出语言统一使用专业安全事件响应表述
            """


            # TEMPLATE = """
            #        # 阿里云安全事件中心 - 进程异常行为安全事件调查报告

            #        ## 事件摘要
            #        告警名称: {event_name}
            #        紧急程度: {event_level}
            #        告警ID: {event_id}
            #        告警类型: {event_type}
            #        状态: {event_status}
            #        攻击阶段: {attacking_phase}
            #        检测模式: {detection_mode}
            #        检测时间: {detection_time}  # 2025-09-26 17:57:36

            #        可疑进程名称: {process_name}  # kdevtmpfsi
            #        进程PID: {process_pid} # 2345
            #        父进程: {parent_process} # /usr/sbin/cron
            #        可疑执行路径: {process_path} # /tmp/kdevtmpfsi
            #        执行用户: {process_user} # nobody
            #        进程启动命令行: {process_cmdline} # /tmp/kdevtmpfsi -k start
            #        进程MD5: {process_md5} # 9e107d9d372bb6826bd81d3542a419d6
            #        CPU占用: {cpu_usage} # 96%
            #        内存占用: {memory_usage} # 450MB
            #        建立外联IP: {remote_ip} # 179.43.13.58
            #        外联端口: {remote_port} # 443
            #        通信协议: {protocol} # TLS
            #        首次发现时间: {first_seen_time} # 2025-09-26 17:55:12
            #        最近活动时间: {last_activity_time} # 2025-09-26 17:56:01

            #        受影响资产: {instance_id} # i-uf6j3z1z1zxxxxxx
            #        资产名称: {instance_name} # prod-web-01
            #        资产内网IP: {private_ip} # 10.10.30.2
            #        资产公网IP: {public_ip} # 47.96.123.45
            #        资产操作系统: {os_name} # CentOS 7.9 64位
            #        资产区域: {region} # cn-shanghai
            #        应用类型: {application_type} # JAVA/PHP/Node.js
            #        资产标签: {instance_tags} # env:prod,app:web,business:algosuite

            #        ## 调查过程
            #        | 步骤 | 描述 | 工具状态 |
            #        | :--- | :--- | :--- |
            #        | 1 | {step1_description} | {step1_tool_status} |
            #        | 2 | {step2_description} | {step2_tool_status} |
            #        | 3 | {step3_description} | {step3_tool_status} |
            #        | 4 | {step4_description} | {step4_tool_status} |
            #        | 5 | {step5_description} | {step5_tool_status} |
            #        | 6 | {step6_description} | {step6_tool_status} |
            #        | 7 | {step7_description} | {step7_tool_status} |
            #        | 8 | {step8_description} | {step8_tool_status} |
            #        | 9 | {step9_description} | {step9_tool_status} |

            #        ## 关键发现
            #        {key_findings}

            #        ## 相关告警
            #        {related_alerts}

            #        ## 风险评估
            #        {risk_indicators}
            #        📊 综合结论：{risk_level} + {risk_reason}

            #        ## 处置建议
            #        {action_items}

            #        ## 待建立的工具
            #        {to_be_setup_tools}
            #        """

            # Mandatory_RULES = self.mandatory_rules

            # CONSTRAINTS = self.constraints

            # STEPS = """
            #        请按以下逻辑链逐步推理并记录中间判断，列出每一步调用了本地工具库中的哪个工具，如果需要调用本地工具库分析但又不存在的，请列出他们写入调查报告中：

            #        1. 【解析告警上下文】
            #           - 提取关键信息（进程名称、PID、执行路径、执行用户、外联行为、安全组关键配置、异常登录行为CPU/内存使用率等）
            #           - 基于实例Tags识别其所属产品线（algosuite、remix等）、环境（prod/stage/dev/test）
            #           - 判断该进程是否运行在关键业务节点、业务核心容器或关键服务组件中
            #           - 分析启动命令行是否含混淆参数、可疑路径（/tmp、/dev/shm 等）
            #           - 将上述要求及结果写入{step1_description}，并汇总至"关键发现"
            #           - 将上述使用到的本地工具名字写入{step1_tool_status}

            #        2. 【分析可疑进程特征】
            #           - 搜索本地工具库中与进程分析相关的prompt并执行调查
            #           - 调查内容：
            #             - 是否属于已知恶意家族（挖矿木马/XMRig/LuaBot/DDOS Agent/后门Shell）
            #             - 进程指纹比对（哈希、路径、命令行）
            #             - 行为分析（文件读写、socket创建、定时任务注入、ptrace行为等）
            #             - 异常资源占用（高CPU、高磁盘IO）
            #           - 将调查结果写入{step2_description}，并汇总至"关键发现"
            #           - 将使用的本地工具写入{step2_tool_status}

            #        3. 【分析网络通信与外联IP威胁情报】
            #           - 查询外联IP信誉、C2情报、是否为矿池地址、TOR节点等
            #           - 分析通信行为：
            #             - 是否具有心跳包特征
            #             - 是否存在横向扫描（批量连接内网端口）
            #             - 是否尝试SSH/Redis/MongoDB爆破
            #           - 记录至{step3_description}并汇总至"关键发现"
            #           - 工具写入{step3_tool_status}

            #        4. 【检查进程关联文件系统行为】
            #           - 调查内容：
            #             - 进程是否写入可疑文件（隐藏文件、加密文件、计划任务、SSH Key）
            #             - 关联可疑落地文件（/tmp、/var/tmp、/dev/shm等）
            #             - ELF文件头特征分析（strip、无符号表、异常节段）
            #             - 时间戳异常（可执行文件创建时间与启动时间不一致）
            #           - 写入{step4_description}并汇总至"关键发现"
            #           - 工具写入{step4_tool_status}

            #        5. 【分析入侵时间线】
            #           - 基于Audit日志/Systemd日志/Web日志/SSH日志提取:
            #             - 进程运行前的可疑命令（curl|wget 下载脚本、base64 解码payload）
            #             - 可疑账号异常登录行为（爆破/异常来源IP）
            #             - 漏洞利用痕迹（命令注入、RCE、弱口令利用）
            #             - 是否有可疑SSH登录、Webshell调用、弱密码攻击
            #             - 是否存在多阶段攻击链（初始入侵 → 下载器 → 落地文件 → 恶意进程 → 横向移动）
            #           - 将结果写入{step5_description}并汇总至"关键发现"
            #           - 工具写入{step5_tool_status}

            #        6. 【检查系统与应用漏洞】
            #           - 搜索本地漏洞扫描工具
            #           - 调查内容：
            #             - Tomcat/Confluence/ThinkPHP/Struts2/Log4j2 等漏洞
            #             - Redis/MongoDB/Elasticsearch 等中间件未授权访问
            #             - 系统弱密码、暴露SSH端口、开放危险端口
            #           - 写入{step6_description}并汇总至"关键发现"
            #           - 工具写入{step6_tool_status}
         
            #        7. 【横向移动与扩散调查】
            #           - 分析SSH爆破、端口扫描、内网连接行为
            #           - 分析是否传播至其他资产
            #           - 写入{step7_description}并汇总至"关键发现"
            #           - 工具写入{step7_tool_status}

            #        8. 【分析该实例的其他相关告警】
            #           - 搜索该实例在同一时间窗口触发的其他告警，如：
            #             - 异常登录告警
            #             - 高频SSH尝试
            #             - Webshell触发
            #             - 异常文件创建
            #             - 异常网络连接
            #             - 内网端口扫描（22、6379、3306、9200等）
            #           - 分析告警之间是否构成完整攻击链（如：漏洞利用 → 文件落地 → 恶意进程 → 横向移动）
            #           - 判断哪些告警是当前恶意进程的前置阶段、并发阶段、后置阶段
            #           - 识别是否存在“多点协同攻击”或复合攻击
            #           - 提取相关告警并加入“相关告警”
            #           - 写入{step8_description}并汇总至"关键发现"
            #           - 将使用到的工具写入{step8_tool_status}

            #        9. 【综合风险评级】
            #           - 基于以上分析评估风险等级（低/中/高/严重）
            #           - 评估因素：
            #             - 是否为已知恶意家族
            #             - 是否具备横向移动能力
            #             - 是否存在C2通信
            #             - 是否占用大量系统资源影响业务
            #             - 是否建立持久化机制
            #           - 写入{step9_description}并汇总至"风险评估"

            #        10. 【输出处置建议】
            #           - 提供基于攻击链的全流程处置建议，包括但不限于：
            #             **立即处置：**
            #             - 立刻终止恶意进程并隔离对应二进制文件
            #             - 禁止对外恶意通信（封禁恶意IP、限制内网扫描）
            #             - 封禁攻击源IP，开启严格访问控制
            #             **根因修复：**
            #             - 修补漏洞、升级中间件、关闭未授权服务
            #             - 修复弱密码、替换并收敛密钥、轮转高危账号
            #             **横向移动防护：**
            #             - 审计所有SSH登录，撤销可疑公钥
            #             - 排查内网其他资产的恶意进程/脚本落地情况
            #             - 启动局部或全网资产基线检查
            #             **持久化清除：**
            #             - 移除crontab/systemd/rc.local中的恶意自启项
            #             - 清理可疑文件与目录（/tmp、/dev/shm、隐藏文件）
            #             **长期加固：**
            #             - 部署主机防护（EDR/HIDS）
            #             - 强化最小权限策略
            #             - 启用SELinux/AppArmor
            #             - 开启文件完整性监控（FIM）
            #           - 写入“处置建议”部分

            #        11. 【待建立的工具】
            #            - 描述需要新增的工具名称、入参、出参，例如：
            #              - 横向移动检测引擎（入参：SSH日志、端口连接；出参：横向路径图）
            #              - ELF 恶意评分工具
            #              - 系统调用行为画像工具（入参：进程PID；出参：行为分类与评分）
            #            - 写入{to_be_setup_tools}
            #        """

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