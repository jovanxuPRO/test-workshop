"""Data models and in-memory store for E-Commerce system."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class LoginRequest(BaseModel):
    username: str
    password: str

class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)
    stock: int = Field(ge=0)
    category: str = "未分类"

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = None

class OrderItem(BaseModel):
    product_id: str
    quantity: int = Field(gt=0)

class OrderCreate(BaseModel):
    items: list[OrderItem]

class StatusTransition(BaseModel):
    status: str

class RefundCreate(BaseModel):
    order_id: str
    reason: str = ""
    amount: Optional[float] = None

# Data store (in-memory, pre-seeded)
_store = {
    "users": [
        {"id":"u001","username":"admin","password":"Admin@123","role":"admin","name":"系统管理员","created":"2026-01-01T00:00:00"},
        {"id":"u002","username":"operator","password":"Oper@123","role":"operator","name":"运营小王","created":"2026-01-01T00:00:00"},
        {"id":"u003","username":"viewer","password":"View@123","role":"viewer","name":"财务小张","created":"2026-01-01T00:00:00"},
    ],
    "products": [
        {"id":"p001","name":"机械键盘 K8 Pro","price":599.00,"stock":120,"category":"外设","created":"2026-01-01T00:00:00","updated":"2026-01-01T00:00:00"},
        {"id":"p002","name":"4K显示器 27寸 IPS","price":2999.00,"stock":35,"category":"显示","created":"2026-01-01T00:00:00","updated":"2026-01-01T00:00:00"},
        {"id":"p003","name":"人体工学椅 Pro","price":1899.00,"stock":18,"category":"家具","created":"2026-01-02T00:00:00","updated":"2026-01-02T00:00:00"},
        {"id":"p004","name":"USB-C 扩展坞 12合1","price":299.00,"stock":200,"category":"配件","created":"2026-01-03T00:00:00","updated":"2026-01-03T00:00:00"},
        {"id":"p005","name":"无线鼠标 MX Master","price":449.00,"stock":88,"category":"外设","created":"2026-01-04T00:00:00","updated":"2026-01-04T00:00:00"},
    ],
    "orders": [
        {"id":"o001","user_id":"u001","items":[{"product_id":"p001","quantity":1,"unit_price":599.00},{"product_id":"p005","quantity":2,"unit_price":449.00}],"total":1497.00,"status":"delivered","created":"2026-01-10T00:00:00","updated":"2026-01-13T00:00:00"},
        {"id":"o002","user_id":"u002","items":[{"product_id":"p002","quantity":1,"unit_price":2999.00}],"total":2999.00,"status":"shipped","created":"2026-01-12T00:00:00","updated":"2026-01-14T00:00:00"},
        {"id":"o003","user_id":"u001","items":[{"product_id":"p003","quantity":1,"unit_price":1899.00}],"total":1899.00,"status":"paid","created":"2026-01-14T00:00:00","updated":"2026-01-14T00:00:00"},
    ],
    "refunds": [
        {"id":"r001","order_id":"o001","reason":"键盘按键失灵","amount":599.00,"status":"approved","created":"2026-01-15T00:00:00"},
    ],
}

VALID_ORDER_STATUSES = ["created","confirmed","paid","shipped","delivered","cancelled"]
STATUS_TRANSITIONS = {
    "created":   ["confirmed","cancelled"],
    "confirmed": ["paid","cancelled"],
    "paid":      ["shipped"],
    "shipped":   ["delivered"],
    "delivered": [],
    "cancelled": [],
}

def now(): return datetime.now().isoformat()
def gen_id(): return str(uuid.uuid4())[:12]
