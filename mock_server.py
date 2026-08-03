"""Enterprise E-Commerce Order System — mock server on port 8000."""
from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn, uuid, jwt
from datetime import datetime, timedelta

app = FastAPI(title="E-Commerce Order System v2.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

JWT_SECRET = "enterprise-mock-secret-key-2026"
JWT_ALGORITHM = "HS256"

# ===== Data Store =====
products = [
    {"id":"p1","name":"机械键盘 K8 Pro","price":599.00,"stock":120,"category":"外设","created":"2026-01-01"},
    {"id":"p2","name":"4K显示器 27寸","price":2999.00,"stock":35,"category":"显示","created":"2026-01-01"},
    {"id":"p3","name":"人体工学椅 Pro","price":1899.00,"stock":18,"category":"家具","created":"2026-01-02"},
    {"id":"p4","name":"USB-C 扩展坞","price":299.00,"stock":200,"category":"配件","created":"2026-01-03"},
    {"id":"p5","name":"无线鼠标 MX","price":449.00,"stock":88,"category":"外设","created":"2026-01-04"},
]
orders = [
    {"id":"o1","user_id":"u1","items":[{"product_id":"p1","quantity":1,"unit_price":599.00},{"product_id":"p5","quantity":2,"unit_price":449.00}],"total":1497.00,"status":"delivered","created":"2026-01-10","updated":"2026-01-13"},
    {"id":"o2","user_id":"u2","items":[{"product_id":"p2","quantity":1,"unit_price":2999.00}],"total":2999.00,"status":"shipped","created":"2026-01-12","updated":"2026-01-14"},
    {"id":"o3","user_id":"u1","items":[{"product_id":"p3","quantity":1,"unit_price":1899.00}],"total":1899.00,"status":"paid","created":"2026-01-14","updated":"2026-01-14"},
    {"id":"o4","user_id":"u3","items":[{"product_id":"p4","quantity":3,"unit_price":299.00}],"total":897.00,"status":"created","created":"2026-01-15","updated":"2026-01-15"},
]
refunds = [
    {"id":"r1","order_id":"o1","reason":"键盘按键失灵","amount":599.00,"status":"approved","created":"2026-01-15"},
]
VALID_STATUSES = ["created","confirmed","paid","shipped","delivered","cancelled"]
STATUS_TRANSITIONS = {
    "created":    ["confirmed","cancelled"],
    "confirmed":  ["paid","cancelled"],
    "paid":       ["shipped"],
    "shipped":    ["delivered"],
    "delivered":  [],
    "cancelled":  [],
}

# ===== Auth =====
def create_token(user: dict) -> str:
    return jwt.encode({"sub": user["id"], "role": user["role"], "exp": datetime.utcnow() + timedelta(hours=24)}, JWT_SECRET, algorithm=JWT_ALGORITHM)

def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return None  # Allow unauthenticated access for reads
    try:
        payload = jwt.decode(authorization[7:], JWT_SECRET, algorithms=[JWT_ALGORITHM])
        u = next((x for x in users if x["id"] == payload["sub"]), None)
        return u
    except Exception:
        return None

def require_admin(user = Depends(get_current_user)):
    if not user or user["role"] != "admin":
        raise HTTPException(403, "Admin role required")
    return user

def require_auth(user = Depends(get_current_user)):
    if not user:
        raise HTTPException(401, "Authentication required")
    return user

# ===== Auth Endpoints =====
@app.post("/api/auth/login")
def login(data: dict):
    u = next((x for x in users if x["username"] == data.get("username") and data.get("password") == "Test123!"), None)
    if not u:
        raise HTTPException(401, "Invalid credentials")
    return {"token": create_token(u), "user": {"id": u["id"], "username": u["username"], "role": u["role"]}}

@app.get("/api/auth/me")
def me(user = Depends(require_auth)):
    return user

# ===== Product Endpoints =====
@app.get("/api/products")
def list_products(page: int = 1, limit: int = 20, category: Optional[str] = None):
    result = [p for p in products if not category or p["category"] == category]
    return result[(page-1)*limit : page*limit]

@app.post("/api/products", status_code=201)
def create_product(data: dict, user = Depends(require_admin)):
    if not data.get("name"): raise HTTPException(400, "name is required")
    if not data.get("price") or data["price"] <= 0: raise HTTPException(400, "price must be > 0")
    if not data.get("stock") or data["stock"] < 0: raise HTTPException(400, "stock must be >= 0")
    p = {"id": str(uuid.uuid4())[:8], "name": data["name"], "price": float(data["price"]),
         "stock": int(data["stock"]), "category": data.get("category", "未分类"), "created": datetime.now().isoformat()}
    products.append(p)
    return p

@app.get("/api/products/{pid}")
def get_product(pid: str):
    p = next((x for x in products if x["id"] == pid), None)
    if not p: raise HTTPException(404, "Product not found")
    return p

@app.put("/api/products/{pid}")
def update_product(pid: str, data: dict, user = Depends(require_admin)):
    p = next((x for x in products if x["id"] == pid), None)
    if not p: raise HTTPException(404, "Product not found")
    for k in ["name","price","stock","category"]:
        if k in data:
            if k == "price" and data[k] <= 0: raise HTTPException(400, "price must be > 0")
            if k == "stock" and data[k] < 0: raise HTTPException(400, "stock must be >= 0")
            p[k] = data[k]
    return p

@app.delete("/api/products/{pid}", status_code=204)
def delete_product(pid: str, user = Depends(require_admin)):
    global products
    before = len(products)
    products = [x for x in products if x["id"] != pid]
    if len(products) == before: raise HTTPException(404, "Product not found")

# ===== Order Endpoints =====
@app.get("/api/orders")
def list_orders(page: int = 1, limit: int = 20, status: Optional[str] = None, user = Depends(require_auth)):
    result = [o for o in orders if not status or o["status"] == status]
    return result[(page-1)*limit : page*limit]

@app.post("/api/orders", status_code=201)
def create_order(data: dict, user = Depends(require_auth)):
    items = data.get("items", [])
    if not items: raise HTTPException(400, "items is required")
    total = 0.0
    order_items = []
    for it in items:
        pid = it.get("product_id")
        qty = it.get("quantity", 1)
        if qty <= 0: raise HTTPException(400, f"quantity must be > 0 for product {pid}")
        p = next((x for x in products if x["id"] == pid), None)
        if not p: raise HTTPException(404, f"Product {pid} not found")
        if p["stock"] < qty: raise HTTPException(400, f"Insufficient stock for {p['name']}: need {qty}, have {p['stock']}")
        p["stock"] -= qty
        order_items.append({"product_id": pid, "quantity": qty, "unit_price": p["price"]})
        total += p["price"] * qty
    o = {"id": str(uuid.uuid4())[:8], "user_id": user["id"], "items": order_items,
         "total": round(total, 2), "status": "created", "created": datetime.now().isoformat(),
         "updated": datetime.now().isoformat()}
    orders.append(o)
    return o

@app.get("/api/orders/{oid}")
def get_order(oid: str, user = Depends(require_auth)):
    o = next((x for x in orders if x["id"] == oid), None)
    if not o: raise HTTPException(404, "Order not found")
    if user["role"] != "admin" and o["user_id"] != user["id"]:
        raise HTTPException(403, "Access denied")
    return o

@app.put("/api/orders/{oid}/status")
def transition_order(oid: str, data: dict, user = Depends(require_auth)):
    o = next((x for x in orders if x["id"] == oid), None)
    if not o: raise HTTPException(404, "Order not found")
    if user["role"] != "admin" and o["user_id"] != user["id"]:
        raise HTTPException(403, "Access denied")
    new_status = data.get("status")
    if new_status not in VALID_STATUSES: raise HTTPException(400, f"Invalid status: {new_status}")
    allowed = STATUS_TRANSITIONS.get(o["status"], [])
    if new_status not in allowed: raise HTTPException(400, f"Cannot transition from {o['status']} to {new_status}. Allowed: {allowed}")
    if new_status == "cancelled":
        for it in o["items"]:
            p = next((x for x in products if x["id"] == it["product_id"]), None)
            if p: p["stock"] += it["quantity"]
    o["status"] = new_status
    o["updated"] = datetime.now().isoformat()
    return o

@app.delete("/api/orders/{oid}", status_code=204)
def cancel_order(oid: str, user = Depends(require_auth)):
    o = next((x for x in orders if x["id"] == oid), None)
    if not o: raise HTTPException(404, "Order not found")
    if o["status"] not in ("created", "confirmed"): raise HTTPException(400, "Only created/confirmed orders can be cancelled")
    for it in o["items"]:
        p = next((x for x in products if x["id"] == it["product_id"]), None)
        if p: p["stock"] += it["quantity"]
    o["status"] = "cancelled"
    o["updated"] = datetime.now().isoformat()
    return {}

# ===== Refund Endpoints =====
@app.post("/api/refunds", status_code=201)
def create_refund(data: dict, user = Depends(require_auth)):
    oid = data.get("order_id")
    o = next((x for x in orders if x["id"] == oid), None)
    if not o: raise HTTPException(404, "Order not found")
    if o["status"] not in ("paid", "shipped", "delivered"): raise HTTPException(400, f"Cannot refund order in status {o['status']}")
    if user["role"] != "admin" and o["user_id"] != user["id"]:
        raise HTTPException(403, "Access denied")
    amount = data.get("amount", o["total"])
    if amount <= 0: raise HTTPException(400, "Refund amount must be > 0")
    if amount > o["total"]: raise HTTPException(400, f"Refund amount {amount} exceeds order total {o['total']}")
    r = {"id": str(uuid.uuid4())[:8], "order_id": oid, "reason": data.get("reason", ""),
         "amount": amount, "status": "pending", "created": datetime.now().isoformat()}
    refunds.append(r)
    return r

@app.get("/api/refunds")
def list_refunds(user = Depends(require_auth)):
    if user["role"] == "admin": return refunds
    return [r for r in refunds if any(o["id"] == r["order_id"] and o["user_id"] == user["id"] for o in orders)]

@app.put("/api/refunds/{rid}/approve")
def approve_refund(rid: str, user = Depends(require_admin)):
    r = next((x for x in refunds if x["id"] == rid), None)
    if not r: raise HTTPException(404, "Refund not found")
    if r["status"] != "pending": raise HTTPException(400, f"Refund already {r['status']}")
    r["status"] = "approved"
    o = next((x for x in orders if x["id"] == r["order_id"]), None)
    if o: o["status"] = "cancelled"
    return r

@app.put("/api/refunds/{rid}/reject")
def reject_refund(rid: str, user = Depends(require_admin)):
    r = next((x for x in refunds if x["id"] == rid), None)
    if not r: raise HTTPException(404, "Refund not found")
    if r["status"] != "pending": raise HTTPException(400, f"Refund already {r['status']}")
    r["status"] = "rejected"
    return r

# ===== Stats =====
@app.get("/api/stats")
def get_stats():
    total_revenue = sum(o["total"] for o in orders if o["status"] not in ("cancelled",))
    return {
        "total_products": len(products),
        "total_orders": len(orders),
        "total_revenue": round(total_revenue, 2),
        "orders_by_status": {s: sum(1 for o in orders if o["status"] == s) for s in VALID_STATUSES},
        "low_stock_products": [p["name"] for p in products if p["stock"] < 20],
        "pending_refunds": sum(1 for r in refunds if r["status"] == "pending"),
    }

# ===== Info =====
@app.get("/api/info")
def info(): return {
    "service": "E-Commerce Order System v2.0",
    "auth": "JWT Bearer Token",
    "roles": ["admin", "operator", "viewer"],
    "endpoints": ["/api/auth/login", "/api/products", "/api/orders", "/api/refunds", "/api/stats"]
}

# ===== Users (pre-seeded) =====
users = [
    {"id":"u1","username":"admin","password":"Test123!","role":"admin","created":"2026-01-01"},
    {"id":"u2","username":"operator","password":"Test123!","role":"operator","created":"2026-01-01"},
    {"id":"u3","username":"viewer","password":"Test123!","role":"viewer","created":"2026-01-01"},
]

# ===== HTML Dashboard =====
INDEX_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>E-Commerce Order System v2.0</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:#0a0e27;color:#e2e8f0;min-height:100vh}
.top{background:linear-gradient(135deg,#1a1f3a,#2a2f5a);padding:32px 24px;text-align:center;border-bottom:2px solid #3a3f6a}
.top h1{font-size:28px;color:#5b8dee}.top p{color:#8899bb;margin-top:6px;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:16px;padding:24px;max-width:1200px;margin:0 auto}
.card{background:#121836;border-radius:12px;padding:20px;border:1px solid #2a2f5a}
.card h2{font-size:16px;color:#5b8dee;margin-bottom:12px;display:flex;align-items:center;gap:8px}
.meth{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;min-width:48px;text-align:center}
.m-GET{background:#0a3d2e;color:#4ade80}.m-POST{background:#162d5a;color:#93c5fd}
.m-PUT{background:#4a3510;color:#fbbf24}.m-DELETE{background:#5a1a1a;color:#fca5a5}
.endpoint{display:flex;align-items:center;justify-content:space-between;padding:10px 12px;background:#0a0e27;border-radius:8px;margin:6px 0;font-family:monospace;font-size:13px}
.endpoint span{color:#8899bb}
.endpoint button{background:#1a1f3a;color:#e2e8f0;border:1px solid #3a3f6a;padding:5px 12px;border-radius:6px;cursor:pointer;font-size:12px;transition:.2s}
.endpoint button:hover{background:#2a2f5a;border-color:#5b8dee}
.result{margin-top:10px;padding:10px;background:#0a0e27;border-radius:8px;font-family:monospace;font-size:12px;max-height:300px;overflow:auto;white-space:pre-wrap;display:none}
.result.ok{border-left:3px solid #4ade80}.result.err{border-left:3px solid #fca5a5}
.stats{display:flex;gap:12px;flex-wrap:wrap;margin-top:12px}
.stat{background:#0a0e27;padding:10px 16px;border-radius:8px;text-align:center;min-width:80px}
.stat .n{font-size:24px;font-weight:700;color:#5b8dee}.stat .l{font-size:11px;color:#8899bb}
</style></head>
<body>
<div class="top">
<h1>E-Commerce Order System v2.0</h1>
<p>Enterprise Mock API — JWT Auth · Role-based Access · Order Workflow · Refund Management</p>
</div>
<div class="grid">
<div class="card">
<h2>Auth</h2>
<div class="endpoint"><span class="meth m-POST">POST</span><span>/api/auth/login</span><button onclick="callAPI('POST','/api/auth/login',this,'{"username":"admin","password":"Test123!"}')">登录</button></div>
<div class="endpoint"><span class="meth m-GET">GET</span><span>/api/auth/me</span><button onclick="callAPI('GET','/api/auth/me',this)">当前用户</button></div>
<div id="res-auth" class="result"></div>
</div>
<div class="card">
<h2>Products</h2>
<div class="endpoint"><span class="meth m-GET">GET</span><span>/api/products</span><button onclick="callAPI('GET','/api/products',this)">测试</button></div>
<div class="endpoint"><span class="meth m-POST">POST</span><span>/api/products</span><button onclick="callAPI('POST','/api/products',this,'{"name":"New Product","price":99,"stock":50}')">测试</button></div>
<div class="endpoint"><span class="meth m-GET">GET</span><span>/api/products/{id}</span><button onclick="callAPI('GET','/api/products/p1',this)">测试</button></div>
<div class="endpoint"><span class="meth m-PUT">PUT</span><span>/api/products/{id}</span><button onclick="callAPI('PUT','/api/products/p1',this,'{"price":109}')">测试</button></div>
<div id="res-products" class="result"></div>
</div>
<div class="card">
<h2>Orders</h2>
<div class="endpoint"><span class="meth m-GET">GET</span><span>/api/orders</span><button onclick="callAPI('GET','/api/orders',this)">测试</button></div>
<div class="endpoint"><span class="meth m-POST">POST</span><span>/api/orders</span><button onclick="callAPI('POST','/api/orders',this,'{"items":[{"product_id":"p1","quantity":1}]}')">测试</button></div>
<div class="endpoint"><span class="meth m-PUT">PUT</span><span>/api/orders/{id}/status</span><button onclick="callAPI('PUT','/api/orders/o1/status',this,'{"status":"confirmed"}')">测试</button></div>
<div id="res-orders" class="result"></div>
</div>
<div class="card">
<h2>Refunds / Stats</h2>
<div class="endpoint"><span class="meth m-POST">POST</span><span>/api/refunds</span><button onclick="callAPI('POST','/api/refunds',this,'{"order_id":"o1","reason":"defect"}')">测试</button></div>
<div class="endpoint"><span class="meth m-GET">GET</span><span>/api/stats</span><button onclick="callAPI('GET','/api/stats',this)">统计</button></div>
<div id="res-refunds" class="result"></div>
<div id="live-stats" class="stats"></div>
</div>
</div>
<script>
var _token = '';
function callAPI(m, path, btn, body) {
var res = document.getElementById('res-'+(path.includes('auth')?'auth':path.includes('product')?'products':path.includes('order')?'orders':'refunds'));
res.style.display='block';res.className='result';res.textContent='请求中...';
try {
var opts={method:m,headers:{}};
if(body){opts.headers['Content-Type']='application/json';opts.body=body;}
if(_token) opts.headers['Authorization']='Bearer '+_token;
var r=await fetch(path,opts);
var t=await r.text();
try{var j=JSON.parse(t);t=JSON.stringify(j,null,2);
if(path=='/api/auth/login'&&j.token){_token=j.token;document.querySelectorAll('.card h2').forEach(function(h){if(h.textContent=='Auth')h.textContent='Auth ✓'})}
if(path=='/api/stats')loadStats(j);
}catch(e){}
res.className='result '+(r.ok?'ok':'err');
res.textContent=r.status+' '+r.statusText+'\\n\\n'+t;
}catch(e){res.className='result err';res.textContent='Error: '+e.message}
}
function loadStats(d){if(!d)return;
var h='<div class="stat"><div class="n">'+d.total_products+'</div><div class="l">Products</div></div><div class="stat"><div class="n">'+d.total_orders+'</div><div class="l">Orders</div></div><div class="stat"><div class="n">'+d.total_revenue+'</div><div class="l">Revenue</div></div>';
if(d.orders_by_status)Object.entries(d.orders_by_status).forEach(function(e){h+='<div class="stat"><div class="n">'+e[1]+'</div><div class="l">'+e[0]+'</div></div>'});
document.getElementById('live-stats').innerHTML=h;
}
fetch('/api/stats').then(r=>r.json()).then(loadStats);
</script>
<footer style="text-align:center;padding:24px;color:#64748b;font-size:12px">
<a href="/" style="color:#5b8dee">Dashboard</a> &middot;
<a href="/docs" style="color:#5b8dee">OpenAPI Docs</a> &middot;
<a href="/api/info" style="color:#5b8dee">API Info</a>
</footer></body></html>"""

@app.get("/", response_class=HTMLResponse)
def index(): return INDEX_HTML

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
