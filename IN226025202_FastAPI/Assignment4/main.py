from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field
main =FastAPI()
app = FastAPI()
 
# ══ PYDANTIC MODELS ═══════════════════════════════════════════════
 
class OrderRequest(BaseModel): # Day 2
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)
 
class NewProduct(BaseModel): # Day 4
    name: str = Field(..., min_length=2, max_length=100)
    price: int = Field(..., gt=0)
    category: str = Field(..., min_length=2)
    in_stock: bool = True
 
# ══ DATA ══════════════════════════════════════════════════════════
 
products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price': 499, 'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook', 'price': 99, 'category': 'Stationery', 'in_stock': True},
    {'id': 3, 'name': 'USB Hub', 'price': 799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set', 'price': 49, 'category': 'Stationery', 'in_stock': True},
]
 
orders = []
order_counter = 1
 
# ══ HELPER FUNCTIONS ══════════════════════════════════════════════
 
def find_product(product_id: int):
    """Search products list by ID. Returns product dict or None."""
    for p in products:
        if p['id'] == product_id:
            return p
    return None
 
def calculate_total(product: dict, quantity: int) -> int:
    """Multiply price by quantity and return total."""
    return product['price'] * quantity
 
def filter_products_logic(category=None, min_price=None,
                          max_price=None, in_stock=None):
    """Apply filters and return matching products."""
    result = products
    if category is not None:
        result = [p for p in result if p['category'] == category]
    if min_price is not None:
        result = [p for p in result if p['price'] >= min_price]
    if max_price is not None:
        result = [p for p in result if p['price'] <= max_price]
    if in_stock is not None:
        result = [p for p in result if p['in_stock'] == in_stock]
    return result
 
# ══ ENDPOINTS ═════════════════════════════════════════════════════
#
# ROUTE ORDER RULE — FastAPI reads top to bottom, first match wins.
# Fixed routes (/filter /compare /audit /discount) BEFORE variable (/{product_id})
#
# ══════════════════════════════════════════════════════════════════
 
# ── DAY 1 ─────────────────────────────────────────────────────────
 
@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}
 
@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}
 
# ── DAY 2 — Filter ────────────────────────────────────────────────
 
@app.get('/products/filter')
def filter_products(
    category: str = Query(None, description='Electronics or Stationery'),
    min_price: int = Query(None, description='Minimum price'),
    max_price: int = Query(None, description='Maximum price'),
    in_stock: bool = Query(None, description='True = in stock only'),
):
    result = filter_products_logic(category, min_price, max_price, in_stock)
    return {'filtered_products': result, 'count': len(result)}
 
# ── DAY 3 — Compare ───────────────────────────────────────────────
 
@app.get('/products/compare')
def compare_products(
    product_id_1: int = Query(..., description='First product ID'),
    product_id_2: int = Query(..., description='Second product ID'),
):
    p1 = find_product(product_id_1)
    p2 = find_product(product_id_2)
    if not p1:
        return {'error': f'Product {product_id_1} not found'}
    if not p2:
        return {'error': f'Product {product_id_2} not found'}
    cheaper = p1 if p1['price'] < p2['price'] else p2
    return {
        'product_1': p1,
        'product_2': p2,
        'better_value': cheaper['name'],
        'price_diff': abs(p1['price'] - p2['price']),
    }
 
# ── DAY 4 — Step 18: Add a new product (POST) ─────────────────────
 
@app.post('/products')
def add_product(new_product: NewProduct, response: Response):
    # Check for duplicate name (case-insensitive)
    existing_names = [p['name'].lower() for p in products]
    if new_product.name.lower() in existing_names:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Product with this name already exists'}
 
    # Auto-generate next ID
    next_id = max(p['id'] for p in products) + 1
 
    product = {
        'id': next_id,
        'name': new_product.name,
        'price': new_product.price,
        'category': new_product.category,
        'in_stock': new_product.in_stock,
    }
    products.append(product)
    response.status_code = status.HTTP_201_CREATED
    return {'message': 'Product added', 'product': product}
 
# ── DAY 4 — Step 19: Update stock or price (PUT) ──────────────────
 
@app.put('/products/{product_id}')
def update_product(
    product_id: int,
    response: Response,
    in_stock: bool = Query(None, description='Update stock status'),
    price: int = Query(None, description='Update price'),
):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}
 
    if in_stock is not None: # must use 'is not None' — False is a valid value
        product['in_stock'] = in_stock
    if price is not None:
        product['price'] = price
 
    return {'message': 'Product updated', 'product': product}
 
# ── DAY 4 — Step 20: Delete a product (DELETE) ────────────────────
 
@app.delete('/products/{product_id}')
def delete_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}
 
    products.remove(product)
    return {'message': f"Product '{product['name']}' deleted"}
#DAY2
#TASK2
#PROBLEM1
from fastapi import FastAPI, Query

app = FastAPI()

# Sample product list
products = [
    {"name": "Wireless Mouse", "price": 499, "category": "electronics"},
    {"name": "USB Hub", "price": 799, "category": "electronics"},
    {"name": "Notebook", "price": 99, "category": "stationery"},
]

@app.get("/products/filter")
def filter_products(
    category: str = Query(None, description="Filter by category"),
    max_price: int = Query(None, description="Maximum price"),
    min_price: int = Query(None, description="Minimum price")
):
    # Start with all products
    result = products

    # Filter by category
    if category:
        result = [p for p in result if p["category"] == category]

    # Filter by maximum price
    if max_price:
        result = [p for p in result if p["price"] <= max_price]

    # Filter by minimum price
    if min_price:
        result = [p for p in result if p["price"] >= min_price]

    return result
    #PROBLEM2
    from fastapi import FastAPI

app = FastAPI()

# Sample product list with IDs
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "electronics"},
    {"id": 2, "name": "Notebook", "price": 99, "category": "stationery"},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "electronics"},
]

@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return {"name": product["name"], "price": product["price"]}
    return {"error": "Product not found"}
   #PROBLEM3
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# Sample product list with IDs
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "electronics"},
    {"id": 2, "name": "Notebook", "price": 99, "category": "stationery"},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "electronics"},
]

# Feedback storage
feedback = []

# Pydantic model for customer feedback
class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=100)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):
    feedback.append(data.dict())
    return {
        "message": "Feedback submitted successfully",
        "feedback": data.dict(),
        "total_feedback": len(feedback),
    }
#PROBLEM4
from fastapi import FastAPI

app = FastAPI()

# Example product data
products = [
    {"name": "USB Hub", "price": 799, "in_stock": True,  "category": "Electronics"},
    {"name": "Pen Set", "price": 49,  "in_stock": True,  "category": "Stationery"},
    {"name": "Notebook", "price": 199, "in_stock": False, "category": "Stationery"},
    {"name": "Wireless Mouse", "price": 499, "in_stock": True, "category": "Electronics"},
]

@app.get("/products/summary")
def product_summary():
    in_stock   = [p for p in products if     p["in_stock"]]
    out_stock  = [p for p in products if not p["in_stock"]]
    expensive  = max(products, key=lambda p: p["price"])
    cheapest   = min(products, key=lambda p: p["price"])
    categories = list(set(p["category"] for p in products))

    return {
        "total_products":     len(products),
        "in_stock_count":     len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive":     {"name": expensive["name"], "price": expensive["price"]},
        "cheapest":           {"name": cheapest["name"],  "price": cheapest["price"]},
        "categories":         categories,
    }
    #PROBLEM5
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

app = FastAPI()

# Example product data with IDs
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "in_stock": True},
    {"id": 2, "name": "Notebook",       "price": 199, "in_stock": False},
    {"id": 3, "name": "USB Hub",        "price": 799, "in_stock": False},
    {"id": 4, "name": "Pen Set",        "price": 49,  "in_stock": True},
]

# OrderItem model
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=50)

#  BulkOrder model
class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_items=1)

#  Bulk Order Endpoint
@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):
    confirmed, failed, grand_total = [], [], 0

    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
        elif not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal
            confirmed.append({"product": product["name"], "qty": item.quantity, "subtotal": subtotal})

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total,
    }
    #BONUS
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List

app = FastAPI()

# In-memory store for orders
orders = []
order_counter = 1

# Example product data
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "in_stock": True},
    {"id": 2, "name": "Notebook",       "price": 199, "in_stock": False},
    {"id": 3, "name": "USB Hub",        "price": 799, "in_stock": False},
    {"id": 4, "name": "Pen Set",        "price": 49,  "in_stock": True},
]

# Models
class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem] = Field(..., min_items=1)

# POST /orders → new orders start as "pending"
@app.post("/orders")
def place_order(order: BulkOrder):
    global order_counter
    confirmed, failed, grand_total = [], [], 0

    for item in order.items:
        product = next((p for p in products if p["id"] == item.product_id), None)
        if not product:
            failed.append({"product_id": item.product_id, "reason": "Product not found"})
        elif not product["in_stock"]:
            failed.append({"product_id": item.product_id, "reason": f"{product['name']} is out of stock"})
        else:
            subtotal = product["price"] * item.quantity
            grand_total += subtotal
            confirmed.append({"product": product["name"], "qty": item.quantity, "subtotal": subtotal})

    new_order = {
        "order_id": order_counter,
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total,
        "status": "pending"   #  start as pending
    }
    orders.append(new_order)
    order_counter += 1
    return {"message": "Order placed", "order": new_order}

# GET /orders/{order_id} → fetch order by ID
@app.get("/orders/{order_id}")
def get_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            return {"order": order}
    return {"error": "Order not found"}

# PATCH /orders/{order_id}/confirm → change status to confirmed
@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):
    for order in orders:
        if order["order_id"] == order_id:
            order["status"] = "confirmed"
            return {"message": "Order confirmed", "order": order}
    return {"error": "Order not found"}
# GET all pending orders
@app.get("/orders/pending")
def get_pending_orders():
    pending = [order for order in orders if order["status"] == "pending"]
    return {"pending_orders": pending}    
####DAY 4
##TASK 4
##PROBLEM 1
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Product catalog
products = {
    1: {"name": "Wireless Mouse", "price": 499, "stock": 10},
    2: {"name": "Notebook", "price": 99, "stock": 5},
    3: {"name": "USB Hub", "price": 299, "stock": 0},   # out of stock
    4: {"name": "Pen Set", "price": 49, "stock": 10}
}

# Global state (resets on server restart)
cart = []
orders = []
order_id_counter = 1


# Add items to cart
@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int):
    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")

    product = products[product_id]
    if product["stock"] <= 0:
        raise HTTPException(status_code=400, detail=f"{product['name']} is out of stock")

    # Check if already in cart
    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            item["subtotal"] = item["quantity"] * product["price"]
            return {"message": "Cart updated", "cart_item": item}

    # New item
    subtotal = quantity * product["price"]
    cart_item = {
        "product_id": product_id,
        "product_name": product["name"],
        "quantity": quantity,
        "unit_price": product["price"],
        "subtotal": subtotal
    }
    cart.append(cart_item)
    return {"message": "Added to cart", "cart_item": cart_item}


#  View cart
@app.get("/cart")
def view_cart():
    if not cart:
        return {"detail": "Cart is empty"}
    grand_total = sum(item["subtotal"] for item in cart)
    return {"items": cart, "item_count": len(cart), "grand_total": grand_total}


#  Remove item
@app.delete("/cart/{product_id}")
def remove_item(product_id: int):
    global cart
    before_count = len(cart)
    cart = [item for item in cart if item["product_id"] != product_id]
    if len(cart) == before_count:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    return {"message": f"Product {product_id} removed from cart"}


# Checkout
@app.post("/cart/checkout")
def checkout(customer_name: str, delivery_address: str):
    global cart, orders, order_id_counter

    # Bonus: empty cart check
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty — add items first")

    placed_orders = []
    for item in cart:
        order = {
            "order_id": order_id_counter,
            "customer_name": customer_name,
            "delivery_address": delivery_address,
            "product": item["product_name"],
            "quantity": item["quantity"],
            "subtotal": item["subtotal"]
        }
        orders.append(order)
        placed_orders.append(order)
        order_id_counter += 1

    cart.clear()
    return {"message": "Order placed successfully", "orders_placed": placed_orders}


#  View orders
@app.get("/orders")
def view_orders():
    return {"orders": orders, "total_orders": len(orders)}