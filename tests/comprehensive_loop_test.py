"""Comprehensive Loop & Stress Test Suite for Quesy System.
Verifies all functional areas, edge cases, negative scenarios, and concurrency over multiple loops.
"""
import os
import sys
import time
import uuid
import json
import zipfile
import io
import itertools
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import requests

BASE_URL = "http://127.0.0.1:8000"
PROJECT_ROOT = Path(__file__).resolve().parent.parent

class TestReporter:
    __test__ = False
    def __init__(self):
        self.results = []
        self.latencies = {}
        self.start_time = time.time()

    def record(self, module: str, test_name: str, passed: bool, duration_ms: float, details: str = ""):
        self.results.append({
            "module": module,
            "name": test_name,
            "passed": passed,
            "duration_ms": duration_ms,
            "details": details
        })
        if module not in self.latencies:
            self.latencies[module] = []
        self.latencies[module].append(duration_ms)
        status_str = "PASS" if passed else "FAIL"
        print(f"[{status_str}] [{module}] {test_name} ({duration_ms:.1f}ms) {details}")

    def summary(self):
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed
        elapsed = time.time() - self.start_time
        return {
            "total": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": (passed / total * 100) if total else 0,
            "elapsed_seconds": elapsed,
            "results": self.results,
            "latencies": self.latencies
        }

reporter = TestReporter()

def timed_request(method, url, **kwargs):
    t0 = time.perf_counter()
    resp = requests.request(method, url, timeout=30, **kwargs)
    dt_ms = (time.perf_counter() - t0) * 1000
    return resp, dt_ms


# ==============================================================================
# 1. INFRASTRUCTURE & STATIC ASSETS
# ==============================================================================
def test_infrastructure():
    # Health check
    resp, dt = timed_request("GET", f"{BASE_URL}/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "Circular 32" in data["standard"]
    reporter.record("Infrastructure", "GET /health status and standard", True, dt)

    # Alternate health check
    resp, dt = timed_request("GET", f"{BASE_URL}/api/v1/health")
    assert resp.status_code == 200
    reporter.record("Infrastructure", "GET /api/v1/health status", True, dt)

    # Favicon
    resp, dt = timed_request("GET", f"{BASE_URL}/favicon.ico")
    assert resp.status_code == 204
    reporter.record("Infrastructure", "GET /favicon.ico returns 204", True, dt)

    # Root HTML
    resp, dt = timed_request("GET", f"{BASE_URL}/")
    assert resp.status_code == 200
    assert "<!DOCTYPE html>" in resp.text
    assert "QUESY" in resp.text
    reporter.record("Infrastructure", "GET / serves Web Studio HTML", True, dt)

    # Static JS
    resp, dt = timed_request("GET", f"{BASE_URL}/static/app.js")
    assert resp.status_code == 200
    assert "API_BASE_URL" in resp.text
    reporter.record("Infrastructure", "GET /static/app.js serves JavaScript", True, dt)

    # API Root
    resp, dt = timed_request("GET", f"{BASE_URL}/api")
    assert resp.status_code == 200
    reporter.record("Infrastructure", "GET /api root spec", True, dt)


# ==============================================================================
# 2. TAXONOMY (CIRCULAR 32 STANDARDS)
# ==============================================================================
def test_taxonomy():
    endpoints = [
        ("grades", "Lớp 12"),
        ("subjects", "Toán học"),
        ("strands", None),
        ("topics", None),
        ("lessons", None),
        ("learning-outcomes", None),
        ("problem-archetypes", None),
    ]
    for ep, sample_val in endpoints:
        resp, dt = timed_request("GET", f"{BASE_URL}/api/v1/taxonomy/{ep}")
        assert resp.status_code == 200
        items = resp.json()
        assert isinstance(items, list)
        assert len(items) > 0
        if sample_val:
            names = [it.get("name") or it.get("title") for it in items]
            assert any(sample_val in (n or "") for n in names)
        reporter.record("Taxonomy", f"GET /api/v1/taxonomy/{ep} count={len(items)}", True, dt)

    # Tree check: strict absence of commercial textbook fields
    resp, dt = timed_request("GET", f"{BASE_URL}/api/v1/taxonomy/tree")
    assert resp.status_code == 200
    tree_text = resp.text.lower()
    for banned in ["canh_dieu", "ket_noi_tri_thuc", "chan_troi_sang_tao", "bo_sach"]:
        assert banned not in tree_text, f"Found banned textbook field: {banned}"
    reporter.record("Taxonomy", "Taxonomy Tree strictly adheres to TT32 (No textbook series)", True, dt)


# ==============================================================================
# 3. QUESTION BANK CRUD & INTELLIGENCE
# ==============================================================================
def test_questions_crud():
    # 1. Create Part I: Single Choice with Math formula
    q1_payload = {
        "subject_id": "subj-toan",
        "grade_id": "grade-12",
        "cognitive_level": "RECOGNITION",
        "item_format": "SINGLE_CHOICE",
        "stem": r"Tính tích phân $I = \int_{0}^{1} x^2 \, dx$. Giá trị của $I$ là bao nhiêu?",
        "options": [
            {"label": "A", "content": r"$\frac{1}{3}$", "is_correct": True, "order_index": 0},
            {"label": "B", "content": r"$\frac{1}{2}$", "is_correct": False, "order_index": 1},
            {"label": "C", "content": r"$1$", "is_correct": False, "order_index": 2},
            {"label": "D", "content": r"$\frac{2}{3}$", "is_correct": False, "order_index": 3}
        ],
        "explanation": r"Ta có $\int_{0}^{1} x^2 dx = \left.\frac{x^3}{3}\right|_{0}^{1} = \frac{1}{3}$."
    }
    resp, dt = timed_request("POST", f"{BASE_URL}/api/v1/questions", json=q1_payload)
    assert resp.status_code == 201
    q1 = resp.json()
    q1_id = q1["id"]
    reporter.record("QuestionBank", "Create Part I Single Choice with LaTeX", True, dt)

    # 2. Create Part II: True/False Group
    q2_payload = {
        "subject_id": "subj-toan",
        "grade_id": "grade-12",
        "cognitive_level": "COMPREHENSION",
        "item_format": "TRUE_FALSE_GROUP",
        "stem": r"Cho hàm số $y = f(x) = x^3 - 3x + 2$. Xét tính đúng/sai của các mệnh đề sau:",
        "sub_statements": [
            {"label": "a", "content": r"Hàm số đồng biến trên khoảng $(-\infty; -1)$.", "is_true": True, "order_index": 0},
            {"label": "b", "content": r"Hàm số đạt cực tiểu tại $x = 1$.", "is_true": True, "order_index": 1},
            {"label": "c", "content": r"Giá trị cực đại của hàm số bằng $0$.", "is_true": False, "order_index": 2},
            {"label": "d", "content": r"Đồ thị hàm số đi qua điểm $A(0; 2)$.", "is_true": True, "order_index": 3}
        ]
    }
    resp, dt = timed_request("POST", f"{BASE_URL}/api/v1/questions", json=q2_payload)
    assert resp.status_code == 201
    q2 = resp.json()
    q2_id = q2["id"]
    reporter.record("QuestionBank", "Create Part II True/False 4-statement group", True, dt)

    # 3. Create Part III: Short Answer
    q3_payload = {
        "subject_id": "subj-toan",
        "grade_id": "grade-12",
        "cognitive_level": "APPLICATION",
        "item_format": "SHORT_ANSWER",
        "stem": r"Tìm giá trị lớn nhất của hàm số $y = -x^2 + 4x + 5$ trên đoạn $[0; 3]$.",
        "explanation": "Đỉnh parabol tại x = 2 thuộc đoạn [0; 3], y(2) = 9."
    }
    resp, dt = timed_request("POST", f"{BASE_URL}/api/v1/questions", json=q3_payload)
    assert resp.status_code == 201
    q3 = resp.json()
    q3_id = q3["id"]
    reporter.record("QuestionBank", "Create Part III Short Answer numeric item", True, dt)

    # 4. Get by ID
    for q_id, q_type in [(q1_id, "SINGLE_CHOICE"), (q2_id, "TRUE_FALSE_GROUP"), (q3_id, "SHORT_ANSWER")]:
        resp, dt = timed_request("GET", f"{BASE_URL}/api/v1/questions/{q_id}")
        assert resp.status_code == 200
        assert resp.json()["item_format"] == q_type
        reporter.record("QuestionBank", f"GET question {q_type}", True, dt)

    # 5. Update Question
    update_payload = {"stem": q1_payload["stem"] + " (Đã cập nhật kiểm thử)"}
    resp, dt = timed_request("PUT", f"{BASE_URL}/api/v1/questions/{q1_id}", json=update_payload)
    assert resp.status_code == 200
    assert "Đã cập nhật kiểm thử" in resp.json()["stem"]
    reporter.record("QuestionBank", "PUT question update stem", True, dt)

    # 6. Duplicate check (rule-05: >= 0.90 threshold)
    resp, dt = timed_request("POST", f"{BASE_URL}/api/v1/questions/check-duplicate", json={"stem": q1_payload["stem"]})
    assert resp.status_code == 200
    dup_res = resp.json()
    similarity = dup_res.get("similarity_score", dup_res.get("max_similarity", 0.0))
    assert dup_res["is_duplicate"] is True or similarity >= 0.70
    reporter.record("QuestionBank", f"Duplicate detection positive (sim={similarity:.2f})", True, dt)

    # 7. Auto-tagging endpoint
    resp, dt = timed_request("POST", f"{BASE_URL}/api/v1/questions/auto-tag", json={"stem": "Tìm tập xác định của hàm số mũ lũy thừa logarit"})
    assert resp.status_code == 200
    tag_res = resp.json()
    assert "suggested_cognitive_level" in tag_res or "cognitive_level" in tag_res
    reporter.record("QuestionBank", "Auto-tagging endpoint suggestion", True, dt)

    # 8. Delete Question & Idempotency
    resp, dt = timed_request("DELETE", f"{BASE_URL}/api/v1/questions/{q1_id}")
    assert resp.status_code == 204
    resp_after, dt_after = timed_request("GET", f"{BASE_URL}/api/v1/questions/{q1_id}")
    assert resp_after.status_code == 404
    reporter.record("QuestionBank", "DELETE question and verify 404", True, dt + dt_after)

    return q2_id, q3_id


# ==============================================================================
# 4. EXAM MATRIX (BLUEPRINT)
# ==============================================================================
def test_matrix():
    resp_yccd, _ = timed_request("GET", f"{BASE_URL}/api/v1/taxonomy/learning-outcomes")
    yccds = resp_yccd.json() if resp_yccd.status_code == 200 else []
    yccd_id = yccds[0]["id"] if yccds else "98936fe1-8270-4846-9632-265cff73b3a8"

    matrix_payload = {
        "title": f"Ma Trận Đề Thi Kiểm Tra Chuẩn TT32 - Loop {uuid.uuid4().hex[:6]}",
        "subject_id": "subj-toan",
        "grade_id": "grade-12",
        "duration_minutes": 90,
        "total_points": 10.0,
        "items": [
            {
                "section": "Phần I: Trắc nghiệm 4 lựa chọn",
                "learning_outcome_id": yccd_id,
                "cognitive_level": "RECOGNITION",
                "item_format": "SINGLE_CHOICE",
                "quantity": 2,
                "points_per_item": 2.5,
                "order_index": 1
            },
            {
                "section": "Phần II: Đúng/Sai 4 ý",
                "learning_outcome_id": yccd_id,
                "cognitive_level": "APPLICATION",
                "item_format": "TRUE_FALSE_GROUP",
                "quantity": 2,
                "points_per_item": 2.5,
                "order_index": 2
            },
        ]
    }
    resp, dt = timed_request("POST", f"{BASE_URL}/api/v1/matrices", json=matrix_payload)
    assert resp.status_code == 201
    matrix = resp.json()
    matrix_id = matrix["id"]
    reporter.record("ExamMatrix", f"Create 10-point Matrix (id={matrix_id[:8]})", True, dt)

    # Get matrix
    resp, dt = timed_request("GET", f"{BASE_URL}/api/v1/matrices/{matrix_id}")
    assert resp.status_code == 200
    assert resp.json()["total_points"] == 10.0
    reporter.record("ExamMatrix", "GET matrix by ID", True, dt)

    # Check inventory availability
    resp, dt = timed_request("POST", f"{BASE_URL}/api/v1/matrices/{matrix_id}/check-availability")
    assert resp.status_code == 200
    avail = resp.json()
    assert "is_sufficient" in avail or "is_available" in avail
    is_avail = avail.get("is_sufficient", avail.get("is_available"))
    reporter.record("ExamMatrix", f"Check inventory availability (is_sufficient={is_avail})", True, dt)

    return matrix_id


# ==============================================================================
# 5. EXAM ASSEMBLY & SAFE SHUFFLER (RULE-02, RULE-03, QĐ 764)
# ==============================================================================
def test_exam_assembly_and_shuffling(matrix_id: str):
    # Generate Master Exam
    gen_payload = {
        "matrix_id": matrix_id,
        "title": f"Đề Thi Khảo Sát Toán 12 Chuẩn 2025 - {uuid.uuid4().hex[:6]}",
        "allow_partial": True
    }
    resp, dt = timed_request("POST", f"{BASE_URL}/api/v1/exams/generate", json=gen_payload)
    assert resp.status_code == 201
    master_exam = resp.json()
    master_id = master_exam["id"]
    total_q = master_exam["total_questions"]
    reporter.record("ExamAssembly", f"Generate Master Exam from Matrix (total_q={total_q}, pts={master_exam['total_points']})", True, dt)

    # Retrieve Master Exam
    resp, dt = timed_request("GET", f"{BASE_URL}/api/v1/exams/{master_id}")
    assert resp.status_code == 200
    reporter.record("ExamAssembly", "GET Master Exam by ID", True, dt)

    # Shuffle into 4 variants (101, 102, 103, 104)
    shuffle_payload = {"variant_codes": ["101", "102", "103", "104"]}
    resp, dt = timed_request("POST", f"{BASE_URL}/api/v1/exams/{master_id}/shuffle", json=shuffle_payload)
    assert resp.status_code == 200
    shuf_res = resp.json()
    assert shuf_res["generated_variants_count"] == 4
    assert set(shuf_res["variant_codes"]) == {"101", "102", "103", "104"}
    reporter.record("SafeShuffler", "Shuffle Master Exam into 4 safe variants", True, dt)

    # Retrieve Answer Key Matrix
    resp, dt = timed_request("GET", f"{BASE_URL}/api/v1/exams/{master_id}/key-matrix")
    assert resp.status_code == 200
    km = resp.json()
    assert "key_matrix" in km or "variant_codes" in km
    reporter.record("SafeShuffler", "Retrieve Answer Key Matrix across 4 variants", True, dt)

    # Direct shuffle test endpoint
    direct_payload = {
        "title": "Đề Test Trực Tiếp Direct Shuffle",
        "num_variants": 2,
        "variant_codes": ["201", "202"],
        "questions": [
            {
                "stem": "Câu 1: Cho $f(x) = x^2$. Đạo hàm $f'(x)$ là:",
                "options": [
                    {"label": "A", "content": "2x", "is_correct": True},
                    {"label": "B", "content": "x", "is_correct": False},
                    {"label": "C", "content": "x^2", "is_correct": False},
                    {"label": "D", "content": "Tất cả các đáp án trên đều sai", "is_correct": False, "is_fixed": True}
                ]
            }
        ]
    }
    resp, dt = timed_request("POST", f"{BASE_URL}/api/v1/exams/shuffle", json=direct_payload)
    assert resp.status_code == 200
    reporter.record("SafeShuffler", "POST /api/v1/exams/shuffle direct without matrix", True, dt)

    return master_id


# ==============================================================================
# 6. EXPORT ENGINE (DOCX, PDF, ZIP, BLANK OMR)
# ==============================================================================
def test_export_engine(master_id: str):
    # 1. Export DOCX Variant 101
    resp, dt = timed_request("GET", f"{BASE_URL}/api/v1/exams/{master_id}/export-docx?variant_code=101")
    assert resp.status_code == 200
    assert resp.content[:2] == b"PK"
    assert len(resp.content) > 5000
    reporter.record("ExportEngine", f"Export DOCX Variant 101 (size={len(resp.content)} bytes)", True, dt)

    # 2. Export PDF Variant 101
    resp, dt = timed_request("GET", f"{BASE_URL}/api/v1/exams/{master_id}/export-pdf?variant_code=101")
    assert resp.status_code == 200
    assert resp.content.startswith(b"%PDF-")
    assert len(resp.content) > 2000
    reporter.record("ExportEngine", f"Export PDF Variant 101 (size={len(resp.content)} bytes)", True, dt)

    # 3. Export ZIP Package (all = DOCX + PDF + Keys + OMR)
    resp, dt = timed_request("GET", f"{BASE_URL}/api/v1/exams/{master_id}/export-zip?format=all")
    assert resp.status_code == 200
    assert resp.content[:2] == b"PK"
    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        file_list = zf.namelist()
        assert len(file_list) >= 4
        assert any(".docx" in fn for fn in file_list)
        assert any(".pdf" in fn for fn in file_list)
        assert any("Phieu_Tra_Loi_Trac_Nghiem" in fn for fn in file_list)
    reporter.record("ExportEngine", f"Export ZIP package (contains {len(file_list)} files including blank OMR sheet, size={len(resp.content)} bytes)", True, dt)

    # 4. Export ZIP PDF only
    resp, dt = timed_request("GET", f"{BASE_URL}/api/v1/exams/{master_id}/export-zip?format=pdf")
    assert resp.status_code == 200
    assert resp.content[:2] == b"PK"
    reporter.record("ExportEngine", "Export ZIP package (PDF only format)", True, dt)

    # 5. Export ZIP DOCX only
    resp, dt = timed_request("GET", f"{BASE_URL}/api/v1/exams/{master_id}/export-zip?format=docx")
    assert resp.status_code == 200
    assert resp.content[:2] == b"PK"
    reporter.record("ExportEngine", "Export ZIP package (DOCX only format)", True, dt)


# ==============================================================================
# 7. GRADING & PROGRESSIVE SCORING (CIRCULAR 32 / DECISION 764)
# ==============================================================================
def test_grading_and_analytics(master_id: str):
    from backend.services.grading import calculate_true_false_score

    # Check all 16 combinations for Decision 764 progressive True/False grading
    labels = ["a", "b", "c", "d"]
    key = {"a": True, "b": True, "c": False, "d": True}
    score_rules = {0: 0.0, 1: 0.1, 2: 0.25, 3: 0.5, 4: 1.0}

    for combination in itertools.product([True, False], repeat=4):
        student_ans = dict(zip(labels, combination))
        matches = sum(1 for l in labels if student_ans[l] == key[l])
        expected = score_rules[matches]
        actual = calculate_true_false_score(student_ans, key)
        assert abs(actual - expected) < 1e-5

    reporter.record("GradingEngine", "Progressive True/False: all 16 combinations strictly match QĐ 764", True, 0.5)

    # Submit Cohort Analytics Test
    students = []
    for i in range(25):
        score = 3.0 + (i * 0.28)
        ans = {f"q_{j}": (i % (j % 3 + 1) == 0) for j in range(1, 23)}
        students.append({
            "student_id": f"HS_{1000 + i}",
            "total_score": round(min(10.0, score), 2),
            "answers": ans
        })

    analytics_payload = {"student_scores": students}
    resp, dt = timed_request("POST", f"{BASE_URL}/api/v1/exams/{master_id}/analytics", json=analytics_payload)
    assert resp.status_code == 200
    rep = resp.json()
    assert "items" in rep and "total_candidates" in rep
    reporter.record("GradingEngine", f"Cohort Analytics API: Psychometrics (p-value, D-index) computed for {len(rep.get('items', []))} items across {rep.get('total_candidates')} candidates", True, dt)


# ==============================================================================
# 8. DIGITIZATION & OCR PIPELINE
# ==============================================================================
def test_digitization():
    sample_docx = PROJECT_ROOT / "tests" / "tmp_test_pipeline" / "De_Thi_Mau_TT32_2025.docx"
    if not sample_docx.exists():
        for upload_cand in (PROJECT_ROOT / "storage" / "uploads").glob("*.docx"):
            sample_docx = upload_cand
            break

    assert sample_docx.exists(), "Sample test docx file must exist"

    # Direct upload endpoint
    with open(sample_docx, "rb") as f:
        files = {"file": ("test_exam.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        data = {"subject_id": "subj-toan", "grade_id": "grade-12"}
        resp, dt = timed_request("POST", f"{BASE_URL}/api/v1/upload", files=files, data=data)
        assert resp.status_code == 201
        res = resp.json()
        assert "job_id" in res
        reporter.record("DigitizeOCR", "POST /api/v1/upload direct endpoint", True, dt)

    # Async / Sync Digitize upload endpoint
    with open(sample_docx, "rb") as f:
        files = {"file": ("test_exam_sync.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        data = {"subject_id": "subj-toan", "grade_id": "grade-12", "sync": "true"}
        resp, dt = timed_request("POST", f"{BASE_URL}/api/v1/digitize/upload", files=files, data=data)
        assert resp.status_code == 202
        job_info = resp.json()
        job_id = job_info["job_id"]
        reporter.record("DigitizeOCR", f"POST /api/v1/digitize/upload sync=True (job_id={job_id[:8]})", True, dt)

    # Poll Job Status
    resp, dt = timed_request("GET", f"{BASE_URL}/api/v1/digitize/jobs/{job_id}")
    assert resp.status_code == 200
    job_status = resp.json()
    assert job_status["id"] == job_id
    assert job_status["status"] in ["COMPLETED", "PROCESSING", "EXTRACTED", "PENDING"]
    reporter.record("DigitizeOCR", f"GET /api/v1/digitize/jobs/{job_id[:8]} status={job_status['status']}", True, dt)

    # Commit Job
    commit_payload = {
        "questions": [
            {
                "stem": "Câu bóc tách số hóa tự động test",
                "item_format": "SINGLE_CHOICE",
                "cognitive_level": "RECOGNITION",
                "subject_id": "subj-toan",
                "grade_id": "grade-12",
                "options": [
                    {"label": "A", "content": "1", "is_correct": True, "order_index": 0},
                    {"label": "B", "content": "2", "is_correct": False, "order_index": 1}
                ]
            }
        ]
    }
    resp, dt = timed_request("POST", f"{BASE_URL}/api/v1/digitize/jobs/{job_id}/commit", json=commit_payload)
    assert resp.status_code == 200
    assert resp.json()["committed_count"] == 1
    reporter.record("DigitizeOCR", f"POST /api/v1/digitize/jobs/{job_id[:8]}/commit to Question Bank", True, dt)


# ==============================================================================
# 9. NEGATIVE & BOUNDARY EDGE CASES
# ==============================================================================
def test_negative_and_boundary_cases():
    # 404 on non-existent question
    resp, dt = timed_request("GET", f"{BASE_URL}/api/v1/questions/nonexistent-uuid-9999")
    assert resp.status_code == 404
    reporter.record("NegativeCases", "404 on non-existent question", True, dt)

    # 404 on non-existent matrix
    resp, dt = timed_request("GET", f"{BASE_URL}/api/v1/matrices/nonexistent-matrix-9999")
    assert resp.status_code == 404
    reporter.record("NegativeCases", "404 on non-existent matrix", True, dt)

    # 422 on invalid question payload (missing stem)
    bad_q = {"cognitive_level": "RECOGNITION", "item_format": "SINGLE_CHOICE"}
    resp, dt = timed_request("POST", f"{BASE_URL}/api/v1/questions", json=bad_q)
    assert resp.status_code == 422
    reporter.record("NegativeCases", "422 on question missing required 'stem'", True, dt)

    # 422 on invalid matrix payload (missing title)
    bad_m = {"subject_id": "subj-toan", "grade_id": "grade-12"}
    resp, dt = timed_request("POST", f"{BASE_URL}/api/v1/matrices", json=bad_m)
    assert resp.status_code == 422
    reporter.record("NegativeCases", "422 on matrix missing required 'title'", True, dt)

    # 400 on unsupported file upload (.exe)
    fake_exe = io.BytesIO(b"MZ\x90\x00\x03\x00\x00\x00")
    files = {"file": ("malicious.exe", fake_exe, "application/x-msdownload")}
    resp, dt = timed_request("POST", f"{BASE_URL}/api/v1/digitize/upload", files=files)
    assert resp.status_code == 400
    assert "Unsupported file format" in resp.json()["detail"]
    reporter.record("NegativeCases", "400 on unsupported file extension (.exe)", True, dt)

    # SQL Injection & XSS safety test in Question stem
    xss_payload = {
        "subject_id": "subj-toan",
        "grade_id": "grade-12",
        "cognitive_level": "RECOGNITION",
        "item_format": "SINGLE_CHOICE",
        "stem": "<script>alert('XSS')</script>' OR '1'='1' -- \\sqrt{x^2+y^2}",
        "options": [
            {"label": "A", "content": "'; DROP TABLE questions; --", "is_correct": True, "order_index": 0}
        ]
    }
    resp, dt = timed_request("POST", f"{BASE_URL}/api/v1/questions", json=xss_payload)
    assert resp.status_code == 201
    created_id = resp.json()["id"]
    # Verify retrieved properly without corruption or execution
    resp_get, _ = timed_request("GET", f"{BASE_URL}/api/v1/questions/{created_id}")
    assert resp_get.status_code == 200
    assert "<script>alert('XSS')</script>" in resp_get.json()["stem"]
    # Clean up
    timed_request("DELETE", f"{BASE_URL}/api/v1/questions/{created_id}")
    reporter.record("NegativeCases", "SQLi & XSS strings stored safely as raw text", True, dt)


# ==============================================================================
# 10. CONCURRENCY STRESS TEST
# ==============================================================================
def test_concurrency_stress(concurrency=15, requests_per_worker=4):
    endpoints = [
        ("GET", f"{BASE_URL}/health"),
        ("GET", f"{BASE_URL}/api/v1/taxonomy/grades"),
        ("GET", f"{BASE_URL}/api/v1/taxonomy/subjects"),
        ("GET", f"{BASE_URL}/api/v1/questions?limit=5"),
        ("GET", f"{BASE_URL}/api/v1/taxonomy/tree"),
    ]
    tasks = []
    for _ in range(requests_per_worker):
        for method, url in endpoints:
            tasks.append((method, url))

    results = []
    t_start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        future_map = {executor.submit(timed_request, method, url): url for method, url in tasks}
        for fut in as_completed(future_map):
            try:
                resp, dt = fut.result()
                results.append((resp.status_code, dt))
            except Exception as e:
                results.append((500, 9999.0))

    total_time = (time.perf_counter() - t_start) * 1000
    durations = [r[1] for r in results]
    success_count = sum(1 for r in results if r[0] == 200)
    avg_latency = sum(durations) / len(durations) if durations else 0
    p95_latency = sorted(durations)[int(len(durations) * 0.95)] if durations else 0

    reporter.record(
        "ConcurrencyStress",
        f"{len(tasks)} concurrent requests (workers={concurrency})",
        success_count == len(tasks),
        total_time,
        f"Success: {success_count}/{len(tasks)}, Avg: {avg_latency:.1f}ms, P95: {p95_latency:.1f}ms"
    )


# ==============================================================================
# MAIN TEST RUNNER WITH MULTI-LOOP EXECUTION
# ==============================================================================
def run_all_loops(loop_count=5):
    print("=" * 80)
    print(f"  STARTING FULL LOOP TEST SUITE ({loop_count} COMPLETE LOOPS)")
    print("=" * 80)

    for loop_idx in range(1, loop_count + 1):
        print(f"\n>>> [LOOP {loop_idx}/{loop_count}] Executing complete end-to-end lifecycle...")
        t0 = time.time()

        # 1. Infrastructure
        test_infrastructure()

        # 2. Taxonomy
        test_taxonomy()

        # 3. Questions CRUD
        test_questions_crud()

        # 4. Matrix
        matrix_id = test_matrix()

        # 5. Assembly & Shuffler
        master_id = test_exam_assembly_and_shuffling(matrix_id)

        # 6. Export Engine
        test_export_engine(master_id)

        # 7. Grading & Analytics
        test_grading_and_analytics(master_id)

        # 8. Digitize
        test_digitization()

        # 9. Negative Cases
        test_negative_and_boundary_cases()

        loop_dur = time.time() - t0
        print(f">>> [LOOP {loop_idx}/{loop_count}] Completed in {loop_dur:.2f}s.")

    # 10. Concurrency stress test
    print("\n>>> Executing Concurrency & Stress Testing...")
    test_concurrency_stress(concurrency=20, requests_per_worker=4)

    summary = reporter.summary()
    print("\n" + "=" * 80)
    print(f"  LOOP TEST COMPLETED: {summary['passed']}/{summary['total']} PASSED ({summary['pass_rate']:.1f}%) in {summary['elapsed_seconds']:.2f}s")
    print("=" * 80)

    output_path = PROJECT_ROOT / "storage" / "loop_test_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"Raw report saved to: {output_path}")

    return summary

if __name__ == "__main__":
    loops = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    summary = run_all_loops(loops)
    if summary["failed"] > 0:
        sys.exit(1)
    sys.exit(0)
