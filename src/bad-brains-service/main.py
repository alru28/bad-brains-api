from fastapi import FastAPI, Request, HTTPException, Response, Depends, BackgroundTasks
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel
from datetime import datetime, timedelta
from pymongo import MongoClient
import yaml
import httpx
import os
import time

# ENV
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth-service:3000")
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://mongo_user:mongo_pass@mongodb:27017/map_db")
DB_NAME = os.getenv("DB_NAME", "map_db")

# MONGODB
client = MongoClient(MONGODB_URL)
db = client.map_db
locations_collection = db["locations"]
stations_collection = db["stations"]


# Models
class ReserveSafeRequest(BaseModel):
    safe_id: int
    pin: str
    duration_minutes: int

class UnlockSafeRequest(BaseModel):
    safe_id: int
    pin: str
    
class CommentRequest(BaseModel):
    text: str

# HELPER FUNCTIONS
def get_station(station_id: str):
    station = stations_collection.find_one({"station_id": station_id})
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    return station

def get_location(location_id: str):
    location = locations_collection.find_one({"location_id": location_id})
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

def unlock_safe_after_duration(station_id: str, safe_id: int, duration_minutes: int):
    # Wait for the specified duration
    end_time = datetime.now() + timedelta(minutes=duration_minutes)
    while datetime.now() < end_time:
        time.sleep(20)
    
    # Unlock the safe
    station = get_station(station_id)
    safe = next((s for s in station["safes"] if s["safe_id"] == safe_id), None)
    if safe and safe["reserved_until"] and safe["reserved_until"] < datetime.now():
        safe["reserved_until"] = None
        safe["pin"] = None
        stations_collection.update_one({"station_id": station_id, "safes.safe_id": safe_id}, {"$set": {"safes.$": safe}})
        print(f"Safe {safe_id} at station {station_id} has been automatically unlocked after reservation expiration.")

# Verify JWT
async def verify_jwt(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Authorization token is missing")

    # Send to auth-service
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{AUTH_SERVICE_URL}/verify", headers={"Authorization": token})

            if response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid token")
            
            user_info = response.json().get("user")
            if not user_info or "username" not in user_info:
                raise HTTPException(status_code=401, detail="Invalid user info")
            return user_info["username"]  # Return the username
        
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=500, detail="Authentication service error")

# Proxy
async def proxy_request(request: Request, target_url: str, headers=None):
    method = request.method
    print(target_url)
    content = await request.body()

    headers = headers or dict(request.headers)

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            
            response = await client.request(method, target_url, headers=headers, content=content)
            return Response(content=response.content, status_code=response.status_code, headers=response.headers)
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=500, detail=f"Gateway error: {str(exc)}")

# MAIN SERVICE APP
app = FastAPI(title="BadBrains API", openapi_url = None)

# AUTH PROXY
@app.api_route("/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], include_in_schema=False)
async def auth_service_proxy(path: str, request: Request):
    target_url = f"{AUTH_SERVICE_URL}/{path}".lstrip("/")
    return await proxy_request(request, target_url)

# STATIONS
@app.get("/stations/{station_id}/safes", dependencies=[Depends(verify_jwt)])
async def get_safes(station_id: str):
    """Retrieve all safes for a given station."""
    station = get_station(station_id)
    return {"station_id": station_id, "address": station["address"], "safes": station["safes"]}

@app.post("/stations/{station_id}/safes/reserve", dependencies=[Depends(verify_jwt)])
async def reserve_safe(station_id: str, request: ReserveSafeRequest, background_tasks: BackgroundTasks):
    """Reserve a safe for a specified time with a PIN."""
    station = get_station(station_id)
    safe = next((s for s in station["safes"] if s["safe_id"] == request.safe_id), None)
    if not safe:
        raise HTTPException(status_code=404, detail="Safe not found")
    if safe["reserved_until"] and safe["reserved_until"] > datetime.now():
        raise HTTPException(status_code=400, detail="Safe is already reserved")

    # Update the safe reservation
    safe["reserved_until"] = datetime.now() + timedelta(minutes=request.duration_minutes)
    safe["pin"] = request.pin
    stations_collection.update_one({"station_id": station_id, "safes.safe_id": request.safe_id}, {"$set": {"safes.$": safe}})

    # Background task to unlock the safe after the reservation expires
    background_tasks.add_task(unlock_safe_after_duration, station_id, request.safe_id, request.duration_minutes)

    return {"message": "Safe reserved successfully", "safe_id": request.safe_id, "reserved_until": safe["reserved_until"]}

@app.post("/stations/{station_id}/safes/unlock", dependencies=[Depends(verify_jwt)])
async def unlock_safe(station_id: str, request: UnlockSafeRequest):
    """Unlock a safe using a PIN."""
    station = get_station(station_id)
    safe = next((s for s in station["safes"] if s["safe_id"] == request.safe_id), None)
    if not safe:
        raise HTTPException(status_code=404, detail="Safe not found")
    if not safe["reserved_until"] or safe["reserved_until"] < datetime.now():
        raise HTTPException(status_code=400, detail="Safe is not reserved or reservation expired")
    if safe["pin"] != request.pin:
        raise HTTPException(status_code=403, detail="Incorrect PIN")

    # Reset the safe
    safe["reserved_until"] = None
    safe["pin"] = None
    stations_collection.update_one({"station_id": station_id, "safes.safe_id": request.safe_id}, {"$set": {"safes.$": safe}})
    return {"message": "Safe unlocked successfully", "safe_id": request.safe_id}

# MAPS

@app.get("/map/{location_id}", dependencies=[Depends(verify_jwt)])
async def get_location_info(location_id: str):
    """Retrieve all information related to a location."""
    location = get_location(location_id)
    return {
        "location_id": location_id,
        "address": location["address"],
        "information": location["information"],
        "type": location["type"],
        "lat": location["lat"],
        "long": location["long"],
        "comments": location["comments"]
    }

@app.post("/map/{location_id}/comment", dependencies=[Depends(verify_jwt)])
async def post_comment(location_id: str, comment: CommentRequest, request: Request):
    """Post a comment for a location."""
    username = await verify_jwt(request)  # Extract the username from the JWT

    location = get_location(location_id)

    # Add the comment to the location's comment list
    locations_collection.update_one(
        {"location_id": location_id},
        {"$push": {"comments": {"username": username, "text": comment.text}}}
    )
    return {"message": "Comment posted successfully", "location_id": location_id}


# CUSTOM DOCS
with open("api-doc.yaml", "r") as file:
    openapi_spec = yaml.safe_load(file)

@app.get("/api-doc.yaml", include_in_schema=False)
async def get_openapi_yaml():
    return Response(content=yaml.dump(openapi_spec), media_type="application/yaml")

@app.get("/docs", include_in_schema=False)
async def custom_docs():
    return get_swagger_ui_html(openapi_url="/api-doc.yaml", title="Custom API Docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)