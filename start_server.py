import os
import sys
from pathlib import Path

# Ensure project root is first in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ["PYTHONPATH"] = str(PROJECT_ROOT)

import uvicorn
from backend.database import engine, Base, SessionLocal
from backend.seed_data import seed_database
from backend.models import Question

def setup_and_run():
    print("================================================================")
    print("  QUESY: Assessment & Item Bank System (Circular 32/2018)")
    print("  Hệ thống Quản lý Đề thi & Ngân hàng Câu hỏi Tích hợp AI")
    print("================================================================")

    # 1. Initialize Tables
    print("[1/3] Khởi tạo cấu trúc bảng Cơ sở dữ liệu...")
    Base.metadata.create_all(bind=engine)

    # 2. Seed Data if database is empty
    print("[2/3] Kiểm tra & nạp dữ liệu chuẩn hóa Thông tư 32...")
    db = SessionLocal()
    try:
        q_count = db.query(Question).count()
        if q_count < 30:
            print(f"       Ngân hàng hiện có {q_count} câu. Đang nạp bộ dữ liệu mẫu Toán 12...")
            seed_database(db, force_reset=False)
            print(f"       Đã nạp thành công! Tổng câu hỏi: {db.query(Question).count()}")
        else:
            print(f"       Ngân hàng đã sẵn sàng ({q_count} câu hỏi).")
    finally:
        db.close()

    # 3. Start Server
    print("[3/3] Khởi động máy chủ Quesy API & Web Studio...")
    print("       -> Ứng dụng Web Studio: http://127.0.0.1:8000")
    print("       -> Tài liệu Swagger API: http://127.0.0.1:8000/docs")
    print("       -> Health check:         http://127.0.0.1:8000/health")
    print("================================================================")

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":
    setup_and_run()
