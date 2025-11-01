import argparse
from typing import Any,cast,TYPE_CHECKING,List
from io import StringIO
import configargparse

OUTPUT_CHOICES = [
    "cli",
    "csv",
    "cyclonedx",
    "cyclonedx_json",
    "json",
    "junitxml",
    "github_failed_only",
    "gitlab_sast",
    "sarif",
    "spdx",
]
SCAN_TYPE_CHOICE= [
    "sourcecode_scan",
    "iac_scan",
    "dependency_scan",
    "image_scan",
    "credential_scan",
    "AI_scan"
]
PACKAGE_TYPE_CHOICE = [
    "yarn",
    "npm",
    "gradle",
    "mvn",
    "nuget",
    "pip"
]
class ExtArgumentParser(configargparse.ArgumentParser):
    def __init__(self, *args:Any, **kwargs:Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields_to_sanitize: set[Any] = set()

    def add(self, *args: Any, **kwargs: Any) -> None:
        if kwargs.pop("sanitize", False):
            self.fields_to_sanitize.add(args[0])
        super().add(*args, **kwargs)


    def add_parser_args(self) -> None:

        self.add(
            "--log_level",
            env_var="LOG_LEVEL",
            help="MCP server log level",
            dest="log_level",
        )
        self.add(
            "--llm",
            help="LLM config, get from internal config file by default",
            dest="llm_config",
        )

        self.add(
            "--alicloud",
            help="Ali Cloud access key & secret",
            nargs="+",
            dest="alicloud_configs",
        )
        self.add(
            "--mcp_debug",
            help="MCP server debug mode",
            action="store_true",
        )
        self.add(
            "--host",
            env_var="HOST",
            help="MCP server host",
            dest="host",
        )
        self.add(
            "--port",
            env_var="PORT",
            type=int,
            help="MCP server port",
            dest="port",
        )
        self.add(
            "--jihulab",
            help="Jihu lab config",
            dest="jihulab",
        )
        self.add(
            "--virustotal",
            help="VirusTotal invetigate the file or urls, here config the apikey",
            dest="virustotal",

        )





    def format_values(self, sanitize: bool = False) -> str:
        if not sanitize:
            return cast(str, super().format_values())

        source_key_to_display_value_map = {
            configargparse._COMMAND_LINE_SOURCE_KEY: "Command Line Args: ",
            configargparse._ENV_VAR_SOURCE_KEY: "Environment Variables:\n",
            configargparse._CONFIG_FILE_SOURCE_KEY: "Config File (%s):\n",
            configargparse._DEFAULTS_SOURCE_KEY: "Defaults:\n",
        }

        r = StringIO()
        for source, settings in self._source_to_settings.items():
            source = source.split("|")
            source = source_key_to_display_value_map[source[0]] % tuple(source[1:])
            r.write(source)
            for key, (action, value) in settings.items():
                if key:
                    if key in self.fields_to_sanitize or action.option_strings[0] in self.fields_to_sanitize:
                        value = "****"
                    r.write("  {:<19}{}\n".format(key + ":", value))
                else:
                    if isinstance(value, str):
                        r.write("  %s\n" % value)
                    elif isinstance(value, list):
                        value = list(value)  # copy
                        if source == "Command Line Args: ":
                            index = 0
                            while index < len(value):
                                if value[index] in self.fields_to_sanitize:
                                    index += 1
                                    value[index] = "****"
                                index += 1
                        r.write("  %s\n" % " ".join(value))

        return r.getvalue()

