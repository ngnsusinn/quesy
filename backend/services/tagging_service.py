import re
import math
import hashlib
import json
import os
from collections import Counter
from typing import Optional, Tuple, Dict, Any, List, Union

try:
    from sqlalchemy.orm import Session
    from backend.models import Question, LearningOutcome, ProblemArchetype, Strand, Topic, Lesson, Grade, Subject
    HAS_SQLALCHEMY = True
except ImportError:
    HAS_SQLALCHEMY = False

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

# Action verbs mapped from Circular 32/2018/TT-BGDĐT
RECOGNITION_KEYWORDS = [
    "nhận biết", "nhận dạng", "chỉ ra", "nêu", "liệt kê", "đọc", "đếm", "viết",
    "làm quen", "cho biết", "xác định điểm", "tọa độ của điểm", "vectơ nào",
    "đồ thị hình bên", "bảng biến thiên", "bảng biến thiên bên", "họ nguyên hàm của",
    "tiệm cận đứng", "tiệm cận ngang", "điểm cực đại", "điểm cực tiểu"
]

COMPREHENSION_KEYWORDS = [
    "thông hiểu", "mô tả", "giải thích", "thể hiện", "sắp xếp", "phân loại",
    "biểu diễn", "chứng tỏ", "suy ra", "tại sao", "mối liên hệ",
    "tìm tập nghiệm", "đồng biến trên khoảng", "nghịch biến trên", "khoảng cách từ",
    "diện tích hình phẳng", "thể tích khối"
]

APPLICATION_KEYWORDS = [
    "vận dụng", "tính", "vẽ", "thực hiện", "sử dụng", "áp dụng", "so sánh",
    "phân biệt", "lí giải", "chứng minh", "giải phương trình", "tìm tập nghiệm",
    "tìm tất cả các giá trị", "tham số m", "tham số $m$", "cực trị", "giá trị lớn nhất",
    "giá trị nhỏ nhất", "tối ưu", "thực tế", "thực tiễn", "thể tích lớn nhất",
    "chi phí nhỏ nhất", "có đúng 3 nghiệm", "cắt tại 3 điểm", "công thức bayes",
    "xác suất toàn phần"
]

# ---------------------------------------------------------------------------
# Circular 32 / 2018 / TT-BGDĐT Taxonomy Knowledge Base
# ---------------------------------------------------------------------------

TAXONOMY_KNOWLEDGE_BASE = [
    {
        "yccd_code": "TOAN12.GT.01",
        "strand": "Số, Đại số và Một số yếu tố giải tích",
        "topic": "Ứng dụng đạo hàm để khảo sát và vẽ đồ thị hàm số",
        "lesson": "Tính đơn điệu và cực trị của hàm số",
        "description": "Nhận biết được tính đơn điệu, điểm cực trị của hàm số thông qua bảng biến thiên hoặc đồ thị hàm số",
        "keywords": [
            "đồng biến", "nghịch biến", "cực trị", "cực đại", "cực tiểu",
            "bảng biến thiên", "đồ thị hàm số", "điểm cực đại", "điểm cực tiểu",
            "giá trị cực đại", "giá trị cực tiểu"
        ],
        "archetypes": [
            "Đọc đồ thị hoặc bảng biến thiên tìm cực trị",
            "Đọc đồ thị tìm khoảng đồng biến, nghịch biến",
            "Cực trị hàm đa thức bậc ba, bậc bốn",
            "Cực trị hàm số chứa tham số m"
        ],
        "default_level": "RECOGNITION"
    },
    {
        "yccd_code": "TOAN12.GT.02",
        "strand": "Số, Đại số và Một số yếu tố giải tích",
        "topic": "Ứng dụng đạo hàm để khảo sát và vẽ đồ thị hàm số",
        "lesson": "Giá trị lớn nhất và giá trị nhỏ nhất của hàm số",
        "description": "Tìm được giá trị lớn nhất, giá trị nhỏ nhất của hàm số trên một đoạn và giải quyết bài toán tối ưu thực tiễn",
        "keywords": [
            "giá trị lớn nhất", "giá trị nhỏ nhất", "GTLN", "GTNN", "max", "min",
            "trên đoạn", "trên khoảng", "tối ưu", "chi phí nhỏ nhất", "thể tích lớn nhất"
        ],
        "archetypes": [
            "Tìm GTLN, GTNN của hàm số trên đoạn [a; b]",
            "Tìm GTLN, GTNN từ bảng biến thiên hoặc đồ thị",
            "GTLN, GTNN chứa tham số m",
            "Bài toán tối ưu thực tiễn liên môn"
        ],
        "default_level": "COMPREHENSION"
    },
    {
        "yccd_code": "TOAN12.GT.03",
        "strand": "Số, Đại số và Một số yếu tố giải tích",
        "topic": "Ứng dụng đạo hàm để khảo sát và vẽ đồ thị hàm số",
        "lesson": "Đường tiệm cận của đồ thị hàm số",
        "description": "Xác định được đường tiệm cận đứng, tiệm cận ngang và tiệm cận xiên của đồ thị hàm số",
        "keywords": [
            "tiệm cận", "tiệm cận đứng", "tiệm cận ngang", "tiệm cận xiên",
            "đường tiệm cận", "lim", "vô cực", "tiến tới vô cùng"
        ],
        "archetypes": [
            "Xác định tiệm cận từ bảng biến thiên",
            "Tìm tiệm cận đứng, tiệm cận ngang của hàm phân thức bậc nhất trên bậc nhất",
            "Tìm số đường tiệm cận của đồ thị hàm số chứa căn thức hoặc tham số"
        ],
        "default_level": "RECOGNITION"
    },
    {
        "yccd_code": "TOAN12.GT.04",
        "strand": "Số, Đại số và Một số yếu tố giải tích",
        "topic": "Ứng dụng đạo hàm để khảo sát và vẽ đồ thị hàm số",
        "lesson": "Khảo sát sự biến thiên và vẽ đồ thị hàm số",
        "description": "Nhận dạng được đồ thị các hàm số bậc ba, phân thức bậc nhất trên bậc nhất, phân thức bậc hai trên bậc nhất",
        "keywords": [
            "khảo sát sự biến thiên", "nhận dạng đồ thị", "đồ thị bên là của hàm số nào",
            "bảng biến thiên bên là của hàm số nào", "tâm đối xứng", "trục đối xứng"
        ],
        "archetypes": [
            "Nhận dạng đồ thị hàm số bậc ba",
            "Nhận dạng đồ thị hàm phân thức (ax+b)/(cx+d)",
            "Tương giao của hai đồ thị hàm số và số nghiệm phương trình f(x) = m"
        ],
        "default_level": "COMPREHENSION"
    },
    {
        "yccd_code": "TOAN12.GT.05",
        "strand": "Số, Đại số và Một số yếu tố giải tích",
        "topic": "Nguyên hàm, Tích phân và Ứng dụng",
        "lesson": "Nguyên hàm",
        "description": "Tìm nguyên hàm của một số hàm số cơ bản và vận dụng các tính chất cơ bản của nguyên hàm",
        "keywords": [
            "nguyên hàm", "họ nguyên hàm", "F(x)", "f(x)dx", "\\int",
            "nguyên hàm cơ bản", "đổi biến số nguyên hàm", "nguyên hàm từng phần"
        ],
        "archetypes": [
            "Tìm nguyên hàm bằng bảng công thức cơ bản",
            "Tìm họ nguyên hàm F(x) thỏa mãn điều kiện F(x0) = y0",
            "Nguyên hàm từng phần và đổi biến số"
        ],
        "default_level": "RECOGNITION"
    },
    {
        "yccd_code": "TOAN12.GT.06",
        "strand": "Số, Đại số và Một số yếu tố giải tích",
        "topic": "Nguyên hàm, Tích phân và Ứng dụng",
        "lesson": "Tích phân và Ứng dụng hình học",
        "description": "Tính tích phân của hàm số và vận dụng tính diện tích hình phẳng, thể tích vật thể tròn xoay",
        "keywords": [
            "tích phân", "tính tích phân", "diện tích hình phẳng", "thể tích vật thể",
            "thể tích khối tròn xoay", "quay quanh trục Ox", "parabol", "giới hạn bởi các đường"
        ],
        "archetypes": [
            "Tính tích phân cơ bản",
            "Tính diện tích hình phẳng giới hạn bởi đồ thị",
            "Tính thể tích khối tròn xoay",
            "Ứng dụng tích phân trong bài toán chuyển động vật lí"
        ],
        "default_level": "COMPREHENSION"
    },
    {
        "yccd_code": "TOAN12.HH.01",
        "strand": "Hình học và Đo lường",
        "topic": "Phương pháp tọa độ trong không gian",
        "lesson": "Hệ trục tọa độ trong không gian Oxyz",
        "description": "Nhận biết và vận dụng tọa độ của vectơ, tọa độ của điểm trong không gian Oxyz",
        "keywords": [
            "Oxyz", "tọa độ", "vectơ", "không gian Oxyz", "tọa độ điểm", "tích vô hướng",
            "độ dài vectơ", "trung điểm", "trọng tâm tam giác", "vectơ chỉ phương", "vectơ pháp tuyến"
        ],
        "archetypes": [
            "Tìm tọa độ điểm, tọa độ vectơ trong hệ Oxyz",
            "Tính độ dài đoạn thẳng, tích vô hướng của hai vectơ",
            "Tìm tọa độ trọng tâm, trung điểm trong không gian"
        ],
        "default_level": "RECOGNITION"
    },
    {
        "yccd_code": "TOAN12.HH.02",
        "strand": "Hình học và Đo lường",
        "topic": "Phương pháp tọa độ trong không gian",
        "lesson": "Phương trình mặt phẳng",
        "description": "Viết phương trình mặt phẳng trong không gian Oxyz và xác định vị trí tương đối",
        "keywords": [
            "mặt phẳng", "phương trình mặt phẳng", "vectơ pháp tuyến", "song song",
            "vuông góc", "khoảng cách từ điểm đến mặt phẳng", "góc giữa hai mặt phẳng"
        ],
        "archetypes": [
            "Viết phương trình mặt phẳng đi qua 1 điểm và có VTPT",
            "Viết phương trình mặt phẳng đi qua 3 điểm",
            "Tính khoảng cách từ điểm đến mặt phẳng"
        ],
        "default_level": "COMPREHENSION"
    },
    {
        "yccd_code": "TOAN12.HH.03",
        "strand": "Hình học và Đo lường",
        "topic": "Phương pháp tọa độ trong không gian",
        "lesson": "Phương trình đường thẳng trong không gian",
        "description": "Viết phương trình chính tắc và tham số của đường thẳng trong không gian Oxyz",
        "keywords": [
            "đường thẳng", "phương trình tham số", "phương trình chính tắc",
            "vectơ chỉ phương", "khoảng cách giữa hai đường thẳng", "vị trí tương đối"
        ],
        "archetypes": [
            "Viết phương trình tham số, chính tắc của đường thẳng",
            "Vị trí tương đối giữa hai đường thẳng hoặc đường thẳng và mặt phẳng",
            "Hình chiếu vuông góc của điểm lên đường thẳng"
        ],
        "default_level": "COMPREHENSION"
    },
    {
        "yccd_code": "TOAN12.HH.04",
        "strand": "Hình học và Đo lường",
        "topic": "Phương pháp tọa độ trong không gian",
        "lesson": "Phương trình mặt cầu",
        "description": "Viết phương trình mặt cầu trong không gian Oxyz và xác định tâm, bán kính",
        "keywords": [
            "mặt cầu", "phương trình mặt cầu", "tâm I", "bán kính R",
            "tiếp xúc mặt phẳng", "cắt mặt phẳng theo đường tròn"
        ],
        "archetypes": [
            "Tìm tâm và bán kính của mặt cầu",
            "Viết phương trình mặt cầu biết tâm và đi qua một điểm",
            "Mặt cầu tiếp xúc với mặt phẳng hoặc đường thẳng"
        ],
        "default_level": "RECOGNITION"
    },
    {
        "yccd_code": "TOAN12.TK.01",
        "strand": "Thống kê và Xác suất",
        "topic": "Một số yếu tố thống kê",
        "lesson": "Các số đặc trưng đo mức độ phân tán của mẫu số liệu ghép nhóm",
        "description": "Tính và giải thích ý nghĩa của khoảng biến thiên, khoảng tứ phân vị, phương sai và độ lệch chuẩn của mẫu số liệu ghép nhóm",
        "keywords": [
            "mẫu số liệu ghép nhóm", "khoảng biến thiên", "khoảng tứ phân vị",
            "tứ phân vị", "phương sai", "độ lệch chuẩn", "tần số", "nhóm [a; b)"
        ],
        "archetypes": [
            "Tính khoảng biến thiên và khoảng tứ phân vị của mẫu số liệu ghép nhóm",
            "Tính phương sai và độ lệch chuẩn của mẫu số liệu ghép nhóm",
            "So sánh mức độ phân tán giữa hai mẫu số liệu thực tế"
        ],
        "default_level": "COMPREHENSION"
    },
    {
        "yccd_code": "TOAN12.XS.01",
        "strand": "Thống kê và Xác suất",
        "topic": "Một số yếu tố xác suất",
        "lesson": "Xác suất có điều kiện và Công thức Bayes",
        "description": "Tính xác suất có điều kiện và vận dụng công thức xác suất toàn phần, công thức Bayes trong giải quyết bài toán thực tế",
        "keywords": [
            "xác suất", "xác suất có điều kiện", "P(A|B)", "công thức xác suất toàn phần",
            "công thức Bayes", "sơ đồ hình cây", "biến cố độc lập", "xác suất xảy ra"
        ],
        "archetypes": [
            "Tính xác suất có điều kiện P(A|B) theo định nghĩa",
            "Vận dụng sơ đồ hình cây tính xác suất",
            "Vận dụng công thức xác suất toàn phần và công thức Bayes trong bài toán y tế, sản xuất"
        ],
        "default_level": "APPLICATION"
    }
]

def classify_cognitive_level(text: str) -> str:
    """Classifies cognitive level into RECOGNITION, COMPREHENSION, APPLICATION
    strictly following Circular 32/2018/TT-BGDĐT verb list.
    """
    t_lower = text.lower()

    app_score = sum(1 for kw in APPLICATION_KEYWORDS if kw in t_lower)
    comp_score = sum(1 for kw in COMPREHENSION_KEYWORDS if kw in t_lower)
    rec_score = sum(1 for kw in RECOGNITION_KEYWORDS if kw in t_lower)

    if app_score > 0 and app_score >= comp_score and app_score >= rec_score:
        return "APPLICATION"
    if rec_score > 0 and rec_score >= comp_score:
        return "RECOGNITION"
    if comp_score > 0:
        return "COMPREHENSION"
    if rec_score > 0:
        return "RECOGNITION"

    # Default to RECOGNITION if unclear
    return "RECOGNITION"


def _normalize_math_text(text: str) -> str:
    t = text.lower()
    t = re.sub(r"giải phương trình", "tìm tập nghiệm của phương trình", t)
    t = re.sub(r"để tìm nghiệm.*", "", t)
    t = re.sub(r"tìm nghiệm.*", "", t)
    t = re.sub(r"[.,;?!\"'()\[\]]", " ", t)
    return " ".join(t.split())


def _text_to_feature_vector(text: str) -> Counter:
    formulas = re.findall(r"\$.*?\$", text)
    clean_text = re.sub(r"\$.*?\$", " ", text)
    normalized = _normalize_math_text(clean_text)

    words = normalized.split()
    features = words + [f.replace(" ", "") for f in formulas] * 5
    return Counter(features)


def compute_cosine_similarity(text1: str, text2: str) -> float:
    """Computes cosine similarity between two question stems with math formula weighting."""
    if not text1 or not text2:
        return 0.0

    t1_clean = text1.strip()
    t2_clean = text2.strip()
    if t1_clean == t2_clean:
        return 1.0

    v1 = _text_to_feature_vector(t1_clean)
    v2 = _text_to_feature_vector(t2_clean)

    common_keys = set(v1.keys()) & set(v2.keys())
    if not common_keys:
        return 0.0

    dot_product = sum(v1[k] * v2[k] for k in common_keys)
    norm1 = math.sqrt(sum(val ** 2 for val in v1.values()))
    norm2 = math.sqrt(sum(val ** 2 for val in v2.values()))

    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0

    return min(1.0, float(dot_product / (norm1 * norm2)))


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Computes cosine similarity between two 1536-dim vectors."""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0

    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))

    if norm1 <= 0.0 or norm2 <= 0.0:
        return 0.0

    sim = dot / (norm1 * norm2)
    return max(min(sim, 1.0), -1.0)


def generate_embedding(text: str, dimension: int = 1536) -> List[float]:
    """Generates a 1536-dimensional normalized vector embedding for question text."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key and HAS_HTTPX:
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={"input": text, "model": "text-embedding-3-small"}
                )
                if resp.status_code == 200:
                    return resp.json()["data"][0]["embedding"]
        except Exception:
            pass

    vec = [0.0] * dimension
    if not text:
        return vec

    normalized = text.lower()
    math_parts = re.findall(r'\$(.*?)\$', normalized)
    for m in math_parts:
        canon_m = re.sub(r'\b[xyzmtuvw]\b', 'VAR', m)
        canon_m = re.sub(r'\b\d+\b', 'NUM', canon_m)
        _hash_token_into_vector(f"MATH:{canon_m}", 2.5, vec, dimension)

    words = re.findall(r'[\w\u00C0-\u024F\u1EA0-\u1EF9]+', normalized)
    for i, w in enumerate(words):
        _hash_token_into_vector(f"W1:{w}", 1.0, vec, dimension)
        if i + 1 < len(words):
            _hash_token_into_vector(f"W2:{w}_{words[i+1]}", 1.5, vec, dimension)
        if i + 2 < len(words):
            _hash_token_into_vector(f"W3:{w}_{words[i+1]}_{words[i+2]}", 2.0, vec, dimension)

    for i in range(len(normalized) - 3):
        _hash_token_into_vector(f"C4:{normalized[i:i+4]}", 0.3, vec, dimension)

    norm = math.sqrt(sum(v * v for v in vec))
    if norm > 0.0:
        vec = [v / norm for v in vec]

    return vec


def _hash_token_into_vector(token: str, weight: float, vec: List[float], dimension: int) -> None:
    h_bytes = hashlib.sha256(token.encode("utf-8")).digest()
    idx = int.from_bytes(h_bytes[:4], byteorder="little") % dimension
    sign = 1.0 if (h_bytes[4] % 2 == 0) else -1.0
    vec[idx] += sign * weight


def check_question_duplicate(
    stem: str,
    db: Any,
    subject_id: Optional[str] = None,
    grade_id: Optional[str] = None,
    threshold: float = 0.90
) -> Tuple[bool, float, Optional[Any]]:
    """Checks whether the new question stem is a duplicate of an existing question
    in the database (threshold >= 0.90 as per TC-BANK-02).
    """
    if not HAS_SQLALCHEMY or not hasattr(db, "query"):
        return False, 0.0, None

    query = db.query(Question)
    if subject_id:
        query = query.filter(Question.subject_id == subject_id)
    if grade_id:
        query = query.filter(Question.grade_id == grade_id)

    candidates = query.all()
    highest_sim = 0.0
    matched_q: Optional[Any] = None

    for q in candidates:
        sim = compute_cosine_similarity(stem, q.stem)
        if sim > highest_sim:
            highest_sim = sim
            matched_q = q

    is_duplicate = highest_sim >= threshold
    return is_duplicate, round(highest_sim, 4), matched_q


def check_duplication(
    stem: str,
    existing_items: List[Dict[str, Any]],
    threshold: float = 0.90
) -> Dict[str, Any]:
    """Checks question stem against items list following FRD 2.8 rules."""
    if not stem or not existing_items:
        return {
            "status": "UNIQUE",
            "is_duplicate": False,
            "is_similar": False,
            "max_similarity": 0.0,
            "matched_item": None,
            "message": "Hợp lệ: Không phát hiện câu hỏi trùng lặp."
        }

    target_emb = generate_embedding(stem)
    max_sim = 0.0
    best_match: Optional[Dict[str, Any]] = None

    for item in existing_items:
        item_stem = item.get("stem", "")
        sim1 = compute_cosine_similarity(stem, item_stem)
        item_emb = item.get("embedding")
        if item_emb:
            sim2 = cosine_similarity(target_emb, item_emb)
            sim = max(sim1, sim2)
        else:
            sim = sim1

        if sim > max_sim:
            max_sim = sim
            best_match = item

    percent = round(max_sim * 100, 1)
    matched_code = best_match.get("code") or best_match.get("id") or "TOAN12-XXXX" if best_match else ""

    if max_sim >= threshold:
        return {
            "status": "DUPLICATE_BLOCKED",
            "is_duplicate": True,
            "is_similar": True,
            "max_similarity": round(max_sim, 4),
            "matched_item": best_match,
            "message": f"Cảnh báo: Trùng lặp {percent}% với câu hỏi [{matched_code}] trong ngân hàng."
        }
    elif max_sim >= 0.80:
        return {
            "status": "SIMILAR_WARNING",
            "is_duplicate": False,
            "is_similar": True,
            "max_similarity": round(max_sim, 4),
            "matched_item": best_match,
            "message": f"Cảnh báo: Câu hỏi tương tự ({percent}%) với câu hỏi [{matched_code}]."
        }
    else:
        return {
            "status": "UNIQUE",
            "is_duplicate": False,
            "is_similar": False,
            "max_similarity": round(max_sim, 4),
            "matched_item": best_match,
            "message": "Hợp lệ: Câu hỏi không trùng lặp."
        }


def auto_tag_question(
    stem: str,
    options: Optional[List[str]] = None,
    subject: str = "Toán học",
    grade: str = "Lớp 12"
) -> Dict[str, Any]:
    """Auto-tags a question with Circular 32 taxonomy attributes."""
    combined_text = stem
    if options:
        combined_text += " " + " ".join(options)
    text_lower = combined_text.lower()

    best_entry = None
    max_score = 0

    for entry in TAXONOMY_KNOWLEDGE_BASE:
        score = 0
        for kw in entry["keywords"]:
            if kw in text_lower:
                score += len(kw)
        if score > max_score:
            max_score = score
            best_entry = entry

    if not best_entry or max_score == 0:
        best_entry = TAXONOMY_KNOWLEDGE_BASE[0]

    best_archetype = best_entry["archetypes"][0]
    for arch in best_entry["archetypes"]:
        arch_tokens = [t.lower() for t in arch.split() if len(t) > 2]
        match_count = sum(1 for t in arch_tokens if t in text_lower)
        if match_count >= 2:
            best_archetype = arch
            break

    cog_level = classify_cognitive_level(stem)
    level_vn_map = {
        "RECOGNITION": "Nhận biết",
        "KNOWLEDGE": "Nhận biết",
        "COMPREHENSION": "Thông hiểu",
        "APPLICATION": "Vận dụng",
        "HIGH_APPLICATION": "Vận dụng cao"
    }

    return {
        "grade": grade,
        "subject": subject,
        "strand": best_entry["strand"],
        "topic": best_entry["topic"],
        "lesson": best_entry["lesson"],
        "learning_outcome_code": best_entry["yccd_code"],
        "learning_outcome_desc": best_entry["description"],
        "problem_archetype": best_archetype,
        "cognitive_level": cog_level,
        "cognitive_level_vn": level_vn_map.get(cog_level, "Biết"),
        "confidence": min(0.98, max(0.85, 0.70 + (max_score / 50.0)))
    }


def suggest_auto_tagging(
    stem: str,
    db: Any = None,
    subject_id: Optional[str] = None,
    grade_id: Optional[str] = None
) -> Dict[str, Any]:
    """Suggests Circular 32 taxonomy tags for a question stem."""
    cog_level = classify_cognitive_level(stem)

    if HAS_SQLALCHEMY and db is not None and hasattr(db, "query"):
        try:
            query = db.query(LearningOutcome)
            outcomes = query.all()

            best_outcome = None
            best_score = 0.0

            for lo in outcomes:
                score = compute_cosine_similarity(stem, lo.description)
                if score > best_score:
                    best_score = score
                    best_outcome = lo

            archetype_id = None
            archetype_name = None
            if best_outcome and best_outcome.problem_archetypes:
                archetype = best_outcome.problem_archetypes[0]
                archetype_id = archetype.id
                archetype_name = archetype.name

            if best_outcome:
                return {
                    "suggested_cognitive_level": cog_level,
                    "suggested_learning_outcome_id": best_outcome.id,
                    "suggested_learning_outcome_code": best_outcome.code,
                    "suggested_problem_archetype_id": archetype_id,
                    "suggested_problem_archetype_name": archetype_name,
                    "confidence": round(max(0.60, best_score), 2)
                }
        except Exception:
            pass

    standalone = auto_tag_question(stem)
    return {
        "suggested_cognitive_level": cog_level,
        "suggested_learning_outcome_id": None,
        "suggested_learning_outcome_code": standalone["learning_outcome_code"],
        "suggested_problem_archetype_id": None,
        "suggested_problem_archetype_name": standalone["problem_archetype"],
        "confidence": standalone["confidence"],
        "strand": standalone["strand"],
        "topic": standalone["topic"],
        "lesson": standalone["lesson"]
    }
