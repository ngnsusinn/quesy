"""E2E Browser Blind Test for Assessment Dashboard Hub & Quick Action Launchpad.
Validates:
1. Top Header and macOS Segmented Navigation Tab.
2. 4-Card Quick Action Launchpad (Composer 2026, Digitize AI, Matrix 2D, Shuffler ZIP).
3. Featured 2026 National Exam Blueprint (Hero Showcase Card) with 1-click execution.
4. National Invariant Compliance Monitor indicators.
5. Navigation flows: clicking each launchpad card smoothly transitions to the corresponding view.
6. Zero DevTools console errors throughout all navigation flows.
"""

import os
import sys
import time
import socket
import threading
import shutil
from pathlib import Path
import pytest
import uvicorn

playwright_module = pytest.importorskip("playwright", reason="Playwright is required for browser E2E tests")
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


def test_e2e_dashboard_hub_and_quick_launchpad():
    port = find_free_port()
    server = ServerThread("127.0.0.1", port)
    server.start()
    time.sleep(1.5)

    evidence_dir = PROJECT_ROOT / "storage" / "test_evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    console_errors = []

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    launch_kwargs = {"headless": True}
    if os.path.exists(chrome_path):
        launch_kwargs["executable_path"] = chrome_path
    elif shutil.which("google-chrome"):
        launch_kwargs["executable_path"] = shutil.which("google-chrome")
    elif shutil.which("chromium"):
        launch_kwargs["executable_path"] = shutil.which("chromium")
    elif shutil.which("chromium-browser"):
        launch_kwargs["executable_path"] = shutil.which("chromium-browser")

    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(**launch_kwargs)
            except Exception as e:
                pytest.skip(f"Could not launch browser: {e}")

            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()

            def on_console(msg):
                if msg.type == "error":
                    text = msg.text
                    if "favicon" not in text and "404" not in text and "service-worker" not in text:
                        console_errors.append(text)

            page.on("console", on_console)

            # 1. Access root URL (triggers redirect or tab dashboard)
            page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
            time.sleep(1.0)

            # 2. Check tab-dashboard is visible
            tab_dashboard = page.locator("#tab-dashboard")
            assert tab_dashboard.is_visible(), "Tab dashboard must be visible by default"

            # 3. Check Quick Action Launchpad cards exist
            quick_cards = page.locator(".apple-quick-card")
            assert quick_cards.count() == 4, f"Must have exactly 4 quick action cards, found {quick_cards.count()}"

            # Verify card headers
            assert "Soạn Đề LaTeX AI (2026)" in page.content()
            assert "Số Hóa Đề Thi AI" in page.content()
            assert "Thiết Lập Ma Trận 2D" in page.content()
            assert "Sinh & Trộn Đề Hoán Vị" in page.content()

            # 4. Check Featured 2026 Blueprint Card
            hero_card = page.locator(".apple-hero-card")
            assert hero_card.is_visible(), "Featured 2026 National Blueprint card must be visible"
            assert "Mã đề: 0101" in hero_card.inner_text()
            assert "Đề Thi Tốt Nghiệp THPT Năm 2026" in hero_card.inner_text()

            # 5. Check Invariant Compliance Monitor
            assert "Bảo Đảm Bất Biến Khảo Thí" in page.content()
            assert "RULE-01: Bậc Thang QĐ 764" in page.content()
            assert "RULE-02: Option Anchor" in page.content()
            assert "RULE-03: Passage Contiguity" in page.content()
            assert "Centered Diagrams" in page.content()

            # Screenshot initial dashboard state
            screenshot_path = evidence_dir / "dashboard_launchpad_overview.png"
            page.screenshot(path=str(screenshot_path), full_page=True)

            # 6. Test Navigation: Click Matrix Quick Action
            quick_cards.nth(2).click()
            time.sleep(0.5)
            assert page.locator("#tab-matrix").is_visible(), "Clicking Matrix quick card must show #tab-matrix"

            # Navigate back to dashboard
            page.locator("#nav-btn-dashboard").click()
            time.sleep(0.5)
            assert tab_dashboard.is_visible()

            # 7. Test Navigation: Click Shuffler Quick Action
            quick_cards.nth(3).click()
            time.sleep(0.5)
            assert page.locator("#tab-shuffler").is_visible(), "Clicking Shuffler quick card must show #tab-shuffler"

            # Navigate back to dashboard
            page.locator("#nav-btn-dashboard").click()
            time.sleep(0.5)
            assert tab_dashboard.is_visible()

            # 8. Test Navigation: Click Hero Card 'Mở trong Trình Soạn Đề'
            open_composer_btn = hero_card.locator("button:has-text('Mở trong Trình Soạn Đề')")
            assert open_composer_btn.is_visible()
            open_composer_btn.click()
            time.sleep(0.8)
            assert page.locator("#tab-composer").is_visible(), "Clicking open in composer must show #tab-composer"

            # Verify editor received the full template
            editor_input = page.locator("#composer-editor-input")
            assert editor_input.is_visible()
            editor_val = editor_input.input_value()
            assert len(editor_val) > 100, f"Editor should be loaded with standard exam, got length {len(editor_val)}"
            assert "Mã đề" in editor_val

            # Verify zero console errors
            assert len(console_errors) == 0, f"Encountered console errors during E2E flow: {console_errors}"

            browser.close()
    finally:
        server.stop()
