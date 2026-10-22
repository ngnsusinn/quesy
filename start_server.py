import os
import sys
import socket
import argparse
import subprocess
from pathlib import Path

# Clean sys.path: remove any foreign hermes venvs from sys.path
sys.path = [p for p in sys.path if "hermes\\installs" not in p and "hermes/installs" not in p]
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
os.environ["PYTHONPATH"] = str(PROJECT_ROOT)

import uvicorn
from backend.database import engine, Base, SessionLocal
from backend.seed_data import seed_database
from backend.models import Question


def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Checks if a TCP port is currently occupied."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0


def find_pid_by_port(port: int) -> list:
    """Finds PIDs listening on a given port on Windows."""
    pids = []
    try:
        output = subprocess.check_output("netstat -ano", shell=True, text=True)
        for line in output.splitlines():
            if f":{port} " in line and "LISTENING" in line:
                parts = line.strip().split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    if pid.isdigit() and int(pid) != os.getpid():
                        pids.append(int(pid))
    except Exception:
        pass
    return list(set(pids))


def free_port(port: int, host: str = "127.0.0.1") -> bool:
    """Attempts to kill processes occupying the port."""
    pids = find_pid_by_port(port)
    if not pids:
        return True
    print(f"[!] Phát hiện tiến trình đang chiếm dụng cổng {port} (PID: {pids}). Đang giải phóng...")
    success = True
    for pid in pids:
        try:
            subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True, check=False)
            print(f"    -> Đã tắt tiến trình PID {pid} thành công.")
        except Exception as e:
            print(f"    -> Không thể tắt PID {pid}: {e}")
            success = False

    # Allow Windows TCP stack a brief moment (up to 1.5s) to release socket
    import time
    for _ in range(8):
        if not is_port_in_use(port, host):
            return True
        time.sleep(0.2)

    return not is_port_in_use(port, host)


def find_next_available_port(start_port: int = 8000, max_attempts: int = 20, host: str = "127.0.0.1") -> int:
    """Finds the next available port if the default is in use."""
    for port in range(start_port, start_port + max_attempts):
        if not is_port_in_use(port, host):
            return port
    return start_port


def parse_args():
    parser = argparse.ArgumentParser(description="Khởi chạy hệ thống Quesy Assessment & Item Bank")
    parser.add_argument("--host", default="127.0.0.1", help="Host address (mặc định: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port máy chủ (mặc định: 8000)")
    parser.add_argument("--kill", action="store_true", default=True, help="Tự động giải phóng cổng nếu đang bị chiếm dụng (mặc định: True)")
    parser.add_argument("--no-kill", dest="kill", action="store_false", help="Không tự động tắt tiến trình cũ, tự đổi sang cổng tiếp theo")
    return parser.parse_args()


def setup_and_run():
    args = parse_args()
    host = args.host
    port = args.port

    print("================================================================")
    print("  QUESY: Assessment & Item Bank System (Circular 32/2018)")
    print("  Hệ thống Quản lý Đề thi & Ngân hàng Câu hỏi Tích hợp AI")
    print("================================================================")

    # Check port availability
    if is_port_in_use(port, host):
        if args.kill:
            freed = free_port(port)
            if not freed:
                new_port = find_next_available_port(port + 1, host=host)
                print(f"[!] Không thể giải phóng cổng {port}. Tự động chuyển sang cổng mới: {new_port}")
                port = new_port
        else:
            new_port = find_next_available_port(port + 1, host=host)
            print(f"[!] Cổng {port} đang bận. Tự động chuyển sang cổng mới: {new_port}")
            port = new_port

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
    print(f"       -> Ứng dụng Web Studio: http://{host}:{port}")
    print(f"       -> Tài liệu Swagger API: http://{host}:{port}/docs")
    print(f"       -> Health check:         http://{host}:{port}/health")
    print("================================================================")

    uvicorn.run("backend.main:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    setup_and_run()
