# Authentication API Documentation

## Overview
This document provides complete documentation for the authentication APIs including signup, login, and OTP verification flows.

## Base URL
```
http://localhost:8000  # Development
https://your-domain.com  # Production
```

---

## Authentication Flow

### New User Flow:
1. **Send OTP** → User receives OTP on mobile
2. **Verify OTP** → OTP is validated
3. **Complete Signup** → User provides details (firstName, lastName, email, password)
4. **Receive JWT Tokens** → User is authenticated

### Existing User Flow:
1. **Login** → User provides phoneNumber and password
2. **Receive JWT Tokens** → User is authenticated

---

## API Endpoints

### 1. Send OTP

**Endpoint:** `POST /apis/auth/send-otp/`

**Description:** Sends a 6-digit OTP to the provided phone number. Creates a user record if it doesn't exist.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "phoneNumber": "+919876543210"
}
```

**Success Response (200 OK):**
```json
{
  "message": "OTP sent successfully",
  "success": true
}
```

**Error Response (400 Bad Request):**
```json
{
  "phoneNumber": [
    "Phone number must be at least 10 digits"
  ]
}
```

**Notes:**
- Phone number can be in any format with country code
- OTP is valid for 10 minutes
- OTP will be sent via SMS (implementation in utils.py)

---

### 2. Verify OTP

**Endpoint:** `POST /apis/auth/verify-otp/`

**Description:** Verifies the OTP sent to the phone number. Returns information about whether the user is new or existing.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "phoneNumber": "+919876543210",
  "otp": "123456"
}
```

**Success Response (200 OK):**
```json
{
  "message": "OTP verified successfully",
  "data": {
    "userId": "eb951e75-c19b-4b91-935e-xxxxxx",
    "phoneNumber": "+919876543210",
    "is_new_user": true
  },
  "success": true
}
```

**Fields Explanation:**
- `is_new_user`: `true` if user needs to complete signup, `false` if user should login

**Error Responses:**

**Invalid OTP (400 Bad Request):**
```json
{
  "success": false,
  "errors": {
    "error": "Invalid OTP or phone number"
  }
}
```

**Expired OTP (400 Bad Request):**
```json
{
  "success": false,
  "errors": {
    "error": "OTP has expired. Please request a new one."
  }
}
```

**Notes:**
- OTP expires after 10 minutes
- After successful verification, phone is marked as verified
- OTP is cleared from database after verification

---

### 3. Complete Signup

**Endpoint:** `POST /apis/auth/signup/`

**Description:** Completes user registration after OTP verification. Creates user with all details and encrypted password.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "phoneNumber": "+919876543210",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@example.com",
  "password": "SecurePassword123"
}
```

**Field Requirements:**
- `phoneNumber`: Required, must be verified via OTP first
- `firstName`: Required, max 25 characters
- `lastName`: Required, max 25 characters
- `email`: Required, must be valid email format, must be unique
- `password`: Required, minimum 6 characters

**Success Response (201 Created):**
```json
{
  "message": "Signup successful",
  "success": true,
  "data": {
    "userId": "eb951e75-c19b-4b91-935e-xxxxxx",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "userId": "eb951e75-c19b-4b91-935e-xxxxxx",
      "firstName": "John",
      "lastName": "Doe",
      "email": "john.doe@example.com",
      "phoneNumber": "+919876543210",
      "is_verified": true,
      "is_active": true,
      "createdAt": "2025-10-10T10:30:00Z",
      "updatedAt": "2025-10-10T10:30:00Z"
    }
  }
}
```

**Error Responses:**

**Phone Not Verified (400 Bad Request):**
```json
{
  "success": false,
  "errors": {
    "phoneNumber": [
      "Phone number not verified. Please verify OTP first."
    ]
  }
}
```

**User Already Exists (400 Bad Request):**
```json
{
  "success": false,
  "errors": {
    "phoneNumber": [
      "User already exists. Please login instead."
    ]
  }
}
```

**Email Already Registered (400 Bad Request):**
```json
{
  "success": false,
  "errors": {
    "email": [
      "Email already registered."
    ]
  }
}
```

**Password Too Short (400 Bad Request):**
```json
{
  "success": false,
  "errors": {
    "password": [
      "Ensure this field has at least 6 characters."
    ]
  }
}
```

**Notes:**
- Password is automatically hashed using Django's built-in password hashing (PBKDF2 algorithm)
- User receives JWT access and refresh tokens upon successful signup
- Success SMS is sent to the phone number
- The password is NEVER stored in plain text

---

### 4. Login

**Endpoint:** `POST /apis/auth/login/`

**Description:** Authenticates existing user with phone number and password.

**Request Headers:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "phoneNumber": "+919876543210",
  "password": "SecurePassword123"
}
```

**Success Response (200 OK):**
```json
{
  "message": "Login successful",
  "success": true,
  "data": {
    "userId": "eb951e75-c19b-4b91-935e-xxxxxx",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "userId": "eb951e75-c19b-4b91-935e-xxxxxx",
      "firstName": "John",
      "lastName": "Doe",
      "email": "john.doe@example.com",
      "phoneNumber": "+919876543210",
      "is_verified": true,
      "is_active": true,
      "createdAt": "2025-10-10T10:30:00Z",
      "updatedAt": "2025-10-10T10:30:00Z"
    }
  }
}
```

**Error Responses:**

**Invalid Credentials (400 Bad Request):**
```json
{
  "success": false,
  "errors": {
    "error": "Invalid phone number or password"
  }
}
```

**Incomplete Signup (400 Bad Request):**
```json
{
  "success": false,
  "errors": {
    "error": "Please complete signup process first"
  }
}
```

**Phone Not Verified (400 Bad Request):**
```json
{
  "success": false,
  "errors": {
    "error": "Phone number not verified"
  }
}
```

**Account Deactivated (400 Bad Request):**
```json
{
  "success": false,
  "errors": {
    "error": "Account is deactivated"
  }
}
```

**Notes:**
- Password is verified using secure password checking
- Returns JWT tokens on successful login
- All error messages are intentionally generic for security

---

## JWT Token Usage

After successful signup or login, you receive two tokens:

### Access Token
- Used for authenticating API requests
- Short-lived (typically 5-60 minutes)
- Include in Authorization header: `Bearer <access_token>`

### Refresh Token
- Used to get new access tokens
- Long-lived (typically 1-7 days)
- Store securely on client

### Using Access Token

**Request Header:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Example Protected Endpoint:**
```bash
curl -X GET http://localhost:8000/apis/auth/update-profile/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
  -H "Content-Type: application/json"
```

---

## Password Security

### Encryption Method
- Passwords are hashed using Django's default password hasher
- Algorithm: PBKDF2 with SHA256 hash
- 600,000 iterations (Django 5.x default)
- Each password has a unique salt

### Password Storage Format
```
pbkdf2_sha256$600000$<salt>$<hash>
```

### Security Features
- Passwords are NEVER stored in plain text
- Each password has a unique salt
- Computationally expensive to crack (600,000 iterations)
- Uses industry-standard cryptographic algorithms
- Automatic password strength validation (minimum 6 characters)

---

## Complete User Flow Examples

### Example 1: New User Registration

**Step 1: Send OTP**
```bash
curl -X POST http://localhost:8000/apis/auth/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "phoneNumber": "+919876543210"
  }'
```

**Step 2: Verify OTP**
```bash
curl -X POST http://localhost:8000/apis/auth/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "phoneNumber": "+919876543210",
    "otp": "123456"
  }'
```

**Step 3: Complete Signup**
```bash
curl -X POST http://localhost:8000/apis/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "phoneNumber": "+919876543210",
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@example.com",
    "password": "SecurePassword123"
  }'
```

### Example 2: Existing User Login

```bash
curl -X POST http://localhost:8000/apis/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "phoneNumber": "+919876543210",
    "password": "SecurePassword123"
  }'
```

---

## Error Codes Summary

| Status Code | Description |
|------------|-------------|
| 200 | Success (GET, POST for login/verify) |
| 201 | Created (POST for signup) |
| 400 | Bad Request (validation errors) |
| 401 | Unauthorized (invalid/expired token) |
| 403 | Forbidden (no permission) |
| 404 | Not Found (resource doesn't exist) |
| 500 | Internal Server Error |

---

## Testing with Swagger/OpenAPI

This project uses `drf-spectacular` for automatic API documentation.

**Access Swagger UI:**
```
http://localhost:8000/api/schema/swagger-ui/
```

**Access ReDoc:**
```
http://localhost:8000/api/schema/redoc/
```

**Download OpenAPI Schema:**
```
http://localhost:8000/api/schema/
```

---

## Database Model

### Users Model Fields

| Field | Type | Description |
|-------|------|-------------|
| userId | UUID | Primary key, auto-generated |
| firstName | CharField(25) | User's first name |
| lastName | CharField(25) | User's last name |
| email | EmailField | Unique email address |
| password | CharField(128) | Hashed password |
| phoneNumber | CharField(15) | Unique phone number |
| otp | CharField(6) | Temporary OTP storage |
| otp_created_at | DateTimeField | OTP creation timestamp |
| is_verified | BooleanField | Phone verification status |
| is_active | BooleanField | Account active status |
| is_staff | BooleanField | Staff access status |
| createdAt | DateTimeField | Account creation timestamp |
| updatedAt | DateTimeField | Last update timestamp |

---

## Best Practices

### For Frontend Developers

1. **Store tokens securely**
   - Use httpOnly cookies or secure storage
   - Never store in localStorage for sensitive apps
   - Clear tokens on logout

2. **Handle token expiry**
   - Implement token refresh logic
   - Handle 401 responses gracefully
   - Redirect to login when refresh fails

3. **Password requirements**
   - Minimum 6 characters (enforced by backend)
   - Recommend: 8+ characters with mixed case, numbers, symbols
   - Show password strength indicator

4. **Phone number format**
   - Accept various formats
   - Include country code selector
   - Validate format client-side

5. **Error handling**
   - Display user-friendly error messages
   - Handle network errors
   - Show loading states

### Security Recommendations

1. **Always use HTTPS in production**
2. **Implement rate limiting on authentication endpoints**
3. **Add CAPTCHA for OTP requests to prevent abuse**
4. **Log authentication attempts**
5. **Implement account lockout after failed attempts**
6. **Use strong JWT secret keys**
7. **Rotate JWT secrets periodically**

---

## Support

For issues or questions:
- Check the error response messages
- Review this documentation
- Contact the development team

---

**Last Updated:** 2025-10-10
**API Version:** 1.0
