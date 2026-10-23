from fastapi.testclient import TestClient
from backend.main import app

def test_export_digitized_pdf_full_endpoint():
    client = TestClient(app)
    payload = {
        "title": "Đề Khảo Sát Toán 12",
        "questions": [
            {
                "id": 1,
                "item_format": "SINGLE_CHOICE",
                "stem": "Cho hàm số $y = \\dfrac{2x-1}{x+1}$. Tìm tiệm cận đứng.",
                "options": [
                    {"label": "A", "content": "$x = -1$"},
                    {"label": "B", "content": "$x = 2$"},
                    {"label": "C", "content": "$y = 2$"},
                    {"label": "D", "content": "$y = -1$"}
                ]
            },
            {
                "id": 2,
                "item_format": "SHORT_ANSWER",
                "stem": "Tính giá trị nhỏ nhất của $f(x) = x^2 - 4x + 5$ trên $[0; 3]$.",
                "short_answer_value": "1"
            }
        ]
    }
    response = client.post("/api/v1/digitize/export-pdf", json=payload)
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/pdf"
    assert len(response.content) > 1000
    assert response.content[:4] == b"%PDF"


def test_export_digitized_pdf_endpoint():
    client = TestClient(app)
    payload = {
        "title": "Đề Khảo Sát Toán 12 PDF",
        "questions": [
            {
                "id": 1,
                "item_format": "SINGLE_CHOICE",
                "stem": "Cho hàm số $y = \\dfrac{2x-1}{x+1}$. Tìm tiệm cận đứng.",
                "options": [
                    {"label": "A", "content": "$x = -1$"},
                    {"label": "B", "content": "$x = 2$"},
                    {"label": "C", "content": "$y = 2$"},
                    {"label": "D", "content": "$y = -1$"}
                ]
            }
        ]
    }
    response = client.post("/api/v1/digitize/export-pdf", json=payload)
    assert response.status_code == 200
    assert response.headers.get("content-type") == "application/pdf"
    assert len(response.content) > 1000
    assert response.content[:4] == b"%PDF"
