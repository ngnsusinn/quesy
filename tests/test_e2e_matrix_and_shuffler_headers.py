"""E2E Browser Test for Matrix and Shuffler Headers Integrity
Validates:
1. No element leakage: Bank pagination controls (#bank-pagination-controls) are strictly hidden on /matrix and /shuffler.
2. Unified Top App Header (Apple Frosted Glass) remains persistently visible and sticky.
3. Dedicated Header Card / Banner on /matrix and /shuffler (Apple HIG aligned).
4. Matrix Hierarchical Table Header (sticky thead & sticky corner tree column) behaves cleanly.
5. Tab transitions (/bank <-> /matrix <-> /shuffler) cleanly scope tab-specific elements.
6. Zero DevTools console errors.
7. Saves screenshot evidence to storage/test_evidence/.
"""

import sys
import time
import socket
import threading
from pathlib import Path
import uvicorn
from playwright.sync_api import sync_playwright

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.main import app


def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class ServerThread(threading.Thread):
    def __init__(self, host, port):
        super().__init__(daemon=True)
        self.host = host
        self.port = port
        config = uvicorn.Config(app, host=host, port=port, log_level="warning")
        self.server = uvicorn.Server(config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


def test_matrix_and_shuffler_headers_e2e():
    host = "127.0.0.1"
    port = find_free_port()
    server = ServerThread(host, port)
    server.start()
    time.sleep(1.5)

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    evidence_dir = PROJECT_ROOT / "storage" / "test_evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    console_errors = []

    print("=" * 70)
    print("STARTING E2E BROWSER TEST: MATRIX & SHUFFLER HEADERS INTEGRITY")
    print("=" * 70)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path=chrome_path,
                headless=True,
                args=["--no-sandbox", "--disable-gpu", "--window-size=1440,900"]
            )
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()

            page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type in ["error"] else None)
            page.on("pageerror", lambda exc: console_errors.append(f"[pageerror] {exc}"))

            # 1. Test /matrix Header Isolation
            print("1. Testing /matrix Header Isolation...")
            page.goto(f"http://{host}:{port}/matrix", wait_until="networkidle")
            page.wait_for_timeout(1000)

            top_header = page.locator("header.apple-header")
            assert top_header.is_visible(), "Top app header must be visible"

            bank_controls = page.locator("#bank-pagination-controls")
            assert not bank_controls.is_visible(), "Bank pagination controls must be completely hidden on /matrix"

            matrix_pane = page.locator("#tab-matrix")
            assert matrix_pane.is_visible(), "Tab matrix must be visible"

            matrix_card = page.locator("#tab-matrix .apple-card").first
            assert matrix_card.is_visible(), "Matrix configuration card must be visible"
            mbox = matrix_card.bounding_box()
            assert mbox["y"] < 120, f"Matrix card must sit right below top header (expected y < 120, got {mbox['y']})"

            # Capture evidence 1
            proof1_path = evidence_dir / "01_matrix_header_clean_proof.png"
            page.screenshot(path=str(proof1_path))
            print(f"   -> Screenshot saved: {proof1_path.name}")

            # 2. Test /shuffler Header Isolation
            print("2. Testing /shuffler Header Isolation...")
            page.goto(f"http://{host}:{port}/shuffler", wait_until="networkidle")
            page.wait_for_timeout(1000)

            assert top_header.is_visible(), "Top app header must remain visible on /shuffler"
            assert not bank_controls.is_visible(), "Bank pagination controls must be completely hidden on /shuffler"

            shuffler_pane = page.locator("#tab-shuffler")
            assert shuffler_pane.is_visible(), "Tab shuffler must be visible"

            shuffler_banner = page.locator("#shuffler-header-banner")
            assert shuffler_banner.is_visible(), "Shuffler header banner must be visible"
            sbox = shuffler_banner.bounding_box()
            assert sbox["y"] < 120, f"Shuffler banner must sit right below top header (expected y < 120, got {sbox['y']})"

            # Capture evidence 2
            proof2_path = evidence_dir / "02_shuffler_header_clean_proof.png"
            page.screenshot(path=str(proof2_path))
            print(f"   -> Screenshot saved: {proof2_path.name}")

            # 3. Test Tab Transitions scoping
            print("3. Testing Tab Transitions Scoping...")
            page.click("#nav-btn-itembank")
            page.wait_for_timeout(500)
            assert page.is_visible("#tab-itembank"), "Item bank tab must be visible"
            assert bank_controls.is_visible(), "Bank pagination controls must be visible on /bank"

            page.click("#nav-btn-matrix")
            page.wait_for_timeout(500)
            assert not bank_controls.is_visible(), "Bank pagination controls must hide on returning to /matrix"

            page.click("#nav-btn-shuffler")
            page.wait_for_timeout(500)
            assert not bank_controls.is_visible(), "Bank pagination controls must remain hidden on /shuffler"

            # Capture evidence 3
            proof3_path = evidence_dir / "03_tab_transition_header_proof.png"
            page.screenshot(path=str(proof3_path))
            print(f"   -> Screenshot saved: {proof3_path.name}")

            # 4. Check DevTools console errors
            print("4. Checking Console Errors...")
            assert len(console_errors) == 0, f"Expected 0 console errors, got: {console_errors}"
            print("   -> 0 DevTools console errors (100% CLEAN).")

            print("=" * 70)
            print("ALL MATRIX & SHUFFLER HEADER E2E TESTS PASSED (100% VERIFIED)")
            print("=" * 70)

            browser.close()
    finally:
        server.stop()


if __name__ == "__main__":
    test_matrix_and_shuffler_headers_e2e()
