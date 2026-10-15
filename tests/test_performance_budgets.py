import time
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal
from backend.models import MasterExam, ExamMatrix
from backend.services.shuffling_engine import generate_shuffled_variants, get_answer_key_matrix
from backend.services.matrix_solver import solve_and_generate_master_exam
from backend.services.docx_exporter import export_exam_package_zip
from backend.services.tagging_service import cosine_similarity

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture(scope="module")
def db_session():
    session = SessionLocal()
    yield session
    session.close()


def test_perf_budget_taxonomy_tree_latency(client):
    """
    Performance Budget: GET /api/v1/taxonomy/tree must respond in < 250ms (Rule: vitals-core-web-vitals-budget)
    """
    # Arrange & Warm up
    client.get("/api/v1/taxonomy/tree")

    # Act
    start_time = time.perf_counter()
    res = client.get("/api/v1/taxonomy/tree")
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    # Assert
    assert res.status_code == 200
    print(f"\n[PERF] Taxonomy Tree Latency: {elapsed_ms:.2f} ms (Budget: < 250 ms)")
    assert elapsed_ms < 250.0, f"Taxonomy tree exceeded latency budget: {elapsed_ms:.2f}ms"


def test_perf_budget_deduplication_cosine_similarity():
    """
    Performance Budget: Computing 500 vector similarity checks must complete in < 150ms
    """
    # Arrange
    v1 = [0.05 * i for i in range(128)]
    v2 = [0.03 * i for i in range(128)]

    # Act
    start_time = time.perf_counter()
    for _ in range(500):
        sim = cosine_similarity(v1, v2)
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    # Assert
    assert sim > 0.0
    print(f"\n[PERF] 500 Vector Cosine Similarity Checks: {elapsed_ms:.2f} ms (Budget: < 150 ms)")
    assert elapsed_ms < 150.0, f"Vector similarity exceeded latency budget: {elapsed_ms:.2f}ms"


def test_perf_budget_shuffling_engine(db_session):
    """
    Performance Budget: Shuffling 4 safe variants with answer key matrix must complete in < 600ms
    """
    # Arrange: find a MasterExam with items
    master = db_session.query(MasterExam).first()
    if not master:
        pytest.skip("No master exam available for shuffling performance test.")

    # Act
    start_time = time.perf_counter()
    variants = generate_shuffled_variants(
        master_exam_id=master.id,
        db=db_session,
        variant_codes=["101", "102", "103", "104"]
    )
    matrix = get_answer_key_matrix(master.id, db_session)
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    # Assert
    assert len(variants) == 4
    assert "key_matrix" in matrix
    print(f"\n[PERF] Shuffling Engine 4 Variants: {elapsed_ms:.2f} ms (Budget: < 600 ms)")
    assert elapsed_ms < 600.0, f"Shuffling engine exceeded latency budget: {elapsed_ms:.2f}ms"


def test_perf_budget_docx_and_zip_export(db_session):
    """
    Performance Budget: Generating complete 4-variant Word DOCX + Answer Sheets ZIP package (9 DOCX files) in < 6000ms (NFR budget: < 10000ms)
    """
    # Arrange: find a master exam
    master = db_session.query(MasterExam).first()
    if not master:
        pytest.skip("No master exam available for docx export performance test.")

    # Act
    start_time = time.perf_counter()
    zip_path = export_exam_package_zip(
        master_exam_id=master.id,
        db=db_session,
        include_pdf=False,
        export_format="docx"
    )
    elapsed_ms = (time.perf_counter() - start_time) * 1000

    # Assert
    import os
    assert os.path.exists(zip_path)
    assert os.path.getsize(zip_path) > 10000
    assert str(zip_path).endswith(".zip")
    print(f"\n[PERF] DOCX & ZIP Bundle Export: {elapsed_ms:.2f} ms (Budget: < 6000 ms, NFR: < 10000 ms)")
    assert elapsed_ms < 6000.0, f"DOCX & ZIP export exceeded latency budget: {elapsed_ms:.2f}ms"
