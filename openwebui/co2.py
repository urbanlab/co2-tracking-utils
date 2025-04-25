"""
title: Co2 Emission
author: Erasme - Yassin Siouda x Claude
author_url: https://github.com/open-webui 
version: 0.0.1
required_open_webui_version: 0.3.9
description: This plugin calculates the amount of CO2 emitted by a message credits to constLiakos for the sec duration count.
"""


from pydantic import BaseModel, Field
from typing import Optional, Callable, Any, Awaitable
from datetime import datetime, timedelta
import aiohttp
import time
import json
import urllib.parse

class Filter:
    class Valves(BaseModel):
        watts: float = 350
        gr_co2_kWh: float = 55
        nocodb_url: str = Field(default="https://nocodb.url")
        nocodb_api_token: str = Field(default="mytoken")
        table_id: str = Field(default="tableId")

    def __init__(self):
        self.valves = self.Valves()
        self.start_time = 0

    def inlet(self, body: dict) -> dict:
        self.start_time = time.time()
        return body

    async def fetch_user_stats(self, user_id: str, nocodb_url: str, headers: dict) -> dict:
        """Fetch user statistics for the past week"""
        try:
            # Create where condition without encoding the "where=" part
            where_raw = f"where=(user,eq,{user_id})"
            
            async with aiohttp.ClientSession() as session:
                url = f"{nocodb_url}/api/v2/tables/{self.valves.table_id}/records"
                params = {
                    "where": where_raw,  # Use raw where condition
                    "sort": "-date",
                    "limit": 1000,
                    "shuffle": 0,
                    "offset": 0
                }
                
                print(f"Fetching stats from URL: {url}")
                print(f"With params: {params}")
                
                async with session.get(
                    url,
                    headers=headers,
                    params=params
                ) as response:
                    response_text = await response.text()
                    print(f"Response status: {response.status}")
                    print(f"Response body: {response_text}")
                    
                    if response.status == 200:
                        return json.loads(response_text)
                    else:
                        print(f"Error fetching stats: {response.status}")
                        return None
        except Exception as e:
            print(f"Exception in fetch_user_stats: {str(e)}")
            return None

    async def outlet(
        self,
        body: dict,
        __event_emitter__: Callable[[Any], Awaitable[None]],
        __user__: Optional[dict] = None,
    ) -> dict:
        try:
            # Calculate current message CO2
            end_time = time.time()
            elapsed_seconds = end_time - self.start_time
            kw = self.valves.watts / 1000
            hours = elapsed_seconds / 3600
            co2 = round((kw * hours) * self.valves.gr_co2_kWh, 2)

            if __user__:
                user_id = __user__.get("id")
                today = datetime.now().strftime("%Y-%m-%d")
                
                headers = {
                    "xc-token": self.valves.nocodb_api_token,
                    "Content-Type": "application/json",
                    "accept": "application/json",
                }

                # Log current message CO2
                data = {"user": user_id, "co2": co2, "date": today}
                
                print(f"Sending data to NocoDB: {data}")
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.valves.nocodb_url}/api/v2/tables/{self.valves.table_id}/records",
                        headers=headers,
                        json=data,
                    ) as response:
                        response_text = await response.text()
                        print(f"NocoDB response status: {response.status}")
                        print(f"NocoDB response body: {response_text}")

                # Fetch weekly stats
                stats = await self.fetch_user_stats(user_id, self.valves.nocodb_url, headers)
                if stats and 'list' in stats:
                    # Calculate total CO2 for the week
                    total_co2 = sum(float(entry.get('co2', 0)) for entry in stats['list'])
                    notif = f"🏭 Current message: {co2}g CO2 | Total: {round(total_co2, 2)}g CO2"
                else:
                    notif = f"🏭 {co2}g CO2 (First message tracked!)"

            await __event_emitter__(
                {"type": "status", "data": {"description": notif, "done": True}}
            )
            return body

        except Exception as e:
            print(f"Error in outlet: {str(e)}")
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": "Error calculating CO2", "done": True},
                }
            )
            return body


class Action:
    class Valves(BaseModel):
        pass

    def __init__(self):
        self.valves = self.Valves()
        pass

    async def action(
        self,
        body: dict,
        __user__=None,
        __event_emitter__=None,
        __event_call__=None,
    ) -> Optional[dict]:
        print(f"action:{__name__}")

        response = await __event_call__(
            {
                "type": "input",
                "data": {
                    "title": "write a message",
                    "message": "here write a message to append",
                    "placeholder": "enter your message",
                },
            }
        )
        print(response)

        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": "adding message", "done": False},
                }
            )
            await asyncio.sleep(1)
            await __event_emitter__({"type": "message", "data": {"content": response}})
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": "added message", "done": True},
                }
            )