"""
title: Co2 Emission
author: Erasme - Yassin Siouda x Claude
author_url: https://github.com/open-webui
version: 0.0.2
required_open_webui_version: 0.3.9
description: This plugin calculates the amount of CO2 emitted by a message and sends metrics to Prometheus API.
"""
import json
import time
import asyncio
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable, Optional
import aiohttp
from pydantic import BaseModel, Field

class Filter:
    class Valves(BaseModel):
        watts: float = 350
        gr_co2_kWh: float = 55
        api_url: str = Field(default="http://localhost:8000")
        api_token: str = Field(default="your-secret-token")
        org: str = Field(default="default-org")
        dashboard_url: str = Field(default="https://dashboard_url.club")

    def __init__(self):
        self.valves = self.Valves()
        self.start_time = 0
        self.user_weekly_cache = {}  # Simple cache for weekly stats

    def inlet(self, body: dict) -> dict:
        self.start_time = time.time()
        return body

    async def send_metrics_to_api(
        self, 
        user_id: str, 
        co2_emission: float, 
        model: str, 
        token_count: int = 0
    ) -> bool:
        """Send metrics to the new API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.valves.api_token}",
                "Content-Type": "application/json",
            }
            
            data = {
                "user_id": user_id,
                "co2_emission": co2_emission,
                "model": model,
                "token_nb": token_count,
                "org": self.valves.org
            }
            
            print(f"Sending metrics to API: {data}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.valves.api_url}/api/v1/request",
                    headers=headers,
                    json=data,
                ) as response:
                    response_text = await response.text()
                    print(f"API response status: {response.status}")
                    print(f"API response body: {response_text}")
                    
                    if response.status == 200:
                        return True
                    else:
                        print(f"Error sending metrics: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"Exception in send_metrics_to_api: {str(e)}")
            return False

    def estimate_token_count(self, messages: list) -> int:
        """Rough estimation of token count based on message content"""
        try:
            total_chars = 0
            for message in messages:
                if isinstance(message, dict) and "content" in message:
                    total_chars += len(str(message["content"]))
            
            # Rough estimation: ~4 characters per token
            estimated_tokens = total_chars // 4
            return max(estimated_tokens, 1)  # At least 1 token
        except Exception as e:
            print(f"Error estimating tokens: {e}")
            return 1

    def extract_model_from_body(self, body: dict) -> str:
        """Extract model name from the request body"""
        try:
            # Try different possible locations for model info
            if "model" in body:
                return body["model"]
            elif "messages" in body and len(body["messages"]) > 0:
                # Sometimes model info might be in metadata
                return body.get("metadata", {}).get("model", "unknown")
            else:
                return "unknown"
        except Exception as e:
            print(f"Error extracting model: {e}")
            return "unknown"

    def update_user_weekly_cache(self, user_id: str, co2: float):
        """Update the local weekly cache"""
        cache_key = f"{user_id}_{datetime.now().strftime('%Y-%W')}"
        self.user_weekly_cache[cache_key] = self.user_weekly_cache.get(cache_key, 0.0) + co2

    def get_user_weekly_total(self, user_id: str) -> float:
        """Get user's weekly CO2 total from cache"""
        cache_key = f"{user_id}_{datetime.now().strftime('%Y-%W')}"
        return self.user_weekly_cache.get(cache_key, 0.0)

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
                
                # Extract model and estimate token count
                model = self.extract_model_from_body(body)
                token_count = self.estimate_token_count(body.get("messages", []))
                
                # Update local cache for weekly totals BEFORE sending to API
                self.update_user_weekly_cache(user_id, co2)
                weekly_total = self.get_user_weekly_total(user_id)
                
                # Send metrics to the new API
                success = await self.send_metrics_to_api(
                    user_id=user_id,
                    co2_emission=co2,
                    model=model,
                    token_count=token_count
                )
                
                if success:
                    print("Metrics sent successfully!")
                else:
                    print("Failed to send metrics")
                
                # Create CO2 consumption message
                co2_message = f"""
<details>
<summary>Ma consommation CO2</summary>
Ce message: {co2}g CO2 (Model: {model}, Tokens: ~{token_count})
Total cette semaine: {round(weekly_total, 2)}g CO2 
Pour en savoir plus, consultez votre tableau de bord: {self.valves.dashboard_url}/user/{user_id}
</details>
"""

                # Append CO2 information to the response
                if body and "messages" in body and len(body["messages"]) > 0:
                    last_message = body["messages"][-1]
                    if "content" in last_message:
                        last_message["content"] += co2_message

                # Emit the CO2 information as a separate message
                await __event_emitter__(
                    {
                        "type": "message",
                        "data": {"content": co2_message},
                    }
                )

            return body

        except Exception as e:
            print(f"Error in outlet: {str(e)}")
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