from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import redis
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="HUST Course Search API",
             description="API for searching HUST courses",
             version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis connection
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

@app.get("/api/search")
async def search_courses(q: str = Query(..., min_length=1)) -> List[Dict[Any, Any]]:
    # Get all course keys
    all_keys = redis_client.keys("course:*")
    results = []
    
    # Convert query to lowercase for case-insensitive search
    query_lower = q.lower()
    
    for key in all_keys:
        course_data = redis_client.hgetall(key)
        
        # Search in course code and name
        if (query_lower in course_data['Mã học phần'].lower() or 
            query_lower in course_data['Tên học phần'].lower()):
            results.append(course_data)
            
        # Limit results to 10 for better performance
        if len(results) >= 10:
            break
    
    return results

@app.get("/")
async def root():
    return {"message": "HUST Course Search API", "status": "healthy"} 