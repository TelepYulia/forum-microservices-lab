import os
import json
from fastapi import FastAPI, Request, Response


STUDENT_N = 16

PORT = int(os.getenv("PORT", 8016))

app = FastAPI(title=f"User Service (Student {STUDENT_N})")

START_ID = 100 * STUDENT_N
user_id_counter = START_ID

db_users = {
    user_id_counter: {"id": user_id_counter, "username": "admin_ivan", "role": "admin", "status": "active"}
}

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
    global user_id_counter
    user_id_counter += 1
    new_user = {"id": user_id_counter, "username": username, "role": "user", "status": "active"}
    db_users[user_id_counter] = new_user
    return new_user

@app.post("/api/v1/users/{id}/ban")
async def ban_user(id: int):
    if id in db_users:
        db_users[id]["status"] = "banned"
        return db_users[id]
    return {"error": "User not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)