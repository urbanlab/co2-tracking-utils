"""
title: Co2 Emission
author: Erasme - Yassin Siouda
author_url: https://github.com/open-webui 
version: 0.0.1
required_open_webui_version: 0.3.9
description: This plugin calculates the amount of CO2 emitted by a message credits to constLiakos for the sec duration count.
"""

from pydantic import BaseModel, Field
from typing import Optional, Union, Generator, Iterator, Callable, Any, Awaitable
from datetime import datetime
import os
import aiohttp
import asyncio
import time


class Filter:
    class Valves(BaseModel):
        watts: float = 350  # Power in watts
        gr_co2_kWh: float = 55
        nocodb_url: str = Field(default="https://nocodb.url")
        nocodb_api_token: str = Field(
            default="mytoken"
        )
        table_id: str = Field(default="tableId")

    def __init__(self):
        self.valves = self.Valves()
        self.start_time = 0

    def inlet(self, body: dict) -> dict:
        self.start_time = time.time()
        return body

    async def outlet(
        self,
        body: dict,
        __event_emitter__: Callable[[Any], Awaitable[None]],
        __user__: Optional[dict] = None,
    ) -> dict:
        try:
            end_time = time.time()
            elapsed_seconds = end_time - self.start_time

            # Calculate CO2 emissions
            kw = self.valves.watts / 1000
            hours = elapsed_seconds / 3600
            co2 = round((kw * hours) * self.valves.gr_co2_kWh, 2)

            notif = f"🏭 {co2}g de Co2"

            # Create NocoDB entry if user is present
            if __user__:
                today = datetime.now().strftime("%Y-%m-%d")

                # Get user ID, default to null if not found
                user_id = __user__.get("id")
                if user_id is None:
                    print("No valid user ID found, skipping database entry")
                    await __event_emitter__(
                        {"type": "status", "data": {"description": notif, "done": True}}
                    )
                    return body

                headers = {
                    "xc-token": self.valves.nocodb_api_token,
                    "Content-Type": "application/json",
                    "accept": "application/json",
                }

                data = {"user": user_id, "co2": co2, "date": today}

                print(f"Sending request to NocoDB with data: {data}")

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.valves.nocodb_url}/api/v2/tables/{self.valves.table_id}/records",
                        headers=headers,
                        json=data,
                    ) as response:
                        if response.status != 201:
                            response_text = await response.text()
                            print(f"Error logging to NocoDB: Status {response.status}")
                            print(f"Response body: {response_text}")
                        else:
                            print("Successfully logged to NocoDB")

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
