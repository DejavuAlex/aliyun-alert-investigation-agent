import requests
import json

from mcp_servers.base_server import BaseServer
from fastmcp.utilities import logging
from cloudflare import Cloudflare
logger = logging.get_logger(__name__)

class CLOUDFLLARE_SERVER(BaseServer):
    def __init__(self, cmd_config):
        super().__init__(cmd_config, "cloudflare_server", prefix="cloudflare_server")
        if cmd_config.cloudflare:
            if isinstance(cmd_config.cloudflare, str):
                cmd_config.cloudflare = json.loads(cmd_config.cloudflare.replace("'", '"'))
            if "api_token" not in cmd_config.cloudflare:
                raise RuntimeError("api_token not found in cloudflare")
        else:
            raise RuntimeError("cloudflare config not found")
        self.api_token = self.cmd_config.cloudflare["api_token"]
        self.client = Cloudflare(
            api_token=self.api_token
        )
        self.setup_server()


    def setup_server(self):

        """

        {
          "errors": [
            {
              "code": 1000,
              "message": "message",
              "documentation_url": "documentation_url",
              "source": {
                "pointer": "pointer"
              }
            }
          ],
          "messages": [
            {
              "code": 1000,
              "message": "message",
              "documentation_url": "documentation_url",
              "source": {
                "pointer": "pointer"
              }
            }
          ],
          "success": true,
          "result": [
            {
              "id": "023e105f4ecef8ad9ca31a8372d0c353",
              "account": {
                "id": "023e105f4ecef8ad9ca31a8372d0c353",
                "name": "Example Account Name"
              },
              "activated_on": "2014-01-02T00:01:00.12345Z",
              "created_on": "2014-01-01T05:20:00.12345Z",
              "development_mode": 7200,
              "meta": {
                "cdn_only": true,
                "custom_certificate_quota": 1,
                "dns_only": true,
                "foundation_dns": true,
                "page_rule_quota": 100,
                "phishing_detected": false,
                "step": 2
              },
              "modified_on": "2014-01-01T05:20:00.12345Z",
              "name": "example.com",
              "name_servers": [
                "bob.ns.cloudflare.com",
                "lola.ns.cloudflare.com"
              ],
              "original_dnshost": "NameCheap",
              "original_name_servers": [
                "ns1.originaldnshost.com",
                "ns2.originaldnshost.com"
              ],
              "original_registrar": "GoDaddy",
              "owner": {
                "id": "023e105f4ecef8ad9ca31a8372d0c353",
                "name": "Example Org",
                "type": "organization"
              },
              "plan": {
                "id": "023e105f4ecef8ad9ca31a8372d0c353",
                "can_subscribe": false,
                "currency": "USD",
                "externally_managed": false,
                "frequency": "monthly",
                "is_subscribed": false,
                "legacy_discount": false,
                "legacy_id": "free",
                "name": "Example Org",
                "price": 10.99
              },
              "cname_suffix": "cdn.cloudflare.com",
              "paused": true,
              "permissions": [
                "#worker:read"
              ],
              "status": "active",
              "tenant": {
                "id": "023e105f4ecef8ad9ca31a8372d0c353",
                "name": "Example Account Name"
              },
              "tenant_unit": {
                "id": "023e105f4ecef8ad9ca31a8372d0c353"
              },
              "type": "full",
              "vanity_name_servers": [
                "ns1.example.com",
                "ns2.example.com"
              ],
              "verification_key": "284344499-1084221259"
        }
        :return:
        """
        @self.mcp_instance.tool
        def get_all_zones():
            """
            获取所有Cloudflare zones
            Returns:
                list:
                [
                    {
                        "zone_id": "zone_id_value",
                        "account_id": {
                            "id":"account_id_value",
                            "name":"account_name_value"
                            }
                    },
                    ...

                ]

            """
            page = self.client.zones.list()
            return  [ {"zone_id":result.id,"account":result.account} for result in page.result]

        """
        {
  "errors": [
    {
      "code": 1000,
      "message": "message",
      "documentation_url": "documentation_url",
      "source": {
        "pointer": "pointer"
      }
    }
  ],
  "messages": [
    {
      "code": 1000,
      "message": "message",
      "documentation_url": "documentation_url",
      "source": {
        "pointer": "pointer"
      }
    }
  ],
  "success": true,
  "result": [
    {
      "name": "example.com",
      "ttl": 3600,
      "type": "A",
      "comment": "Domain verification record",
      "content": "198.51.100.4",
      "proxied": true,
      "settings": {
        "ipv4_only": true,
        "ipv6_only": true
      },
      "tags": [
        "owner:dns-team"
      ],
      "id": "023e105f4ecef8ad9ca31a8372d0c353",
      "created_on": "2014-01-01T05:20:00.12345Z",
      "meta": {},
      "modified_on": "2014-01-01T05:20:00.12345Z",
      "proxiable": true,
      "comment_modified_on": "2024-01-01T05:20:00.12345Z",
      "tags_modified_on": "2025-01-01T05:20:00.12345Z"
    }
  ],
  "result_info": {
    "count": 1,
    "page": 1,
    "per_page": 20,
    "total_count": 2000
  }
}
        """
        @self.mcp_instance.tool
        def get_dns_records(zone_id: str):
            """
            获取指定zone的DNS记录,返回dns record naem, record ip, proxied status,type, whether record ip is Internet ip or not
            Args:
                zone_id (str): Cloudflare Zone ID
            Returns:
                list:
                [
                    {
                        "id": "record_id_value",
                        "name": "record_name_value",
                        "type": "A",
                        "content": "record_content_value",
                        "proxied": true,
                        "is_internet_accessible": true
                    },
                    ...
                ]



            """
            import ipaddress
            def is_public_ip(ip: str) -> bool:
                try:
                    ip_obj = ipaddress.ip_address(ip)
                    return not (ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved or ip_obj.is_multicast)
                except ValueError:
                    return False



            page = self.client.dns.records.list(zone_id=zone_id)
            dns_records = []
            for record in page.result:
                record_type = record.type
                if record_type in ["A", "AAAA"]:
                    return is_public_ip(record.content)
                elif record_type == "CNAME":
                    try:
                        import dns.resolver
                        answers = dns.resolver.resolve(record.content, 'A')
                        for rdata in answers:
                            if is_public_ip(rdata.address):
                                return True
                        return False
                    except Exception as e:
                        logger.error("DNS resolution error for CNAME %s: %s", record.content, str(e))
                        return False

                dns_records.append({
                    "id": record.id,
                    "name": record.name,
                    "type": record.type,
                    "content": record.content,
                    "proxied": record.proxied,
                    "is_internet_accessible": is_public_ip(record.content) if record.type in ["A", "AAAA","CNAME"] else None
                })
            return dns_records

        # """
        # {
        #   "errors": [
        #     {
        #       "message": "something bad happened",
        #       "code": 10000,
        #       "source": {
        #         "pointer": "/rules/0/action"
        #       }
        #     }
        #   ],
        #   "messages": [
        #     {
        #       "message": "something bad happened",
        #       "code": 10000,
        #       "source": {
        #         "pointer": "/rules/0/action"
        #       }
        #     }
        #   ],
        #   "result": [
        #     {
        #       "id": "2f2feab2026849078ba485f918791bdc",
        #       "kind": "root",
        #       "last_updated": "2000-01-01T00:00:00.000000Z",
        #       "name": "My ruleset",
        #       "phase": "http_request_firewall_custom",
        #       "version": "1",
        #       "description": "A description for my ruleset."
        #     }
        #   ],
        #   "success": true,
        #   "result_info": {
        #     "cursors": {
        #       "after": "dGhpc2lzYW5leGFtcGxlCg"
        #     }
        #   }
        # }
        # """
        # @self.mcp_instance.tool
        # def list_account_rulesets(account_id: str):
        #     """
        #     列出指定account的所有rulesets
        #     Args:
        #         account_id (str): Cloudflare Account ID
        #     Returns:
        #         list:
        #         [
        #             {
        #                 "id": "ruleset_id_value",
        #                 "kind": "root",
        #                 "name": "ruleset_name_value",
        #                 "phase": "http_request_firewall_custom",
        #                 "version": "1",
        #                 "description": "ruleset_description_value"
        #             },
        #             ...
        #         ]
        #     """
        #     page = self.client.rulesets.list(account_id=account_id)
        #     return [ {"id":result.id,
        #               "kind":result.kind,
        #               "name":result.name,
        #               "phase":result.phase,
        #               "version":result.version,
        #               "description":result.description
        #               } for result in page.result]

#         """
#         {
#   "errors": [
#     {
#       "message": "something bad happened",
#       "code": 10000,
#       "source": {
#         "pointer": "/rules/0/action"
#       }
#     }
#   ],
#   "messages": [
#     {
#       "message": "something bad happened",
#       "code": 10000,
#       "source": {
#         "pointer": "/rules/0/action"
#       }
#     }
#   ],
#   "result": {
#     "id": "2f2feab2026849078ba485f918791bdc",
#     "kind": "root",
#     "last_updated": "2000-01-01T00:00:00.000000Z",
#     "name": "My ruleset",
#     "phase": "http_request_firewall_custom",
#     "rules": [
#       {
#         "last_updated": "2000-01-01T00:00:00.000000Z",
#         "version": "1",
#         "id": "3a03d665bac047339bb530ecb439a90d",
#         "action": "block",
#         "action_parameters": {
#           "response": {
#             "content": "{\n  \"success\": false,\n  \"error\": \"you have been blocked\"\n}",
#             "content_type": "application/json",
#             "status_code": 400
#           }
#         },
#         "categories": [
#           "directory-traversal"
#         ],
#         "description": "Block the request.",
#         "enabled": true,
#         "exposed_credential_check": {
#           "password_expression": "url_decode(http.request.body.form[\\\"password\\\"][0])",
#           "username_expression": "url_decode(http.request.body.form[\\\"username\\\"][0])"
#         },
#         "expression": "ip.src eq 1.1.1.1",
#         "logging": {
#           "enabled": true
#         },
#         "ratelimit": {
#           "characteristics": [
#             "cf.colo.id"
#           ],
#           "period": 60,
#           "counting_expression": "http.request.body.raw eq \"abcd\"",
#           "mitigation_timeout": 600,
#           "requests_per_period": 1000,
#           "requests_to_origin": true,
#           "score_per_period": 400,
#           "score_response_header_name": "my-score"
#         },
#         "ref": "my_ref"
#       }
#     ],
#     "version": "1",
#     "description": "A description for my ruleset."
#   },
#   "success": true
# }
#         """
#         @self.mcp_instance.tool
#         def list_rules_from_account_rulesets(account_id: str, ruleset_id: str):
#             """
#             获取指定account的指定ruleset的详细信息
#             Args:
#                 account_id (str): Cloudflare Account ID
#                 ruleset_id (str): Cloudflare Ruleset ID
#             Returns:
#                 dict:
#                 {
#                     "id": "ruleset_id_value",
#                     "kind": "root",
#                     "name": "ruleset_name_value",
#                     "phase": "http_request_firewall_custom",
#                     "version": "1",
#                     "description": "ruleset_description_value",
#                     "rules": [
#                         {
#                             "id": "rule_id_value",
#                             "action": "block",
#                             "expression": "ip.src eq
#                             ...",
#                             ...
#                         },
#                         ...
#                     ]
#                 }
#             """
#             result = self.client.rulesets.get(account_id=account_id, ruleset_id=ruleset_id)
#             rules = []
#             for rule in result.rules:
#                 rules.append({
#                     "id": rule.id,
#                     "action": rule.action,
#                     "expression": rule.expression,
#                     "description": rule.description,
#                     "enabled": rule.enabled,
#                     # Add other fields as needed
#                 })
#             return {
#                 "id": result.id,
#                 "kind": result.kind,
#                 "name": result.name,
#                 "phase": result.phase,
#                 "version": result.version,
#                 "description": result.description,
#                 "rules": rules
#             }


        """
        {
          "errors": [
            {
              "message": "something bad happened",
              "code": 10000,
              "source": {
                "pointer": "/rules/0/action"
              }
            }
          ],
          "messages": [
            {
              "message": "something bad happened",
              "code": 10000,
              "source": {
                "pointer": "/rules/0/action"
              }
            }
          ],
          "result": {
            "id": "2f2feab2026849078ba485f918791bdc",
            "kind": "root",
            "last_updated": "2000-01-01T00:00:00.000000Z",
            "name": "My ruleset",
            "phase": "http_request_firewall_custom",
            "rules": [
              {
                "last_updated": "2000-01-01T00:00:00.000000Z",
                "version": "1",
                "id": "3a03d665bac047339bb530ecb439a90d",
                "action": "block",
                "action_parameters": {
                  "response": {
                    "content": "{\n  \"success\": false,\n  \"error\": \"you have been blocked\"\n}",
                    "content_type": "application/json",
                    "status_code": 400
                  }
                },
                "categories": [
                  "directory-traversal"
                ],
                "description": "Block the request.",
                "enabled": true,
                "exposed_credential_check": {
                  "password_expression": "url_decode(http.request.body.form[\\\"password\\\"][0])",
                  "username_expression": "url_decode(http.request.body.form[\\\"username\\\"][0])"
                },
                "expression": "ip.src eq 1.1.1.1",
                "logging": {
                  "enabled": true
                },
                "ratelimit": {
                  "characteristics": [
                    "cf.colo.id"
                  ],
                  "period": 60,
                  "counting_expression": "http.request.body.raw eq \"abcd\"",
                  "mitigation_timeout": 600,
                  "requests_per_period": 1000,
                  "requests_to_origin": true,
                  "score_per_period": 400,
                  "score_response_header_name": "my-score"
                },
                "ref": "my_ref"
              }
            ],
            "version": "1",
            "description": "A description for my ruleset."
          },
          "success": true
        }
        """
        @self.mcp_instance.tool
        def get_rules_from_custom_rulesets(account_id: str):
            """
            获取指定account的自定义http_request_firewall_custom ruleset的所有规则,这些规则通常是域名的访问控制策略，查询访问控制策略，可以描述该域名可以被容许访问的源IP网段及user agent等信息
            Args:
                account_id (str): Cloudflare Account ID
            Returns:
                dict:
                {
                    "ruleset_phase": "http_request_firewall_custom",
                    "ruleset_name": "ruleset_name_value",
                    "rules": [
                        {
                            "id": "rule_id_value",
                            "action": "block",
                            "expression": "ip.src eq
                            ...",
                            ...
                        },
                        ...
                    ]
                }

            """
            phase = self.client.rulesets.phases.get(
                ruleset_phase="http_request_firewall_custom",
                account_id=account_id
                )
            ruleset_phase = phase.phase
            ruleset_name = phase.name
            rules = []
            for rule in phase.rules:
                rules.append({
                    "id": rule.id,
                    "action": rule.action,
                    "expression": rule.expression,
                    "description": rule.description,
                    "enabled": rule.enabled,
                    # Add other fields as needed
                })
            return {
                "ruleset_phase": ruleset_phase,
                "ruleset_name": ruleset_name,
                "rules": rules
            }
