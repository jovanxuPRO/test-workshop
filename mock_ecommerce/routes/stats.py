"""Dashboard stats routes."""
from fastapi import APIRouter, Depends
from auth import require_auth
from models import _store

router = APIRouter(prefix="/api/stats", tags=["Stats"])

@router.get("")
def get_stats(user = Depends(require_auth)):
    orders = _store["orders"]
    revenue = sum(o["total"] for o in orders if o["status"] not in ("cancelled",))
    return {
        "total_products": len(_store["products"]),
        "total_orders": len(orders),
        "total_revenue": round(revenue, 2),
        "orders_by_status": {s: sum(1 for o in orders if o["status"] == s) for s in ["created","confirmed","paid","shipped","delivered","cancelled"]},
        "low_stock_products": [p["name"] for p in _store["products"] if p["stock"] < 20],
        "pending_refunds": sum(1 for r in _store["refunds"] if r["status"] == "pending"),
        "pending_refund_amount": sum(r["amount"] for r in _store["refunds"] if r["status"] == "pending"),
    }
