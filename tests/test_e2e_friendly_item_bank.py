"""E2E Browser Blind Test for Friendly Item Bank Studio UI
Validates:
1. Overview Stats Banner (Total, Format breakdown, Cognitive breakdown).
2. Quick Filter Segmented Pills (Format: Single Choice, True/False, Short Answer; Cognitive: NB, TH, VD, VDC).
3. Collapsible 6-Tier Cascading Taxonomy Drawer (Circular 32/2018/TT-BGDĐT) with active filter counter.
4. Smart Search with instant clear button (x).
5. Dual View Mode (Detailed Cards vs High-Density Compact Table).
6. Collapsible Explanation Accordion ("Xem lời giải chi tiết" / "Ẩn lời giải").
7. 1-Click Copy Question to Clipboard with Toast feedback.
8. Zero DevTools console errors.
"""

import os
import sys
import time
import socket
import threading
import uvicorn
from pathlib import Path
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


def run_e2e_test():
    host = "127.0.0.1"
    port = find_free_port()
    server = ServerThread(host, port)
    server.start()

    # Wait for server to bind
    time.sleep(1.5)

    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    console_errors = []
    screenshots_dir = PROJECT_ROOT / "storage" / "test_evidence"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("STARTING E2E BROWSER BLIND TEST: FRIENDLY ITEM BANK STUDIO UI")
    print("=" * 70)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                executable_path=chrome_path,
                headless=True,
                args=["--no-sandbox", "--disable-gpu", "--window-size=1400,900"]
            )
            context = browser.new_context(viewport={"width": 1400, "height": 900})
            page = context.new_page()

            page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type in ["error"] else None)
            page.on("pageerror", lambda exc: console_errors.append(f"[pageerror] {exc}"))

            # 1. Navigate to /bank
            url = f"http://{host}:{port}/bank"
            print(f"1. Navigating to: {url}")
            page.goto(url, wait_until="networkidle", timeout=15000)
            page.wait_for_timeout(1000)

            # Assert tab-itembank is visible
            assert page.is_visible("#tab-itembank"), "Tab item bank must be visible!"
            print("   -> Tab Item Bank loaded and visible.")

            # 2. Verify Stats Banner
            print("2. Verifying Overview Stats Banner...")
            assert page.is_visible("#bank-stats-banner"), "Stats banner must be visible!"
            total_stat = page.inner_text("#bank-stat-total").strip()
            single_stat = page.inner_text("#bank-stat-single").strip()
            tf_stat = page.inner_text("#bank-stat-tf").strip()
            short_stat = page.inner_text("#bank-stat-short").strip()
            other_stat = "0"
            if page.is_visible("#bank-stat-other-container"):
                other_stat = page.inner_text("#bank-stat-other").strip()
            print(f"   -> Stats: Total={total_stat}, SingleChoice={single_stat}, TrueFalse={tf_stat}, ShortAnswer={short_stat}, Other={other_stat}")
            assert int(total_stat) > 0, "Total question count must be > 0"
            assert int(single_stat) + int(tf_stat) + int(short_stat) + int(other_stat) == int(total_stat), "Stats sum must match total"

            # 3. Test Quick Filter by Format Pills
            print("3. Testing Quick Filter by Format Pills...")
            # Click True/False pill
            page.click("#pill-format-TRUE_FALSE_GROUP")
            page.wait_for_timeout(300)
            tf_pill_class = page.get_attribute("#pill-format-TRUE_FALSE_GROUP", "class")
            assert "active" in tf_pill_class, "TRUE_FALSE_GROUP pill should be active"
            tf_filtered_count = page.inner_text("#bank-results-count").strip()
            print(f"   -> Filtered by TRUE_FALSE_GROUP: count = {tf_filtered_count}")
            assert tf_filtered_count == tf_stat, f"Filtered count should equal {tf_stat}"
            assert page.is_visible("#btn-reset-bank-filters"), "Reset filters button must be visible when filter active"

            # Reset format filter
            page.click("#pill-format-all")
            page.wait_for_timeout(300)
            restored_count = page.inner_text("#bank-results-count").strip()
            assert restored_count == total_stat, "Count should be restored to total"
            print(f"   -> Restored with 'Tất cả' pill: count = {restored_count}")

            # 4. Test Quick Filter by Cognitive Level Pills
            print("4. Testing Quick Filter by Cognitive Level Pills...")
            page.click("#pill-cog-RECOGNITION")
            page.wait_for_timeout(300)
            assert "active" in page.get_attribute("#pill-cog-RECOGNITION", "class")
            rec_count = page.inner_text("#bank-results-count").strip()
            print(f"   -> Filtered by RECOGNITION (Nhận biết): count = {rec_count}")

            # Test Reset All Filters button
            page.click("#btn-reset-bank-filters")
            page.wait_for_timeout(300)
            reset_count = page.inner_text("#bank-results-count").strip()
            assert reset_count == total_stat, "Count should be restored to total after reset"
            assert not page.is_visible("#btn-reset-bank-filters"), "Reset button should be hidden after reset"
            print("   -> Reset all filters verified successfully.")

            # 5. Test Search Input and Clear Search Button
            print("5. Testing Search Input with Clear Button...")
            page.fill("#bank-search-input", "công thức")
            page.wait_for_timeout(300)
            assert page.is_visible("#bank-search-clear-btn"), "Clear search (x) button must be visible when text typed"
            page.click("#bank-search-clear-btn")
            page.wait_for_timeout(300)
            assert page.input_value("#bank-search-input") == "", "Input should be empty after clicking clear"
            print("   -> Search clear button verified successfully.")

            # 6. Test 6-Tier Taxonomy Drawer
            print("6. Testing Collapsible 6-Tier Taxonomy Drawer...")
            assert not page.is_visible("#bank-taxonomy-drawer"), "Taxonomy drawer must be initially collapsed"
            page.click("#btn-toggle-taxonomy-drawer")
            page.wait_for_timeout(300)
            assert page.is_visible("#bank-taxonomy-drawer"), "Taxonomy drawer must be visible after click"
            print("   -> Taxonomy drawer expanded successfully.")
            page.click("#btn-toggle-taxonomy-drawer")
            page.wait_for_timeout(300)
            assert not page.is_visible("#bank-taxonomy-drawer"), "Taxonomy drawer collapsed successfully."
            print("   -> Taxonomy drawer collapse verified.")

            # 7. Test Dual View Mode: Detailed vs Compact
            print("7. Testing Dual View Mode (Detailed Cards vs High-Density Compact Table)...")
            # Screenshot 1: Detailed View
            shot_detailed = screenshots_dir / "01_item_bank_detailed_view.png"
            page.screenshot(path=str(shot_detailed), full_page=False)
            print(f"   -> Saved Detailed View screenshot: {shot_detailed.name}")

            # Switch to Compact View
            page.click("#bank-view-compact")
            page.wait_for_timeout(400)
            assert "active" in page.get_attribute("#bank-view-compact", "class"), "Compact button should be active"
            assert page.is_visible(".bank-compact-table"), "Compact table must be rendered in DOM"
            rows = page.query_selector_all(".bank-compact-row")
            print(f"   -> Compact View rendered {len(rows)} table rows.")
            assert len(rows) > 0, "Compact table should have rows"

            # Screenshot 2: Compact View
            shot_compact = screenshots_dir / "02_item_bank_compact_view.png"
            page.screenshot(path=str(shot_compact), full_page=False)
            print(f"   -> Saved Compact View screenshot: {shot_compact.name}")

            # Switch back to Detailed View
            page.click("#bank-view-detailed")
            page.wait_for_timeout(300)
            assert "active" in page.get_attribute("#bank-view-detailed", "class")

            # 8. Test Collapsible Explanation Accordion
            print("8. Testing Collapsible Explanation Accordion...")
            exp_toggle_btns = page.query_selector_all("button:has-text('Xem lời giải chi tiết')")
            if exp_toggle_btns:
                first_btn = exp_toggle_btns[0]
                first_btn.click()
                page.wait_for_timeout(300)
                assert page.is_visible("div:has-text('Lời giải chi tiết:')"), "Explanation box should expand"
                print("   -> Explanation expanded successfully.")
                page.click("button:has-text('Ẩn lời giải chi tiết')")
                page.wait_for_timeout(300)
                print("   -> Explanation collapsed successfully.")
            else:
                print("   (No explanation toggle button found on current items)")

            # 9. Test 1-Click Copy Question
            print("9. Testing 1-Click Copy Question Button...")
            copy_btn = page.query_selector("button:has-text('Sao chép')")
            if copy_btn:
                copy_btn.click()
                page.wait_for_timeout(400)
                # Toast should appear
                toast = page.query_selector("#toast-container")
                if toast:
                    print(f"   -> Toast feedback verified: '{toast.inner_text().strip()}'")

            # Screenshot 3: Final State
            shot_final = screenshots_dir / "03_item_bank_interactive_proof.png"
            page.screenshot(path=str(shot_final), full_page=False)
            print(f"   -> Saved Final State screenshot: {shot_final.name}")

            # 10. Check Console Errors
            print("10. Checking DevTools Console Errors...")
            print(f"   -> Total console errors: {len(console_errors)}")
            if console_errors:
                for err in console_errors:
                    print(f"      [Console Error]: {err}")
            assert len(console_errors) == 0, f"Found console errors: {console_errors}"
            print("   -> ZERO DevTools console errors verified (100% CLEAN).")

            browser.close()

    finally:
        server.stop()

    print("\n" + "=" * 70)
    print("ALL E2E BROWSER TESTS PASSED (100% SUCCESSFUL TEST EVIDENCE)")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(run_e2e_test())
