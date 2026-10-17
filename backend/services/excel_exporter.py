"""Excel & CSV Roster Import/Export Service for Quesy
Supports teacher grade sheet export with UTF-8 BOM encoding for seamless Microsoft Excel compatibility.
Conforms to MoET Circular 32/2018/TT-BGDĐT and Circular 22/2021/TT-BGDĐT grading rules.
"""

import csv
import io
from typing import List, Dict, Any, Union


def export_roster_to_csv_bytes(
    students: List[Dict[str, Any]],
    classroom_name: str = "12A1",
    exam_title: str = "Khảo sát chất lượng Toán 12"
) -> bytes:
    """Exports student scores and roster to a CSV with UTF-8 BOM for Microsoft Excel."""
    output = io.StringIO()
    # Write UTF-8 BOM so Excel opens it with Vietnamese diacritics rendered perfectly
    output.write('\ufeff')

    writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)

    # Title & Metadata
    writer.writerow([f"BẢNG ĐIỂM CHI TIẾT - {exam_title.upper()}"])
    writer.writerow([f"Lớp: {classroom_name}", f"Tổng số học sinh: {len(students)}"])
    writer.writerow([])

    # Header Row
    headers = [
        "STT",
        "Số Báo Danh (SBD)",
        "Họ và Tên",
        "Mã Đề",
        "Điểm Phần I (TN 4 lựa chọn)",
        "Điểm Phần II (Đúng/Sai)",
        "Điểm Phần III (Trả lời ngắn)",
        "Tổng Điểm (Thang 10)",
        "Xếp Loại"
    ]
    writer.writerow(headers)

    # Student Rows
    for idx, s in enumerate(students):
        score_p1 = float(s.get("score_part_1", 0.0))
        score_p2 = float(s.get("score_part_2", 0.0))
        score_p3 = float(s.get("score_part_3", 0.0))
        total_score = round(s.get("total_score", score_p1 + score_p2 + score_p3), 2)

        # Vietnamese High School grading scale (Circular 22/2021)
        if total_score >= 8.0:
            rank = "Giỏi"
        elif total_score >= 6.5:
            rank = "Khá"
        elif total_score >= 5.0:
            rank = "Trung bình"
        else:
            rank = "Chưa đạt"

        writer.writerow([
            idx + 1,
            s.get("student_code", f"{idx + 1:04d}"),
            s.get("full_name", f"Học sinh {idx + 1}"),
            s.get("variant_code", "101"),
            f"{score_p1:.2f}",
            f"{score_p2:.2f}",
            f"{score_p3:.2f}",
            f"{total_score:.2f}",
            rank
        ])

    return output.getvalue().encode('utf-8')


def parse_student_roster_csv(csv_text_or_bytes: Union[str, bytes]) -> List[Dict[str, str]]:
    """Parses an uploaded student list CSV or TSV file."""
    if isinstance(csv_text_or_bytes, bytes):
        # Handle UTF-8 BOM if present
        text = csv_text_or_bytes.decode('utf-8-sig', errors='ignore')
    else:
        text = csv_text_or_bytes

    reader = csv.reader(io.StringIO(text))
    students: List[Dict[str, str]] = []

    header_found = False
    sbd_idx, name_idx, dob_idx, gender_idx = 1, 2, 3, 4

    for row in reader:
        if not row or not any(row):
            continue

        row_str = " ".join(row).lower()
        if "sbd" in row_str or "họ và tên" in row_str or "họ tên" in row_str or "mã học sinh" in row_str:
            header_found = True
            for i, col in enumerate(row):
                c = col.strip().lower()
                if "sbd" in c or "mã" in c:
                    sbd_idx = i
                elif "họ" in c or "tên" in c:
                    name_idx = i
                elif "sinh" in c or "ngày" in c:
                    dob_idx = i
                elif "giới" in c:
                    gender_idx = i
            continue

        if header_found:
            sbd = row[sbd_idx].strip() if sbd_idx < len(row) else ""
            name = row[name_idx].strip() if name_idx < len(row) else ""
            dob = row[dob_idx].strip() if dob_idx < len(row) else ""
            gender = row[gender_idx].strip() if gender_idx < len(row) else "Nam"

            if sbd or name:
                students.append({
                    "student_code": sbd or f"{len(students) + 1:04d}",
                    "full_name": name or f"Học sinh {len(students) + 1}",
                    "date_of_birth": dob,
                    "gender": gender
                })

    return students
