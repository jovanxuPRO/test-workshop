"""Refund routes."""
from fastapi import APIRouter, Depends, HTTPException
from auth import require_auth, require_admin
from models import RefundCreate, _store, now, gen_id

VALID_REFUND_STATUSES = ["pending", "approved", "rejected"]

router = APIRouter(prefix="/api/refunds", tags=["Refunds"])

@router.post("", status_code=201)
def create_refund(body: RefundCreate, user = Depends(require_auth)):
    o = next((x for x in _store["orders"] if x["id"] == body.order_id), None)
    if not o: raise HTTPException(404, "订单不存在")
    if o["status"] not in ("paid", "shipped", "delivered"):
        raise HTTPException(400, f"订单状态 [{o['status']}] 不允许退款")
    if user["role"] != "admin" and o["user_id"] != user["id"]:
        raise HTTPException(403, "无权申请退款")
    amount = body.amount if body.amount is not None else o["total"]
    if amount <= 0: raise HTTPException(400, "退款金额必须 > 0")
    if amount > o["total"]: raise HTTPException(400, f"退款金额 {amount} 超过订单总额 {o['total']}")
    if body.status and body.status not in VALID_REFUND_STATUSES:
        raise HTTPException(400, f"无效的退款状态: {body.status}，有效值: {', '.join(VALID_REFUND_STATUSES)}")
    r = {"id": gen_id(), "order_id": body.order_id, "reason": body.reason, "amount": amount,
         "status": "pending", "created": now()}
    _store["refunds"].append(r)
    return r

@router.get("")
def list_refunds(user = Depends(require_auth)):
    if user["role"] == "admin": return _store["refunds"]
    return [r for r in _store["refunds"] if any(o["id"] == r["order_id"] and o["user_id"] == user["id"] for o in _store["orders"])]

@router.put("/{rid}/approve")
def approve_refund(rid: str, user = Depends(require_admin)):
    r = next((x for x in _store["refunds"] if x["id"] == rid), None)
    if not r: raise HTTPException(404, "退款单不存在")
    if r["status"] != "pending": raise HTTPException(400, f"退款已{r['status']}")
    r["status"] = "approved"
    o = next((x for x in _store["orders"] if x["id"] == r["order_id"]), None)
    if o:
        o["status"] = "cancelled"
        for it in o.get("items", []):
            p = next((x for x in _store["products"] if x["id"] == it["product_id"]), None)
            if p: p["stock"] += it["quantity"]
    return r

@router.put("/{rid}/reject")
def reject_refund(rid: str, user = Depends(require_admin)):
    r = next((x for x in _store["refunds"] if x["id"] == rid), None)
    if not r: raise HTTPException(404, "退款单不存在")
    if r["status"] != "pending": raise HTTPException(400, f"退款已{r['status']}")
    r["status"] = "rejected"
    return r
