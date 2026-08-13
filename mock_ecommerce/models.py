"""Data models and in-memory store for E-Commerce system."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid
import hashlib
import os

def hash_pw(pw: str) -> str:
    salt = os.urandom(16).hex()
    return salt + ":" + hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 100_000).hex()

def verify_pw(stored: str, pw: str) -> bool:
    salt, h = stored.split(":", 1)
    return h == hashlib.pbkdf2_hmac("sha256", pw.encode(), salt.encode(), 100_000).hex()

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
    reason: str = Field(default="", max_length=500)
    amount: Optional[float] = None
    status: Optional[str] = None

# Data store (in-memory, pre-seeded)
_store = {
    "users": [
        {"id":"u001","username":"admin","password":"cd5e2681b60e722fd18600c883a51948:4d35abb979d4e2605e8d78e8385715bf711505bdf9fae75a5d6fe2f88b4692a5","role":"admin","name":"系统管理员","created":"2026-01-01T00:00:00"},
        {"id":"u002","username":"operator","password":"0cd0f786ab03da101e2dfbe03609b7d8:a249e2f0c5af138e876f29cde568b8f58fe8ae750734e76292b909bb1efd0722","role":"operator","name":"运营小王","created":"2026-01-01T00:00:00"},
        {"id":"u003","username":"viewer","password":"92d8c8f70f8818fea645682217a32880:ea4e66bbdfb87bd8227e18f2c21ad6f32ee478501e7f8ce226bde050b2ce9cec","role":"viewer","name":"财务小张","created":"2026-01-01T00:00:00"},
    ],
    "products": [
        {"id":"1","name":"机械键盘 K8 Pro","price":599.00,"stock":120,"category":"外设","created":"2026-01-01T00:00:00","updated":"2026-01-01T00:00:00"},
        {"id":"2","name":"4K显示器 27寸 IPS","price":2999.00,"stock":35,"category":"显示","created":"2026-01-01T00:00:00","updated":"2026-01-01T00:00:00"},
        {"id":"3","name":"人体工学椅 Pro","price":1899.00,"stock":18,"category":"家具","created":"2026-01-02T00:00:00","updated":"2026-01-02T00:00:00"},
        {"id":"4","name":"USB-C 扩展坞 12合1","price":299.00,"stock":200,"category":"配件","created":"2026-01-03T00:00:00","updated":"2026-01-03T00:00:00"},
        {"id":"5","name":"无线鼠标 MX Master","price":449.00,"stock":88,"category":"外设","created":"2026-01-04T00:00:00","updated":"2026-01-04T00:00:00"},
    ],
    "orders": [
        {"id":"1","user_id":"u001","items":[{"product_id":"1","quantity":1,"unit_price":599.00},{"product_id":"5","quantity":2,"unit_price":449.00}],"total":1497.00,"status":"delivered","created":"2026-01-10T00:00:00","updated":"2026-01-13T00:00:00"},
        {"id":"2","user_id":"u002","items":[{"product_id":"2","quantity":1,"unit_price":2999.00}],"total":2999.00,"status":"shipped","created":"2026-01-12T00:00:00","updated":"2026-01-14T00:00:00"},
        {"id":"3","user_id":"u001","items":[{"product_id":"3","quantity":1,"unit_price":1899.00}],"total":1899.00,"status":"paid","created":"2026-01-14T00:00:00","updated":"2026-01-14T00:00:00"},
    ],
    "refunds": [
        {"id":"1","order_id":"1","reason":"键盘按键失灵","amount":599.00,"status":"approved","created":"2026-01-15T00:00:00"},
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
