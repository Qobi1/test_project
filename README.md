# 🔐 Custom Authentication & Authorization System (Django + DRF + JWT)

This project implements a **custom authentication and authorization backend** using Django REST Framework.  
It demonstrates how to build a full authentication flow and a **role-based access control (RBAC)** system without relying fully on Django’s built-in permission model.

---

## 🚀 Features

- Custom **User** model (email-based login)
- **JWT authentication** via `djangorestframework-simplejwt`
- **Role / BusinessElement / AccessRule** tables for fine-grained authorization
- **Soft delete** (`is_active=False`) instead of physical user removal
- Custom **HasAccessPermission** class returning proper `401` / `403`
- **Swagger / ReDoc** API docs via `drf-spectacular`
- **Logout with JWT token blacklisting**
- **Mock resources** (e.g. `/api/products/`) showing permission behavior

---

## 🧱 Tech Stack
| Component | Tool |
|------------|------|
| Backend | Django 5 + Django REST Framework |
| Auth | SimpleJWT |
| Docs | drf-spectacular |
| Database | PostgreSQL |
| Language | Python 3.x |

---

## ⚙️ Installation

```bash
git clone https://github.com/Qobi1/test_project.git
cd test_project
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
```

Edit **`settings.py`** for PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'auth_system',
        'USER': 'postgres',
        'PASSWORD': 'yourpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

Run migrations and start the server:

```bash
python manage.py migrate
python manage.py runserver
```

---

## 🔑 Authentication (JWT)

### Endpoints
| URL | Method | Description |
|-----|---------|-------------|
| `/api/token/` | POST | Login – returns `access` + `refresh` |
| `/api/token/refresh/` | POST | Get new access token |
| `/api/logout/` | POST | Blacklist refresh token |

### Example login
```json
POST /api/token/
{
  "email": "admin@example.com",
  "password": "12345"
}
```

Response:
```json
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}
```
Use the access token:
```
Authorization: Bearer <access_token>
```

---

## 👥 User Management

| Endpoint | Method | Description | Auth |
|-----------|------|-------------|------|
| `/api/users/` | POST | Register new user | ❌ |
| `/api/users/<id>/` | PUT | Update user info | ✅ |
| `/api/users/<id>/delete/` | DELETE | Soft-delete user | ✅ |

---

## 🧠 Role-Based Access Control (RBAC)

### Data Models

| Model | Description |
|--------|--------------|
| **Role** | User category (`admin`, `manager`, `user`) |
| **BusinessElement** | Protected resource (`users`, `products`, `orders`) |
| **AccessRoleRule** | Permissions per role-element pair |
| **User** | Linked to one Role |

### Example Schema

| Role | Element | read | create | update | delete |
|------|----------|------|---------|---------|---------|
| admin | users | ✅ | ✅ | ✅ | ✅ |
| user | products | ✅ | ❌ | ❌ | ❌ |

Each API view defines:
```python
business_element = "products"
permission_classes = [HasAccessPermission]
```
`HasAccessPermission` then checks:
1. Is user authenticated? → else **401**
2. Does role have permission for this element/action? → else **403**
3. Otherwise → allow (200 OK)

---

## 🔐 Custom Permission Logic (simplified)

```python
class HasAccessPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False  # 401
        element = BusinessElement.objects.filter(name=view.business_element).first()
        rule = AccessRoleRule.objects.filter(role=request.user.role, element=element).first()
        if not rule:
            return False  # 403
        if request.method == "GET" and rule.read_permission:
            return True
        if request.method == "POST" and rule.create_permission:
            return True
        if request.method in ["PUT","PATCH"] and rule.update_permission:
            return True
        if request.method == "DELETE" and rule.delete_permission:
            return True
        return False
```

---

## 🧩 Example Mock API

```python
class ProductsView(APIView):
    permission_classes = [HasAccessPermission]
    business_element = "products"

    def get(self, request):
        return Response([
            {"id": 1, "name": "Product A"},
            {"id": 2, "name": "Product B"},
        ])
```

### Behavior
| User | Role | Access | Result |
|------|------|---------|--------|
| No token | – | ❌ | 401 Unauthorized |
| Normal user w/out rule | user | ❌ | 403 Forbidden |
| Admin | admin | ✅ | 200 OK |

---

## 📚 API Documentation

| Type | URL |
|------|-----|
| Swagger UI | [/api/docs/](http://127.0.0.1:8000/api/docs/) |
| ReDoc | [/api/redoc/](http://127.0.0.1:8000/api/redoc/) |
| OpenAPI JSON | [/api/schema/](http://127.0.0.1:8000/api/schema/) |

Click **Authorize** in Swagger and paste your `Bearer <access_token>` to test secured endpoints.

---

## 🧾 Error Codes

| Code | Meaning |
|------|----------|
| **401** | User not authenticated or token invalid |
| **403** | Authenticated but no permission |
| **200** | Success |
| **205** | Logged out (token blacklisted) |
| **400** | Invalid input / token |

---

## 🧪 Quick Demo

1. Create two roles: **admin**, **user**
2. Create business elements: **users**, **products**
3. Create access rules:
   - Admin → full access to everything  
   - User → only read `products`
4. Register two users and assign roles
5. Login both → get tokens
6. Call `/api/products/`
   - No token → **401**
   - User → **403** or **200** (if allowed)
   - Admin → **200**

---

## 🏁 Summary

This backend demonstrates:

- ✅ Custom **User** + JWT authentication  
- ✅ Custom **RBAC** structure (`Role`, `BusinessElement`, `AccessRoleRule`)  
- ✅ Correct **401 / 403 / 200** handling  
- ✅ Swagger & ReDoc documentation  
- ✅ Clean, extensible architecture ready for real projects

---

