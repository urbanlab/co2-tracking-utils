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

import os
import requests
import asyncio
import time


class Filter:
    class Valves(BaseModel):
        watts: float = 350  # Power in watts
        gr_co2_kWh: float = 55
    
    def __init__(self):
        self.valves = self.Valves()
        self.start_time = 0

    def inlet(self, body: dict) -> dict:
        self.start_time = time.time()
        return body  

    async def outlet(self, body: dict, __event_emitter__: Callable[[Any], Awaitable[None]], __user__: Optional[dict] = None) -> dict:
        end_time = time.time()
        elapsed_seconds = end_time - self.start_time
        
        # Convert watts to kW and calculate energy used
        kw = self.valves.watts / 1000
        hours = elapsed_seconds / 3600
        co2 = (kw * hours) * self.valves.gr_co2_kWh
        # rount to 0.00
        co2 = round(co2, 2)
        
        notif = f"🏭 {co2}g de Co2"

        await __event_emitter__({"type": "status", "data": {"description": notif, "done": True}})
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