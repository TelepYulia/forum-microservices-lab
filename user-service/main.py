import json
from fastapi import FastAPI, Request, Response

app = FastAPI()

STUDENT_N = 16

@app.middleware("http")
async def add_student_id_metadata(request: Request, call_next):
    response = await call_next(request)
    content_type = response.headers.get("content-type", "").lower()
    
    if "application/json" in content_type:
        try:
            response_body = [chunk async for chunk in response.body_iterator]
            body = b"".join(response_body)
            
            data = json.loads(body.decode("utf-8"))
            if isinstance(data, dict):
                data["student_id"] = STUDENT_N
            elif isinstance(data, list):
                data = {"data": data, "student_id": STUDENT_N}
                
            modified_body = json.dumps(data).encode("utf-8")
            
            return Response(
                content=modified_body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type="application/json"
            )
        except Exception:
            return Response(
                content=b"".join(response_body),
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=content_type
            )
            
    return response

@app.get("/api/v1/posts/topics/search")
async def search_topics(query: str):
    return {
        "message": f"Search results for topic: {query}",
        "topics": ["Docker Basics", "Advanced Kubernetes", "Microservices Architecture"]
    }