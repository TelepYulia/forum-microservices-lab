import os
import json
from fastapi import FastAPI, Request, Response

STUDENT_N = 16

PORT = int(os.getenv("PORT", 9016))

app = FastAPI(title=f"Forum Service (Student {STUDENT_N})")

START_ID = 100 * STUDENT_N
topic_id_counter = START_ID


db_topics = {
    topic_id_counter: {"id": topic_id_counter, "title": "Перші кроки в Docker", "content": "Як налаштувати контейнери?", "status": "active"}
}


@app.middleware("http")
async def add_student_id_metadata(request: Request, call_next):
    response = await call_next(request)
    
    if response.headers.get("content-type") == "application/json":
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        
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
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type="application/json"
            )
            
    return response


@app.post("/api/v1/posts/topics")
async def create_topic(title: str, content: str):
    global topic_id_counter
    topic_id_counter += 1
    new_topic = {"id": topic_id_counter, "title": title, "content": content, "status": "active"}
    db_topics[topic_id_counter] = new_topic
    return new_topic

@app.patch("/api/v1/posts/topics/{id}/status")
async def moderate_topic(id: int, status: str):
    if id in db_topics:
        db_topics[id]["status"] = status
        return db_topics[id]
    return {"error": "Topic not found"}

@app.get("/api/v1/posts/topics/search")
async def search_topics(query: str):
    results = [topic for topic in db_topics.values() if query.lower() in topic["title"].lower()]
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)