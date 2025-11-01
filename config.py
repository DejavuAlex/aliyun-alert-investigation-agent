import json
from argparse import Namespace

import argcomplete
import configargparse
from pydantic import BaseModel, Field
from typing import Optional

from ext_argument_parser import ExtArgumentParser




# class ServerConfig(BaseModel):
#     host: str= "127.0.0.1"
#     port: int=8000
#     # llm_api_key:str = Field(..., min_length=1)
#     # model_name: str = "gpt-4o-2024-08-06"
#     access_key_id: str = Field(..., min_length=1)
#     access_key_secret: str = Field(..., min_length=1)
#     region_id: str = Field(..., min_length=1)

def check_config(parser,config) -> None:

    """ get llm config """
    # config.llm_config = json.loads(config.llm_config.replace("'", '"'))
    # if "api_key" not in config.llm_config:
    #     parser.error(
    #         f'--llm.api_key must be set'
    #     )
    #
    # if "model" not in  config.llm_config:
    #     parser.error(
    #         f'--llm.model must be set'
    #     )

    """ get alicloud configs """
    temp_configs = []
    if type(config.alicloud_configs) is not list:
        parser.error(f'--alicloud is a list')
    else:
        for iter_config in config.alicloud_configs:
            iter_config = json.loads(iter_config.replace("'", '"'))
            if "access_key_secret" not in iter_config:
                parser.error(
                    f'--alicloud.[].access_key_secret must be set'
                )
            if "region_id" not in iter_config:
                parser.error(
                    f'--alicloud.[].region_id must be set'
                )
            temp_configs.append(iter_config)
    config.alicloud_configs = temp_configs
    # get virustotal config
    if config.virustotal:
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
        default_config_files=['config/internal_config.yaml'],
    )
    parser.add_parser_args()
    argcomplete.autocomplete(parser)
    config = parser.parse_args(argv)
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