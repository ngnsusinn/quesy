import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

import uuid
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_auth_register_and_login():
    unique_email = f"testteacher_{uuid.uuid4().hex[:6]}@quesy.vn"
    reg_res = client.post("/api/v1/auth/register", json={
        "email": unique_email,
        "password": "password123",
        "full_name": "Test Teacher",
        "role": "TEACHER"
    })
    assert reg_res.status_code == 201
    data = reg_res.json()
    assert "access_token" in data
    assert data["user"]["email"] == unique_email
    token = data["access_token"]

    login_res = client.post("/api/v1/auth/login", json={
        "email": unique_email,
        "password": "password123"
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data

    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == unique_email

def test_question_bank_count_and_filters():
    res = client.get("/api/v1/questions/count")
    assert res.status_code == 200
    counts = res.json()
    assert "total" in counts
    assert "single_choice" in counts

    list_res = client.get("/api/v1/questions?limit=5")
    assert list_res.status_code == 200
    assert isinstance(list_res.json(), list)

def test_composer_save_to_bank():
    latex_sample = r"""
    \begin{ex}
    Cho hàm số $y = x^3 - 3x$. Giá trị cực tiểu của hàm số là:
    \choice
    {\True $-2$}
    {$2$}
    {$0$}
    {$-1$}
    \begin{loigiai}
    Đạo hàm $y' = 3x^2 - 3$, cho $y' = 0 \Rightarrow x = \pm 1$. Giá trị cực tiểu là $y(1) = -2$.
    \end{loigiai}
    \end{ex}
    """
    res = client.post("/api/v1/composer/save-to-bank", json={"latex_code": latex_sample})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["total_saved"] >= 1
    assert "counts" in data
