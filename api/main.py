from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from prometheus_client import make_asgi_app, Counter
import os 
import requests

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://prometheus:9090")

# llm_request_by_model_count{model="cicas"} 
request_by_model_count = Counter("requests_by_model", "Number of requests by model", ["model", "org"])
co2_emission_by_user = Counter("co2_emission_by_user", "Total CO2 emission by user", ["user_id", "org"])
co2_emission_by_model = Counter("co2_emission_by_model", "Total CO2 emission by model", ["model", "org"])
token_count_by_model = Counter("token_count_by_model", "Total token count by model", ["model", "org"])


# Request Model
class Request(BaseModel):
    user_id: str
    co2_emission: float
    model: str
    token_nb: int
    org: str

AUTH_TOKEN = os.getenv("AUTH_TOKEN", "your-secret-token")
app = FastAPI()
security = HTTPBearer()

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != AUTH_TOKEN:
        raise HTTPException(
            status_code=401, 
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/api/v1/request")
async def api_request(data: Request, token: str = Depends(get_current_user)):
    request_by_model_count.labels(model=data.model, org=data.org).inc()
    co2_emission_by_user.labels(user_id=data.user_id, org=data.org).inc(data.co2_emission)
    token_count_by_model.labels(model=data.model, org=data.org).inc(data.token_nb)
    co2_emission_by_model.labels(model=data.model, org=data.org).inc(data.co2_emission)

    return {"status": "request received", "data": data}

@app.get("/api/v1/co2/user/{user_id}")
async def get_user_co2_emission(user_id: str, range: str = "daily"):
    if range not in ["daily", "weekly", "monthly", "yearly"]:
        raise HTTPException(status_code=400, detail="Invalid range parameter")
    
    # For Counter metrics, you typically want to get the increase over time
    # Using rate() or increase() functions with range selectors
    time_range = {
        "daily": "1d",
        "weekly": "7d", 
        "monthly": "30d",
        "yearly": "365d",
    }[range]
    
    # Option 1: Get the increase over the time period
    query = f'round(sum(increase(co2_emission_by_user_total{{user_id="{user_id}"}}[{time_range}])) by (user_id), 0.01)'
    
    print("Querying Prometheus with:", query)
    print("Using Prometheus URL:", PROMETHEUS_URL)
    
    try:
        response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
        response.raise_for_status()  # This will raise an exception for bad status codes
        
        result = response.json()
        
        # Check if the query was successful
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=f"Prometheus query failed: {result}")
            
        # round to integer
        for item in result["data"]["result"]:
            item["value"][1] = int(float(item["value"][1]))

        return result
        
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to query Prometheus: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
