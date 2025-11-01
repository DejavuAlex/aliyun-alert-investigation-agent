import requests
from pydantic import Field

from mcp_servers.base_server import BaseServer


class VIRUSTOTAL_SERVER(BaseServer):
    def __init__(self, cmd_config):
        super().__init__(cmd_config, "virustotal_server", prefix="virustotal_server")
        self.api_key = cmd_config.virustotal_api_key
        self.setup_server()

    def setup_server(self):
        @self.mcp_instance.tool
        async def check_file_malicious(sha256_hash, malicious_threshold=5) -> dict:
            """
            根据SHA256哈希判断文件是否为恶意

            参数:
                sha256_hash (str): 文件的SHA256哈希值
                api_key (str): 你的VirusTotal API密钥
                malicious_threshold (int): 判断为恶意的阈值，默认5个引擎报毒即为恶意

            返回:
                dict: 包含判断结果和详细信息的字典
            """

            # VirusTotal v3 API 端点
            url = f'https://www.virustotal.com/api/v3/files/{sha256_hash}'
            headers = {
                'x-apikey': self.api_key
            }

            try:
                response = requests.get(url, headers=headers,**{"verify": False})

                # 处理免费API的速率限制 (每分钟4次请求)
                if response.status_code == 429:
                    return {"error": "API速率限制已达，请稍后再试。"}

                # 如果文件未找到
                if response.status_code == 404:
                    return {"error": "该哈希值在VirusTotal中不存在，可能是一个未知的新文件。"}

                # 如果请求成功
                if response.status_code == 200:
                    data = response.json()
                    attributes = data['data']['attributes']
                    stats = attributes['last_analysis_stats']

                    # 核心判断逻辑
                    malicious_count = stats['malicious']
                    suspicious_count = stats['suspicious']
                    total_engines = sum(stats.values())

                    # 组装结果
                    result = {
                        'sha256': sha256_hash,
                        'malicious_detections': malicious_count,
                        'suspicious_detections': suspicious_count,
                        'total_engines': total_engines,
                        'malicious_threshold': malicious_threshold,
                        'verdict': None,
                        'details': stats
                    }

                    # 做出判断
                    if malicious_count >= malicious_threshold:
                        result['verdict'] = " MALICIOUS"
                    elif malicious_count > 0 or suspicious_count > 0:
                        result['verdict'] = " SUSPICIOUS"
                    else:
                        result['verdict'] = " CLEAN"

                    return result
                else:
                    return {"error": f"VirusTotal API错误: {response.status_code}", "response_text": response.text}

            except requests.exceptions.RequestException as e:
                return {"error": f"网络请求失败: {str(e)}"}