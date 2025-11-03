# Stack


## DB

### Schema

```
requests: 
- id: integer, primary key
- user_id: integer
- date: datetime
- co2_emission: float
- model: string
```


## API 

### Endpoints
- `POST /requests`: Track a new request
  - Header:
    - Authorization: Bearer <API_KEY>
  - Body:
    - user_id: integer
    - model: string
    - co2_emission: float
    


## Prometheus Exporter

### Metrics

llm_request_by_model_count{model="cicas"} 12

# TYPE llm_request_by_model_count counter
llm_request_by_model_count{model="pizza"} 2

# TYPE llm_request_by_model_count counter
llm_request_by_model_count{model="maison"} 90

llm_request_by_user_count{user="titi"} 90

