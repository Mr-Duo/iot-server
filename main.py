from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import uvicorn
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from config import settings
from apps.routers import router as todo_router
from apps.voice import VoiceModel

import time
from collections import defaultdict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.mongodb_client = MongoClient(settings.DB_URL, server_api=ServerApi('1'))
app.mongodb = app.mongodb_client[settings.DB_NAME]
app.state.voice = VoiceModel("model/model-en", "model/deep-speaker/ResCNN_triplet_training_checkpoint_265.h5")

try:
    app.mongodb_client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)
   
    
# Initialize the limiter with default key function
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Store timestamps of user requests to track interval
request_times = defaultdict(list)

# Custom exception handler for rate limits
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"message": "Rate limit exceeded. Maximum 10 calls per minute allowed."},
    )

# Function to check if interval between requests is less than 1 second
def is_interval_valid(client_ip: str) -> bool:
    current_time = time.time()
    if client_ip in request_times:
        last_request_time = request_times[client_ip][-1]
        if current_time - last_request_time < 1:
            return False
    return True

# Endpoint with both limits
@app.get("/limited-endpoint")
@limiter.limit("10/minute")  # Allow max 10 calls per minute
async def limited_endpoint(request: Request):
    client_ip = request.client.host
    
    # Check the minimum interval condition
    if not is_interval_valid(client_ip):
        return JSONResponse(
            status_code=429,
            content={"message": "Requests must be at least 1 second apart."},
        )
    
    # Record the request time
    request_times[client_ip].append(time.time())
    
    return {"message": "Request accepted. You are within the rate limit."}


app.include_router(todo_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        reload=settings.DEBUG_MODE,
        port=settings.PORT,
    )
    
    app.mongodb_client.close()