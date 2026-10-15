import json
import logging
from datetime import datetime
from sqlalchemy.orm import Session
from backend.database import SessionLocal, Base, engine
from backend.models import (
    Grade,
    Subject,
    Strand,
    Topic,
    Lesson,
    LearningOutcome,
    ProblemArchetype,
    Question,
    QuestionOption,
    SubStatement,
    ExamMatrix,
    ExamMatrixItem,
    MasterExam,
    MasterExamItem,
    ExamVariant,
    ExamVariantItem,
    AIDigitizeJob,
)

logger = logging.getLogger("quesy.seed")
logging.basicConfig(level=logging.INFO)


def seed_database(db: Session, force_reset: bool = True):
    """Populates the database with realistic Circular 32/2018/TT-BGDĐT Grade 12 Math data:
    - 4 Content Strands (Giải tích & Đại số, Hình học & Đo lường, Thống kê & Xác suất, Hoạt động thực hành)
    - Topics, Lessons, YCCDs (e.g. TOAN12.GT.01, TOAN12.HH.01), Problem Archetypes
    - 32 diverse questions with rich LaTeX across SINGLE_CHOICE, TRUE_FALSE_GROUP, SHORT_ANSWER, PASSAGE_GROUP, ESSAY
    - Exam Matrix, Master Exam, and Exam Variants.
    """
    if force_reset:
        logger.info("Dropping and recreating all tables to ensure clean schema...")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
    else:
        Base.metadata.create_all(bind=engine)
        if db.query(Question).count() >= 30:
            logger.info("Database already seeded with sufficient questions. Skipping.")
            return

    logger.info("Seeding Circular 32/2018/TT-BGDĐT Grade 12 Math taxonomy and questions...")

    # ==============================================================================
    # 1. GRADES
    # ==============================================================================
    g10 = Grade(code="GRADE_10", name="Lớp 10", level=10, order_index=1)
    g11 = Grade(code="GRADE_11", name="Lớp 11", level=11, order_index=2)
    g12 = Grade(code="GRADE_12", name="Lớp 12", level=12, order_index=3)
    db.add_all([g10, g11, g12])
    db.flush()

    # ==============================================================================
    # 2. SUBJECTS
    # ==============================================================================
    sub_math = Subject(
        code="TOAN",
        name="Toán học",
        description="Môn Toán theo Chương trình GDPT 2018 (Thông tư 32/2018/TT-BGDĐT)",
        order_index=1,
    )
    sub_phys = Subject(code="VATLI", name="Vật lí", description="Môn Vật lí", order_index=2)
    sub_chem = Subject(code="HOAHOC", name="Hoá học", description="Môn Hoá học", order_index=3)
    sub_bio = Subject(code="SINHHOC", name="Sinh học", description="Môn Sinh học", order_index=4)
    sub_eng = Subject(code="TIENGANH", name="Tiếng Anh", description="Môn Tiếng Anh", order_index=5)
    db.add_all([sub_math, sub_phys, sub_chem, sub_bio, sub_eng])
    db.flush()

    # ==============================================================================
    # 3. 4 STRANDS FOR GRADE 12 MATH (MẠCH NỘI DUNG THEO THÔNG TƯ 32/2018/TT-BGDĐT)
    # Strictly competency-based; ABSOLUTELY NO textbook edition fields or tables.
    # ==============================================================================
    strand_gt_ds = Strand(
        subject_id=sub_math.id,
        grade_id=g12.id,
        code="TOAN12.STRAND.GT_DS",
        name="Số, Đại số và Một số yếu tố giải tích",
        description="Ứng dụng đạo hàm, nguyên hàm, tích phân và hàm số",
        order_index=1,
    )
    strand_hh_dl = Strand(
        subject_id=sub_math.id,
        grade_id=g12.id,
        code="TOAN12.STRAND.HH_DL",
        name="Hình học và Đo lường",
        description="Toạ độ vectơ, phương pháp toạ độ trong không gian Oxyz",
        order_index=2,
    )
    strand_tk_xs = Strand(
        subject_id=sub_math.id,
        grade_id=g12.id,
        code="TOAN12.STRAND.TK_XS",
        name="Thống kê và Xác suất",
        description="Xác suất có điều kiện, công thức Bayes, thống kê mẫu ghép nhóm",
        order_index=3,
    )
    strand_th_tn = Strand(
        subject_id=sub_math.id,
        grade_id=g12.id,
        code="TOAN12.STRAND.TH_TN",
        name="Hoạt động thực hành và trải nghiệm",
        description="Ứng dụng toán học trong thực tiễn, kinh tế và đời sống",
        order_index=4,
    )
    db.add_all([strand_gt_ds, strand_hh_dl, strand_tk_xs, strand_th_tn])
    db.flush()

    # ==============================================================================
    # 4. TOPICS (CHỦ ĐỀ / CHUYÊN ĐỀ)
    # ==============================================================================
    top_daoham = Topic(
        strand_id=strand_gt_ds.id,
        code="TOAN12.CD.DAOHAM",
        name="Ứng dụng đạo hàm để khảo sát và vẽ đồ thị của hàm số",
        order_index=1,
    )
    top_tichphan = Topic(
        strand_id=strand_gt_ds.id,
        code="TOAN12.CD.TICHPHAN",
        name="Nguyên hàm, tích phân và ứng dụng",
        order_index=2,
    )
    top_oxyz = Topic(
        strand_id=strand_hh_dl.id,
        code="TOAN12.CD.OXYZ",
        name="Phương pháp toạ độ trong không gian",
        order_index=3,
    )
    top_xacsuat = Topic(
        strand_id=strand_tk_xs.id,
        code="TOAN12.CD.XACSUAT",
        name="Xác suất có điều kiện và các quy tắc tính xác suất",
        order_index=4,
    )
    top_thongke = Topic(
        strand_id=strand_tk_xs.id,
        code="TOAN12.CD.THONGKE",
        name="Các số đặc trưng đo mức độ phân tán cho mẫu số liệu ghép nhóm",
        order_index=5,
    )
    top_thuchanh = Topic(
        strand_id=strand_th_tn.id,
        code="TOAN12.CD.THUCHANH",
        name="Thực hành ứng dụng giải tích và xác suất trong mô hình hoá thực tế",
        order_index=6,
    )
    db.add_all([top_daoham, top_tichphan, top_oxyz, top_xacsuat, top_thongke, top_thuchanh])
    db.flush()

    # ==============================================================================
    # 5. LESSONS (BÀI HỌC)
    # ==============================================================================
    les_dondieu = Lesson(topic_id=top_daoham.id, code="TOAN12.LES.01", name="Tính đơn điệu và cực trị của hàm số", order_index=1)
    les_gtln = Lesson(topic_id=top_daoham.id, code="TOAN12.LES.02", name="Giá trị lớn nhất và giá trị nhỏ nhất của hàm số", order_index=2)
    les_tiemcan = Lesson(topic_id=top_daoham.id, code="TOAN12.LES.03", name="Đường tiệm cận của đồ thị hàm số", order_index=3)
    les_do_thi = Lesson(topic_id=top_daoham.id, code="TOAN12.LES.04", name="Khảo sát sự biến thiên và vẽ đồ thị của hàm số", order_index=4)

    les_nguyenham = Lesson(topic_id=top_tichphan.id, code="TOAN12.LES.05", name="Nguyên hàm và các tính chất cơ bản", order_index=5)
    les_tichphan = Lesson(topic_id=top_tichphan.id, code="TOAN12.LES.06", name="Tích phân và ứng dụng hình học", order_index=6)

    les_vecto = Lesson(topic_id=top_oxyz.id, code="TOAN12.LES.07", name="Toạ độ của vectơ và điểm trong không gian Oxyz", order_index=7)
    les_matphang = Lesson(topic_id=top_oxyz.id, code="TOAN12.LES.08", name="Phương trình tổng quát của mặt phẳng", order_index=8)
    les_duongthang = Lesson(topic_id=top_oxyz.id, code="TOAN12.LES.09", name="Phương trình đường thẳng trong không gian", order_index=9)
    les_matcau = Lesson(topic_id=top_oxyz.id, code="TOAN12.LES.10", name="Phương trình mặt cầu trong không gian", order_index=10)

    les_xscodk = Lesson(topic_id=top_xacsuat.id, code="TOAN12.LES.11", name="Xác suất có điều kiện và công thức nhân xác suất", order_index=11)
    les_bayes = Lesson(topic_id=top_xacsuat.id, code="TOAN12.LES.12", name="Công thức xác suất toàn phần và công thức Bayes", order_index=12)

    les_phuongsai = Lesson(topic_id=top_thongke.id, code="TOAN12.LES.13", name="Phương sai và độ lệch chuẩn của mẫu số liệu ghép nhóm", order_index=13)
    les_toiuu = Lesson(topic_id=top_thuchanh.id, code="TOAN12.LES.14", name="Vận dụng giải tích giải quyết bài toán tối ưu thực tiễn", order_index=14)

    db.add_all([
        les_dondieu, les_gtln, les_tiemcan, les_do_thi,
        les_nguyenham, les_tichphan,
        les_vecto, les_matphang, les_duongthang, les_matcau,
        les_xscodk, les_bayes, les_phuongsai, les_toiuu
    ])
    db.flush()

    # ==============================================================================
    # 6. LEARNING OUTCOMES (YÊU CẦU CẦN ĐẠT - YCCĐ THEO TT 32/2018)
    # ==============================================================================
    yccd_gt_01 = LearningOutcome(
        lesson_id=les_dondieu.id,
        code="TOAN12.GT.01",
        description="Nhận biết được tính đơn điệu, điểm cực trị của hàm số thông qua bảng biến thiên hoặc đồ thị hàm số.",
        competence="Năng lực tư duy và lập luận toán học",
        cognitive_level="RECOGNITION",
        order_index=1,
    )
    yccd_gt_02 = LearningOutcome(
        lesson_id=les_gtln.id,
        code="TOAN12.GT.02",
        description="Tìm được giá trị lớn nhất, giá trị nhỏ nhất của hàm số trên một khoảng hoặc đoạn cho trước.",
        competence="Năng lực giải quyết vấn đề toán học",
        cognitive_level="APPLICATION",
        order_index=2,
    )
    yccd_gt_03 = LearningOutcome(
        lesson_id=les_tiemcan.id,
        code="TOAN12.GT.03",
        description="Xác định được đường tiệm cận đứng, tiệm cận ngang, tiệm cận xiên của đồ thị hàm số.",
        competence="Năng lực tư duy và lập luận toán học",
        cognitive_level="COMPREHENSION",
        order_index=3,
    )
    yccd_gt_04 = LearningOutcome(
        lesson_id=les_do_thi.id,
        code="TOAN12.GT.04",
        description="Khảo sát được sự biến thiên và vẽ đồ thị của hàm số bậc ba, hàm phân thức bậc nhất trên bậc nhất, bậc hai trên bậc nhất.",
        competence="Năng lực sử dụng công cụ, phương tiện học toán",
        cognitive_level="APPLICATION",
        order_index=4,
    )
    yccd_gt_05 = LearningOutcome(
        lesson_id=les_nguyenham.id,
        code="TOAN12.GT.05",
        description="Nhận biết được định nghĩa và các tính chất cơ bản của nguyên hàm; tìm được nguyên hàm của các hàm số cơ bản.",
        competence="Năng lực tư duy và lập luận toán học",
        cognitive_level="RECOGNITION",
        order_index=5,
    )
    yccd_gt_06 = LearningOutcome(
        lesson_id=les_tichphan.id,
        code="TOAN12.GT.06",
        description="Tính được tích phân của một số hàm số bằng định nghĩa và phương pháp đổi biến số, từng phần.",
        competence="Năng lực giải quyết vấn đề toán học",
        cognitive_level="APPLICATION",
        order_index=6,
    )
    yccd_gt_07 = LearningOutcome(
        lesson_id=les_tichphan.id,
        code="TOAN12.GT.07",
        description="Sử dụng được tích phân để tính diện tích hình phẳng và thể tích khối tròn xoay.",
        competence="Năng lực mô hình hoá toán học",
        cognitive_level="APPLICATION",
        order_index=7,
    )

    yccd_hh_01 = LearningOutcome(
        lesson_id=les_vecto.id,
        code="TOAN12.HH.01",
        description="Nhận biết được toạ độ của điểm và vectơ trong hệ toạ độ Oxyz; tính được tích vô hướng của hai vectơ.",
        competence="Năng lực tư duy và lập luận toán học",
        cognitive_level="RECOGNITION",
        order_index=8,
    )
    yccd_hh_02 = LearningOutcome(
        lesson_id=les_matphang.id,
        code="TOAN12.HH.02",
        description="Lập được phương trình tổng quát của mặt phẳng; tính được khoảng cách từ một điểm đến mặt phẳng.",
        competence="Năng lực giải quyết vấn đề toán học",
        cognitive_level="COMPREHENSION",
        order_index=9,
    )
    yccd_hh_03 = LearningOutcome(
        lesson_id=les_duongthang.id,
        code="TOAN12.HH.03",
        description="Lập được phương trình tham số và chính tắc của đường thẳng trong không gian.",
        competence="Năng lực giải quyết vấn đề toán học",
        cognitive_level="APPLICATION",
        order_index=10,
    )
    yccd_hh_04 = LearningOutcome(
        lesson_id=les_matcau.id,
        code="TOAN12.HH.04",
        description="Nhận biết và viết được phương trình mặt cầu trong không gian; xác định toạ độ tâm và bán kính.",
        competence="Năng lực tư duy và lập luận toán học",
        cognitive_level="COMPREHENSION",
        order_index=11,
    )

    yccd_tk_01 = LearningOutcome(
        lesson_id=les_xscodk.id,
        code="TOAN12.TK.01",
        description="Nhận biết được khái niệm xác suất có điều kiện; áp dụng được công thức nhân xác suất.",
        competence="Năng lực tư duy và lập luận toán học",
        cognitive_level="RECOGNITION",
        order_index=12,
    )
    yccd_tk_02 = LearningOutcome(
        lesson_id=les_bayes.id,
        code="TOAN12.TK.02",
        description="Vận dụng được công thức xác suất toàn phần và công thức Bayes trong tính toán xác suất thực tiễn.",
        competence="Năng lực giải quyết vấn đề toán học",
        cognitive_level="APPLICATION",
        order_index=13,
    )
    yccd_tk_03 = LearningOutcome(
        lesson_id=les_phuongsai.id,
        code="TOAN12.TK.03",
        description="Tính và giải thích được ý nghĩa của phương sai, độ lệch chuẩn cho mẫu số liệu ghép nhóm.",
        competence="Năng lực giải quyết vấn đề toán học",
        cognitive_level="COMPREHENSION",
        order_index=14,
    )

    yccd_th_01 = LearningOutcome(
        lesson_id=les_toiuu.id,
        code="TOAN12.TH.01",
        description="Vận dụng kiến thức giải tích để giải quyết các bài toán tối ưu hoá chi phí, diện tích, thể tích trong thực tiễn.",
        competence="Năng lực mô hình hoá toán học",
        cognitive_level="APPLICATION",
        order_index=15,
    )

    db.add_all([
        yccd_gt_01, yccd_gt_02, yccd_gt_03, yccd_gt_04,
        yccd_gt_05, yccd_gt_06, yccd_gt_07,
        yccd_hh_01, yccd_hh_02, yccd_hh_03, yccd_hh_04,
        yccd_tk_01, yccd_tk_02, yccd_tk_03,
        yccd_th_01,
    ])
    db.flush()

    # ==============================================================================
    # 7. PROBLEM ARCHETYPES (DẠNG CÂU HỎI / BÀI TẬP CHUYÊN ĐỀ)
    # ==============================================================================
    pa_gt01_d1 = ProblemArchetype(learning_outcome_id=yccd_gt_01.id, code="TOAN12.GT.01.D01", name="Đọc BBT hoặc đồ thị tìm khoảng đơn điệu và cực trị", order_index=1)
    pa_gt01_d2 = ProblemArchetype(learning_outcome_id=yccd_gt_01.id, code="TOAN12.GT.01.D02", name="Cực trị hàm đa thức bậc 3 chứa tham số m", order_index=2)
    pa_gt01_d3 = ProblemArchetype(learning_outcome_id=yccd_gt_01.id, code="TOAN12.GT.01.D03", name="Cực trị hàm hợp f(u(x))", order_index=3)

    pa_gt02_d1 = ProblemArchetype(learning_outcome_id=yccd_gt_02.id, code="TOAN12.GT.02.D01", name="GTLN - GTNN của hàm số trên đoạn [a, b]", order_index=1)
    pa_gt02_d2 = ProblemArchetype(learning_outcome_id=yccd_gt_02.id, code="TOAN12.GT.02.D02", name="Bài toán tối ưu ứng dụng GTLN - GTNN", order_index=2)

    pa_gt03_d1 = ProblemArchetype(learning_outcome_id=yccd_gt_03.id, code="TOAN12.GT.03.D01", name="Tìm đường tiệm cận đứng, tiệm cận ngang của hàm phân thức", order_index=1)
    pa_gt03_d2 = ProblemArchetype(learning_outcome_id=yccd_gt_03.id, code="TOAN12.GT.03.D02", name="Tiệm cận của đồ thị chứa tham số m", order_index=2)

    pa_gt04_d1 = ProblemArchetype(learning_outcome_id=yccd_gt_04.id, code="TOAN12.GT.04.D01", name="Nhận dạng đồ thị và bảng biến thiên", order_index=1)

    pa_gt05_d1 = ProblemArchetype(learning_outcome_id=yccd_gt_05.id, code="TOAN12.GT.05.D01", name="Nguyên hàm của hàm số cơ bản và đa thức, lượng giác", order_index=1)

    pa_gt06_d1 = ProblemArchetype(learning_outcome_id=yccd_gt_06.id, code="TOAN12.GT.06.D01", name="Tính tích phân bằng phương pháp đổi biến số và từng phần", order_index=1)
    pa_gt07_d1 = ProblemArchetype(learning_outcome_id=yccd_gt_07.id, code="TOAN12.GT.07.D01", name="Ứng dụng tích phân tính diện tích hình phẳng và thể tích", order_index=1)

    pa_hh01_d1 = ProblemArchetype(learning_outcome_id=yccd_hh_01.id, code="TOAN12.HH.01.D01", name="Tìm toạ độ điểm, toạ độ vectơ, độ dài vectơ và tích vô hướng", order_index=1)
    pa_hh02_d1 = ProblemArchetype(learning_outcome_id=yccd_hh_02.id, code="TOAN12.HH.02.D01", name="Viết phương trình mặt phẳng và tính khoảng cách từ điểm đến mặt phẳng", order_index=1)
    pa_hh03_d1 = ProblemArchetype(learning_outcome_id=yccd_hh_03.id, code="TOAN12.HH.03.D01", name="Viết phương trình đường thẳng và vị trí tương đối", order_index=1)
    pa_hh04_d1 = ProblemArchetype(learning_outcome_id=yccd_hh_04.id, code="TOAN12.HH.04.D01", name="Xác định tâm, bán kính và viết phương trình mặt cầu", order_index=1)

    pa_tk01_d1 = ProblemArchetype(learning_outcome_id=yccd_tk_01.id, code="TOAN12.TK.01.D01", name="Tính xác suất có điều kiện P(A|B)", order_index=1)
    pa_tk02_d1 = ProblemArchetype(learning_outcome_id=yccd_tk_02.id, code="TOAN12.TK.02.D01", name="Áp dụng công thức xác suất toàn phần và công thức Bayes", order_index=1)
    pa_tk03_d1 = ProblemArchetype(learning_outcome_id=yccd_tk_03.id, code="TOAN12.TK.03.D01", name="Tính phương sai, độ lệch chuẩn mẫu số liệu ghép nhóm", order_index=1)

    pa_th01_d1 = ProblemArchetype(learning_outcome_id=yccd_th_01.id, code="TOAN12.TH.01.D01", name="Bài toán tối ưu chi phí và mô hình hoá thực tế", order_index=1)

    db.add_all([
        pa_gt01_d1, pa_gt01_d2, pa_gt01_d3,
        pa_gt02_d1, pa_gt02_d2,
        pa_gt03_d1, pa_gt03_d2,
        pa_gt04_d1,
        pa_gt05_d1, pa_gt06_d1, pa_gt07_d1,
        pa_hh01_d1, pa_hh02_d1, pa_hh03_d1, pa_hh04_d1,
        pa_tk01_d1, pa_tk02_d1, pa_tk03_d1,
        pa_th01_d1,
    ])
    db.flush()

    # ==============================================================================
    # 8. 32 SAMPLE QUESTIONS (CIRCULAR 32 & DECISION 764/QĐ-BGDĐT)
    # Rich LaTeX, 5 formats, cognitive levels, fixed options, True/False stepwise
    # ==============================================================================

    questions_to_add = []

    # Q01: SINGLE_CHOICE - RECOGNITION (Đọc BBT tìm khoảng đồng biến)
    q01 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_gt_ds.id, topic_id=top_daoham.id,
        lesson_id=les_dondieu.id, learning_outcome_id=yccd_gt_01.id, problem_archetype_id=pa_gt01_d1.id,
        cognitive_level="RECOGNITION", question_type="SINGLE_CHOICE",
        stem="Cho hàm số $y = f(x)$ liên tục trên $\\mathbb{R}$ và có bảng xét dấu đạo hàm $f'(x)$ như sau:\n\n$$\\begin{array}{c|ccccccc} x & -\\infty & & -1 & & 2 & & +\\infty \\\\ \\hline f'(x) & & + & 0 & - & 0 & + & \\end{array}$$\n\nHàm số đã cho đồng biến trên khoảng nào dưới đây?",
        explanation="Dựa vào bảng xét dấu, $f'(x) > 0$ khi $x \\in (-\\infty; -1)$ và $x \\in (2; +\\infty)$. Do đó hàm số đồng biến trên các khoảng $(-\\infty; -1)$ và $(2; +\\infty)$.",
        source_reference="Đề tham khảo Tốt nghiệp THPT 2025 - Bộ GD&ĐT", status="APPROVED", difficulty_p=0.85, discrimination_d=0.35,
    )
    q01.options = [
        QuestionOption(label="A", content="$(-\\infty; -1)$", is_correct=True, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="$(-1; 2)$", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="$(-\\infty; 2)$", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="$(-1; +\\infty)$", is_correct=False, is_fixed=False, order_index=4),
    ]
    questions_to_add.append(q01)

    # Q02: SINGLE_CHOICE - APPLICATION (Cực trị chứa tham số m, có fixed option)
    q02 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_gt_ds.id, topic_id=top_daoham.id,
        lesson_id=les_dondieu.id, learning_outcome_id=yccd_gt_01.id, problem_archetype_id=pa_gt01_d2.id,
        cognitive_level="APPLICATION", question_type="SINGLE_CHOICE",
        stem="Cho hàm số $y = x^3 - 3mx^2 + 4$. Tìm tất cả các giá trị của tham số thực $m$ để hàm số có hai điểm cực trị $x_1, x_2$ thoả mãn $x_1 x_2 < 0$ (hai điểm cực trị nằm về hai phía trục tung).",
        explanation="Ta có $y' = 3x^2 - 6mx = 3x(x - 2m)$. Phương trình $y' = 0 \\iff x = 0$ hoặc $x = 2m$. Một nghiệm luôn bằng $0$, nên tích hai nghiệm $x_1 x_2 = 0 \\cdot 2m = 0$, không thể thoả mãn $x_1 x_2 < 0$ với mọi $m$. Do đó không có giá trị $m$ nào thoả mãn.",
        source_reference="Đề Khảo sát Chuyên đề Sở GD&ĐT", status="APPROVED", difficulty_p=0.42, discrimination_d=0.48,
    )
    q02.options = [
        QuestionOption(label="A", content="$m > 0$", is_correct=False, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="$m < 0$", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="$m \\ne 0$", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="Không có giá trị nào của tham số $m$", is_correct=True, is_fixed=True, order_index=4),
    ]
    questions_to_add.append(q02)

    # Q03: SINGLE_CHOICE - RECOGNITION (Fixed option 'Cả A và B đều đúng')
    q03 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_gt_ds.id, topic_id=top_daoham.id,
        lesson_id=les_tiemcan.id, learning_outcome_id=yccd_gt_03.id, problem_archetype_id=pa_gt03_d1.id,
        cognitive_level="RECOGNITION", question_type="SINGLE_CHOICE",
        stem="Cho hàm số $y = \\frac{2x - 1}{x + 1}$. Khẳng định nào sau đây về đường tiệm cận của đồ thị hàm số là đúng?",
        explanation="Đồ thị hàm số có tiệm cận đứng là $x = -1$ và tiệm cận ngang là $y = 2$. Do đó cả hai đường thẳng $x = -1$ và $y = 2$ đều là đường tiệm cận.",
        source_reference="Đề ôn tập Khảo thí 2025", status="APPROVED", difficulty_p=0.78, discrimination_d=0.30,
    )
    q03.options = [
        QuestionOption(label="A", content="Đường thẳng $x = -1$ là tiệm cận đứng của đồ thị hàm số", is_correct=False, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="Đường thẳng $y = 2$ là tiệm cận ngang của đồ thị hàm số", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="Đường thẳng $y = -1$ là tiệm cận ngang của đồ thị hàm số", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="Cả A và B đều đúng", is_correct=True, is_fixed=True, order_index=4),
    ]
    questions_to_add.append(q03)

    # Q04: SINGLE_CHOICE - RECOGNITION (Nguyên hàm cơ bản)
    q04 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_gt_ds.id, topic_id=top_tichphan.id,
        lesson_id=les_nguyenham.id, learning_outcome_id=yccd_gt_05.id, problem_archetype_id=pa_gt05_d1.id,
        cognitive_level="RECOGNITION", question_type="SINGLE_CHOICE",
        stem="Họ tất cả các nguyên hàm của hàm số $f(x) = 3x^2 + \\sin x$ trên $\\mathbb{R}$ là:",
        explanation="Áp dụng công thức nguyên hàm cơ bản: $\\int (3x^2 + \\sin x) dx = x^3 - \\cos x + C$.",
        source_reference="Đề tham khảo Tốt nghiệp THPT 2025", status="APPROVED", difficulty_p=0.88, discrimination_d=0.25,
    )
    q04.options = [
        QuestionOption(label="A", content="$F(x) = x^3 - \\cos x + C$", is_correct=True, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="$F(x) = 6x + \\cos x + C$", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="$F(x) = x^3 + \\cos x + C$", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="$F(x) = 3x^3 - \\cos x + C$", is_correct=False, is_fixed=False, order_index=4),
    ]
    questions_to_add.append(q04)

    # Q05: SINGLE_CHOICE - COMPREHENSION (Tích phân đổi biến)
    q05 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_gt_ds.id, topic_id=top_tichphan.id,
        lesson_id=les_tichphan.id, learning_outcome_id=yccd_gt_06.id, problem_archetype_id=pa_gt06_d1.id,
        cognitive_level="COMPREHENSION", question_type="SINGLE_CHOICE",
        stem="Tính tích phân $I = \\int_{0}^{1} x e^{x^2} dx$.",
        explanation="Đặt $u = x^2 \\implies du = 2x dx \\implies x dx = \\frac{1}{2}du$. Đổi cận: $x = 0 \\implies u = 0; x = 1 \\implies u = 1$. Khi đó $I = \\frac{1}{2} \\int_{0}^{1} e^u du = \\frac{1}{2}(e - 1)$.",
        source_reference="Ngân hàng Đề thi Quốc gia 2025", status="APPROVED", difficulty_p=0.65, discrimination_d=0.45,
    )
    q05.options = [
        QuestionOption(label="A", content="$I = \\frac{e - 1}{2}$", is_correct=True, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="$I = e - 1$", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="$I = \\frac{e}{2}$", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="$I = 2(e - 1)$", is_correct=False, is_fixed=False, order_index=4),
    ]
    questions_to_add.append(q05)

    # Q06: SINGLE_CHOICE - RECOGNITION (Toạ độ điểm và hình chiếu trong Oxyz)
    q06 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_hh_dl.id, topic_id=top_oxyz.id,
        lesson_id=les_vecto.id, learning_outcome_id=yccd_hh_01.id, problem_archetype_id=pa_hh01_d1.id,
        cognitive_level="RECOGNITION", question_type="SINGLE_CHOICE",
        stem="Trong không gian $Oxyz$, cho điểm $M(2; -3; 5)$. Hình chiếu vuông góc của điểm $M$ trên mặt phẳng toạ độ $(Oxy)$ có toạ độ là:",
        explanation="Hình chiếu vuông góc của điểm $M(x_0; y_0; z_0)$ lên mặt phẳng $(Oxy)$ có toạ độ là $(x_0; y_0; 0)$. Vậy toạ độ cần tìm là $(2; -3; 0)$.",
        source_reference="Đề tham khảo Tốt nghiệp THPT 2025", status="APPROVED", difficulty_p=0.92, discrimination_d=0.22,
    )
    q06.options = [
        QuestionOption(label="A", content="$(2; -3; 0)$", is_correct=True, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="$(0; 0; 5)$", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="$(2; 0; 5)$", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="$(0; -3; 5)$", is_correct=False, is_fixed=False, order_index=4),
    ]
    questions_to_add.append(q06)

    # Q07: SINGLE_CHOICE - RECOGNITION (VTPT mặt phẳng Oxyz)
    q07 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_hh_dl.id, topic_id=top_oxyz.id,
        lesson_id=les_matphang.id, learning_outcome_id=yccd_hh_02.id, problem_archetype_id=pa_hh02_d1.id,
        cognitive_level="RECOGNITION", question_type="SINGLE_CHOICE",
        stem="Trong không gian $Oxyz$, một vectơ pháp tuyến của mặt phẳng $(P): 2x - y + 3z - 4 = 0$ là:",
        explanation="Mặt phẳng có phương trình tổng quát $Ax + By + Cz + D = 0$ nhận $\\overrightarrow{n} = (A; B; C)$ làm một VTPT. Do đó $\\overrightarrow{n} = (2; -1; 3)$.",
        source_reference="Đề thi thử THPT Quốc gia 2025", status="APPROVED", difficulty_p=0.90, discrimination_d=0.28,
    )
    q07.options = [
        QuestionOption(label="A", content="$\\overrightarrow{n_1} = (2; -1; 3)$", is_correct=True, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="$\\overrightarrow{n_2} = (2; 1; 3)$", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="$\\overrightarrow{n_3} = (2; -1; -4)$", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="$\\overrightarrow{n_4} = (-1; 3; -4)$", is_correct=False, is_fixed=False, order_index=4),
    ]
    questions_to_add.append(q07)

    # Q08: SINGLE_CHOICE - COMPREHENSION (Phương trình mặt cầu)
    q08 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_hh_dl.id, topic_id=top_oxyz.id,
        lesson_id=les_matcau.id, learning_outcome_id=yccd_hh_04.id, problem_archetype_id=pa_hh04_d1.id,
        cognitive_level="COMPREHENSION", question_type="SINGLE_CHOICE",
        stem="Trong không gian $Oxyz$, cho mặt cầu $(S): (x - 1)^2 + (y + 2)^2 + (z - 4)^2 = 16$. Toạ độ tâm $I$ và bán kính $R$ của mặt cầu $(S)$ là:",
        explanation="Phương trình chuẩn $(x - a)^2 + (y - b)^2 + (z - c)^2 = R^2$ có tâm $I(a; b; c) = (1; -2; 4)$ và bán kính $R = \\sqrt{16} = 4$.",
        source_reference="Đề khảo sát năng lực Toán 12", status="APPROVED", difficulty_p=0.82, discrimination_d=0.32,
    )
    q08.options = [
        QuestionOption(label="A", content="$I(1; -2; 4)$ và $R = 4$", is_correct=True, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="$I(-1; 2; -4)$ và $R = 4$", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="$I(1; -2; 4)$ và $R = 16$", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="$I(-1; 2; -4)$ và $R = 16$", is_correct=False, is_fixed=False, order_index=4),
    ]
    questions_to_add.append(q08)

    # Q09: SINGLE_CHOICE - RECOGNITION (Xác suất có điều kiện cơ bản)
    q09 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_tk_xs.id, topic_id=top_xacsuat.id,
        lesson_id=les_xscodk.id, learning_outcome_id=yccd_tk_01.id, problem_archetype_id=pa_tk01_d1.id,
        cognitive_level="RECOGNITION", question_type="SINGLE_CHOICE",
        stem="Cho hai biến cố $A$ và $B$ bất kì với $P(B) > 0$. Công thức tính xác suất có điều kiện của biến cố $A$ khi biến cố $B$ đã xảy ra là:",
        explanation="Theo định nghĩa xác suất có điều kiện: $P(A|B) = \\frac{P(A \\cap B)}{P(B)}$.",
        source_reference="Chương trình GDPT 2018 - Thông tư 32/2018/TT-BGDĐT", status="APPROVED", difficulty_p=0.91, discrimination_d=0.20,
    )
    q09.options = [
        QuestionOption(label="A", content="$P(A|B) = \\frac{P(A \\cap B)}{P(B)}$", is_correct=True, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="$P(A|B) = \\frac{P(A \\cap B)}{P(A)}$", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="$P(A|B) = \\frac{P(A)}{P(B)}$", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="$P(A|B) = P(A) \\cdot P(B)$", is_correct=False, is_fixed=False, order_index=4),
    ]
    questions_to_add.append(q09)

    # Q10: SINGLE_CHOICE - COMPREHENSION (Tính xác suất có điều kiện)
    q10 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_tk_xs.id, topic_id=top_xacsuat.id,
        lesson_id=les_xscodk.id, learning_outcome_id=yccd_tk_01.id, problem_archetype_id=pa_tk01_d1.id,
        cognitive_level="COMPREHENSION", question_type="SINGLE_CHOICE",
        stem="Một lớp học có 40 học sinh gồm 25 nữ và 15 nam. Trong đó có 10 bạn nữ và 5 bạn nam giỏi môn Toán. Chọn ngẫu nhiên một học sinh. Biết rằng học sinh được chọn giỏi môn Toán, xác suất để học sinh đó là nữ bằng:",
        explanation="Gọi $B$ là biến cố 'học sinh giỏi Toán', $A$ là biến cố 'học sinh là nữ'. Tổng số học sinh giỏi Toán là $10 + 5 = 15$. Số học sinh nữ giỏi Toán là 10. Vậy $P(A|B) = \\frac{10}{15} = \\frac{2}{3}$.",
        source_reference="Đề kiểm tra Định kỳ 2025", status="APPROVED", difficulty_p=0.74, discrimination_d=0.38,
    )
    q10.options = [
        QuestionOption(label="A", content="$\\frac{2}{3}$", is_correct=True, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="$\\frac{1}{3}$", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="$\\frac{2}{5}$", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="$\\frac{5}{8}$", is_correct=False, is_fixed=False, order_index=4),
    ]
    questions_to_add.append(q10)

    # Q11: SINGLE_CHOICE - RECOGNITION (Thống kê số đặc trưng)
    q11 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_tk_xs.id, topic_id=top_thongke.id,
        lesson_id=les_phuongsai.id, learning_outcome_id=yccd_tk_03.id, problem_archetype_id=pa_tk03_d1.id,
        cognitive_level="RECOGNITION", question_type="SINGLE_CHOICE",
        stem="Trong thống kê, số đặc trưng nào sau đây dùng để đo mức độ phân tán của mẫu số liệu?",
        explanation="Phương sai và độ lệch chuẩn (cùng khoảng biến thiên, khoảng tứ phân vị) là các đại lượng dùng để đo mức độ phân tán. Số trung bình, trung vị, mốt là số đo xu thế trung tâm.",
        source_reference="Sách chuyên đề Thống kê GDPT 2018", status="APPROVED", difficulty_p=0.86, discrimination_d=0.28,
    )
    q11.options = [
        QuestionOption(label="A", content="Độ lệch chuẩn", is_correct=True, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="Số trung bình", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="Số trung vị", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="Mốt của mẫu số liệu", is_correct=False, is_fixed=False, order_index=4),
    ]
    questions_to_add.append(q11)

    # Q12: SINGLE_CHOICE - APPLICATION (Bài toán tối ưu rào vườn - Thực hành trải nghiệm)
    q12 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_th_tn.id, topic_id=top_thuchanh.id,
        lesson_id=les_toiuu.id, learning_outcome_id=yccd_th_01.id, problem_archetype_id=pa_th01_d1.id,
        cognitive_level="APPLICATION", question_type="SINGLE_CHOICE",
        stem="Một hộ nông dân có $100\\text{ m}$ lưới thép muốn rào một khu đất hình chữ nhật giáp với một bờ tường thẳng (không cần rào phía bờ tường). Diện tích lớn nhất của khu đất có thể rào được bằng bao nhiêu mét vuông?",
        explanation="Gọi chiều rộng là $x$ ($0 < x < 50$), chiều dài là $100 - 2x$. Diện tích $S(x) = x(100 - 2x) = -2x^2 + 100x$. Đạo hàm $S'(x) = -4x + 100 = 0 \\iff x = 25\\text{ m}$. Diện tích cực đại $S(25) = 25 \\times 50 = 1250\\text{ m}^2$.",
        source_reference="Đề tham khảo Tốt nghiệp THPT 2025 - Câu toán thực tế", status="APPROVED", difficulty_p=0.58, discrimination_d=0.46,
    )
    q12.options = [
        QuestionOption(label="A", content="$1250\\text{ m}^2$", is_correct=True, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="$1000\\text{ m}^2$", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="$625\\text{ m}^2$", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="$2500\\text{ m}^2$", is_correct=False, is_fixed=False, order_index=4),
    ]
    questions_to_add.append(q12)

    # Q13: SINGLE_CHOICE - APPLICATION (Tiệm cận đứng chứa tham số m, có fixed option)
    q13 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_gt_ds.id, topic_id=top_daoham.id,
        lesson_id=les_tiemcan.id, learning_outcome_id=yccd_gt_03.id, problem_archetype_id=pa_gt03_d2.id,
        cognitive_level="APPLICATION", question_type="SINGLE_CHOICE",
        stem="Tìm tất cả các giá trị của tham số $m$ để đồ thị hàm số $y = \\frac{x - 1}{x^2 - 2mx + 9}$ có đúng một đường tiệm cận đứng.",
        explanation="Để đồ thị có đúng 1 tiệm cận đứng thì mẫu số $g(x) = x^2 - 2mx + 9 = 0$ có nghiệm kép, hoặc có 2 nghiệm phân biệt trong đó có 1 nghiệm $x = 1$. TH1: $\\Delta' = m^2 - 9 = 0 \\iff m = \\pm 3$. TH2: $g(1) = 1 - 2m + 9 = 0 \\iff m = 5$. Với $m = 5$, mẫu có nghiệm $x=1, x=9$, khi đó $x=1$ triệt tiêu với tử, còn lại tiệm cận $x=9$ (thoả mãn). Vậy $m \\in \\{-3; 3; 5\\}$.",
        source_reference="Đề bồi dưỡng học sinh THPT 2025", status="APPROVED", difficulty_p=0.38, discrimination_d=0.52,
    )
    q13.options = [
        QuestionOption(label="A", content="$m \\in \\{-3; 3; 5\\}$", is_correct=True, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="$m = \\pm 3$", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="$m = 5$", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="Tất cả các phương án trên đều sai", is_correct=False, is_fixed=True, order_index=4),
    ]
    questions_to_add.append(q13)

    # Q14: SINGLE_CHOICE - COMPREHENSION (Khoảng cách điểm đến mặt phẳng)
    q14 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_hh_dl.id, topic_id=top_oxyz.id,
        lesson_id=les_matphang.id, learning_outcome_id=yccd_hh_02.id, problem_archetype_id=pa_hh02_d1.id,
        cognitive_level="COMPREHENSION", question_type="SINGLE_CHOICE",
        stem="Trong không gian $Oxyz$, khoảng cách từ điểm $A(1; 2; -1)$ đến mặt phẳng $(P): 2x - 2y + z + 8 = 0$ bằng:",
        explanation="Công thức khoảng cách: $d(A, (P)) = \\frac{|2(1) - 2(2) + (-1) + 8|}{\\sqrt{2^2 + (-2)^2 + 1^2}} = \\frac{|2 - 4 - 1 + 8|}{3} = \\frac{5}{3}$.",
        source_reference="Đề kiểm tra Đánh giá Năng lực 2025", status="APPROVED", difficulty_p=0.76, discrimination_d=0.36,
    )
    q14.options = [
        QuestionOption(label="A", content="$\\frac{5}{3}$", is_correct=True, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="$\\frac{5}{9}$", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="$3$", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="$\\frac{7}{3}$", is_correct=False, is_fixed=False, order_index=4),
    ]
    questions_to_add.append(q14)

    # Q15: SINGLE_CHOICE - RECOGNITION (Tích vô hướng hai vectơ trong không gian)
    q15 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_hh_dl.id, topic_id=top_oxyz.id,
        lesson_id=les_vecto.id, learning_outcome_id=yccd_hh_01.id, problem_archetype_id=pa_hh01_d1.id,
        cognitive_level="RECOGNITION", question_type="SINGLE_CHOICE",
        stem="Trong không gian $Oxyz$, cho hai vectơ $\\overrightarrow{u} = (1; -2; 3)$ và $\\overrightarrow{v} = (4; 0; -1)$. Tích vô hướng $\\overrightarrow{u} \\cdot \\overrightarrow{v}$ bằng:",
        explanation="$\\overrightarrow{u} \\cdot \\overrightarrow{v} = 1 \\cdot 4 + (-2) \\cdot 0 + 3 \\cdot (-1) = 4 + 0 - 3 = 1$.",
        source_reference="Đề thi Tốt nghiệp THPT 2025", status="APPROVED", difficulty_p=0.89, discrimination_d=0.24,
    )
    q15.options = [
        QuestionOption(label="A", content="$1$", is_correct=True, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="$-1$", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="$7$", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="$\\sqrt{14}$", is_correct=False, is_fixed=False, order_index=4),
    ]
    questions_to_add.append(q15)

    # Q16: SINGLE_CHOICE - COMPREHENSION (Nhận dạng đồ thị hàm phân thức bậc 1 / bậc 1)
    q16 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_gt_ds.id, topic_id=top_daoham.id,
        lesson_id=les_do_thi.id, learning_outcome_id=yccd_gt_04.id, problem_archetype_id=pa_gt04_d1.id,
        cognitive_level="COMPREHENSION", question_type="SINGLE_CHOICE",
        stem="Đường cong trong hình vẽ bên là đồ thị của hàm số nào dưới đây, biết đồ thị có tiệm cận đứng $x = 1$, tiệm cận ngang $y = 2$ và đi qua điểm $(0; -1)$?",
        explanation="Tiệm cận đứng $x = 1$, tiệm cận ngang $y = 2$, giao điểm với $Oy$ tại $(0; -1)$. Hàm số thoả mãn là $y = \\frac{2x - 1}{x - 1}$.",
        source_reference="Ngân hàng Khảo thí TT 32", status="APPROVED", difficulty_p=0.81, discrimination_d=0.34,
    )
    q16.options = [
        QuestionOption(label="A", content="$y = \\frac{2x - 1}{x - 1}$", is_correct=True, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="$y = \\frac{2x + 1}{x - 1}$", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="$y = \\frac{x + 2}{x - 1}$", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="$y = \\frac{2x - 1}{x + 1}$", is_correct=False, is_fixed=False, order_index=4),
    ]
    questions_to_add.append(q16)

    # Q17: SINGLE_CHOICE - RECOGNITION (Vector chỉ phương đường thẳng)
    q17 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_hh_dl.id, topic_id=top_oxyz.id,
        lesson_id=les_duongthang.id, learning_outcome_id=yccd_hh_03.id, problem_archetype_id=pa_hh03_d1.id,
        cognitive_level="RECOGNITION", question_type="SINGLE_CHOICE",
        stem="Trong không gian $Oxyz$, cho đường thẳng $d: \\frac{x - 3}{2} = \\frac{y + 1}{-1} = \\frac{z - 4}{5}$. Vectơ nào sau đây là một vectơ chỉ phương của đường thẳng $d$?",
        explanation="Đường thẳng dạng $\\frac{x - x_0}{a} = \\frac{y - y_0}{b} = \\frac{z - z_0}{c}$ có VTCP là $\\overrightarrow{u} = (a; b; c) = (2; -1; 5)$.",
        source_reference="Đề thi Tốt nghiệp THPT 2025", status="APPROVED", difficulty_p=0.87, discrimination_d=0.26,
    )
    q17.options = [
        QuestionOption(label="A", content="$\\overrightarrow{u} = (2; -1; 5)$", is_correct=True, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="$\\overrightarrow{u} = (3; -1; 4)$", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="$\\overrightarrow{u} = (-2; -1; 5)$", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="$\\overrightarrow{u} = (2; 1; 5)$", is_correct=False, is_fixed=False, order_index=4),
    ]
    questions_to_add.append(q17)

    # Q18: SINGLE_CHOICE - COMPREHENSION (Diện tích hình phẳng giới hạn bởi parabol và trục hoành)
    q18 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_gt_ds.id, topic_id=top_tichphan.id,
        lesson_id=les_tichphan.id, learning_outcome_id=yccd_gt_07.id, problem_archetype_id=pa_gt07_d1.id,
        cognitive_level="COMPREHENSION", question_type="SINGLE_CHOICE",
        stem="Diện tích hình phẳng giới hạn bởi đồ thị hàm số $y = 4 - x^2$ và trục hoành $Ox$ bằng:",
        explanation="Phương trình hoành độ giao điểm: $4 - x^2 = 0 \\iff x = \\pm 2$. Diện tích $S = \\int_{-2}^{2} (4 - x^2) dx = \\left[ 4x - \\frac{x^3}{3} \\right]_{-2}^{2} = \\frac{32}{3}$.",
        source_reference="Đề kiểm tra Cuối kì 1 Toán 12", status="APPROVED", difficulty_p=0.72, discrimination_d=0.38,
    )
    q18.options = [
        QuestionOption(label="A", content="$S = \\frac{32}{3}$", is_correct=True, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="$S = \\frac{16}{3}$", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="$S = 16$", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="$S = 8$", is_correct=False, is_fixed=False, order_index=4),
    ]
    questions_to_add.append(q18)

    # ==============================================================================
    # PART II: TRUE / FALSE GROUP QUESTIONS (4 INDEPENDENT AFFIRMATIONS)
    # Decision 764/QĐ-BGDĐT: Stepwise Scoring (0.1, 0.25, 0.5, 1.0)
    # ==============================================================================

    # Q19: TRUE_FALSE_GROUP - COMPREHENSION (Hàm phân thức f(x) = (x^2 - 3x + 6)/(x - 1))
    q19 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_gt_ds.id, topic_id=top_daoham.id,
        lesson_id=les_dondieu.id, learning_outcome_id=yccd_gt_01.id, problem_archetype_id=pa_gt01_d1.id,
        cognitive_level="COMPREHENSION", question_type="TRUE_FALSE_GROUP",
        stem="Cho hàm số $y = f(x) = \\frac{x^2 - 3x + 6}{x - 1}$. Các khẳng định sau đây là đúng hay sai?",
        explanation="Ta biến đổi $f(x) = x - 2 + \\frac{4}{x - 1}$. Đạo hàm $f'(x) = 1 - \\frac{4}{(x-1)^2} = \\frac{(x+1)(x-3)}{(x-1)^2}$. Nghiệm của $f'(x) = 0$ là $x = -1, x = 3$.",
        source_reference="Đề tham khảo Quyết định 764/QĐ-BGDĐT Môn Toán 2025", status="APPROVED", difficulty_p=0.55, discrimination_d=0.45,
    )
    q19.sub_statements = [
        SubStatement(label="a", content="Đồ thị hàm số có đường tiệm cận xiên là $y = x - 2$.", is_true=True, explanation="Do $\\lim_{x \\to \\pm\\infty} [f(x) - (x - 2)] = \\lim_{x \\to \\pm\\infty} \\frac{4}{x - 1} = 0$.", order_index=1),
        SubStatement(label="b", content="Hàm số đạt cực đại tại điểm $x = 3$.", is_true=False, explanation="Qua $x = 3$, đạo hàm đổi dấu từ âm sang dương nên $x = 3$ là điểm cực tiểu.", order_index=2),
        SubStatement(label="c", content="Hàm số đồng biến trên khoảng $(3; +\\infty)$.", is_true=True, explanation="Với $x > 3$, $f'(x) > 0$ nên hàm số đồng biến trên $(3; +\\infty)$.", order_index=3),
        SubStatement(label="d", content="Tâm đối xứng của đồ thị hàm số là giao điểm của hai đường tiệm cận $I(1; -1)$.", is_true=True, explanation="Tiệm cận đứng $x = 1$, tiệm cận xiên $y = x - 2$. Giao điểm là $I(1; -1)$.", order_index=4),
    ]
    questions_to_add.append(q19)

    # Q20: TRUE_FALSE_GROUP - APPLICATION (Hình học Oxyz: 4 điểm, mặt phẳng, thể tích tứ diện)
    q20 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_hh_dl.id, topic_id=top_oxyz.id,
        lesson_id=les_matphang.id, learning_outcome_id=yccd_hh_02.id, problem_archetype_id=pa_hh02_d1.id,
        cognitive_level="APPLICATION", question_type="TRUE_FALSE_GROUP",
        stem="Trong không gian $Oxyz$, cho bốn điểm $A(1; 0; 0)$, $B(0; 2; 0)$, $C(0; 0; 3)$ và $D(1; 2; 3)$. Các khẳng định sau đúng hay sai?",
        explanation="Mặt phẳng $(ABC)$ theo đoạn chắn: $\\frac{x}{1} + \\frac{y}{2} + \\frac{z}{3} = 1 \\iff 6x + 3y + 2z - 6 = 0$.",
        source_reference="Đề thi tốt nghiệp THPT 2025 - Định dạng mới", status="APPROVED", difficulty_p=0.48, discrimination_d=0.50,
    )
    q20.sub_statements = [
        SubStatement(label="a", content="Mặt phẳng $(ABC)$ có một vectơ pháp tuyến là $\\overrightarrow{n} = (6; 3; 2)$.", is_true=True, explanation="Phương trình $(ABC): 6x + 3y + 2z - 6 = 0$ có VTPT $\\overrightarrow{n} = (6; 3; 2)$.", order_index=1),
        SubStatement(label="b", content="Điểm $D(1; 2; 3)$ thuộc mặt phẳng $(ABC)$.", is_true=False, explanation="Thay toạ độ $D$: $6(1) + 3(2) + 2(3) - 6 = 6 + 6 + 6 - 6 = 12 \\ne 0$.", order_index=2),
        SubStatement(label="c", content="Thể tích của khối tứ diện $OABC$ bằng $1$ (đơn vị thể tích).", is_true=True, explanation="$V_{OABC} = \\frac{1}{6} OA \\cdot OB \\cdot OC = \\frac{1}{6} \\cdot 1 \\cdot 2 \\cdot 3 = 1$.", order_index=3),
        SubStatement(label="d", content="Khoảng cách từ điểm $D$ đến mặt phẳng $(ABC)$ bằng $\\frac{12}{7}$.", is_true=True, explanation="$d(D, (ABC)) = \\frac{|6(1) + 3(2) + 2(3) - 6|}{\\sqrt{6^2 + 3^2 + 2^2}} = \\frac{12}{\\sqrt{49}} = \\frac{12}{7}$.", order_index=4),
    ]
    questions_to_add.append(q20)

    # Q21: TRUE_FALSE_GROUP - APPLICATION (Mặt cầu phụ thuộc tham số m)
    q21 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_hh_dl.id, topic_id=top_oxyz.id,
        lesson_id=les_matcau.id, learning_outcome_id=yccd_hh_04.id, problem_archetype_id=pa_hh04_d1.id,
        cognitive_level="APPLICATION", question_type="TRUE_FALSE_GROUP",
        stem="Trong không gian $Oxyz$, cho phương trình $(S_m): x^2 + y^2 + z^2 - 2mx + 4y - 6z + 10 = 0$ với $m$ là tham số thực. Các khẳng định sau đúng hay sai?",
        explanation="Hệ số: $a = m, b = -2, c = 3, d = 10$. Điều kiện để là mặt cầu: $a^2 + b^2 + c^2 - d > 0 \\iff m^2 + 4 + 9 - 10 > 0 \\iff m^2 + 3 > 0$ (luôn đúng với mọi $m$).",
        source_reference="Đề kiểm tra Khảo sát Chất lượng 2025", status="APPROVED", difficulty_p=0.52, discrimination_d=0.48,
    )
    q21.sub_statements = [
        SubStatement(label="a", content="Phương trình $(S_m)$ là phương trình mặt cầu với mọi giá trị của tham số $m \\in \\mathbb{R}$.", is_true=True, explanation="Do $R^2 = m^2 + 3 > 0$ với mọi $m$.", order_index=1),
        SubStatement(label="b", content="Tâm của mặt cầu $(S_m)$ có toạ độ là $I(m; -2; 3)$.", is_true=True, explanation="Toạ độ tâm $I = (-a/2; -b/2; -c/2) = (m; -2; 3)$.", order_index=2),
        SubStatement(label="c", content="Bán kính của mặt cầu $(S_m)$ đạt giá trị nhỏ nhất bằng $3$.", is_true=False, explanation="$R = \\sqrt{m^2 + 3} \\ge \\sqrt{3}$. Giá trị nhỏ nhất bằng $\\sqrt{3}$, không phải $3$.", order_index=3),
        SubStatement(label="d", content="Khi $m = 1$, mặt cầu $(S_1)$ tiếp xúc với mặt phẳng $(Oxy)$.", is_true=False, explanation="Khoảng cách từ $I(1; -2; 3)$ đến $(Oxy)$ là $|z_I| = 3$. Bán kính $R = \\sqrt{1 + 3} = 2$. Do $d \\ne R$ nên không tiếp xúc.", order_index=4),
    ]
    questions_to_add.append(q21)

    # Q22: TRUE_FALSE_GROUP - COMPREHENSION (Xác suất có điều kiện: bài toán bốc thăm)
    q22 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_tk_xs.id, topic_id=top_xacsuat.id,
        lesson_id=les_xscodk.id, learning_outcome_id=yccd_tk_01.id, problem_archetype_id=pa_tk01_d1.id,
        cognitive_level="COMPREHENSION", question_type="TRUE_FALSE_GROUP",
        stem="Một hộp kín đựng 10 quả cầu có cùng kích thước và khối lượng, gồm 6 quả màu xanh và 4 quả màu đỏ. Lấy ngẫu nhiên lần lượt 2 quả cầu (không hoàn lại). Gọi $A$ là biến cố 'Quả cầu lấy lần 1 màu xanh', $B$ là biến cố 'Quả cầu lấy lần 2 màu xanh'. Các khẳng định sau đúng hay sai?",
        explanation="Xác suất quả 1 xanh: $P(A) = 6/10 = 3/5$. Sau khi lấy 1 quả xanh, trong hộp còn 9 quả (5 xanh, 4 đỏ). Xác suất quả 2 xanh khi quả 1 xanh: $P(B|A) = 5/9$.",
        source_reference="Sách bài tập Toán 12 - Chương trình GDPT 2018", status="APPROVED", difficulty_p=0.62, discrimination_d=0.40,
    )
    q22.sub_statements = [
        SubStatement(label="a", content="Xác suất của biến cố $A$ là $P(A) = \\frac{3}{5}$.", is_true=True, explanation="$P(A) = 6/10 = 3/5$.", order_index=1),
        SubStatement(label="b", content="Xác suất có điều kiện $P(B|A) = \\frac{5}{9}$.", is_true=True, explanation="Còn 5 quả xanh trên tổng số 9 quả còn lại.", order_index=2),
        SubStatement(label="c", content="Xác suất để cả hai lần đều lấy được quả cầu màu xanh là $\\frac{1}{3}$.", is_true=True, explanation="$P(AB) = P(A) \\cdot P(B|A) = \\frac{3}{5} \\cdot \\frac{5}{9} = \\frac{1}{3}$.", order_index=3),
        SubStatement(label="d", content="Hai biến cố $A$ và $B$ là hai biến cố độc lập.", is_true=False, explanation="Vì việc lấy không hoàn lại làm thay đổi tỉ lệ quả xanh, $P(B|A) = 5/9 \\ne P(B) = 3/5$.", order_index=4),
    ]
    questions_to_add.append(q22)

    # Q23: TRUE_FALSE_GROUP - APPLICATION (Công thức xác suất toàn phần và Bayes trong y tế)
    q23 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_tk_xs.id, topic_id=top_xacsuat.id,
        lesson_id=les_bayes.id, learning_outcome_id=yccd_tk_02.id, problem_archetype_id=pa_tk02_d1.id,
        cognitive_level="APPLICATION", question_type="TRUE_FALSE_GROUP",
        stem="Tỉ lệ người mắc bệnh sốt rét trong một vùng dân cư là $2\\%$. Một xét nghiệm chẩn đoán bệnh có độ nhạy (xác suất dương tính khi có bệnh) là $95\\%$ và độ đặc hiệu (xác suất âm tính khi không có bệnh) là $90\\%$. Chọn ngẫu nhiên một người trong vùng để xét nghiệm. Các khẳng định sau đúng hay sai?",
        explanation="Gọi $B$ là biến cố có bệnh: $P(B) = 0.02, P(\\overline{B}) = 0.98$. Gọi $T$ là biến cố xét nghiệm dương tính: $P(T|B) = 0.95, P(T|\\overline{B}) = 1 - 0.90 = 0.10$.",
        source_reference="Toán ứng dụng đời sống - CT GDPT 2018", status="APPROVED", difficulty_p=0.45, discrimination_d=0.52,
    )
    q23.sub_statements = [
        SubStatement(label="a", content="Xác suất để một người được chọn ngẫu nhiên có kết quả xét nghiệm dương tính là $11.7\\%$.", is_true=True, explanation="$P(T) = P(B)P(T|B) + P(\\overline{B})P(T|\\overline{B}) = 0.02 \\times 0.95 + 0.98 \\times 0.10 = 0.019 + 0.098 = 0.117 = 11.7\\%$.", order_index=1),
        SubStatement(label="b", content="Nếu một người có kết quả xét nghiệm dương tính, xác suất người đó thực sự mắc bệnh lớn hơn $50\\%$.", is_true=False, explanation="Áp dụng công thức Bayes: $P(B|T) = \\frac{0.019}{0.117} \\approx 16.24\\% < 50\\%$.", order_index=2),
        SubStatement(label="c", content="Nếu một người có kết quả xét nghiệm âm tính, xác suất người đó không mắc bệnh xấp xỉ $99.9\\%$.", is_true=True, explanation="$P(\\overline{B}|\\overline{T}) = \\frac{0.98 \\times 0.90}{0.02 \\times 0.05 + 0.98 \\times 0.90} = \\frac{0.882}{0.001 + 0.882} = \\frac{0.882}{0.883} \\approx 99.89\\%$.", order_index=3),
        SubStatement(label="d", content="Xét nghiệm này là hoàn hảo không có sai số trong kết luận y khoa.", is_true=False, explanation="Vẫn tồn tại tỉ lệ dương tính giả ($9.8\\%$) và âm tính giả ($0.1\\%$).", order_index=4),
    ]
    questions_to_add.append(q23)

    # Q24: TRUE_FALSE_GROUP - APPLICATION (Mẫu số liệu ghép nhóm)
    q24 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_tk_xs.id, topic_id=top_thongke.id,
        lesson_id=les_phuongsai.id, learning_outcome_id=yccd_tk_03.id, problem_archetype_id=pa_tk03_d1.id,
        cognitive_level="APPLICATION", question_type="TRUE_FALSE_GROUP",
        stem="Khảo sát thời gian sử dụng điện thoại mỗi ngày của 50 học sinh lớp 12 thu được mẫu số liệu ghép nhóm sau:\n\n$$\\begin{array}{|c|c|c|c|c|} \\hline \\text{Thời gian (giờ)} & [1; 2) & [2; 3) & [3; 4) & [4; 5) \\\\ \\hline \\text{Số học sinh} & 8 & 16 & 20 & 6 \\\\ \\hline \\end{array}$$\n\nCác khẳng định sau đúng hay sai?",
        explanation="Giá trị đại diện các nhóm: $c_1 = 1.5, c_2 = 2.5, c_3 = 3.5, c_4 = 4.5$. Tổng số học sinh $n = 50$.",
        source_reference="Đề kiểm tra Đánh giá Định kỳ Toán 12", status="APPROVED", difficulty_p=0.60, discrimination_d=0.42,
    )
    q24.sub_statements = [
        SubStatement(label="a", content="Số trung bình của mẫu số liệu ghép nhóm là $\\bar{x} = 2.88$ giờ.", is_true=False, explanation="$\\bar{x} = \\frac{8(1.5) + 16(2.5) + 20(3.5) + 6(4.5)}{50} = \\frac{12 + 40 + 70 + 27}{50} = \\frac{149}{50} = 2.98$ giờ.", order_index=1),
        SubStatement(label="b", content="Nhóm chứa mốt của mẫu số liệu là nhóm $[3; 4)$.", is_true=True, explanation="Tần số lớn nhất là 20 thuộc nhóm $[3; 4)$.", order_index=2),
        SubStatement(label="c", content="Khoảng biến thiên của mẫu số liệu ghép nhóm là $4$ giờ.", is_true=True, explanation="$R = 5 - 1 = 4$ giờ.", order_index=3),
        SubStatement(label="d", content="Độ lệch chuẩn của mẫu số liệu ghép nhóm nhỏ hơn $1.0$ giờ.", is_true=True, explanation="Phương sai $s^2 \\approx 0.76$, suy ra $s \\approx 0.87 < 1.0$.", order_index=4),
    ]
    questions_to_add.append(q24)

    # Q25: TRUE_FALSE_GROUP - APPLICATION (Thiết kế bao bì hình hộp chữ nhật - Thực hành trải nghiệm)
    q25 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_th_tn.id, topic_id=top_thuchanh.id,
        lesson_id=les_toiuu.id, learning_outcome_id=yccd_th_01.id, problem_archetype_id=pa_th01_d1.id,
        cognitive_level="APPLICATION", question_type="TRUE_FALSE_GROUP",
        stem="Một doanh nghiệp dự định sản xuất vỏ hộp sữa bột hình trụ có thể tích $V = 500\\pi\\text{ cm}^3$. Doanh nghiệp muốn tiết kiệm chi phí kim loại làm vỏ hộp bằng cách tối thiểu hoá diện tích toàn phần của hình trụ. Các khẳng định sau đúng hay sai?",
        explanation="Thể tích $V = \\pi r^2 h = 500\\pi \\implies h = \\frac{500}{r^2}$. Diện tích toàn phần $S_{tp} = 2\\pi r h + 2\\pi r^2 = \\frac{1000\\pi}{r} + 2\\pi r^2$.",
        source_reference="Toán ứng dụng thực tiễn - Quyết định 764/QĐ-BGDĐT", status="APPROVED", difficulty_p=0.40, discrimination_d=0.55,
    )
    q25.sub_statements = [
        SubStatement(label="a", content="Hàm số biểu diễn diện tích toàn phần theo bán kính đáy $r$ là $S(r) = \\frac{1000\\pi}{r} + 2\\pi r^2$ ($r > 0$).", is_true=True, explanation="Đúng theo công thức biến đổi hình học.", order_index=1),
        SubStatement(label="b", content="Diện tích toàn phần nhỏ nhất khi bán kính đáy $r = 5\\text{ cm}$.", is_true=False, explanation="$S'(r) = -\\frac{1000\\pi}{r^2} + 4\\pi r = 0 \\iff r^3 = 250 \\implies r = \\sqrt[3]{250} \\approx 6.3\\text{ cm} \\ne 5\\text{ cm}$.", order_index=2),
        SubStatement(label="c", content="Tại điểm cực tiểu, chiều cao của hình trụ gấp đôi bán kính đáy ($h = 2r$).", is_true=True, explanation="Ta có $h = \\frac{V}{\\pi r^2} = \\frac{500}{r^2}$. Khi $4\\pi r = \\frac{1000\\pi}{r^2} \\implies 2r = \\frac{500}{r^2} = h$.", order_index=3),
        SubStatement(label="d", content="Chi phí vỏ hộp luôn tỉ lệ thuận với thể tích dung tích chứa.", is_true=False, explanation="Chi phí tỉ lệ với diện tích toàn phần, không tỉ lệ bậc nhất với thể tích.", order_index=4),
    ]
    questions_to_add.append(q25)

    # ==============================================================================
    # PART III: SHORT ANSWER QUESTIONS (TRẢ LỜI NGẮN)
    # Decision 764/QĐ-BGDĐT: Numeric / Short text output
    # ==============================================================================

    # Q26: SHORT_ANSWER - APPLICATION (GTLN, GTNN trên đoạn [0; 2])
    q26 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_gt_ds.id, topic_id=top_daoham.id,
        lesson_id=les_gtln.id, learning_outcome_id=yccd_gt_02.id, problem_archetype_id=pa_gt02_d1.id,
        cognitive_level="APPLICATION", question_type="SHORT_ANSWER",
        stem="Tìm giá trị nhỏ nhất của hàm số $f(x) = x^4 - 2x^2 + 3$ trên đoạn $[0; 2]$.",
        explanation="Đạo hàm $f'(x) = 4x^3 - 4x = 4x(x^2 - 1) = 0 \\iff x = 0$ hoặc $x = 1$ (do xét trên $[0; 2]$). Ta tính: $f(0) = 3$, $f(1) = 2$, $f(2) = 11$. Vậy $\\min_{[0; 2]} f(x) = 2$ tại $x = 1$.",
        short_answer_key="2", tolerance=0.0,
        source_reference="Đề tham khảo Tốt nghiệp THPT 2025 - Phần III", status="APPROVED", difficulty_p=0.72, discrimination_d=0.35,
    )
    questions_to_add.append(q26)

    # Q27: SHORT_ANSWER - APPLICATION (Khoảng cách điểm đến đường thẳng trong Oxyz)
    q27 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_hh_dl.id, topic_id=top_oxyz.id,
        lesson_id=les_duongthang.id, learning_outcome_id=yccd_hh_03.id, problem_archetype_id=pa_hh03_d1.id,
        cognitive_level="APPLICATION", question_type="SHORT_ANSWER",
        stem="Trong không gian $Oxyz$, cho điểm $A(2; 1; -1)$ và mặt phẳng $(P): x + 2y - 2z + 3 = 0$. Tính khoảng cách từ điểm $A$ đến mặt phẳng $(P)$.",
        explanation="$d(A, (P)) = \\frac{|2 + 2(1) - 2(-1) + 3|}{\\sqrt{1^2 + 2^2 + (-2)^2}} = \\frac{|2 + 2 + 2 + 3|}{\\sqrt{9}} = \\frac{9}{3} = 3$.",
        short_answer_key="3", tolerance=0.0,
        source_reference="Đề tham khảo Định dạng mới 2025 - Phần III", status="APPROVED", difficulty_p=0.80, discrimination_d=0.30,
    )
    questions_to_add.append(q27)

    # Q28: SHORT_ANSWER - APPLICATION (Tích phân tính diện tích)
    q28 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_gt_ds.id, topic_id=top_tichphan.id,
        lesson_id=les_tichphan.id, learning_outcome_id=yccd_gt_07.id, problem_archetype_id=pa_gt07_d1.id,
        cognitive_level="APPLICATION", question_type="SHORT_ANSWER",
        stem="Một vật chuyển động với vận tốc $v(t) = 3t^2 + 2t\\text{ (m/s)}$. Quãng đường vật đi được trong khoảng thời gian từ $t = 0\\text{ s}$ đến $t = 3\\text{ s}$ bằng bao nhiêu mét?",
        explanation="Quãng đường $s = \\int_{0}^{3} v(t) dt = \\int_{0}^{3} (3t^2 + 2t) dt = \\left[ t^3 + t^2 \\right]_{0}^{3} = 3^3 + 3^2 = 27 + 9 = 36\\text{ m}$.",
        short_answer_key="36", tolerance=0.0,
        source_reference="Toán thực tiễn Vật lí 12", status="APPROVED", difficulty_p=0.68, discrimination_d=0.40,
    )
    questions_to_add.append(q28)

    # Q29: SHORT_ANSWER - APPLICATION (Xác suất toàn phần Bayes)
    q29 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_tk_xs.id, topic_id=top_xacsuat.id,
        lesson_id=les_bayes.id, learning_outcome_id=yccd_tk_02.id, problem_archetype_id=pa_tk02_d1.id,
        cognitive_level="APPLICATION", question_type="SHORT_ANSWER",
        stem="Tại một nhà máy lắp ráp, phân xưởng I sản xuất $70\\%$ số lượng sản phẩm, phân xưởng II sản xuất $30\\%$. Tỉ lệ phế phẩm của phân xưởng I là $1\\%$, của phân xưởng II là $2\\%$. Lấy ngẫu nhiên một sản phẩm thì thấy là phế phẩm. Tính xác suất để sản phẩm đó do phân xưởng I sản xuất (viết kết quả dưới dạng số thập phân làm tròn đến hàng phần trăm).",
        explanation="Gọi $A_1, A_2$ là sản phẩm do xưởng I, II; $B$ là phế phẩm. $P(B) = 0.7 \\times 0.01 + 0.3 \\times 0.02 = 0.007 + 0.006 = 0.013$. $P(A_1|B) = \\frac{0.007}{0.013} = \\frac{7}{13} \\approx 0.54$.",
        short_answer_key="0.54", tolerance=0.01,
        source_reference="Đề kiểm tra Khảo sát Toán 12 năm 2025", status="APPROVED", difficulty_p=0.45, discrimination_d=0.48,
    )
    questions_to_add.append(q29)

    # ==============================================================================
    # PASSAGE GROUP (CÂU HỎI CHÙM NGỮ LIỆU) & SUB-QUESTIONS
    # ==============================================================================
    # Q30: PASSAGE_GROUP Parent (Ngữ liệu chung: Mô hình tăng trưởng dân số)
    q30_parent = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_gt_ds.id, topic_id=top_daoham.id,
        lesson_id=les_dondieu.id, learning_outcome_id=yccd_gt_01.id, problem_archetype_id=pa_gt01_d1.id,
        cognitive_level="COMPREHENSION", question_type="PASSAGE_GROUP",
        stem="**Ngữ liệu đọc hiểu chung cho Câu 30.1 và Câu 30.2:**\n\nSự tăng trưởng của một quần thể vi khuẩn trong phòng thí nghiệm tuân theo mô hình hàm mũ $N(t) = N_0 \\cdot e^{kt}$, trong đó $N_0$ là số lượng vi khuẩn ban đầu, $t$ là thời gian tính bằng giờ, và $k$ là hằng số tăng trưởng. Biết rằng ban đầu có $N_0 = 1000$ con vi khuẩn và sau $2$ giờ số lượng vi khuẩn tăng lên thành $4000$ con.",
        explanation="Từ giả thiết $N(2) = 1000 e^{2k} = 4000 \\iff e^{2k} = 4 \\iff 2k = \\ln 4 = 2\\ln 2 \\iff k = \\ln 2$. Khi đó $N(t) = 1000 \\cdot 2^t$.",
        source_reference="Đề Khảo sát THPT 2025 - Câu hỏi chùm", status="APPROVED", difficulty_p=0.60, discrimination_d=0.40,
    )
    db.add(q30_parent)
    db.flush()

    # Sub-question 30.1
    q30_sub1 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_gt_ds.id, topic_id=top_daoham.id,
        lesson_id=les_dondieu.id, learning_outcome_id=yccd_gt_01.id, problem_archetype_id=pa_gt01_d1.id,
        parent_id=q30_parent.id, cognitive_level="COMPREHENSION", question_type="SINGLE_CHOICE",
        stem="Tìm hằng số tăng trưởng $k$ của quần thể vi khuẩn.",
        explanation="$k = \\ln 2 \\approx 0.693$.",
        source_reference="Đề Khảo sát THPT 2025 - Câu 30.1", status="APPROVED", difficulty_p=0.65, discrimination_d=0.35, order_index=1,
    )
    q30_sub1.options = [
        QuestionOption(label="A", content="$k = \\ln 2$", is_correct=True, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="$k = 2\\ln 2$", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="$k = \\frac{\\ln 2}{2}$", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="$k = 2$", is_correct=False, is_fixed=False, order_index=4),
    ]
    questions_to_add.append(q30_sub1)

    # Sub-question 30.2
    q30_sub2 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_gt_ds.id, topic_id=top_daoham.id,
        lesson_id=les_dondieu.id, learning_outcome_id=yccd_gt_01.id, problem_archetype_id=pa_gt01_d1.id,
        parent_id=q30_parent.id, cognitive_level="APPLICATION", question_type="SINGLE_CHOICE",
        stem="Sau bao nhiêu giờ kể từ thời điểm ban đầu, số lượng vi khuẩn sẽ đạt $32\\,000$ con?",
        explanation="Phương trình $1000 \\cdot 2^t = 32000 \\iff 2^t = 32 = 2^5 \\iff t = 5\\text{ giờ}$.",
        source_reference="Đề Khảo sát THPT 2025 - Câu 30.2", status="APPROVED", difficulty_p=0.70, discrimination_d=0.38, order_index=2,
    )
    q30_sub2.options = [
        QuestionOption(label="A", content="$5$ giờ", is_correct=True, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="$4$ giờ", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="$6$ giờ", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="$8$ giờ", is_correct=False, is_fixed=False, order_index=4),
    ]
    questions_to_add.append(q30_sub2)

    # ==============================================================================
    # ESSAY QUESTION (CÂU HỎI TỰ LUẬN KÈM RUBRIC CHẤM ĐIỂM)
    # ==============================================================================
    q31_essay = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_th_tn.id, topic_id=top_thuchanh.id,
        lesson_id=les_toiuu.id, learning_outcome_id=yccd_th_01.id, problem_archetype_id=pa_th01_d1.id,
        cognitive_level="APPLICATION", question_type="ESSAY",
        stem="**Bài toán thiết kế tối ưu đường ống dẫn dầu:**\n\nMột giàn khoan dầu khí trên biển đặt tại vị trí $A$ cách bờ biển thẳng một khoảng $d_1 = 6\\text{ km}$. Nhà máy lọc dầu đặt tại vị trí $B$ nằm trên bờ biển, cách hình chiếu vuông góc $H$ của $A$ trên bờ biển một khoảng $d_2 = 10\\text{ km}$. Chi phí lắp đặt mỗi kilômét đường ống ngầm dưới biển là $50\\,000$ USD, và chi phí lắp đặt mỗi kilômét đường ống trên đất liền là $30\\,000$ USD. Kỹ sư cần chọn một vị trí $P$ trên bờ biển (nằm giữa $H$ và $B$) để nối đường ống ngầm từ $A$ đến $P$, rồi từ $P$ nối đường ống trên cạn đến $B$ sao cho tổng chi phí lắp đặt là nhỏ nhất. Hãy xác định khoảng cách $HP$ và tính tổng chi phí nhỏ nhất đó.",
        explanation="Đặt $HP = x\\text{ km}$ ($0 \\le x \\le 10$). Chiều dài ống biển $AP = \\sqrt{6^2 + x^2} = \\sqrt{x^2 + 36}$. Chiều dài ống trên cạn $PB = 10 - x$. Hàm chi phí: $C(x) = 50\\sqrt{x^2 + 36} + 30(10 - x)$ (nghìn USD). Đạo hàm $C'(x) = \\frac{50x}{\\sqrt{x^2 + 36}} - 30 = 0 \\iff 5x = 3\\sqrt{x^2 + 36} \\iff 25x^2 = 9(x^2 + 36) \\iff 16x^2 = 324 \\iff x = 4.5\\text{ km}$. Khi đó chi phí cực tiểu là $C(4.5) = 50\\sqrt{4.5^2 + 36} + 30(10 - 4.5) = 50(7.5) + 30(5.5) = 375 + 165 = 540$ nghìn USD.",
        rubric={
            "criteria": [
                {"name": "Mô hình hoá và thiết lập ẩn số", "points": 0.5, "desc": "Đặt ẩn x = HP, tìm tập xác định [0; 10], biểu diễn độ dài AP và PB"},
                {"name": "Thiết lập hàm chi phí C(x)", "points": 0.5, "desc": "Thiết lập đúng hàm số C(x) = 50*sqrt(x^2+36) + 30*(10-x)"},
                {"name": "Khảo sát và tìm cực tiểu", "points": 0.5, "desc": "Tính đúng đạo hàm C'(x), giải phương trình C'(x) = 0 ra x = 4.5"},
                {"name": "Kết luận thực tế", "points": 0.5, "desc": "Kết luận HP = 4.5 km và chi phí tối thiểu 540.000 USD"}
            ],
            "max_score": 2.0
        },
        source_reference="Bài toán tối ưu hoá thực tế - Sách chuyên đề Toán 12", status="APPROVED", difficulty_p=0.35, discrimination_d=0.55,
    )
    questions_to_add.append(q31_essay)

    # Q32: SINGLE_CHOICE - APPLICATION (Thể tích khối tròn xoay quanh trục Ox)
    q32 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_gt_ds.id, topic_id=top_tichphan.id,
        lesson_id=les_tichphan.id, learning_outcome_id=yccd_gt_07.id, problem_archetype_id=pa_gt07_d1.id,
        cognitive_level="APPLICATION", question_type="SINGLE_CHOICE",
        stem="Cho hình phẳng $(H)$ giới hạn bởi đồ thị hàm số $y = \\sqrt{x}$, trục hoành và hai đường thẳng $x = 0, x = 4$. Thể tích $V$ của khối tròn xoay sinh ra khi quay hình phẳng $(H)$ quanh trục hoành $Ox$ bằng:",
        explanation="Công thức thể tích tròn xoay: $V = \\pi \\int_{0}^{4} [f(x)]^2 dx = \\pi \\int_{0}^{4} (\\sqrt{x})^2 dx = \\pi \\int_{0}^{4} x dx = \\pi \\left[ \\frac{x^2}{2} \\right]_{0}^{4} = 8\\pi$.",
        source_reference="Đề kiểm tra Định kỳ Toán 12", status="APPROVED", difficulty_p=0.75, discrimination_d=0.35,
    )
    q32.options = [
        QuestionOption(label="A", content="$V = 8\\pi$", is_correct=True, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="$V = 16\\pi$", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="$V = \\frac{16\\pi}{3}$", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="$V = 4\\pi$", is_correct=False, is_fixed=False, order_index=4),
    ]
    questions_to_add.append(q32)

    # Q33: SINGLE_CHOICE - RECOGNITION (Tập xác định của logarit)
    q33 = Question(
        subject_id=sub_math.id, grade_id=g12.id, strand_id=strand_gt_ds.id, topic_id=top_daoham.id,
        lesson_id=les_dondieu.id, learning_outcome_id=yccd_gt_01.id, problem_archetype_id=pa_gt01_d1.id,
        cognitive_level="RECOGNITION", question_type="SINGLE_CHOICE",
        stem="Tìm tập nghiệm $S$ của phương trình $\\log_2(x - 1) = 3$.",
        explanation="Điều kiện $x > 1$. Phương trình tương đương $x - 1 = 2^3 = 8 \\iff x = 9$. Vậy $S = \\{9\\}$.",
        source_reference="Đề kiểm tra khảo sát 2025", status="APPROVED", difficulty_p=0.93, discrimination_d=0.20,
    )
    q33.options = [
        QuestionOption(label="A", content="$S = \\{9\\}$", is_correct=True, is_fixed=False, order_index=1),
        QuestionOption(label="B", content="$S = \\{7\\}$", is_correct=False, is_fixed=False, order_index=2),
        QuestionOption(label="C", content="$S = \\{8\\}$", is_correct=False, is_fixed=False, order_index=3),
        QuestionOption(label="D", content="$S = \\{10\\}$", is_correct=False, is_fixed=False, order_index=4),
    ]
    questions_to_add.append(q33)

    # Commit all questions to DB
    db.add_all(questions_to_add)
    db.flush()

    # ==============================================================================
    # 9. EXAM MATRIX & BLUEPRINT (ĐỊNH DẠNG ĐỀ THI 2025 - QĐ 764/QĐ-BGDĐT)
    # ==============================================================================
    exam_matrix = ExamMatrix(
        title="Ma trận Đề kiểm tra Cuối kì 1 Toán 12 - Chuẩn Định dạng 2025",
        subject_id=sub_math.id,
        grade_id=g12.id,
        description="Ma trận đánh giá chuẩn năng lực và YCCĐ Thông tư 32/2018/TT-BGDĐT",
        duration_minutes=90,
        total_points=10.0,
    )
    db.add(exam_matrix)
    db.flush()

    # Matrix items covering Parts I, II, III
    matrix_items = [
        # Phần I: Trắc nghiệm 4 lựa chọn (12 câu x 0.25 = 3.0 điểm)
        ExamMatrixItem(matrix_id=exam_matrix.id, learning_outcome_id=yccd_gt_01.id, problem_archetype_id=pa_gt01_d1.id, cognitive_level="RECOGNITION", question_type="SINGLE_CHOICE", quantity=2, points_per_item=0.25, section_number=1, order_index=1),
        ExamMatrixItem(matrix_id=exam_matrix.id, learning_outcome_id=yccd_gt_03.id, problem_archetype_id=pa_gt03_d1.id, cognitive_level="RECOGNITION", question_type="SINGLE_CHOICE", quantity=2, points_per_item=0.25, section_number=1, order_index=2),
        ExamMatrixItem(matrix_id=exam_matrix.id, learning_outcome_id=yccd_gt_05.id, problem_archetype_id=pa_gt05_d1.id, cognitive_level="RECOGNITION", question_type="SINGLE_CHOICE", quantity=2, points_per_item=0.25, section_number=1, order_index=3),
        ExamMatrixItem(matrix_id=exam_matrix.id, learning_outcome_id=yccd_hh_01.id, problem_archetype_id=pa_hh01_d1.id, cognitive_level="RECOGNITION", question_type="SINGLE_CHOICE", quantity=2, points_per_item=0.25, section_number=1, order_index=4),
        ExamMatrixItem(matrix_id=exam_matrix.id, learning_outcome_id=yccd_hh_02.id, problem_archetype_id=pa_hh02_d1.id, cognitive_level="COMPREHENSION", question_type="SINGLE_CHOICE", quantity=2, points_per_item=0.25, section_number=1, order_index=5),
        ExamMatrixItem(matrix_id=exam_matrix.id, learning_outcome_id=yccd_tk_01.id, problem_archetype_id=pa_tk01_d1.id, cognitive_level="COMPREHENSION", question_type="SINGLE_CHOICE", quantity=2, points_per_item=0.25, section_number=1, order_index=6),

        # Phần II: Trắc nghiệm Đúng/Sai 4 ý (4 câu x 1.0 = 4.0 điểm)
        ExamMatrixItem(matrix_id=exam_matrix.id, learning_outcome_id=yccd_gt_01.id, problem_archetype_id=pa_gt01_d1.id, cognitive_level="COMPREHENSION", question_type="TRUE_FALSE_GROUP", quantity=1, points_per_item=1.0, section_number=2, order_index=7),
        ExamMatrixItem(matrix_id=exam_matrix.id, learning_outcome_id=yccd_hh_02.id, problem_archetype_id=pa_hh02_d1.id, cognitive_level="APPLICATION", question_type="TRUE_FALSE_GROUP", quantity=1, points_per_item=1.0, section_number=2, order_index=8),
        ExamMatrixItem(matrix_id=exam_matrix.id, learning_outcome_id=yccd_tk_01.id, problem_archetype_id=pa_tk01_d1.id, cognitive_level="COMPREHENSION", question_type="TRUE_FALSE_GROUP", quantity=1, points_per_item=1.0, section_number=2, order_index=9),
        ExamMatrixItem(matrix_id=exam_matrix.id, learning_outcome_id=yccd_th_01.id, problem_archetype_id=pa_th01_d1.id, cognitive_level="APPLICATION", question_type="TRUE_FALSE_GROUP", quantity=1, points_per_item=1.0, section_number=2, order_index=10),

        # Phần III: Trắc nghiệm trả lời ngắn (6 câu x 0.5 = 3.0 điểm)
        ExamMatrixItem(matrix_id=exam_matrix.id, learning_outcome_id=yccd_gt_02.id, problem_archetype_id=pa_gt02_d1.id, cognitive_level="APPLICATION", question_type="SHORT_ANSWER", quantity=2, points_per_item=0.5, section_number=3, order_index=11),
        ExamMatrixItem(matrix_id=exam_matrix.id, learning_outcome_id=yccd_gt_07.id, problem_archetype_id=pa_gt07_d1.id, cognitive_level="APPLICATION", question_type="SHORT_ANSWER", quantity=2, points_per_item=0.5, section_number=3, order_index=12),
        ExamMatrixItem(matrix_id=exam_matrix.id, learning_outcome_id=yccd_tk_02.id, problem_archetype_id=pa_tk02_d1.id, cognitive_level="APPLICATION", question_type="SHORT_ANSWER", quantity=2, points_per_item=0.5, section_number=3, order_index=13),
    ]
    db.add_all(matrix_items)
    db.flush()

    # ==============================================================================
    # 10. MASTER EXAM & SHUFFLED EXAM VARIANTS (MÃ ĐỀ 101, 102)
    # ==============================================================================
    master_exam = MasterExam(
        matrix_id=exam_matrix.id,
        title="Đề thi Gốc Kỳ thi Tốt nghiệp THPT 2025 - Môn Toán (Mã Gốc)",
        subject_id=sub_math.id,
        grade_id=g12.id,
        total_questions=10,
        total_points=10.0,
        duration_minutes=90,
        status="APPROVED",
    )
    db.add(master_exam)
    db.flush()

    selected_questions = [
        (q01, 1, 1, 0.25),
        (q02, 1, 2, 0.25),
        (q03, 1, 3, 0.25),
        (q04, 1, 4, 0.25),
        (q19, 2, 5, 1.00),
        (q20, 2, 6, 1.00),
        (q22, 2, 7, 1.00),
        (q26, 3, 8, 0.50),
        (q27, 3, 9, 0.50),
        (q28, 3, 10, 0.50),
    ]

    master_items = []
    for q, sec, num, pts in selected_questions:
        m_item = MasterExamItem(
            master_exam_id=master_exam.id,
            question_id=q.id,
            section_number=sec,
            question_number=num,
            points=pts,
        )
        master_items.append(m_item)
    db.add_all(master_items)
    db.flush()

    # Create 2 Shuffled Exam Variants: Mã 101 & Mã 102
    v101 = ExamVariant(master_exam_id=master_exam.id, variant_code="101")
    v102 = ExamVariant(master_exam_id=master_exam.id, variant_code="102")
    db.add_all([v101, v102])
    db.flush()

    # Variant 101 Items
    for i, (q, sec, orig_num, pts) in enumerate(selected_questions, start=1):
        v101_item = ExamVariantItem(
            variant_id=v101.id,
            question_id=q.id,
            section_number=sec,
            question_number=i,
            original_question_number=orig_num,
            option_mapping={"A": "A", "B": "B", "C": "C", "D": "D"} if q.question_type == "SINGLE_CHOICE" else None,
            answer_key="A" if q.question_type == "SINGLE_CHOICE" and q.options and q.options[0].is_correct else "D" if q.id == q02.id else None,
        )
        db.add(v101_item)

    # Variant 102 Items (Safe shuffling: options shuffled while respecting RULE-02 is_fixed)
    for i, (q, sec, orig_num, pts) in enumerate(selected_questions, start=1):
        # In Q02 and Q03, option D has is_fixed=True ("Không có giá trị", "Cả A và B"), so D stays D!
        opt_map = None
        if q.question_type == "SINGLE_CHOICE":
            if q.id in (q02.id, q03.id):
                opt_map = {"A": "B", "B": "C", "C": "A", "D": "D"}  # D is locked!
            else:
                opt_map = {"A": "B", "B": "A", "C": "D", "D": "C"}

        v102_item = ExamVariantItem(
            variant_id=v102.id,
            question_id=q.id,
            section_number=sec,
            question_number=i,
            original_question_number=orig_num,
            option_mapping=opt_map,
            answer_key="B" if q.id == q01.id else "D" if q.id == q02.id else None,
        )
        db.add(v102_item)

    # ==============================================================================
    # 11. SAMPLE AI DIGITIZATION JOB (HITL REVIEW TESTING)
    # ==============================================================================
    sample_job = AIDigitizeJob(
        filename="De_Khao_Sat_Toan_12_2025.docx",
        file_path="storage/uploads/sample_user/sample_job/De_Khao_Sat_Toan_12_2025.docx",
        file_type=".docx",
        subject_id=sub_math.id,
        grade_id=g12.id,
        status="COMPLETED",
        confidence_score=96.5,
        extracted_json=[
            {
                "stem": "Cho hàm số $y = x^3 - 3x + 1$. Điểm cực đại của đồ thị hàm số là:",
                "question_type": "SINGLE_CHOICE",
                "cognitive_level": "RECOGNITION",
                "options": [
                    {"label": "A", "content": "$(-1; 3)$", "is_correct": True, "is_fixed": False},
                    {"label": "B", "content": "$(1; -1)$", "is_correct": False, "is_fixed": False},
                    {"label": "C", "content": "$(0; 1)$", "is_correct": False, "is_fixed": False},
                    {"label": "D", "content": "$(2; 3)$", "is_correct": False, "is_fixed": False},
                ],
                "confidence_score": 98.0,
            }
        ],
    )
    db.add(sample_job)

    db.commit()
    logger.info("Database seeding completed successfully with all Circular 32 entities, questions, and variants.")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_database(db, force_reset=True)
        print("Successfully seeded Quesy database with Circular 32 Grade 12 Math data!")
    finally:
        db.close()

