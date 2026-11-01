"""Test suite for Composer Bottom Toolbar Apple HIG compliance.
Verifies removal of redundant 'CÂU HIỆN TẠI' button (#composer-compile-partial-btn)
and validates clean 2-button layout (BIÊN DỊCH and LƯU NGÂN HÀNG).
"""

from pathlib import Path
from html.parser import HTMLParser
import re


def test_composer_bottom_toolbar_button_removal_and_layout():
    """Kiểm thử bất biến thanh công cụ đáy của phân hệ Soạn đề (Composer):
    1. Nút '#composer-compile-partial-btn' ('⚡ CÂU HIỆN TẠI') đã bị loại bỏ hoàn toàn khỏi DOM.
    2. Chuỗi text 'CÂU HIỆN TẠI' tuyệt đối không còn xuất hiện trong frontend/index.html.
    3. Thanh công cụ đáy chứa chính xác 2 nút:
       - '#composer-compile-btn' (BIÊN DỊCH) với class 'flex-1 py-2.5 px-4 bg-[#0071e3]'.
       - '#btn-composer-save-to-bank' (LƯU NGÂN HÀNG).
    4. Cấu trúc HTML toàn bộ tệp frontend/index.html không có lỗi thẻ đóng mismatched/unclosed nào.
    """
    html_path = Path("frontend/index.html")
    assert html_path.exists(), "frontend/index.html phải tồn tại"
    html_content = html_path.read_text(encoding="utf-8")

    # 1. Khẳng định nút câu hiện tại không còn tồn tại
    assert "composer-compile-partial-btn" not in html_content, (
        "Nút #composer-compile-partial-btn bắt buộc phải bị loại bỏ hoàn toàn khỏi frontend/index.html"
    )
    assert "CÂU HIỆN TẠI" not in html_content, (
        "Chuỗi 'CÂU HIỆN TẠI' không được phép xuất hiện trong frontend/index.html"
    )

    # 2. Khẳng định 2 nút còn lại hoạt động chuẩn xác
    assert 'id="composer-compile-btn"' in html_content, "Phải tồn tại nút BIÊN DỊCH (#composer-compile-btn)"
    assert 'id="btn-composer-save-to-bank"' in html_content, "Phải tồn tại nút LƯU NGÂN HÀNG (#btn-composer-save-to-bank)"

    # 3. Kiểm tra container thanh công cụ chứa class flex-1 cho nút BIÊN DỊCH
    toolbar_match = re.search(
        r'<!-- Bottom Distinct Standalone Blue BIÊN DỊCH Button Container -->\s*<div[^>]*>([\s\S]*?)</div>\s*</div>\s*</div>\s*</section>',
        html_content
    )
    assert toolbar_match is not None, "Phải tìm thấy container thanh công cụ đáy của tab-composer"
    toolbar_html = toolbar_match.group(1)

    # Đếm số lượng thẻ button trong toolbar đáy
    button_matches = re.findall(r'<button\b', toolbar_html)
    assert len(button_matches) == 2, f"Thanh công cụ đáy phải chứa chính xác 2 nút, tìm thấy {len(button_matches)}"

    # Nút BIÊN DỊCH có flex-1 để lấp đầy không gian tối ưu
    compile_btn_match = re.search(r'<button[^>]*id="composer-compile-btn"[^>]*class="([^"]*)"', toolbar_html)
    assert compile_btn_match is not None
    classes = compile_btn_match.group(1).split()
    assert "flex-1" in classes, "Nút #composer-compile-btn phải có class 'flex-1'"
    assert "bg-[#0071e3]" in classes, "Nút #composer-compile-btn phải có class 'bg-[#0071e3]'"

    # 4. Kiểm tra toàn vẹn thẻ HTML
    class FullValidator(HTMLParser):
        def __init__(self):
            super().__init__()
            self.stack = []
            self.void_tags = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
            self.errors = []
        def handle_starttag(self, tag, attrs):
            if tag.lower() not in self.void_tags:
                self.stack.append((tag.lower(), dict(attrs).get('id', ''), self.getpos()))
        def handle_endtag(self, tag):
            tag = tag.lower()
            if tag in self.void_tags:
                return
            if not self.stack:
                self.errors.append(f'Unexpected closing </{tag}> at {self.getpos()}')
                return
            if self.stack[-1][0] == tag:
                self.stack.pop()
            else:
                found = False
                for i in range(len(self.stack)-1, -1, -1):
                    if self.stack[i][0] == tag:
                        found = True
                        for unclosed in self.stack[i+1:]:
                            self.errors.append(f'Unclosed <{unclosed[0]} id="{unclosed[1]}"> opened at {unclosed[2]} when closing </{tag}> at {self.getpos()}')
                        self.stack = self.stack[:i]
                        break
                if not found:
                    self.errors.append(f'Mismatched closing </{tag}> at {self.getpos()}')

    validator = FullValidator()
    validator.feed(html_content)
    assert len(validator.errors) == 0, f"HTML nesting errors detected: {validator.errors}"
