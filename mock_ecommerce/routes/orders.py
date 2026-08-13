"""Order routes — create, status transition, stock management."""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from auth import require_auth, require_operator
from models import OrderCreate, StatusTransition, _store, now, gen_id, VALID_ORDER_STATUSES, STATUS_TRANSITIONS

router = APIRouter(prefix="/api/orders", tags=["Orders"])

@router.get("")
def list_orders(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
                status: Optional[str] = None, user = Depends(require_auth)):
    result = _store["orders"]
    if user["role"] != "admin":
        result = [o for o in result if o["user_id"] == user["id"]]
    if status:
        if status not in VALID_ORDER_STATUSES: raise HTTPException(400, f"无效状态: {status}")
        result = [o for o in result if o["status"] == status]
    total = len(result)
    return {"data": result[(page-1)*limit:page*limit], "page": page, "limit": limit, "total": total}

@router.post("", status_code=201)
def create_order(body: OrderCreate, user = Depends(require_operator)):
    total = 0.0
    order_items = []
    products_snapshot = {}  # pid -> product dict
    for it in body.items:
        p = next((x for x in _store["products"] if x["id"] == it.product_id), None)
        if not p: raise HTTPException(404, f"商品 {it.product_id} 不存在")
        if p["stock"] < it.quantity:
            raise HTTPException(400, f"商品 [{p['name']}] 库存不足: 需要 {it.quantity}, 当前 {p['stock']}")
        p["stock"] -= it.quantity
        p["updated"] = now()
        unit_price = p["price"]
        order_items.append({"product_id": it.product_id, "quantity": it.quantity, "unit_price": unit_price})
        total += unit_price * it.quantity
    o = {"id": gen_id(), "user_id": user["id"], "items": order_items, "total": round(total, 2),
         "status": "created", "created": now(), "updated": now()}
    _store["orders"].append(o)
    return o

@router.get("/{oid}")
def get_order(oid: str, user = Depends(require_auth)):
    o = next((x for x in _store["orders"] if x["id"] == oid), None)
    if not o: raise HTTPException(404, "订单不存在")
    if user["role"] != "admin" and o["user_id"] != user["id"]:
        raise HTTPException(403, "无权查看此订单")
    return o

@router.put("/{oid}/status")
def transition_order(oid: str, body: StatusTransition, user = Depends(require_operator)):
    o = next((x for x in _store["orders"] if x["id"] == oid), None)
    if not o: raise HTTPException(404, "订单不存在")
    if user["role"] != "admin" and o["user_id"] != user["id"]:
        raise HTTPException(403, "无权操作此订单")
    new_status = body.status
    if new_status not in VALID_ORDER_STATUSES:
        raise HTTPException(400, f"无效状态: {new_status}. 有效值: {VALID_ORDER_STATUSES}")
    allowed = STATUS_TRANSITIONS.get(o["status"], [])
    if new_status not in allowed:
        raise HTTPException(400, f"不允许从 [{o['status']}] 转换到 [{new_status}]. 允许: {allowed}")
    if new_status == "cancelled":
        for it in o["items"]:
            p = next((x for x in _store["products"] if x["id"] == it["product_id"]), None)
            if p:
                p["stock"] += it["quantity"]
                p["updated"] = now()
    o["status"] = new_status
    o["updated"] = now()
    return o

@router.post("/{oid}/status")
def transition_order_post(oid: str, body: StatusTransition, user = Depends(require_operator)):
    return transition_order(oid, body, user)

@router.delete("/{oid}", status_code=204)
def cancel_order(oid: str, user = Depends(require_operator)):
    o = next((x for x in _store["orders"] if x["id"] == oid), None)
    if not o: raise HTTPException(404, "订单不存在")
    if user["role"] != "admin" and o["user_id"] != user["id"]:
        raise HTTPException(403, "无权操作此订单")
    if o["status"] not in ("created", "confirmed"):
        raise HTTPException(400, f"订单状态为 [{o['status']}]，不可取消")
    for it in o["items"]:
        p = next((x for x in _store["products"] if x["id"] == it["product_id"]), None)
        if p:
            p["stock"] += it["quantity"]
            p["updated"] = now()
    o["status"] = "cancelled"
    o["updated"] = now()

@router.post("/{oid}/cancel", status_code=204)
def cancel_order_post(oid: str, user = Depends(require_operator)):
    return cancel_order(oid, user)
