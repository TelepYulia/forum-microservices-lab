import json
from fastapi import FastAPI, Request, Response

app = FastAPI()

STUDENT_N = 16

@app.middleware("http")
async def add_student_id_metadata(request: Request, call_next):
    response = await call_next(request)
    content_type = response.headers.get("content-type", "").lower()
    
    body = b""
    async for chunk in response.body_iterator:
        body += chunk
        
    if "application/json" in content_type:
        try:
            data = json.loads(body.decode("utf-8"))
            if isinstance(data, dict):
                data["student_id"] = STUDENT_N
            elif isinstance(data, list):
                data = {"data": data, "student_id": STUDENT_N}
                
            modified_body = json.dumps(data).encode("utf-8")
            
            new_headers = dict(response.headers)
            new_headers["content-length"] = str(len(modified_body))
            
            return Response(
                content=modified_body,
                status_code=response.status_code,
                headers=new_headers,
                media_type="application/json"
            )
        except Exception:
            pass

    new_headers = dict(response.headers)
    new_headers["content-length"] = str(len(body))
    return Response(
        content=body,
        status_code=response.status_code,
        headers=new_headers,
        media_type=content_type
    )

@app.post("/api/v1/users/register")
async def register_user(username: str):
    return {"message": "User registered successfully", "username": username}