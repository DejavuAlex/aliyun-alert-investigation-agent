import json
from datetime import datetime, timedelta

from aliyunsdkactiontrail.request.v20200706 import LookupEventsRequest
from aliyunsdkcore.client import AcsClient

import asyncio
from fastmcp import Client
from typing import List, Optional, Dict, Any

client = Client("http://127.0.0.1:8000/mcp")


def test_call_aliyun_action_trail_MCP_server():
    async def call_tool():
        async with client:
            result = await client.call_tool(name="list_all_tools")
            print(result)
    asyncio.run(call_tool())

def test_math():
    async def call_tool():
        async with client:
            result = await client.call_tool(name="math_add", arguments={"a": 5, "b": 3})
            print(result)
    asyncio.run(call_tool())

async def list_all_tools():
    async with client:
        from mcp.types import Tool
        tools:List[Tool] = await client.list_tools()
        #print("Available tools:", tools)
        for tool in tools:
            print(f"Tool name: {tool.name}, Description: {tool.description}")
async def list_all_prompts():
    async with client:
        from mcp.types import Prompt
        prompts:List[Prompt] = await client.list_prompts()
        for prompt in prompts:
            print(f"Prompt name: {prompt.name}, Description: {prompt.description}")

def test_list_all_tools_prompts():
    asyncio.run(list_all_tools())
    asyncio.run(list_all_prompts())

def test_visit_aliyun_action_trail_by_aliyun_sdk():
    access_key_id="YOUR_ACCESS_KEY_ID"
    access_key_secret="YOUR_ACCESS_KEY_SECRET"
    region_id="cn-shanghai"
    client = AcsClient(ak=access_key_id, secret=access_key_secret, region_id=region_id)
    lookup_events(client)

def lookup_events(
        client: AcsClient,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        event_name: Optional[str] = None,
        event_source: Optional[str] = None,
        event_rw: Optional[str] = None,
        resource_type: Optional[str] = None,
        max_results: int = 50,
) -> List[Dict[str, Any]]:
    """
    查询ActionTrail事件

    Args:
        start_time: 开始时间，格式：YYYY-MM-DDTHH:MM:SSZ (UTC时间)
        end_time: 结束时间，格式：YYYY-MM-DDTHH:MM:SSZ (UTC时间)
        event_name: 事件名称
        event_source: 事件来源
        event_rw: 事件类型 (Read/Write)
        resource_type: 资源类型
        max_results: 最大返回结果数 (1-50)

    Returns:
        事件列表
    """
    try:
        print("Beginning to run lookup_events for aliyun action trail")
        # 设置默认时间范围（最近1小时）
        if not start_time:
            start_time = (datetime.utcnow() - timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
        if not end_time:
            end_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        request = LookupEventsRequest.LookupEventsRequest()
        request.set_StartTime(start_time)
        request.set_EndTime(end_time)
        request.set_MaxResults(max_results)

        # 设置过滤条件
        filter_params = {}
        if event_name:
            filter_params['EventName'] = event_name
        if event_source:
            filter_params['EventSource'] = event_source
        if event_rw:
            filter_params['EventRw'] = event_rw
        if resource_type:
            filter_params['ResourceType'] = resource_type

        if filter_params:
            request.set_LookupAttributes([{"Key": k, "Value": v} for k, v in filter_params.items()])

        response = client.do_action_with_exception(request)
        result = json.loads(response.decode('utf-8'))

        print(result.get('Events', []))

    except Exception as e:
        raise RuntimeError(f"查询失败: {str(e)}")