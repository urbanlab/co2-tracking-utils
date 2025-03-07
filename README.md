# GPU Co2 Tracking tools
A set of tool to help track easely the gpu usage and co2 emission of a machine service metered 

**It is a proof of concept**

## Features 
- [x] OpenWebui function to track co2 consumption per user
- [ ] Use grist instead of nocodb ?

## Requirements
- OpenWebui
- Docker
- nocodb (to store the tracking data)


## Quick start
```bash
docker compose up
```



## Development


Copy the `.env.example` to `.env` and fill the required fields

```bash
docker compose build
docker compose up
```

Dashboard: http://localhost:5173