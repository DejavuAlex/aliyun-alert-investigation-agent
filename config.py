import json
import os
from argparse import Namespace

import argcomplete
import configargparse

from ext_argument_parser import ExtArgumentParser
logger = None

def check_config(parser,config) -> None:
    # set logger level
    if config.log_level:
        os.environ["LOG_LEVEL"] = config.log_level
        print("set log level to:", config.log_level)
    from log_config import get_logger
    global logger
    logger = get_logger(__name__)
    """ get alicloud configs """
    temp_configs = []
    # Accept either a JSON string list or list of JSON fragments (legacy)
    if isinstance(config.alicloud_configs, str):
        try:
            parsed = json.loads(config.alicloud_configs)
        except Exception as e:
            parser.error(f'--alicloud malformed JSON list: {e}')
        if not isinstance(parsed, list):
            parser.error(f'--alicloud must be a JSON list')
        source_list = parsed
    elif isinstance(config.alicloud_configs, list):
        source_list = []
        for s in config.alicloud_configs:
            source_list.append(json.loads(s.replace("'", '"')))
    else:
        parser.error(f'--alicloud must be a JSON list string')
        source_list = []
    for iter_config in source_list:
        if "access_key_secret" not in iter_config:
            parser.error(f'--alicloud.[].access_key_secret must be set')
        if "region_id" not in iter_config:
            parser.error(f'--alicloud.[].region_id must be set')
        temp_configs.append(iter_config)
    config.alicloud_configs = temp_configs
    logger.debug("set alicloud account configs: %s", config.alicloud_configs)
    # get virustotal config
    if config.virustotal:
        if isinstance(config.virustotal, str):
            config.virustotal = json.loads(config.virustotal.replace("'", '"'))
        if "api_key" not in config.virustotal:
            parser.error(
                f'--virustotal.api_key must be set'
            )
        else:
            config.virustotal_api_key = config.virustotal["api_key"]
    else:
        parser.error("--virustotal must be set")

    if "host" not in config:
        parser.error(
            f'--host must be set'
        )

    if "port" not in config:
        parser.error(
            f'--port must be set'
        )

    if isinstance(config.jihulab, str):
        config.jihulab = json.loads(config.jihulab.replace("'", '"'))
    if "token" not in config.jihulab:
        parser.error(
            f'--jihulab.token must be set'
        )
    if "url" not in config.jihulab:
        parser.error(
            f'--jihulab.url must be set'
        )
    if "roche_parent_group" not in config.jihulab:
        parser.error(
            f'--jihulab.roche_parent_group must be set'
        )


def parse_cmd_config(argv: list[str]) -> Namespace:
    parser = ExtArgumentParser(
        description="Security MCP server",
        add_env_var_help=True,
        config_file_parser_class=configargparse.YAMLConfigFileParser,
        # 命令行优先级还是大于文件，所以文件里面的定义会被命令行覆盖，而在生产环境，命令行又是通过env变量注入的，这里主要是为了本地调试用
        default_config_files = [
            os.path.join(os.getcwd(), "config/internal_config.yaml"),

        ],
    )
    parser.add_parser_args()
    argcomplete.autocomplete(parser)
    config = parser.parse_args(argv)
    # Optional fallback: if K8S mounted secret file path provided
    # secret_file = os.environ.get("K8S_SECRET_CONFIG_FILE")
    # if secret_file and os.path.isfile(secret_file):
    #     with open(secret_file, "r", encoding="utf-8") as f:
    #         data = json.loads(f.read())
    #     # Merge only missing attributes
    #     if not getattr(config, "alicloud_configs", None) and "alicloud" in data:
    #         config.alicloud_configs = json.dumps(data["alicloud"])
    #     if not getattr(config, "jihulab", None) and "jihulab" in data:
    #         config.jihulab = json.dumps(data["jihulab"])
    #     if not getattr(config, "virustotal", None) and "virustotal" in data:
    #         config.virustotal = json.dumps(data["virustotal"])
    #     if not getattr(config, "host", None) and "host" in data:
    #         config.host = data["host"]
    #     if not getattr(config, "port", None) and "port" in data:
    #         config.port = data["port"]
    check_config(parser,config)
    return config

# def load_cmd_config(argv: list[str]) -> configargparse.Namespace:
#     cmd_config = parse_cmd_config(argv)
#     return cmd_config
    # return ServerConfig(
    #     # llm_api_key=cmd_config.llm_config["api_key"],
    #     # model_name=cmd_config.llm_config["model"],
    #     access_key_id=cmd_config.alicloud_config["access_key_id"],
    #     access_key_secret=cmd_config.alicloud_config["access_key_secret"],
    #     region_id=cmd_config.alicloud_config["region_id"],
    # )