# Gallery API

A RESTful backend API built with Flask and MongoDB, designed to manage Aboriginal artworks, artists, tribes, and user authentication. Developed for SIT331 5.2HD, it demonstrates secure, scalable backend design with clean architecture and CI integration.

---

## 🔧 Technologies Used

| Category         | Technology               | Purpose                                                                 |
|------------------|---------------------------|-------------------------------------------------------------------------|
| Framework        | Flask                     | Web application framework for building REST APIs                        |
| ORM              | MongoEngine               | Object-Document Mapper for MongoDB                                      |
| Database         | MongoDB (Atlas)           | NoSQL database to store and manage JSON-like documents                  |
| Testing          | Pytest                    | Framework for unit and integration testing                              |
| Auth             | Flask-JWT-Extended        | Provides JWT-based authentication with role-based access                |
| Validation       | Marshmallow               | For data validation and (de)serialization                               |
| API Docs         | Flask-Smorest + Swagger   | For auto-generating interactive API documentation                       |
| CI/CD            | GitHub Actions            | Automates test runs on push, pull requests, and manual dispatch         |
| Env Config       | Python-dotenv             | Manages environment variables from `.env`                               |

---

## ✅ Features

### 1. **RESTful CRUD API**
- `Tribe`, `Artist`, and `Artifact` entities with full CRUD operations.
- Input validation using Marshmallow schemas (including PATCH schemas for partial updates).
- Routes: `/api/v1/tribes/`, `/api/v1/artists/`, `/api/v1/artifacts/`.

### 2. **Authentication**
- User registration and login via `/auth/register` and `/auth/login`.
- JWT authentication with secure token issuance.
- Role-based access control (`admin_required` decorator for write/delete access).

### 3. **Schema Validation & Error Handling**
- All input data is validated via Marshmallow.
- Returns 422 errors on bad input, 401/403 on unauthorized access, and 404 for missing resources.
- Extra fields are rejected to enforce schema contracts.

### 4. **Testing**
- Comprehensive Pytest test suite for all API endpoints.
- Coverage includes:
  - Success paths for CRUD
  - Unauthorized access
  - Role-based authorization
  - Validation failures
  - 404 errors for invalid resource IDs
- DB is isolated using a `_test` instance with pre/post test cleanup.

### 5. **Continuous Integration**
- GitHub Actions workflow:
  - Runs `pytest` on push, PR, and manual dispatch.
  - Uses Python 3.10 with `requirements.txt` setup.
  - Provides feedback directly in PRs.

---

## 📁 Project Structure

```bash
gallery-api/
├── app.py                  # App factory + blueprint registration
├── models/                 # MongoEngine document models
├── resources/              # Flask-Smorest route handlers (controllers)
├── schemas/                # Marshmallow schemas for validation
├── tests/                  # Pytest suite with DB-clearing fixture
├── requirements.txt        # Dependencies
└── .github/workflows/ci.yml  # GitHub Actions workflow
