# 🛍️ FastAPI Fashion Store Backend

## 🚀 Project Overview
This project is a complete backend system built using FastAPI as part of a FastAPI Internship Final Project.

It simulates a real-world fashion store where users can:
- Browse products
- Place orders
- Manage wishlist
- Perform advanced search, sorting, and pagination

---

## 🧩 Features Implemented

### ✅ Day 1 — GET APIs
- Home route (`/`)
- Get all products (`/products`)
- Get product by ID (`/products/{product_id}`)
- Products summary (`/products/summary`)
- Get all orders (`/orders`)

---

### ✅ Day 2 — POST + Pydantic Validation
- Order creation using Pydantic model
- Field validations:
  - Minimum length
  - Greater than (gt)
  - Less than equal (le)
- Proper error handling for invalid input

---

### ✅ Day 3 — Helper Functions & Filtering
- `find_product()` → Find product by ID
- `calculate_order_total()` → Price calculation with:
  - Season discount
  - Bulk discount
  - Gift wrap charges
- `filter_products_logic()` → Filtering using query params

---

### ✅ Day 4 — CRUD Operations
- Add product (`POST /products`)
- Update product (`PUT /products/{product_id}`)
- Delete product (`DELETE /products/{product_id}`)
- Proper status codes:
  - 201 Created
  - 404 Not Found
  - 400 Bad Request

---

### ✅ Day 5 — Multi-Step Workflow
Wishlist system:
- Add to wishlist (`/wishlist/add`)
- Remove from wishlist (`/wishlist/remove`)
- Order all wishlist items (`/wishlist/order-all`)

---

### ✅ Day 6 — Advanced APIs
- Search products (`/products/search`)
- Sort products (`/products/sort`)
- Pagination (`/products/page`)
- Combined browsing (`/products/browse`)

---

## 📦 Tech Stack
- Python
- FastAPI
- Pydantic
- Uvicorn

---

## ▶️ How to Run the Project

### 1️⃣ Install dependencies
```bash
pip install -r requirements.txt

2️⃣ Run the server
uvicorn main:app --reload

3️⃣ Open Swagger UI
http://127.0.0.1:8000/docs