# API Quick Reference Guide

## Authentication Flow Summary

### New User Signup Flow
```
1. POST /apis/auth/send-otp/          → Send OTP to phone
2. POST /apis/auth/verify-otp/        → Verify OTP
3. POST /apis/auth/signup/            → Complete signup with details
   ✓ Returns JWT tokens
```

### Existing User Login Flow
```
1. POST /apis/auth/login/             → Login with phone & password
   ✓ Returns JWT tokens
```

---

## API Endpoints Quick Reference

### 1. Send OTP
```http
POST /apis/auth/send-otp/
Content-Type: application/json

{
  "phoneNumber": "+919876543210"
}
```

### 2. Verify OTP
```http
POST /apis/auth/verify-otp/
Content-Type: application/json

{
  "phoneNumber": "+919876543210",
  "otp": "123456"
}
```
**Returns:** `is_new_user` flag to determine next step

### 3. Complete Signup (New Users Only)
```http
POST /apis/auth/signup/
Content-Type: application/json

{
  "phoneNumber": "+919876543210",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "password": "SecurePassword123"
}
```
**Returns:** JWT tokens + user data


### 4. Login (Existing Users Only)
```http
POST /apis/auth/login/
Content-Type: application/json

{
  "phoneNumber": "+919876543210",
  "password": "SecurePassword123"
}
```
**Returns:** JWT tokens + user data

---

## Response Structure

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "errors": {
    "field": ["error message"]
  }
}
```

---

## Using JWT Tokens

### Protected Requests
```http
GET /apis/auth/update-profile/
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Token Response Format
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",  // Short-lived
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...", // Long-lived
  "userId": "uuid-here"
}
```

---

## Key Features

✅ **OTP Validation Required** - Phone verification mandatory before signup
✅ **Password Encryption** - PBKDF2 SHA256 with 600,000 iterations
✅ **JWT Authentication** - Secure token-based auth
✅ **10-Minute OTP Expiry** - Enhanced security
✅ **Required Fields** - firstName, lastName, email, phoneNumber, password
✅ **Email Uniqueness** - Each email can only be registered once
✅ **Phone Uniqueness** - Each phone can only be registered once

---

## Testing Endpoints

### Using cURL

**Send OTP:**
```bash
curl -X POST http://localhost:8000/apis/auth/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phoneNumber": "+919876543210"}'
```

**Verify OTP:**
```bash
curl -X POST http://localhost:8000/apis/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{"phoneNumber": "+919876543210", "otp": "123456"}'
```

**Signup:**
```bash
curl -X POST http://localhost:8000/apis/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "phoneNumber": "+919876543210",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/apis/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"phoneNumber": "+919876543210", "password": "SecurePass123"}'
```

---

## Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Invalid OTP or phone number" | Wrong OTP or phone | Check OTP/phone and retry |
| "OTP has expired" | OTP older than 10 min | Request new OTP |
| "Phone number not verified" | Skipped OTP step | Complete OTP verification |
| "User already exists" | Phone already registered | Use login instead |
| "Email already registered" | Email already used | Use different email |
| "Invalid phone number or password" | Wrong credentials | Check and retry |

---

## Validation Rules

### Phone Number
- Minimum 10 digits
- Can include country code and special characters
- Must be unique

### Email
- Valid email format
- Must be unique

### Password
- Minimum 6 characters
- Stored as encrypted hash (NEVER plain text)

### Names
- Maximum 25 characters each
- Both firstName and lastName required

---

## Security Features

🔒 **Password Hashing** - Django's built-in PBKDF2
🔒 **OTP Expiry** - 10-minute validity
🔒 **Phone Verification** - Mandatory OTP validation
🔒 **JWT Tokens** - Secure authentication
🔒 **Email Validation** - Prevents duplicate accounts
🔒 **Account Status Checks** - Verifies active/verified status

---

For detailed documentation, see: **AUTH_API_DOCUMENTATION.md**
