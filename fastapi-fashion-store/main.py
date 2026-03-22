from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI()

# ---------------- DATA ----------------

products = [
    {"id": 1, "name": "Casual Shirt", "brand": "Zara", "category": "Shirt", "price": 1200, "sizes_available": ["S","M","L"], "in_stock": True},
    {"id": 2, "name": "Blue Jeans", "brand": "Levis", "category": "Jeans", "price": 2000, "sizes_available": ["M","L"], "in_stock": True},
    {"id": 3, "name": "Running Shoes", "brand": "Nike", "category": "Shoes", "price": 3500, "sizes_available": ["8","9","10"], "in_stock": True},
    {"id": 4, "name": "Summer Dress", "brand": "H&M", "category": "Dress", "price": 1800, "sizes_available": ["S","M"], "in_stock": False},
    {"id": 5, "name": "Winter Jacket", "brand": "Puma", "category": "Jacket", "price": 4000, "sizes_available": ["L","XL"], "in_stock": True},
    {"id": 6, "name": "Formal Shirt", "brand": "Arrow", "category": "Shirt", "price": 1500, "sizes_available": ["M","L","XL"], "in_stock": True}
]

orders = []
wishlist = []
order_counter = 1
product_counter = 7

# ---------------- HELPERS ----------------

def find_product(product_id):
    for p in products:
        if p["id"] == product_id:
            return p
    return None

def calculate_order_total(price, quantity, gift_wrap, season_sale):
    base = price * quantity

    season_discount = 0
    bulk_discount = 0
    gift_charge = 0

    if season_sale:
        season_discount = 0.15 * base
        base -= season_discount

    if quantity >= 5:
        bulk_discount = 0.05 * base
        base -= bulk_discount

    if gift_wrap:
        gift_charge = 50 * quantity
        base += gift_charge

    return {
        "final_total": int(base),
        "season_discount": int(season_discount),
        "bulk_discount": int(bulk_discount),
        "gift_charge": gift_charge
    }

def filter_products_logic(category=None, brand=None, max_price=None, in_stock=None):
    result = products

    if category is not None:
        result = [p for p in result if p["category"].lower() == category.lower()]

    if brand is not None:
        result = [p for p in result if p["brand"].lower() == brand.lower()]

    if max_price is not None:
        result = [p for p in result if p["price"] <= max_price]

    if in_stock is not None:
        result = [p for p in result if p["in_stock"] == in_stock]

    return result

# ---------------- DAY 1 ----------------

@app.get("/")
def home():
    return {"message": "Welcome to TrendZone Fashion Store"}

@app.get("/products")
def get_products():
    total = len(products)
    in_stock_count = len([p for p in products if p["in_stock"]])
    return {"products": products, "total": total, "in_stock_count": in_stock_count}

@app.get("/products/summary")
def summary():
    total = len(products)
    in_stock = len([p for p in products if p["in_stock"]])
    out_stock = total - in_stock
    brands = list(set(p["brand"] for p in products))

    category_count = {}
    for p in products:
        category_count[p["category"]] = category_count.get(p["category"], 0) + 1

    return {
        "total": total,
        "in_stock": in_stock,
        "out_of_stock": out_stock,
        "brands": brands,
        "category_count": category_count
    }

@app.get("/products/filter")
def filter_products(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    max_price: Optional[int] = None,
    in_stock: Optional[bool] = None
):
    result = filter_products_logic(category, brand, max_price, in_stock)
    return {"results": result, "count": len(result)}

@app.get("/products/search")
def search_products(keyword: str):
    result = [p for p in products if keyword.lower() in (p["name"] + p["brand"] + p["category"]).lower()]
    if not result:
        return {"message": "No products found"}
    return {"results": result, "total_found": len(result)}

@app.get("/products/sort")
def sort_products(sort_by: str = "price", order: str = "asc"):
    valid_fields = ["price", "name", "brand", "category"]
    if sort_by not in valid_fields:
        raise HTTPException(400, "Invalid sort field")

    reverse = True if order == "desc" else False
    sorted_list = sorted(products, key=lambda x: x[sort_by], reverse=reverse)

    return {"sorted_by": sort_by, "order": order, "data": sorted_list}

@app.get("/products/page")
def paginate_products(page: int = 1, limit: int = 3):
    total = len(products)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    return {
        "page": page,
        "total_pages": total_pages,
        "data": products[start:end]
    }

@app.get("/products/browse")
def browse(
    keyword: Optional[str] = None,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    in_stock: Optional[bool] = None,
    max_price: Optional[int] = None,
    sort_by: str = "price",
    order: str = "asc",
    page: int = 1,
    limit: int = 3
):
    result = products

    if keyword:
        result = [p for p in result if keyword.lower() in (p["name"] + p["brand"] + p["category"]).lower()]

    result = filter_products_logic(category, brand, max_price, in_stock)

    reverse = True if order == "desc" else False
    result = sorted(result, key=lambda x: x[sort_by], reverse=reverse)

    total = len(result)
    total_pages = (total + limit - 1) // limit

    start = (page - 1) * limit
    end = start + limit

    return {
        "total": total,
        "page": page,
        "total_pages": total_pages,
        "results": result[start:end]
    }

@app.get("/products/{product_id}")
def get_product(product_id: int):
    product = find_product(product_id)
    if not product:
        raise HTTPException(404, "Product not found")
    return product

# ---------------- DAY 2–4 ----------------

class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    size: str = Field(..., min_length=1)
    quantity: int = Field(..., gt=0, le=10)
    delivery_address: str = Field(..., min_length=10)
    gift_wrap: bool = False
    season_sale: bool = False

@app.get("/orders")
def get_orders():
    total = len(orders)
    revenue = sum(o["total_cost"] for o in orders)
    return {"orders": orders, "total": total, "total_revenue": revenue}

@app.post("/orders", status_code=201)
def create_order(order: OrderRequest):
    global order_counter

    product = find_product(order.product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    if not product["in_stock"]:
        raise HTTPException(400, "Out of stock")

    if order.size not in product["sizes_available"]:
        raise HTTPException(400, f"Available sizes: {product['sizes_available']}")

    calc = calculate_order_total(product["price"], order.quantity, order.gift_wrap, order.season_sale)

    new_order = {
        "order_id": order_counter,
        "customer_name": order.customer_name,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "size": order.size,
        "total_cost": calc["final_total"]
    }

    orders.append(new_order)
    order_counter += 1

    return {"order": new_order, "breakdown": calc}

# ---------------- CRUD ----------------

class NewProduct(BaseModel):
    name: str = Field(..., min_length=2)
    brand: str = Field(..., min_length=2)
    category: str = Field(..., min_length=2)
    price: int = Field(..., gt=0)
    sizes_available: List[str]
    in_stock: bool = True

@app.post("/products", status_code=201)
def add_product(p: NewProduct):
    global product_counter

    for prod in products:
        if prod["name"] == p.name and prod["brand"] == p.brand:
            raise HTTPException(400, "Product already exists")

    new = p.dict()
    new["id"] = product_counter
    product_counter += 1

    products.append(new)
    return new

@app.put("/products/{product_id}")
def update_product(product_id: int, price: Optional[int] = None, in_stock: Optional[bool] = None):
    product = find_product(product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    if price is not None:
        product["price"] = price
    if in_stock is not None:
        product["in_stock"] = in_stock

    return product

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    product = find_product(product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    for o in orders:
        if o["product_id"] == product_id:
            raise HTTPException(400, "Cannot delete product with orders")

    products.remove(product)
    return {"message": "Deleted successfully"}

# ---------------- WORKFLOW ----------------

@app.post("/wishlist/add")
def add_wishlist(customer_name: str, product_id: int, size: str):
    product = find_product(product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    if size not in product["sizes_available"]:
        raise HTTPException(400, "Invalid size")

    for w in wishlist:
        if w["customer_name"] == customer_name and w["product_id"] == product_id and w["size"] == size:
            raise HTTPException(400, "Already exists")

    wishlist.append({"customer_name": customer_name, "product_id": product_id, "size": size})
    return {"message": "Added to wishlist"}

@app.get("/wishlist")
def get_wishlist():
    total_value = 0
    for w in wishlist:
        p = find_product(w["product_id"])
        if p:
            total_value += p["price"]

    return {"wishlist": wishlist, "total_value": total_value}

@app.delete("/wishlist/remove")
def remove_wishlist(customer_name: str, product_id: int):
    for w in wishlist:
        if w["customer_name"] == customer_name and w["product_id"] == product_id:
            wishlist.remove(w)
            return {"message": "Removed"}
    raise HTTPException(404, "Not found")

@app.post("/wishlist/order-all", status_code=201)
def order_all(customer_name: str, delivery_address: str):
    global order_counter

    user_items = [w for w in wishlist if w["customer_name"] == customer_name]

    if not user_items:
        raise HTTPException(400, "Wishlist empty")

    confirmations = []
    total = 0

    for item in user_items:
        p = find_product(item["product_id"])
        calc = calculate_order_total(p["price"], 1, False, False)

        new_order = {
            "order_id": order_counter,
            "customer_name": customer_name,
            "product_id": p["id"],
            "quantity": 1,
            "size": item["size"],
            "total_cost": calc["final_total"]
        }

        orders.append(new_order)
        confirmations.append(new_order)
        total += calc["final_total"]
        order_counter += 1

    wishlist[:] = [w for w in wishlist if w["customer_name"] != customer_name]

    return {"orders": confirmations, "grand_total": total}