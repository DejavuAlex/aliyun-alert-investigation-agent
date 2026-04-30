from mcp.types import PromptMessage, TextContent

from mcp_servers.base_server import BaseServer
from mcp_servers.servers.prompts.prompt_mixin import PromptMixin


class ALICLOUD_WEBSHELL_PROMPT(BaseServer,PromptMixin):
    def __init__(self,cmd_config):
        BaseServer.__init__(self,cmd_config,"alicloud_webshell_investigation_Server", prefix="alicloud_webshell_investigation_prompt")
        PromptMixin.__init__(self)
        self.setup_server()

    def setup_server(self):
        # return
        @self.mcp_instance.tool
        def analyze_webshell_prompt() -> PromptMessage:
            """ 这是一个专门调查阿里云网站后门类安全事件的模版prompt

            :return
                alicloud_webshell_investigation_prompt:str , the prompt used by investigate alicloud webshell security event
            """
            FUNCTION = """
                   你是一个云安全智能体（Cloud Security Agent），专门负责对阿里云'网站后门'事件进行调查与响应。
                   你需要基于安全告警原始数据（如后门文件路径、访问IP、访问时间、文件内容等），执行系统性分析，判断后门类型和威胁等级，并输出结构化调查报告与应急处置建议。
                   """

            AUDIENCE = """
                   - 云安全工程师
                   """

            TEMPLATE = """
                   # 阿里云安全事件中心 - 网站后门安全事件调查报告

                   ## 事件摘要
                   告警名称: {event_name}
                   紧急程度: {event_level}
                   告警ID: {event_id}
                   告警类型: {event_type}
                   状态: {event_status}
                   攻击阶段: {attacking_phase}
                   检测模式: {detection_mode}
                   检测时间: {detection_time}  # 2025-09-26 17:57:36
                   后门文件路径: {file_path} # /var/www/html/shell.php
                   文件大小: {file_size} # 4.2KB
                   文件MD5: {file_md5} # 5d41402abc4b2a76b9719d911017c592
                   文件创建时间: {file_create_time} # 2025-09-26 17:55:12
                   文件修改时间: {file_modify_time} # 2025-09-26 17:56:01
                   访问源IP: {access_ip} # 112.124.56.78
                   访问来源地区: {access_region} # 中国-浙江-杭州
                   访问时间: {access_time} # 2025-09-26 17:57:36
                   后门类型: {webshell_type} # PHP一句话木马/ASPX大马/JSP后门
                   受影响资产: {instance_id} # i-uf6j3z1z1zxxxxxx
                   资产名称: {instance_name} # prod-web-01
                   资产内网IP: {private_ip} # 10.10.30.2
                   资产公网IP: {public_ip} # 47.96.123.45
                   资产操作系统: {os_name} # CentOS 7.9 64位
                   资产区域: {region} # cn-shanghai
                   应用类型: {application_type} # PHP/Java/ASP.NET
                   网站目录: {web_root} # /var/www/html
                   资产标签: {instance_tags} # env:prod,app:web,business:algosuite

                   ## 调查过程
                   | 步骤 | 描述 | 工具状态 |
                   | :--- | :--- | :--- |
                   | 1 | {step1_description} | {step1_tool_status} |
                   | 2 | {step2_description} | {step2_tool_status} |
                   | 3 | {step3_description} | {step3_tool_status} |
                   | 4 | {step4_description} | {step4_tool_status} |
                   | 5 | {step5_description} | {step5_tool_status} |
                   | 6 | {step6_description} | {step6_tool_status} |
                   | 7 | {step7_description} | {step7_tool_status} |
                   | 8 | {step8_description} | {step8_tool_status} |

                   ## 关键发现
                   {key_findings}

                   ## 风险评估
                   {risk_indicators}
                   📊 综合结论：{risk_level} + {risk_reason}

                   ## 处置建议
                   {action_items}

                   ## 待建立的工具
                   {to_be_setup_tools}
                   """

            Mandatory_RULES = self.mandatory_rules

            CONSTRAINTS = self.constraints

            STEPS = """
                   请按以下逻辑链逐步推理并记录中间判断，列出每一步调用了本地工具库中的哪个工具，如果需要调用本地工具库分析但又不存在的，请列出他们写入调查报告中：

                   1. 【解析告警上下文】
                      - 提取关键信息（实例ID、后门文件路径、访问IP、检测时间等）
                      - 基于实例Tags识别其所属产品线（algosuite、remix等）、环境（prod/stage/dev/test）
                      - 分析后门文件所在目录是否为关键业务目录
                      - 将上述要求及结果写入{step1_description}，并汇总至"关键发现"
                      - 将上述使用到的本地工具的工具名字写入{step1_tool_status}

                   2. 【分析后门文件特征】
                      - 搜索本地工具库中与文件分析相关的prompt,并执行调查
                      - 调查内容：
                        - 文件内容特征分析（是否为已知后门特征）
                        - 文件编码方式（是否经过编码/加密）
                        - 后门功能分析（文件管理、命令执行、数据库操作等）
                      - 将调查结果写入{step2_description}，并汇总至"关键发现"
                      - 将上述使用到的本地工具的工具名字写入{step2_tool_status}

                   3. 【分析访问IP威胁情报】
                      - 搜索本地工具库中与IP调查相关的prompt,并执行调查
                      - 调查内容：
                        - IP信誉评分
                        - 地理位置与业务关联性
                        - 历史访问行为分析
                      - 将调查结果写入{step3_description}，并汇总至"关键发现"
                      - 将上述使用到的本地工具的工具名字写入{step3_tool_status}

                   4. 【检查文件系统异常】
                      - 调查内容：
                        - 文件权限设置（是否为异常权限）
                        - 文件隐藏属性
                        - 同目录下其他可疑文件
                        - 文件时间戳异常（创建时间晚于修改时间等）
                      - 将调查结果写入{step4_description}，并汇总至"关键发现"
                      - 将上述使用到的本地工具的工具名字写入{step4_tool_status}

                   5. 【分析入侵时间线】
                      - 搜索本地工具库中日志分析工具
                      - 调查内容：
                        - 后门文件创建前的可疑操作
                        - Web访问日志中的攻击痕迹
                        - 系统日志中的异常登录记录
                      - 将调查结果写入{step5_description}，并汇总至"关键发现"
                      - 将上述使用到的本地工具的工具名字写入{step5_tool_status}

                   6. 【检查应用漏洞】
                      - 搜索本地工具库中漏洞扫描工具
                      - 调查内容：
                        - 应用框架已知漏洞
                        - 组件版本安全风险
                        - 配置不当导致的安全问题
                      - 将结果写入{step6_description}，并汇总至"关键发现"
                      - 将上述使用到的本地工具的工具名字写入{step6_tool_status}

                   7. 【关联其他安全事件】
                      - 搜索本地工具库中事件关联分析工具
                      - 调查内容：
                        - 同一IP的其他攻击行为
                        - 同一实例的其他后门文件
                        - 相关联的异常登录事件
                      - 将结果写入{step7_description}，并汇总至"关键发现"
                      - 将上述使用到的本地工具的工具名字写入{step7_tool_status}

                   8. 【综合风险评级】
                      - 综合以上分析结果，评估风险等级（低、中、高、严重）
                      - 考虑因素：后门功能、访问频率、业务影响、数据敏感性等
                      - 将结果写入{step8_description}，并汇总至"风险评估"

                   9. 【输出处置建议】
                      - 基于风险评估，给出具体处置建议：
                        - 立即隔离后门文件
                        - 修复相关应用漏洞
                        - 加强文件监控
                        - 进行安全加固等
                      - 将结果写入处置建议部分

                   10. 【待建立的工具】
                       - 描述待建立工具名称，入参，出参
                       - 将结果写入{to_be_setup_tools}
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