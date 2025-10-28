from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from prometheus_client import make_asgi_app, Counter
import os 


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

