"""Mock Task Manager API — runs on port 8000. Use with Test Workshop Pro templates."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn, uuid
from datetime import datetime

app = FastAPI(title="Task Manager API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

users = [{"id":"u1","username":"admin","email":"admin@example.com","role":"admin","created":"2026-01-01"}]
tasks = [{"id":"t1","title":"完成项目文档","status":"done","assignee":"admin","created":"2026-01-02"},
         {"id":"t2","title":"修复登录bug","status":"todo","assignee":"admin","created":"2026-01-03"},
         {"id":"t3","title":"性能优化","status":"in_progress","assignee":"admin","created":"2026-01-04"}]

@app.get("/api/users")
def list_users(): return users

@app.post("/api/users", status_code=201)
def create_user(data: dict):
    if not data.get("username"): raise HTTPException(400, "username required")
    if any(u["username"]==data["username"] for u in users): raise HTTPException(400, "username exists")
    u = {"id":str(uuid.uuid4())[:8],"username":data["username"],"email":data.get("email",""),"role":data.get("role","user"),"created":datetime.now().isoformat()}
    users.append(u); return u

@app.get("/api/users/{uid}")
def get_user(uid: str):
    u = next((x for x in users if x["id"]==uid), None)
    if not u: raise HTTPException(404,"Not found")
    return u

@app.put("/api/users/{uid}")
def update_user(uid: str, data: dict):
    u = next((x for x in users if x["id"]==uid), None)
    if not u: raise HTTPException(404,"Not found")
    for k in ["username","email","role"]:
        if k in data: u[k] = data[k]
    return u

@app.delete("/api/users/{uid}", status_code=204)
def delete_user(uid: str):
    global users
    before = len(users)
    users = [x for x in users if x["id"]!=uid]
    if len(users)==before: raise HTTPException(404,"Not found")

@app.get("/api/tasks")
def list_tasks(): return tasks

@app.post("/api/tasks", status_code=201)
def create_task(data: dict):
    t = {"id":str(uuid.uuid4())[:8],"title":data.get("title","Untitled"),"status":data.get("status","todo"),"assignee":data.get("assignee",""),"created":datetime.now().isoformat()}
    tasks.append(t); return t

@app.put("/api/tasks/{tid}")
def update_task(tid: str, data: dict):
    t = next((x for x in tasks if x["id"]==tid), None)
    if not t: raise HTTPException(404,"Not found")
    for k in ["title","status","assignee"]:
        if k in data: t[k] = data[k]
    return t

@app.delete("/api/tasks/{tid}", status_code=204)
def delete_task(tid: str):
    global tasks
    before = len(tasks)
    tasks = [x for x in tasks if x["id"]!=tid]
    if len(tasks)==before: raise HTTPException(404,"Not found")

@app.get("/api/stats")
def get_stats():
    return {"total_users":len(users),"total_tasks":len(tasks),"tasks_by_status":{"done":sum(1 for t in tasks if t["status"]=="done"),"todo":sum(1 for t in tasks if t["status"]=="todo"),"in_progress":sum(1 for t in tasks if t["status"]=="in_progress")}}

@app.get("/")
def index(): return {"service":"Task Manager API","version":"1.0","endpoints":["/api/users","/api/tasks","/api/stats"]}

@app.get("/users-page")
def users_page(): return "<h1>用户管理</h1><p>User management page</p>"

@app.get("/tasks-page")
def tasks_page(): return "<h1>任务管理</h1><p>Task management page</p>"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
