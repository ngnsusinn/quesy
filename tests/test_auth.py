"""Unit tests for Quesy Authentication System (Task AUTH-01)
Verifies:
- PBKDF2-HMAC-SHA256 password hashing (600,000 iterations, 32-byte salt, safe verification)
- JWT access token generation and HMAC-SHA256 signature validation with expiration
- POST /api/v1/auth/register (successful registration, 400 on duplicate email, 422 on short password)
- POST /api/v1/auth/login (success with 200 + token, 401 on wrong password, 401 on nonexistent email, 403 on inactive)
- GET /api/v1/auth/me (200 with valid Bearer token, 401 on invalid/missing/expired token)
- POST /api/v1/auth/oauth/google and POST /api/v1/auth/oauth/github (new user creation, existing user profile sync)
- POST /api/v1/auth/logout
- Default seeded accounts login (teacher@quesy.vn and admin@quesy.vn)
- Role authorization dependency enforcement (require_role)
"""

import base64
import uuid
from datetime import timedelta
import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException

from backend.main import app
from backend.database import SessionLocal
from backend.models import User
from backend.services.auth_service import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    require_role,
)

client = TestClient(app)


# ==============================================================================
# 1. PBKDF2 PASSWORD HASHING & CRYPTOGRAPHIC VERIFICATION
# ==============================================================================

def test_pbkdf2_hashing_format_and_random_salt():
    """Verifies PBKDF2 hashing conforms to standard format and uses random salts."""
    pwd = "SecureTeacherPass2025!"
    hash1 = hash_password(pwd)
    hash2 = hash_password(pwd)

    # Standard format: pbkdf2:sha256:600000$<salt_b64>$<hash_b64>
    parts1 = hash1.split("$")
    assert len(parts1) == 3, f"Hash format must have 3 parts separated by $, got: {hash1}"
    algo_info, salt_b64, hash_b64 = parts1
    assert algo_info == "pbkdf2:sha256:600000", "Must use 600,000 iterations with sha256"

    # Salt must be 32 bytes decoded
    salt_bytes = base64.b64decode(salt_b64)
    assert len(salt_bytes) == 32, "Salt must be 32 random bytes"

    # Random salt ensures two hashes of identical password are distinct
    assert hash1 != hash2, "Two hashes of the same password must differ due to unique salts"


def test_pbkdf2_verification_correct_and_incorrect():
    """Verifies that verify_password correctly matches passwords and resists timing/format attacks."""
    pwd = "ComplexPassword#890"
    hashed = hash_password(pwd)

    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword#890", hashed) is False
    assert verify_password("", hashed) is False
    assert verify_password(pwd, "") is False
    assert verify_password(pwd, "corrupted_hash_without_delimiter") is False
    assert verify_password(pwd, "pbkdf2:sha256:600000$invalidsalt$invalidhash") is False


# ==============================================================================
# 2. JWT TOKEN CREATION & VALIDATION
# ==============================================================================

def test_create_and_decode_jwt_token():
    """Verifies JWT token generation and standard payload decoding."""
    payload = {"sub": "usr-test-123", "role": "TEACHER", "custom_key": "val"}
    token = create_access_token(payload, expires_delta=timedelta(hours=2))

    parts = token.split(".")
    assert len(parts) == 3, "JWT must consist of header.payload.signature"

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "usr-test-123"
    assert decoded["role"] == "TEACHER"
    assert decoded["custom_key"] == "val"
    assert "exp" in decoded


def test_decode_jwt_token_tampered_signature():
    """Verifies that tampered JWT signatures are rejected."""
    token = create_access_token({"sub": "usr-test-456", "role": "ADMIN"})
    header, payload, sig = token.split(".")
    tampered_token = f"{header}.{payload}.{sig[:-4]}XXXX"

    assert decode_access_token(tampered_token) is None


def test_decode_jwt_token_expired():
    """Verifies that expired JWT tokens return None."""
    token = create_access_token({"sub": "usr-test-expired"}, expires_delta=timedelta(seconds=-10))
    assert decode_access_token(token) is None


def test_decode_jwt_token_invalid_format():
    """Verifies that malformed tokens are handled gracefully."""
    assert decode_access_token("not-a-token") is None
    assert decode_access_token("part1.part2") is None
    assert decode_access_token("") is None


# ==============================================================================
# 3. FASTAPI AUTH ENDPOINTS: REGISTER, LOGIN, ME, LOGOUT
# ==============================================================================

def test_auth_register_success():
    """Verifies successful registration of a new user."""
    unique_email = f"teacher_{uuid.uuid4().hex[:8]}@quesy.vn"
    res = client.post("/api/v1/auth/register", json={
        "email": unique_email,
        "password": "validPassword123",
        "full_name": "Giáo Viên Kiểm Thử",
        "role": "TEACHER"
    })
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == unique_email
    assert data["user"]["full_name"] == "Giáo Viên Kiểm Thử"
    assert data["user"]["role"] == "TEACHER"
    assert data["user"]["oauth_provider"] == "local"


def test_auth_register_duplicate_email_400():
    """Verifies that registering with an already existing email returns 400 Bad Request."""
    unique_email = f"dup_{uuid.uuid4().hex[:8]}@quesy.vn"
    payload = {
        "email": unique_email,
        "password": "validPassword123",
        "full_name": "Người Dùng 1",
        "role": "TEACHER"
    }
    res1 = client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 400
    assert "already registered" in res2.json()["detail"].lower()


def test_auth_register_short_password_422():
    """Verifies that passwords shorter than 6 characters trigger Pydantic 422 validation error."""
    res = client.post("/api/v1/auth/register", json={
        "email": f"short_{uuid.uuid4().hex[:6]}@quesy.vn",
        "password": "123",
        "full_name": "Short Pass User"
    })
    assert res.status_code == 422


def test_auth_login_success():
    """Verifies successful login returning JWT token and user profile."""
    unique_email = f"login_{uuid.uuid4().hex[:8]}@quesy.vn"
    client.post("/api/v1/auth/register", json={
        "email": unique_email,
        "password": "mypassword123",
        "full_name": "Login User"
    })

    res = client.post("/api/v1/auth/login", json={
        "email": unique_email,
        "password": "mypassword123"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == unique_email


def test_auth_login_wrong_password_401():
    """Verifies that login with wrong password returns 401 Unauthorized."""
    unique_email = f"login_wrong_{uuid.uuid4().hex[:8]}@quesy.vn"
    client.post("/api/v1/auth/register", json={
        "email": unique_email,
        "password": "correctPassword123",
        "full_name": "Wrong Pass User"
    })

    res = client.post("/api/v1/auth/login", json={
        "email": unique_email,
        "password": "INCORRECT_PASSWORD"
    })
    assert res.status_code == 401
    assert "invalid email or password" in res.json()["detail"].lower()


def test_auth_login_nonexistent_email_401():
    """Verifies that login with non-existent email returns 401 Unauthorized."""
    res = client.post("/api/v1/auth/login", json={
        "email": f"ghost_{uuid.uuid4().hex[:8]}@quesy.vn",
        "password": "anyPassword"
    })
    assert res.status_code == 401
    assert "invalid email or password" in res.json()["detail"].lower()


def test_auth_login_inactive_user_403():
    """Verifies that an inactive user account cannot log in and returns 403 Forbidden."""
    unique_email = f"inactive_{uuid.uuid4().hex[:8]}@quesy.vn"
    reg_res = client.post("/api/v1/auth/register", json={
        "email": unique_email,
        "password": "password123",
        "full_name": "Inactive User"
    })
    assert reg_res.status_code == 201

    # Deactivate the user directly in DB
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == unique_email).first()
        assert user is not None
        user.is_active = False
        db.commit()
    finally:
        db.close()

    res = client.post("/api/v1/auth/login", json={
        "email": unique_email,
        "password": "password123"
    })
    assert res.status_code == 403
    assert "inactive" in res.json()["detail"].lower()


def test_auth_get_me_valid_and_invalid_token():
    """Verifies GET /api/v1/auth/me behavior with valid, invalid, and missing tokens."""
    unique_email = f"me_test_{uuid.uuid4().hex[:8]}@quesy.vn"
    reg_res = client.post("/api/v1/auth/register", json={
        "email": unique_email,
        "password": "password123",
        "full_name": "Me User",
        "role": "TEACHER"
    })
    token = reg_res.json()["access_token"]

    # 1. Valid token
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == unique_email
    assert me_data["full_name"] == "Me User"
    assert me_data["role"] == "TEACHER"

    # 2. Invalid / forged token
    bad_res = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer fake.token.here"})
    assert bad_res.status_code == 401

    # 3. Missing Authorization header
    none_res = client.get("/api/v1/auth/me")
    assert none_res.status_code == 401


# ==============================================================================
# 4. OAUTH GOOGLE & GITHUB FLOWS
# ==============================================================================

def test_auth_oauth_google_flow():
    """Verifies OAuth Google login creating a new user and syncing an existing user."""
    oauth_email = f"google_{uuid.uuid4().hex[:8]}@gmail.com"

    # Step 1: New user registration via Google OAuth
    res1 = client.post("/api/v1/auth/oauth/google", json={
        "email": oauth_email,
        "full_name": "Google User 1",
        "oauth_provider": "google",
        "oauth_id": "google-sub-12345",
        "avatar_url": "https://lh3.googleusercontent.com/avatar1.jpg"
    })
    assert res1.status_code == 200
    data1 = res1.json()
    assert "access_token" in data1
    assert data1["user"]["email"] == oauth_email
    assert data1["user"]["oauth_provider"] == "google"
    assert data1["user"]["avatar_url"] == "https://lh3.googleusercontent.com/avatar1.jpg"

    # Step 2: Existing user login via Google OAuth with updated avatar
    res2 = client.post("/api/v1/auth/oauth/google", json={
        "email": oauth_email,
        "full_name": "Google User 1 Updated",
        "oauth_provider": "google",
        "oauth_id": "google-sub-12345",
        "avatar_url": "https://lh3.googleusercontent.com/avatar_new.jpg"
    })
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["user"]["email"] == oauth_email
    assert data2["user"]["full_name"] == "Google User 1 Updated"
    assert data2["user"]["avatar_url"] == "https://lh3.googleusercontent.com/avatar_new.jpg"


def test_auth_oauth_github_flow():
    """Verifies OAuth GitHub login creating a new user and syncing an existing user."""
    oauth_email = f"github_{uuid.uuid4().hex[:8]}@github.com"

    # Step 1: New user registration via GitHub OAuth
    res1 = client.post("/api/v1/auth/oauth/github", json={
        "email": oauth_email,
        "full_name": "GitHub Dev",
        "oauth_provider": "github",
        "oauth_id": "gh-99999",
        "avatar_url": "https://avatars.githubusercontent.com/u/99999"
    })
    assert res1.status_code == 200
    data1 = res1.json()
    assert "access_token" in data1
    assert data1["user"]["email"] == oauth_email
    assert data1["user"]["oauth_provider"] == "github"

    # Step 2: Existing user login via GitHub OAuth
    res2 = client.post("/api/v1/auth/oauth/github", json={
        "email": oauth_email,
        "full_name": "GitHub Dev Senior",
        "oauth_provider": "github",
        "oauth_id": "gh-99999"
    })
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["user"]["full_name"] == "GitHub Dev Senior"


# ==============================================================================
# 5. LOGOUT & SEEDED DEFAULT ACCOUNTS
# ==============================================================================

def test_auth_logout():
    """Verifies POST /api/v1/auth/logout endpoint."""
    res = client.post("/api/v1/auth/logout")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "logged out" in data["message"].lower()


def test_auth_seeded_default_accounts():
    """Verifies that default seeded accounts (teacher@quesy.vn & admin@quesy.vn) can authenticate."""
    # 1. Teacher account
    res_teacher = client.post("/api/v1/auth/login", json={
        "email": "teacher@quesy.vn",
        "password": "quesy123456"
    })
    assert res_teacher.status_code == 200
    teacher_data = res_teacher.json()
    assert teacher_data["user"]["role"] == "TEACHER"
    assert "access_token" in teacher_data

    # 2. Admin account
    res_admin = client.post("/api/v1/auth/login", json={
        "email": "admin@quesy.vn",
        "password": "admin123456"
    })
    assert res_admin.status_code == 200
    admin_data = res_admin.json()
    assert admin_data["user"]["role"] == "ADMIN"
    assert "access_token" in admin_data


def test_require_role_dependency_logic():
    """Verifies role-based access control dependency behaviour."""
    admin_user = User(id="u-admin", email="admin@test.com", role="ADMIN", is_active=True)
    teacher_user = User(id="u-teacher", email="teacher@test.com", role="TEACHER", is_active=True)

    # Admin always passes any required role
    dep_admin_check = require_role("TEACHER")
    assert dep_admin_check(admin_user) == admin_user

    # Teacher passes TEACHER role
    assert dep_admin_check(teacher_user) == teacher_user

    # Teacher fails ADMIN role
    dep_require_admin = require_role("ADMIN")
    with pytest.raises(HTTPException) as exc_info:
        dep_require_admin(teacher_user)
    assert exc_info.value.status_code == 403
    assert "Required role: ADMIN" in exc_info.value.detail
