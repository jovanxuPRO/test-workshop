"""Product CRUD routes."""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from auth import require_admin, require_auth
from models import ProductCreate, ProductUpdate, _store, gen_id, now

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("")
def list_products(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
                  category: Optional[str] = None, search: Optional[str] = None,
                  user = Depends(require_auth)):
    result = _store["products"]
    if category: result = [p for p in result if p["category"] == category]
    if search: result = [p for p in result if search.lower() in p["name"].lower()]
    total = len(result)
    return {"data": result[(page-1)*limit:page*limit], "page": page, "limit": limit, "total": total}

@router.post("", status_code=201)
def create_product(body: ProductCreate, user = Depends(require_admin)):
    p = {"id": gen_id(), "name": body.name, "price": body.price, "stock": body.stock,
         "category": body.category, "created": now(), "updated": now()}
    _store["products"].append(p)
    return p

@router.get("/{pid}")
def get_product(pid: str, user = Depends(require_auth)):
    p = next((x for x in _store["products"] if x["id"] == pid), None)
    if not p: raise HTTPException(404, "商品不存在")
    return p

@router.put("/{pid}")
def update_product(pid: str, body: ProductUpdate, user = Depends(require_admin)):
    p = next((x for x in _store["products"] if x["id"] == pid), None)
    if not p: raise HTTPException(404, "商品不存在")
    for k, v in body.model_dump(exclude_unset=True).items():
        p[k] = v
    p["updated"] = now()
    return p

@router.delete("/{pid}", status_code=204)
def delete_product(pid: str, user = Depends(require_admin)):
    before = len(_store["products"])
    _store["products"] = [x for x in _store["products"] if x["id"] != pid]
    if len(_store["products"]) == before: raise HTTPException(404, "商品不存在")
