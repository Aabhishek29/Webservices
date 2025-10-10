# E-Commerce Model Analysis & Issues Found

## Critical Issues Found

### 1. **CartItem Model - Line 56 (transactions/models.py)**
**Issue**: References `self.product.name` but Products model has `productName`
```python
# WRONG:
def __str__(self):
    return f"{self.product.name} x {self.quantity}"

# CORRECT:
def __str__(self):
    return f"{self.product.productName} x {self.quantity}"
```

### 2. **Wishlist Model - Line 81 (transactions/models.py)**
**Issue**: References `self.product.name` but Products model has `productName`
```python
# WRONG:
def __str__(self):
    return f'{self.user} - {self.product.name}'

# CORRECT:
def __str__(self):
    return f'{self.user} - {self.product.productName}'
```

### 3. **OrderItem Model - Line 211 (transactions/models.py)**
**Issue**: References `self.product.name` and `self.product.sku`
```python
# WRONG:
self.productName = self.product.name
if hasattr(self.product, 'sku'):
    self.productSku = self.product.sku

# CORRECT:
self.productName = self.product.productName
self.productSku = self.product.SKU  # Products model has 'SKU' field
```

### 4. **Products Model - Missing Stock Field**
**Issue**: Serializers and views reference `product.stock` but it doesn't exist
- ProductStockModel exists but no direct `stock` field on Products
- Need to add a property or method to get total stock

### 5. **Cart Model - Line 23 (transactions/models.py)**
**Issue**: References `self.user.username` but Users model doesn't have username field
```python
# WRONG:
return f"Cart - {self.user.username if hasattr(self.user, 'username') else self.user}"

# CORRECT:
return f"Cart - {self.user.phoneNumber}"
```

## Model Relationship Issues

### 1. **Users Model - Not using Django's Authentication**
**Problem**: Custom Users model but not extending AbstractBaseUser properly
- Has `USERNAME_FIELD = 'phoneNumber'` but not used in auth system
- Missing `is_superuser` field for Django admin
- Missing `last_login` field

### 2. **Products - Stock Management**
**Problem**: Stock is tracked in ProductStockModel (by size/color) but no easy way to check total stock
**Solution**: Add property to Products model

### 3. **Transaction - User Field Redundancy**
**Issue**: Transaction has both `user` and `order` (which already has `user`)
- Redundant data
- Could lead to inconsistency

## E-Commerce Logic Issues

### 1. **No Stock Validation in Cart**
- CartItem doesn't check stock before adding
- Users can add unlimited quantity

### 2. **No Price Snapshot in CartItem**
- If product price changes, cart total changes
- Should snapshot price when added to cart

### 3. **Order Creation Missing Steps**
**Missing**:
- Clear cart after order
- Reduce stock after order
- Send order confirmation

### 4. **Discount Calculation Issues**
Products model has both:
- `discount` (amount)
- `discountPerc` (percentage)

Which one to use? Inconsistent.

### 5. **No Product Reviews/Ratings**
Standard e-commerce feature missing

### 6. **No Coupon/Promo Code System**
Order has `discountAmount` but no way to apply coupons

## Missing E-Commerce Features

1. **Product Variants**
   - Size/Color should be proper variants, not just stock tracking

2. **Order Cancellation Logic**
   - Can cancel order but no refund process

3. **Return/Exchange Management**
   - Status exists but no return model

4. **Shipping Integration**
   - No shipping carrier integration
   - No shipping rate calculation

5. **Inventory Management**
   - No low stock alerts
   - No reorder points

## Recommendations

### Immediate Fixes Required:
1. Fix all `.name` → `.productName` references
2. Fix `.sku` → `.SKU` references
3. Fix `user.username` → `user.phoneNumber` references
4. Add `total_stock` property to Products model
5. Add stock validation in cart operations

### Short-term Improvements:
1. Price snapshot in CartItem
2. Stock reduction on order
3. Proper discount calculation logic
4. Add indexes on frequently queried fields

### Long-term Enhancements:
1. Proper product variants system
2. Reviews and ratings
3. Coupon system
4. Shipping integration
5. Inventory alerts
