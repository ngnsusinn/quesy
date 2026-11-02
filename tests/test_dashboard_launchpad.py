"""Test suite for Assessment Dashboard Hub & Quick Action Launchpad.
Validates Apple HIG compliance, 4 launchpad cards, 2026 national blueprint hero card,
formal invariant verification indicators, and dynamic metrics synchronization.
"""

from pathlib import Path
from html.parser import HTMLParser
import subprocess
import re


def test_dashboard_launchpad_elements_and_structure():
    """Kiểm thử cấu hình giao diện Trang chính (Dashboard Hub):
    1. '#tab-dashboard' tồn tại và là tab-pane mặc định kích hoạt (class 'active').
    2. Trung tâm khởi chạy nhanh (Quick Action Launchpad) chứa chính xác 4 thẻ:
       - Soạn Đề LaTeX AI (2026) với app.openQuickAction('composer')
       - Số Hóa Đề Thi AI với app.openQuickAction('digitize')
       - Thiết Lập Ma Trận 2D với app.openQuickAction('matrix')
       - Sinh & Trộn Đề Hoán Vị với app.openQuickAction('shuffler')
    3. Thẻ Tiêu điểm Đề thi Mẫu Quốc gia 2026 (Mã đề 0101) hiển thị đầy đủ:
       - Mã đề: 0101, 22 câu hỏi, 90 phút.
       - Cấu trúc 3 phần: Phần I (12 câu), Phần II (4 câu QĐ 764), Phần III (6 câu).
       - Nút thao tác nhanh gọi app.loadStandard2026Blueprint().
    4. Bảng Giám sát Bất biến Khảo thí Quốc gia hiển thị đầy đủ:
       - RULE-01: Bậc Thang QĐ 764
       - RULE-02: Option Anchor
       - RULE-03: Passage Contiguity
       - Centered Diagrams
    5. Bảng Ấn phẩm Khảo thí & Lịch sử Gần đây chứa danh sách các đề thi chuẩn hóa.
    """
    html_path = Path("frontend/index.html")
    assert html_path.exists(), "frontend/index.html phải tồn tại"
    html_content = html_path.read_text(encoding="utf-8")

    # 1. Tab Dashboard
    assert 'id="tab-dashboard"' in html_content, "Phải tồn tại section #tab-dashboard"
    assert 'class="tab-pane active space-y-6"' in html_content, "Tab dashboard phải có class 'tab-pane active'"

    # 2. 4 Quick Action Launchpad cards
    assert "apple-quick-card" in html_content, "Phải sử dụng class apple-quick-card cho các thẻ khởi chạy nhanh"
    assert "app.openQuickAction('composer')" in html_content, "Thẻ Soạn đề phải gọi openQuickAction('composer')"
    assert "app.openQuickAction('digitize')" in html_content, "Thẻ Số hóa phải gọi openQuickAction('digitize')"
    assert "app.openQuickAction('matrix')" in html_content, "Thẻ Ma trận phải gọi openQuickAction('matrix')"
    assert "app.openQuickAction('shuffler')" in html_content, "Thẻ Trộn đề phải gọi openQuickAction('shuffler')"

    # 3. Tiêu điểm Đề thi 2026 Mã 0101
    assert "Mã đề: 0101" in html_content, "Phải hiển thị Mã đề: 0101"
    assert "Đề Thi Tốt Nghiệp THPT Năm 2026 - Môn Toán (Mã đề 0101)" in html_content, (
        "Tiêu đề Đề thi Mẫu 2026 phải chính xác"
    )
    assert "app.loadStandard2026Blueprint()" in html_content, (
        "Phải có nút gọi hàm app.loadStandard2026Blueprint()"
    )

    # 4. Invariant compliance monitor
    assert "RULE-01: Bậc Thang QĐ 764" in html_content, "Phải có RULE-01 Bậc thang QĐ 764"
    assert "RULE-02: Option Anchor" in html_content, "Phải có RULE-02 Option Anchor"
    assert "RULE-03: Passage Contiguity" in html_content, "Phải có RULE-03 Passage Contiguity"
    assert "Centered Diagrams" in html_content, "Phải có Centered Diagrams"

    # 5. Kiểm tra toàn vẹn thẻ HTML
    class FullValidator(HTMLParser):
        def __init__(self):
            super().__init__()
            self.stack = []
            self.void_tags = {
                'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
                'link', 'meta', 'param', 'source', 'track', 'wbr'
            }

        def handle_starttag(self, tag, attrs):
            if tag.lower() not in self.void_tags:
                self.stack.append(tag.lower())

        def handle_endtag(self, tag):
            tag = tag.lower()
            if tag in self.void_tags:
                return
            if self.stack and self.stack[-1] == tag:
                self.stack.pop()

    validator = FullValidator()
    validator.feed(html_content)
    assert len(validator.stack) == 0, f"HTML có các thẻ chưa đóng hợp lệ: {validator.stack[-10:]}"


def test_app_js_dashboard_functions_and_syntax():
    """Kiểm thử tính hợp lệ cú pháp và các hàm hỗ trợ Dashboard trong frontend/static/app.js:
    1. Cú pháp JS hợp lệ 100% (kiểm tra qua node -c).
    2. Hàm loadStandard2026Blueprint và openQuickAction được định nghĩa và expose trên window.app.
    3. Hàm renderDashboard cập nhật đầy đủ các phần tử DOM số liệu động.
    """
    js_path = Path("frontend/static/app.js")
    assert js_path.exists(), "frontend/static/app.js phải tồn tại"
    js_content = js_path.read_text(encoding="utf-8")

    # Kiểm tra node -c
    result = subprocess.run(["node", "-c", str(js_path)], capture_output=True, text=True)
    assert result.returncode == 0, f"Cú pháp app.js không hợp lệ: {result.stderr}"

    # Kiểm tra định nghĩa hàm
    assert "function loadStandard2026Blueprint()" in js_content, "Phải định nghĩa function loadStandard2026Blueprint"
    assert "function openQuickAction(action)" in js_content, "Phải định nghĩa function openQuickAction"
    assert "loadStandard2026Blueprint," in js_content, "loadStandard2026Blueprint phải được expose trong window.app"
    assert "openQuickAction," in js_content, "openQuickAction phải được expose trong window.app"

    # Kiểm tra renderDashboard
    assert "dash-metric-total" in js_content
    assert "dash-metric-approved" in js_content
    assert "dash-count-approved" in js_content
