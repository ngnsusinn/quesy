"""Unit tests for Excel / CSV Roster Import and Export (Task GM-03)
Verifies UTF-8 BOM encoding for Vietnamese Microsoft Excel and roster parsing.
"""

from backend.services.excel_exporter import (
    export_roster_to_csv_bytes,
    parse_student_roster_csv
)


def test_export_roster_to_csv_bytes_contains_utf8_bom():
    """Verifies that the generated CSV bytes starts with the UTF-8 BOM marker."""
    students = [
        {
            "student_code": "012001",
            "full_name": "Nguyễn Văn An",
            "score_part_1": 2.75,
            "score_part_2": 3.5,
            "score_part_3": 2.0,
            "total_score": 8.25
        },
        {
            "student_code": "012002",
            "full_name": "Trần Thị Bích",
            "score_part_1": 2.0,
            "score_part_2": 2.25,
            "score_part_3": 1.5,
            "total_score": 5.75
        }
    ]

    csv_bytes = export_roster_to_csv_bytes(students, classroom_name="12A1")
    assert csv_bytes.startswith(b'\xef\xbb\xbf'), "CSV must start with UTF-8 BOM for Microsoft Excel"

    text = csv_bytes.decode('utf-8-sig')
    assert "Nguyễn Văn An" in text
    assert "Trần Thị Bích" in text
    assert "8.25" in text
    assert "Giỏi" in text
    assert "Trung bình" in text


def test_parse_student_roster_csv():
    """Tests parsing an incoming student roster CSV file."""
    mock_csv = """STT,Số Báo Danh,Họ và Tên,Ngày Sinh,Giới Tính
1,012001,Lê Hoàng Nam,12/05/2007,Nam
2,012002,Phạm Mai Chi,23/09/2007,Nữ
"""
    parsed = parse_student_roster_csv(mock_csv)
    assert len(parsed) == 2
    assert parsed[0]["student_code"] == "012001"
    assert parsed[0]["full_name"] == "Lê Hoàng Nam"
    assert parsed[1]["student_code"] == "012002"
    assert parsed[1]["gender"] == "Nữ"
