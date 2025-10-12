# Cart & Wishlist API Reference

## Authentication

**All APIs require JWT token authentication** using the `Authorization` header:

```
Authorization: Bearer <your_jwt_token>
```

## Base URL
- Local: `http://localhost:8000/api/transactions/`
- Production: `http://3.110.46.10/api/transactions/`

---

# Wishlist APIs

## 1. Get User's Wishlist

**Endpoint:** `GET /wishlist/<user_id>/`

**Authorization:** ✅ Required (IsAuthenticated)

**Permission Check:** User can only view their own wishlist (unless admin/staff)

**URL Parameters:**
- `user_id` (UUID, required): User's unique identifier

**Response:**
```json
{
    "success": true,
    "data": [
        {
            "wishlistId": "uuid",
            "product": {
                "productId": "uuid",
                "name": "Product Name",
                "price": 999.99,
                "discountedPrice": 899.99
            },
            "createdAt": "2025-10-12T10:30:00Z"
        }
    ],
    "count": 1
}
```

---

## 2. Add Product to Wishlist

**Endpoint:** `POST /wishlist/add/`

**Authorization:** ✅ Required (IsAuthenticated)

**Request Body:**
```json
{
    "product_id": "uuid-of-product"
}
```

**Response (Success):**
```json
{
    "success": true,
    "message": "Product added to wishlist successfully",
    "data": {
        "wishlistId": "uuid",
        "product": {
            "productId": "uuid",
            "name": "Product Name",
            "price": 999.99,
            "discountedPrice": 899.99
        },
        "createdAt": "2025-10-12T10:30:00Z"
    }
}
```

**Response (Error - Already in Wishlist):**
```json
{
    "success": false,
    "error": "Product already in wishlist"
}
```

**Response (Error - Product Not Found):**
```json
{
    "success": false,
    "errors": {
        "product_id": ["Product does not exist."]
    }
}
```

---

## 3. Remove Product from Wishlist

**Endpoint:** `DELETE /wishlist/<user_id>/remove/<product_id>/`

**Authorization:** ✅ Required (IsAuthenticated)

**Permission Check:** User can only remove from their own wishlist (unless admin/staff)

**URL Parameters:**
- `user_id` (UUID, required): User's unique identifier
- `product_id` (UUID, required): Product's unique identifier

**Response (Success):**
```json
{
    "success": true,
    "message": "Product removed from wishlist successfully"
}
```

**Response (Error - Not Found):**
```json
{
    "success": false,
    "error": "Item not found in wishlist"
}
```

---

## 4. Clear User's Wishlist

**Endpoint:** `DELETE /wishlist/<user_id>/clear/`

**Authorization:** ✅ Required (IsAuthenticated)

**Permission Check:** User can only clear their own wishlist (unless admin/staff)

**URL Parameters:**
- `user_id` (UUID, required): User's unique identifier

**Response:**
```json
{
    "success": true,
    "message": "Wishlist cleared successfully. 5 items removed."
}
```

---

# Cart APIs

## 1. Get User's Cart

**Endpoint:** `GET /cart/<user_id>/`

**Authorization:** ✅ Required (IsAuthenticated)

**Permission Check:** User can only view their own cart (unless admin/staff)

**URL Parameters:**
- `user_id` (UUID, required): User's unique identifier

**Response:**
```json
{
    "success": true,
    "data": {
        "cartId": "uuid",
        "user": "user-uuid",
        "items": [
            {
                "id": 123,
                "product": {
                    "productId": "uuid",
                    "name": "Product Name",
                    "price": 999.99,
                    "discountedPrice": 899.99,
                    "image": "http://example.com/image.jpg",
                    "isActive": true
                },
                "quantity": 2,
                "unit_price": 899.99,
                "total_price": 1799.98,
                "addedAt": "2025-10-12T10:30:00Z",
                "updatedAt": "2025-10-12T10:30:00Z"
            }
        ],
        "total_items": 2,
        "total_amount": 1799.98,
        "items_count": 1,
        "createdAt": "2025-10-12T10:00:00Z",
        "updatedAt": "2025-10-12T10:30:00Z"
    },
    "is_new_cart": false
}
```

---

## 2. Add Item to Cart

**Endpoint:** `POST /cart/add/` or `POST /cart/add`

**Authorization:** ✅ Required (IsAuthenticated)

**Permission Check:** User can only add to their own cart (unless admin/staff)

**Request Body:**
```json
{
    "user_id": "uuid-of-user",
    "product_id": "uuid-of-product",
    "quantity": 2
}
```

**Field Validations:**
- `user_id` (UUID, required): Must be a valid user
- `product_id` (UUID, required): Must be a valid and active product
- `quantity` (integer, optional): Min=1, Max=999, Default=1

**Response (Success - New Item):**
```json
{
    "success": true,
    "message": "Item added to cart successfully",
    "data": {
        "cartId": "uuid",
        "items": [...],
        "total_items": 2,
        "total_amount": 1799.98
    }
}
```

**Response (Success - Updated Quantity):**
```json
{
    "success": true,
    "message": "Updated quantity to 5",
    "data": {
        "cartId": "uuid",
        "items": [...],
        "total_items": 5,
        "total_amount": 4499.95
    }
}
```

**Response (Error - Out of Stock):**
```json
{
    "success": false,
    "errors": {
        "non_field_errors": ["Only 3 items available in stock."]
    }
}
```

**Response (Error - Product Not Active):**
```json
{
    "success": false,
    "errors": {
        "product_id": ["Product is not available."]
    }
}
```

---

## 3. Update Cart Item Quantity

**Endpoint:** `PUT /cart/<user_id>/update/<item_id>/`

**Authorization:** ✅ Required (IsAuthenticated)

**Permission Check:** User can only update their own cart (unless admin/staff)

**URL Parameters:**
- `user_id` (UUID, required): User's unique identifier
- `item_id` (integer, required): Cart item ID (not product ID)

**Request Body:**
```json
{
    "quantity": 5
}
```

**Field Validations:**
- `quantity` (integer, required): Min=1, Max=999

**Response (Success):**
```json
{
    "success": true,
    "message": "Cart item updated successfully",
    "data": {
        "cartId": "uuid",
        "items": [...],
        "total_items": 5,
        "total_amount": 4499.95
    }
}
```

**Response (Error - Not Found):**
```json
{
    "success": false,
    "error": "Cart item not found"
}
```

**Response (Error - Out of Stock):**
```json
{
    "success": false,
    "errors": {
        "quantity": ["Only 3 items available in stock."]
    }
}
```

---

## 4. Remove Item from Cart

**Endpoint:** `DELETE /cart/<user_id>/remove/<item_id>/`

**Authorization:** ✅ Required (IsAuthenticated)

**Permission Check:** User can only remove from their own cart (unless admin/staff)

**URL Parameters:**
- `user_id` (UUID, required): User's unique identifier
- `item_id` (integer, required): Cart item ID (not product ID)

**Response (Success):**
```json
{
    "success": true,
    "message": "Product Name removed from cart successfully"
}
```

**Response (Error - Not Found):**
```json
{
    "success": false,
    "error": "Cart item not found"
}
```

---

## 5. Clear User's Cart

**Endpoint:** `DELETE /cart/<user_id>/clear/`

**Authorization:** ✅ Required (IsAuthenticated)

**Permission Check:** User can only clear their own cart (unless admin/staff)

**URL Parameters:**
- `user_id` (UUID, required): User's unique identifier

**Response (Success):**
```json
{
    "success": true,
    "message": "Cart cleared successfully. 3 items removed."
}
```

**Response (Already Empty):**
```json
{
    "success": true,
    "message": "Cart is already empty"
}
```

---

# Common Error Responses

## 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

## 403 Forbidden
```json
{
    "error": "Permission denied"
}
```

## 404 Not Found
```json
{
    "success": false,
    "error": "User does not exist."
}
```

---

# Example cURL Commands

## Wishlist Examples

### Get Wishlist
```bash
curl -X GET "http://3.110.46.10/api/transactions/wishlist/{user_id}/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Add to Wishlist
```bash
curl -X POST "http://3.110.46.10/api/transactions/wishlist/add/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "123e4567-e89b-12d3-a456-426614174000"
  }'
```

### Remove from Wishlist
```bash
curl -X DELETE "http://3.110.46.10/api/transactions/wishlist/{user_id}/remove/{product_id}/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Clear Wishlist
```bash
curl -X DELETE "http://3.110.46.10/api/transactions/wishlist/{user_id}/clear/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Cart Examples

### Get Cart
```bash
curl -X GET "http://3.110.46.10/api/transactions/cart/{user_id}/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Add to Cart
```bash
curl -X POST "http://3.110.46.10/api/transactions/cart/add/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "product_id": "987e6543-e21b-12d3-a456-426614174000",
    "quantity": 2
  }'
```

### Update Cart Item
```bash
curl -X PUT "http://3.110.46.10/api/transactions/cart/{user_id}/update/{item_id}/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 5
  }'
```

### Remove from Cart
```bash
curl -X DELETE "http://3.110.46.10/api/transactions/cart/{user_id}/remove/{item_id}/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Clear Cart
```bash
curl -X DELETE "http://3.110.46.10/api/transactions/cart/{user_id}/clear/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

---

# Important Notes

## Authorization Summary
✅ **All APIs require JWT authentication** - No anonymous access allowed

## Permission Levels
1. **User Access**: Users can only access their own wishlist/cart
2. **Admin/Staff Access**: Admin users can access any user's data

## Key Differences: Cart vs Wishlist

### Cart Item Identification
- Cart items use **integer item_id** (auto-increment primary key)
- When updating/removing cart items, use the `item_id` from the cart response

### Wishlist Item Identification
- Wishlist uses **product_id** (UUID) directly
- No separate item ID concept

## Data Relationships

### Cart Structure
```
Cart (one per user)
  └── CartItem (multiple items)
       └── Product (reference)
```

### Wishlist Structure
```
Wishlist Items (multiple per user)
  └── Product (reference)
```

## Stock Validation
- Cart APIs validate product stock availability
- Adding items that exceed stock will fail with error message
- Stock check happens on both add and update operations

## Price Calculation
- `unit_price`: Current product price (at time of adding to cart)
- `total_price`: unit_price × quantity
- If product has discount > 0: discountedPrice = price - discount

---

**Last Updated:** October 12, 2025
**API Version:** 1.0
**Django Version:** 4.2+
