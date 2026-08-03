"""E-Commerce Order System — Enterprise Mock Server
Start: python mock_ecommerce/server.py
Serves: REST API + Frontend pages on http://localhost:8000
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routes.auth_routes import router as auth_router
from routes.products import router as product_router
from routes.orders import router as order_router
from routes.refunds import router as refund_router
from routes.stats import router as stats_router

app = FastAPI(title="E-Commerce Order System v2.0", docs_url="/docs", redoc_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(auth_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(refund_router)
app.include_router(stats_router)

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def index(): return FileResponse(os.path.join(static_dir, "dashboard.html"))

@app.get("/login")
def login_page(): return FileResponse(os.path.join(static_dir, "login.html"))

@app.get("/products")
def products_page(): return FileResponse(os.path.join(static_dir, "products.html"))

@app.get("/orders")
def orders_page(): return FileResponse(os.path.join(static_dir, "orders.html"))

@app.get("/api/info")
def info():
    return {"service": "E-Commerce Order System v2.0", "auth": "JWT Bearer", "roles": ["admin","operator","viewer"],
            "endpoints": ["/api/auth/login","/api/products","/api/orders","/api/refunds","/api/stats"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
