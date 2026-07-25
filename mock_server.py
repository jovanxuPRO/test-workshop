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

from fastapi.responses import HTMLResponse

INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Task Manager API</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh}
.top{background:linear-gradient(135deg,#1e293b,#334155);padding:32px 24px;text-align:center;border-bottom:2px solid #475569}
.top h1{font-size:28px;color:#38bdf8}.top p{color:#94a3b8;margin-top:6px;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px;padding:24px;max-width:1200px;margin:0 auto}
.card{background:#1e293b;border-radius:12px;padding:20px;border:1px solid #334155}
.card h2{font-size:16px;color:#38bdf8;margin-bottom:12px;display:flex;align-items:center;gap:8px}
.meth{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;min-width:44px;text-align:center}
.m-GET{background:#166534;color:#4ade80}.m-POST{background:#1e3a5f;color:#93c5fd}
.m-PUT{background:#713f12;color:#fbbf24}.m-DELETE{background:#7f1d1d;color:#fca5a5}
.endpoint{display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:#0f172a;border-radius:8px;margin:6px 0;font-family:monospace;font-size:13px}
.endpoint span{color:#94a3b8}
.endpoint button{background:#334155;color:#e2e8f0;border:1px solid #475569;padding:5px 12px;border-radius:6px;cursor:pointer;font-size:12px;transition:.2s}
.endpoint button:hover{background:#475569;border-color:#38bdf8}
.result{margin-top:10px;padding:10px;background:#0f172a;border-radius:8px;font-family:monospace;font-size:12px;max-height:300px;overflow:auto;white-space:pre-wrap;display:none}
.result.ok{border-left:3px solid #4ade80}.result.err{border-left:3px solid #fca5a5}
.stats{display:flex;gap:12px;flex-wrap:wrap;margin-top:12px}
.stat{background:#0f172a;padding:10px 16px;border-radius:8px;text-align:center;min-width:80px}
.stat .n{font-size:24px;font-weight:700;color:#38bdf8}.stat .l{font-size:11px;color:#94a3b8}
.status-dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:4px}
.status-done{background:#4ade80}.status-todo{background:#fbbf24}.status-ip{background:#93c5fd}
</style></head>
<body>
<div class="top">
<h1>Task Manager API</h1>
<p>Mock REST API v1.0 &mdash; 测试工坊 Pro 靶机</p>
</div>
<div class="grid">
<div class="card">
<h2>Users</h2>
<div class="endpoint"><span class="meth m-GET">GET</span><span>/api/users</span><button onclick="callAPI('GET','/api/users',this)">测试</button></div>
<div class="endpoint"><span class="meth m-POST">POST</span><span>/api/users</span><button onclick="callAPI('POST','/api/users',this,'{"username":"new","email":"new@t.com"}')">测试</button></div>
<div class="endpoint"><span class="meth m-GET">GET</span><span>/api/users/{id}</span><button onclick="callAPI('GET','/api/users/u1',this)">测试</button></div>
<div class="endpoint"><span class="meth m-PUT">PUT</span><span>/api/users/{id}</span><button onclick="callAPI('PUT','/api/users/u1',this,'{"email":"u@t.com"}')">测试</button></div>
<div class="endpoint"><span class="meth m-DELETE">DEL</span><span>/api/users/{id}</span><button onclick="callAPI('DELETE','/api/users/u1',this)">测试</button></div>
<div id="res-users" class="result"></div>
</div>
<div class="card">
<h2>Tasks</h2>
<div class="endpoint"><span class="meth m-GET">GET</span><span>/api/tasks</span><button onclick="callAPI('GET','/api/tasks',this)">测试</button></div>
<div class="endpoint"><span class="meth m-POST">POST</span><span>/api/tasks</span><button onclick="callAPI('POST','/api/tasks',this,'{"title":"New Task"}')">测试</button></div>
<div class="endpoint"><span class="meth m-PUT">PUT</span><span>/api/tasks/{id}</span><button onclick="callAPI('PUT','/api/tasks/t1',this,'{"title":"Updated"}')">测试</button></div>
<div class="endpoint"><span class="meth m-DELETE">DEL</span><span>/api/tasks/{id}</span><button onclick="callAPI('DELETE','/api/tasks/t1',this)">测试</button></div>
<div id="res-tasks" class="result"></div>
</div>
<div class="card">
<h2>Stats</h2>
<div class="endpoint"><span class="meth m-GET">GET</span><span>/api/stats</span><button onclick="callAPI('GET','/api/stats',this)">测试</button></div>
<div id="res-stats" class="result"></div>
<div id="live-stats" class="stats"></div>
</div>
</div>
<script>
async function callAPI(m, path, btn, body) {
var res = document.getElementById('res-'+(path.includes('users')?'users':path.includes('tasks')?'tasks':'stats'));
res.style.display='block';res.className='result';res.textContent='请求中...';
try {
var opts={method:m,headers:{}};
if(body){opts.headers['Content-Type']='application/json';opts.body=body;}
var r=await fetch(path,opts);
var t=await r.text();
try{var j=JSON.parse(t);t=JSON.stringify(j,null,2)}catch(e){}
res.className='result '+(r.ok?'ok':'err');
res.textContent=r.status+' '+r.statusText+'\\n\\n'+t;
if(path=='/api/stats')loadStats(j);
}catch(e){res.className='result err';res.textContent='Error: '+e.message}
}
function loadStats(d){if(!d)return;
document.getElementById('live-stats').innerHTML='<div class="stat"><div class="n">'+d.total_users+'</div><div class="l">Users</div></div><div class="stat"><div class="n">'+d.total_tasks+'</div><div class="l">Tasks</div></div>'+
(d.tasks_by_status?Object.entries(d.tasks_by_status).map(function(e){var icon=e[0]==='done'?'done':e[0]==='todo'?'todo':'ip';return'<div class="stat"><div class="n"><span class="status-dot status-'+icon+'"></span>'+e[1]+'</div><div class="l">'+e[0]+'</div></div>'}).join(''):'');
}
fetch('/api/stats').then(r=>r.json()).then(loadStats);
</script>
<footer style="text-align:center;padding:24px;color:#64748b;font-size:12px">
<a href="/" style="color:#38bdf8">首页</a> &middot;
<a href="/users-page" style="color:#38bdf8">用户管理</a> &middot;
<a href="/tasks-page" style="color:#38bdf8">任务管理</a> &middot;
<a href="/api/info" style="color:#38bdf8">API信息</a>
</footer></body></html>"""

@app.get("/api/info")
def info(): return {"service":"Task Manager API","version":"1.0","endpoints":["/api/users","/api/tasks","/api/stats"]}

@app.get("/", response_class=HTMLResponse)
def index(): return INDEX_HTML

@app.get("/users-page")
def users_page(): return "<h1>用户管理</h1><p>User management page</p>"

@app.get("/tasks-page")
def tasks_page(): return "<h1>任务管理</h1><p>Task management page</p>"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
