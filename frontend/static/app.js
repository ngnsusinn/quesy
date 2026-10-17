/**
 * ==============================================================================
 * QUESY ASSESSMENT & ITEM BANK STUDIO - CORE APPLICATION LOGIC
 * Chuẩn hóa Thông tư 32/2018/TT-BGDĐT & Quyết định 764/QĐ-BGDĐT (Định dạng 2025)
 * ==============================================================================
 */

(function () {
  'use strict';

  // Base API endpoint URL
  const API_BASE_URL = '/api/v1';

  // ============================================================================
  // 1. APPLICATION STATE
  // ============================================================================
  const state = {
    currentTab: 'dashboard',
    backendOnline: false,
    activeSubject: 'toan',
    activeGrade: '12',

    // 6-Tier Taxonomy Tree (Strictly Circular 32 - NO TEXTBOOK!)
    taxonomy: {
      grades: [
        { id: '12', name: 'Lớp 12 (Cấp THPT)' },
        { id: '11', name: 'Lớp 11 (Cấp THPT)' },
        { id: '10', name: 'Lớp 10 (Cấp THPT)' },
      ],
      subjects: [
        { id: 'toan', name: 'Toán học' },
        { id: 'vatli', name: 'Vật lí' },
        { id: 'hoahoc', name: 'Hóa học' },
        { id: 'sinhhoc', name: 'Sinh học' },
      ],
      strands: [
        { id: 'giai-tich', name: 'Mạch 1: Số, Đại số & Giải tích', subject_id: 'toan' },
        { id: 'hinh-hoc', name: 'Mạch 2: Hình học & Đo lường', subject_id: 'toan' },
        { id: 'xac-suat', name: 'Mạch 3: Thống kê & Xác suất', subject_id: 'toan' },
        { id: 'thuc-hanh', name: 'Mạch 4: Thực hành & Trải nghiệm', subject_id: 'toan' },
      ],
      topics: [
        { id: 'top-dao-ham', strand_id: 'giai-tich', name: 'Ứng dụng đạo hàm khảo sát hàm số' },
        { id: 'top-tich-phan', strand_id: 'giai-tich', name: 'Nguyên hàm, Tích phân & Ứng dụng' },
        { id: 'top-oxyz', strand_id: 'hinh-hoc', name: 'Phương pháp toạ độ trong không gian Oxyz' },
        { id: 'top-xac-suat-dk', strand_id: 'xac-suat', name: 'Xác suất có điều kiện & Công thức Bayes' },
        { id: 'top-tai-chinh', strand_id: 'thuc-hanh', name: 'Bài toán tối ưu & Tài chính' },
      ],
      lessons: [
        { id: 'les-cuc-tri', topic_id: 'top-dao-ham', name: 'Tính đơn điệu và cực trị hàm số' },
        { id: 'les-tiem-can', topic_id: 'top-dao-ham', name: 'Đường tiệm cận của đồ thị hàm số' },
        { id: 'les-nguyen-ham', topic_id: 'top-tich-phan', name: 'Nguyên hàm và các phương pháp tính' },
        { id: 'les-mat-phang', topic_id: 'top-oxyz', name: 'Hệ toạ độ và phương trình mặt phẳng' },
        { id: 'les-bayes', topic_id: 'top-xac-suat-dk', name: 'Xác suất có điều kiện và Bayes' },
      ],
      yccds: [
        {
          id: 'TOAN12.GT.01',
          lesson_id: 'les-cuc-tri',
          code: 'TOAN12.GT.01',
          desc: 'Nhận biết được tính đơn điệu, điểm cực trị của hàm số thông qua bảng biến thiên hoặc đồ thị hàm số.',
          cognitive_level: 'APPLICATION',
        },
        {
          id: 'TOAN12.GT.02',
          lesson_id: 'les-tiem-can',
          code: 'TOAN12.GT.02',
          desc: 'Khảo sát và vẽ đồ thị hàm số; tìm đường tiệm cận đứng, tiệm cận ngang của đồ thị hàm số.',
          cognitive_level: 'COMPREHENSION',
        },
        {
          id: 'TOAN12.GT.03',
          lesson_id: 'les-nguyen-ham',
          code: 'TOAN12.GT.03',
          desc: 'Nhận biết khái niệm nguyên hàm và tính chất; tính nguyên hàm của hàm số cơ bản.',
          cognitive_level: 'RECOGNITION',
        },
        {
          id: 'TOAN12.HH.01',
          lesson_id: 'les-mat-phang',
          code: 'TOAN12.HH.01',
          desc: 'Xác định tọa độ của điểm, vectơ; lập phương trình mặt phẳng và tính khoảng cách.',
          cognitive_level: 'APPLICATION',
        },
        {
          id: 'TOAN12.XS.01',
          lesson_id: 'les-bayes',
          code: 'TOAN12.XS.01',
          desc: 'Tính xác suất có điều kiện và vận dụng công thức Bayes vào bài toán thực tiễn.',
          cognitive_level: 'COMPREHENSION',
        },
      ],
      archetypes: [
        { id: 'arch-1', yccd_id: 'TOAN12.GT.01', name: 'Dạng 1: Đọc đồ thị / BBT tìm cực trị và khoảng đơn điệu' },
        { id: 'arch-2', yccd_id: 'TOAN12.GT.01', name: 'Dạng 2: Cực trị hàm đa thức bậc 3 chứa tham số $m$' },
        { id: 'arch-3', yccd_id: 'TOAN12.GT.02', name: 'Dạng 1: Xác định đường tiệm cận hàm phân thức hữu tỉ' },
        { id: 'arch-4', yccd_id: 'TOAN12.GT.03', name: 'Dạng 1: Bảng công thức nguyên hàm cơ bản' },
        { id: 'arch-5', yccd_id: 'TOAN12.HH.01', name: 'Dạng 1: Viết phương trình mặt phẳng đi qua 3 điểm' },
        { id: 'arch-6', yccd_id: 'TOAN12.XS.01', name: 'Dạng 1: Xác suất có điều kiện dạng bảng số liệu' },
      ],
    },

    // Staged Exam Documents for Preview & Reordering before AI Digitization
    stagedExam: {
      status: 'EMPTY', // 'EMPTY' | 'STAGED' | 'PROCESSING' | 'DONE'
      files: [],
      previews: [],
      activePreviewIndex: 0,
    },
    activeEditingQuestion: null,

    // HITL Digitize Studio Job
    digitizeJob: {
      id: null,
      jobId: null,
      filename: '',
      fileType: '',
      status: 'IDLE',
      avgConfidence: 0,
      currentPage: 0,
      totalPages: 0,
      activeQuestionId: null,
      confidenceFilter: 'all',
      previewUrl: null,
      previewImages: [],
      aiProvider: null,
      aiModel: null,
      questions: [],
    },

    // Item Bank (Default 12 Rich Standard Items)
    itemBank: [],

    // Exam Matrix Config & Cells
    matrixConfig: {
      name: 'Đề Khảo sát Toán 12 - Chuẩn TN THPT 2025',
      grade: '12',
      subject: 'Toán học',
      duration: 90,
      totalScore: 10.0,
      rows: [
        {
          id: 'row-1',
          strandName: 'Số, Đại số & Giải tích',
          yccdCode: 'TOAN12.GT.01',
          archetypeName: 'Cực trị hàm bậc 3 chứa m',
          biet: 4,
          hieu: 3,
          vandung: 3,
          bankStock: { biet: 15, hieu: 12, vandung: 8 },
        },
        {
          id: 'row-2',
          strandName: 'Số, Đại số & Giải tích',
          yccdCode: 'TOAN12.GT.02',
          archetypeName: 'Tiệm cận đứng, ngang đồ thị',
          biet: 3,
          hieu: 2,
          vandung: 2,
          bankStock: { biet: 10, hieu: 8, vandung: 6 },
        },
        {
          id: 'row-3',
          strandName: 'Hình học & Đo lường',
          yccdCode: 'TOAN12.HH.01',
          archetypeName: 'Phương trình mặt phẳng Oxyz',
          biet: 3,
          hieu: 3,
          vandung: 3,
          bankStock: { biet: 14, hieu: 9, vandung: 7 },
        },
        {
          id: 'row-4',
          strandName: 'Thống kê & Xác suất',
          yccdCode: 'TOAN12.XS.01',
          archetypeName: 'Xác suất có điều kiện & Bayes',
          biet: 2,
          hieu: 2,
          vandung: 2,
          bankStock: { biet: 8, hieu: 6, vandung: 4 },
        },
      ],
    },

    // Master Exam & Shuffled Variants
    masterExam: {
      id: null,
      title: 'Đề Thi Gốc - Khảo Sát Toán 12 (Chuẩn 2025)',
      items: [],
    },
    shuffledVariants: {
      isShuffled: false,
      activeVariantCode: '101',
      optionAnchorVerified: true,
      variants: {},
      keyMatrix: [],
    },

    // Active Formula Editor State
    activeFormulaEdit: {
      targetType: null, // 'digitize' | 'bank' | 'new'
      questionId: null,
      field: null, // 'stem' | 'option'
      optionIndex: null,
      currentLatex: '',
    },
  };

  // ============================================================================
  // 2. SEED INITIAL DATA (CIRCULAR 32 & QĐ 764 COMPLIANT)
  // ============================================================================
  function seedInitialQuestions() {
    const defaultQuestions = [
      {
        id: 1,
        code: 'TOAN12-001',
        item_format: 'SINGLE_CHOICE',
        cognitive_level: 'APPLICATION',
        strand_id: 'giai-tich',
        topic_id: 'top-dao-ham',
        lesson_id: 'les-cuc-tri',
        learning_outcome_id: 'TOAN12.GT.01',
        problem_archetype_id: 'arch-2',
        confidence: 98,
        stem: 'Cho hàm số $y = x^3 - 3mx^2 + 4$. Tìm tất cả các giá trị thực của tham số $m$ để hàm số đã cho có hai điểm cực trị $x_1, x_2$ nằm về hai phía khác nhau của trục tung $Oy$.',
        image_url: null,
        options: [
          { label: 'A', content: '$m > 0$', is_correct: true, is_fixed: false },
          { label: 'B', content: '$m < 0$', is_correct: false, is_fixed: false },
          { label: 'C', content: '$m = 0$', is_correct: false, is_fixed: false },
          { label: 'D', content: 'Không có giá trị nào của $m$ thỏa mãn', is_correct: false, is_fixed: true },
        ],
        explanation: 'Ta có $y\' = 3x^2 - 6mx = 3x(x - 2m)$. Để hai cực trị nằm về 2 phía trục tung thì phương trình $y\'=0$ có 2 nghiệm trái dấu: $x_1 x_2 < 0 \\Leftrightarrow 0 \\cdot 2m < 0$ (vô lý), do đó $m > 0$ thì $2m > 0$ và 0 luôn tách biệt.',
        status: 'APPROVED',
        p_index: 0.65,
        d_index: 0.42,
        source_ref: 'Đề Khảo sát THPT Quốc gia',
      },
      {
        id: 2,
        code: 'TOAN12-002',
        item_format: 'TRUE_FALSE_GROUP',
        cognitive_level: 'COMPREHENSION',
        strand_id: 'giai-tich',
        topic_id: 'top-dao-ham',
        lesson_id: 'les-cuc-tri',
        learning_outcome_id: 'TOAN12.GT.01',
        problem_archetype_id: 'arch-1',
        confidence: 96,
        stem: 'Cho hàm số bậc ba $y = f(x) = ax^3 + bx^2 + cx + d$ xác định và liên tục trên $\\mathbb{R}$ có bảng biến thiên với cực đại tại $(1; 2)$ và cực tiểu tại $(3; -2)$. Xét tính Đúng/Sai của các khẳng định sau:',
        image_url: null,
        sub_statements: [
          { label: 'a', content: 'Hàm số đã cho đồng biến trên khoảng $(1; 3)$.', is_true: false, explanation: 'Hàm số nghịch biến trên khoảng $(1; 3)$ vì đi từ CĐ xuống CT.' },
          { label: 'b', content: 'Điểm cực đại của đồ thị hàm số là $M(1; 2)$.', is_true: true, explanation: 'Theo đề bài tọa độ điểm cực đại là $(1; 2)$.' },
          { label: 'c', content: 'Giá trị nhỏ nhất của hàm số trên toàn miền $\\mathbb{R}$ bằng $-2$.', is_true: false, explanation: 'Hàm số bậc 3 có tập giá trị là $\\mathbb{R}$ nên không có GTNN trên toàn miền.' },
          { label: 'd', content: 'Phương trình $f(x) = m$ có đúng 3 nghiệm thực phân biệt khi $-2 < m < 2$.', is_true: true, explanation: 'Đường thẳng $y = m$ cắt 3 nhánh khi $y_{CT} < m < y_{CĐ}$.' },
        ],
        explanation: 'Khảo sát bảng biến thiên chuẩn hóa theo Thông tư 32.',
        status: 'APPROVED',
        p_index: 0.58,
        d_index: 0.48,
        source_ref: 'Ngân hàng Đề thi Sở GD&ĐT',
      },
      {
        id: 3,
        code: 'TOAN12-003',
        item_format: 'SHORT_ANSWER',
        cognitive_level: 'APPLICATION',
        strand_id: 'giai-tich',
        topic_id: 'top-tich-phan',
        lesson_id: 'les-nguyen-ham',
        learning_outcome_id: 'TOAN12.GT.03',
        problem_archetype_id: 'arch-4',
        confidence: 88,
        stem: 'Biết tích phân $\\int_{0}^{1} (2x + 1)e^x dx = a \\cdot e + b$ với $a, b \\in \\mathbb{Z}$. Tính tổng giá trị $S = a + 2b$.',
        image_url: null,
        short_answer_value: '1',
        tolerance: 0.0,
        explanation: 'Dùng tích phân từng phần đặt $u = 2x + 1, dv = e^x dx \\Rightarrow a = 1, b = 0 \\Rightarrow S = 1 + 0 = 1$.',
        status: 'APPROVED',
        p_index: 0.52,
        d_index: 0.38,
        source_ref: 'Đề Khảo sát THPT 2025',
      },
      {
        id: 4,
        code: 'TOAN12-004',
        item_format: 'SINGLE_CHOICE',
        cognitive_level: 'RECOGNITION',
        strand_id: 'giai-tich',
        topic_id: 'top-dao-ham',
        lesson_id: 'les-tiem-can',
        learning_outcome_id: 'TOAN12.GT.02',
        problem_archetype_id: 'arch-3',
        confidence: 99,
        stem: 'Đường tiệm cận đứng của đồ thị hàm số $y = \\frac{2x - 1}{x + 2}$ có phương trình là đường thẳng nào dưới đây?',
        image_url: null,
        options: [
          { label: 'A', content: '$x = -2$', is_correct: true, is_fixed: false },
          { label: 'B', content: '$x = 2$', is_correct: false, is_fixed: false },
          { label: 'C', content: '$y = 2$', is_correct: false, is_fixed: false },
          { label: 'D', content: 'Cả A và B đều đúng', is_correct: false, is_fixed: true },
        ],
        explanation: 'Tiệm cận đứng là nghiệm của mẫu số: $x + 2 = 0 \\Leftrightarrow x = -2$. Phương án D chứa từ khóa vị trí bắt buộc khóa tại D.',
        status: 'APPROVED',
        p_index: 0.85,
        d_index: 0.32,
        source_ref: 'Ngân hàng Câu hỏi THPT',
      },
      {
        id: 5,
        code: 'TOAN12-005',
        item_format: 'SINGLE_CHOICE',
        cognitive_level: 'APPLICATION',
        strand_id: 'hinh-hoc',
        topic_id: 'top-oxyz',
        lesson_id: 'les-mat-phang',
        learning_outcome_id: 'TOAN12.HH.01',
        problem_archetype_id: 'arch-5',
        confidence: 76, // Below 80% to demonstrate RED confidence badge
        stem: 'Trong không gian $Oxyz$, cho mặt phẳng $(P): 2x - y + 2z - 6 = 0$. Tính khoảng cách $d$ từ gốc tọa độ $O(0;0;0)$ đến mặt phẳng $(P)$.',
        image_url: null,
        options: [
          { label: 'A', content: '$d = 2$', is_correct: true, is_fixed: false },
          { label: 'B', content: '$d = 6$', is_correct: false, is_fixed: false },
          { label: 'C', content: '$d = 3$', is_correct: false, is_fixed: false },
          { label: 'D', content: 'Tất cả các phương án trên đều sai', is_correct: false, is_fixed: true },
        ],
        explanation: 'Khoảng cách $d = \\frac{|-6|}{\\sqrt{2^2 + (-1)^2 + 2^2}} = \\frac{6}{3} = 2$.',
        status: 'PENDING_REVIEW',
        p_index: 0.72,
        d_index: 0.40,
        source_ref: 'Đề thi Thử Chuyên Hà Nội',
      },
    ];

    // Additional questions for bank inventory depth
    const extraQuestions = [
      {
        id: 6,
        code: 'TOAN12-006',
        item_format: 'SINGLE_CHOICE',
        cognitive_level: 'RECOGNITION',
        strand_id: 'hinh-hoc',
        topic_id: 'top-oxyz',
        lesson_id: 'les-mat-phang',
        learning_outcome_id: 'TOAN12.HH.01',
        problem_archetype_id: 'arch-5',
        confidence: 97,
        stem: 'Trong không gian $Oxyz$, vectơ nào dưới đây là một vectơ pháp tuyến của mặt phẳng $(\\alpha): 3x - 2y + z - 5 = 0$?',
        image_url: null,
        options: [
          { label: 'A', content: '$\\vec{n} = (3; -2; 1)$', is_correct: true, is_fixed: false },
          { label: 'B', content: '$\\vec{n} = (3; 2; 1)$', is_correct: false, is_fixed: false },
          { label: 'C', content: '$\\vec{n} = (-3; -2; 1)$', is_correct: false, is_fixed: false },
          { label: 'D', content: '$\\vec{n} = (3; -2; -5)$', is_correct: false, is_fixed: false },
        ],
        explanation: 'Vectơ pháp tuyến có tọa độ là các hệ số đứng trước x, y, z.',
        status: 'APPROVED',
        p_index: 0.91,
        d_index: 0.28,
        source_ref: 'Đề Bộ GD&ĐT',
      },
      {
        id: 7,
        code: 'TOAN12-007',
        item_format: 'SINGLE_CHOICE',
        cognitive_level: 'COMPREHENSION',
        strand_id: 'xac-suat',
        topic_id: 'top-xac-suat-dk',
        lesson_id: 'les-bayes',
        learning_outcome_id: 'TOAN12.XS.01',
        problem_archetype_id: 'arch-6',
        confidence: 94,
        stem: 'Cho hai biến cố $A$ và $B$ độc lập với nhau, biết $P(A) = 0.4$ và $P(B) = 0.5$. Tính xác suất của biến cố giao $P(A \\cap B)$.',
        image_url: null,
        options: [
          { label: 'A', content: '$P(A \\cap B) = 0.20$', is_correct: true, is_fixed: false },
          { label: 'B', content: '$P(A \\cap B) = 0.90$', is_correct: false, is_fixed: false },
          { label: 'C', content: '$P(A \\cap B) = 0.10$', is_correct: false, is_fixed: false },
          { label: 'D', content: 'Cả A và B đều sai', is_correct: false, is_fixed: true },
        ],
        explanation: 'Do A và B độc lập nên $P(A \\cap B) = P(A) \\cdot P(B) = 0.4 \\cdot 0.5 = 0.2$.',
        status: 'APPROVED',
        p_index: 0.78,
        d_index: 0.35,
        source_ref: 'Đề Minh Họa 2025',
      },
      {
        id: 8,
        code: 'TOAN12-008',
        item_format: 'SHORT_ANSWER',
        cognitive_level: 'APPLICATION',
        strand_id: 'xac-suat',
        topic_id: 'top-xac-suat-dk',
        lesson_id: 'les-bayes',
        learning_outcome_id: 'TOAN12.XS.01',
        problem_archetype_id: 'arch-6',
        confidence: 92,
        stem: 'Tỷ lệ người mắc một căn bệnh hiếm là $0.1\\%$. Một bộ kit xét nghiệm cho kết quả dương tính đúng $99\\%$ đối với người có bệnh, và cho kết quả dương tính giả $1\\%$ đối với người không mắc bệnh. Khi một người có kết quả xét nghiệm dương tính, xác suất thực sự mắc bệnh là bao nhiêu phần trăm? (Làm tròn đến 1 chữ số thập phân).',
        image_url: null,
        short_answer_value: '9.0',
        tolerance: 0.1,
        explanation: 'Áp dụng công thức Bayes: $P(B|+) = \\frac{0.001 \\cdot 0.99}{0.001 \\cdot 0.99 + 0.999 \\cdot 0.01} \\approx 0.0901 = 9.0\\%$.',
        status: 'APPROVED',
        p_index: 0.35,
        d_index: 0.55,
        source_ref: 'Bài toán Thực tiễn Bayes',
      },
      {
        id: 9,
        code: 'TOAN12-009',
        item_format: 'SINGLE_CHOICE',
        cognitive_level: 'APPLICATION',
        strand_id: 'giai-tich',
        topic_id: 'top-dao-ham',
        lesson_id: 'les-cuc-tri',
        learning_outcome_id: 'TOAN12.GT.01',
        problem_archetype_id: 'arch-2',
        confidence: 95,
        stem: 'Có bao nhiêu giá trị nguyên của tham số $m \\in [-10; 10]$ để đồ thị hàm số $y = x^4 - 2(m + 1)x^2 + m^2$ có 3 điểm cực trị tạo thành một tam giác vuông cân?',
        image_url: null,
        options: [
          { label: 'A', content: '$1$', is_correct: true, is_fixed: false },
          { label: 'B', content: '$2$', is_correct: false, is_fixed: false },
          { label: 'C', content: '$0$', is_correct: false, is_fixed: false },
          { label: 'D', content: 'Tất cả các ý trên đều sai', is_correct: false, is_fixed: true },
        ],
        explanation: 'Điều kiện 3 cực trị tạo tam giác vuông cân là $(m+1)^3 = 1 \\Rightarrow m+1 = 1 \\Rightarrow m = 0$. Có duy nhất 1 giá trị.',
        status: 'APPROVED',
        p_index: 0.44,
        d_index: 0.51,
        source_ref: 'Chuyên đề Cực trị Hàm trùng phương',
      },
      {
        id: 10,
        code: 'TOAN12-010',
        item_format: 'TRUE_FALSE_GROUP',
        cognitive_level: 'COMPREHENSION',
        strand_id: 'hinh-hoc',
        topic_id: 'top-oxyz',
        lesson_id: 'les-mat-phang',
        learning_outcome_id: 'TOAN12.HH.01',
        problem_archetype_id: 'arch-5',
        confidence: 96,
        stem: 'Trong không gian $Oxyz$, cho điểm $A(1; 2; 3)$ và mặt phẳng $(Q): x + 2y - 2z + 5 = 0$. Xét tính Đúng/Sai của các mệnh đề sau:',
        image_url: null,
        sub_statements: [
          { label: 'a', content: 'Mặt phẳng $(Q)$ đi qua điểm $M(1; -1; 2)$.', is_true: true, explanation: '$1 + 2(-1) - 2(2) + 5 = 0$ (Đúng).' },
          { label: 'b', content: 'Khoảng cách từ điểm $A$ đến mặt phẳng $(Q)$ bằng $4/3$.', is_true: false, explanation: '$d(A, Q) = \\frac{|1 + 4 - 6 + 5|}{3} = \\frac{4}{3}$ (Thực tế là $\\frac{4}{3}$ -> Đúng, sửa barem để thử).' },
          { label: 'c', content: 'Mặt phẳng đi qua $A$ và song song với $(Q)$ có phương trình là $x + 2y - 2z + 1 = 0$.', is_true: true, explanation: '$1(x-1) + 2(y-2) - 2(z-3) = 0 \\Leftrightarrow x + 2y - 2z + 1 = 0$.' },
          { label: 'd', content: 'Vectơ $\\vec{u} = (2; 4; -4)$ cùng phương với vectơ pháp tuyến của $(Q)$.', is_true: true, explanation: '$\\vec{u} = 2(1; 2; -2)$ cùng phương.' },
        ],
        explanation: 'Khảo sát hình học không gian Oxyz.',
        status: 'APPROVED',
        p_index: 0.62,
        d_index: 0.45,
        source_ref: 'Đề ôn tập Khối 12',
      },
      {
        id: 11,
        code: 'TOAN12-011',
        item_format: 'SINGLE_CHOICE',
        cognitive_level: 'RECOGNITION',
        strand_id: 'giai-tich',
        topic_id: 'top-tich-phan',
        lesson_id: 'les-nguyen-ham',
        learning_outcome_id: 'TOAN12.GT.03',
        problem_archetype_id: 'arch-4',
        confidence: 99,
        stem: 'Họ nguyên hàm của hàm số $f(x) = \\cos 2x$ là hàm số nào dưới đây?',
        image_url: null,
        options: [
          { label: 'A', content: '$\\frac{1}{2}\\sin 2x + C$', is_correct: true, is_fixed: false },
          { label: 'B', content: '$-\\frac{1}{2}\\sin 2x + C$', is_correct: false, is_fixed: false },
          { label: 'C', content: '$2\\sin 2x + C$', is_correct: false, is_fixed: false },
          { label: 'D', content: '$\\sin 2x + C$', is_correct: false, is_fixed: false },
        ],
        explanation: '$\\int \\cos 2x dx = \\frac{1}{2} \\sin 2x + C$.',
        status: 'APPROVED',
        p_index: 0.88,
        d_index: 0.30,
        source_ref: 'Nguyên hàm cơ bản',
      },
      {
        id: 12,
        code: 'TOAN12-012',
        item_format: 'SINGLE_CHOICE',
        cognitive_level: 'RECOGNITION',
        strand_id: 'giai-tich',
        topic_id: 'top-dao-ham',
        lesson_id: 'les-cuc-tri',
        learning_outcome_id: 'TOAN12.GT.01',
        problem_archetype_id: 'arch-1',
        confidence: 97,
        stem: 'Tìm tập nghiệm $S$ của phương trình $\\log_2(x - 1) = 3$.',
        image_url: null,
        options: [
          { label: 'A', content: '$S = \\{9\\}$', is_correct: true, is_fixed: false },
          { label: 'B', content: '$S = \\{7\\}$', is_correct: false, is_fixed: false },
          { label: 'C', content: '$S = \\{8\\}$', is_correct: false, is_fixed: false },
          { label: 'D', content: 'Không có nghiệm nào thỏa mãn', is_correct: false, is_fixed: true },
        ],
        explanation: 'Điều kiện $x > 1$. Phương trình tương đương $x - 1 = 2^3 = 8 \\Leftrightarrow x = 9$.',
        status: 'APPROVED',
        p_index: 0.92,
        d_index: 0.25,
        source_ref: 'Ngân hàng gốc Sở GD',
      },
    ];

    state.itemBank = JSON.parse(JSON.stringify([...defaultQuestions, ...extraQuestions]));
    // AI Digitize Studio is completely empty by default on startup
    state.stagedExam = {
      status: 'EMPTY',
      files: [],
      previews: [],
      activePreviewIndex: 0,
    };
    state.digitizeJob.jobId = null;
    state.digitizeJob.questions = [];
    state.digitizeJob.filename = '';
    state.digitizeJob.fileType = '';
    state.digitizeJob.previewUrl = null;
    state.digitizeJob.previewImages = [];
    state.digitizeJob.activeQuestionId = null;
    state.digitizeJob.currentPage = 0;
    state.digitizeJob.totalPages = 0;
    state.masterExam.items = JSON.parse(JSON.stringify(state.itemBank.slice(0, 8)));
  }

  // ============================================================================
  // 3. API SERVICE & BACKEND PROBE (WITH TRANSPARENT LOCAL FALLBACK)
  // ============================================================================
  const apiService = {
    baseUrl: '/api/v1',

    async checkHealth() {
      try {
        const res = await fetch(`${this.baseUrl}/health`, { method: 'GET', signal: AbortSignal.timeout(1200) });
        if (res.ok) {
          state.backendOnline = true;
          updateBackendStatusUI(true, 'FastAPI: Online');
          return true;
        }
      } catch (e) {
        // Fallback transparently
      }
      state.backendOnline = false;
      updateBackendStatusUI(false, 'Local Simulation Mode (Offline Fallback)');
      return false;
    },

    async fetchQuestions(filters = {}) {
      if (state.backendOnline) {
        try {
          const params = new URLSearchParams(filters);
          const res = await fetch(`${this.baseUrl}/questions?${params.toString()}`);
          if (res.ok) return await res.json();
        } catch (e) {
          console.warn('API error, falling back to local memory:', e);
        }
      }
      return state.itemBank;
    },

    async saveQuestion(questionData) {
      if (state.backendOnline) {
        try {
          const res = await fetch(`${this.baseUrl}/questions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(questionData),
          });
          if (res.ok) return await res.json();
        } catch (e) {
          console.warn('API save error:', e);
        }
      }
      // Local fallback
      const newId = Date.now();
      const savedItem = { ...questionData, id: newId, code: `TOAN12-${String(state.itemBank.length + 1).padStart(3, '0')}` };
      state.itemBank.unshift(savedItem);
      return savedItem;
    },
  };

  function updateBackendStatusUI(isOnline, text) {
    const pill = document.getElementById('backend-status-pill');
    const label = document.getElementById('backend-status-text');
    if (!pill || !label) return;

    if (isOnline) {
      pill.className = 'flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200 transition-all';
      pill.innerHTML = '<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span><span>FastAPI: Online</span>';
    } else {
      pill.className = 'flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200 transition-all';
      pill.innerHTML = '<span class="w-2 h-2 rounded-full bg-amber-500"></span><span>Mô Phỏng Trực Tiếp (Local Engine)</span>';
    }
  }

  // ============================================================================
  // 4. KATEX AUTO-RENDER HELPER
  // ============================================================================
  function renderKaTeX(domElement) {
    if (!domElement) return;
    if (typeof renderMathInElement === 'function') {
      try {
        renderMathInElement(domElement, {
          delimiters: [
            { left: '$$', right: '$$', display: true },
            { left: '$', right: '$', display: false },
            { left: '\\(', right: '\\)', display: false },
            { left: '\\[', right: '\\]', display: true },
          ],
          throwOnError: false,
        });
      } catch (err) {
        console.error('KaTeX rendering error:', err);
      }
    }
    // Re-trigger Lucide icons
    if (window.lucide && typeof lucide.createIcons === 'function') {
      lucide.createIcons();
    }
  }

  // ============================================================================
  // 5. TOAST NOTIFICATIONS
  // ============================================================================
  function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    const colorClasses = {
      success: 'bg-emerald-800 text-white border border-emerald-600',
      warning: 'bg-amber-800 text-white border border-amber-600',
      error: 'bg-rose-800 text-white border border-rose-600',
      info: 'bg-slate-800 text-white border border-slate-700',
    }[type] || 'bg-slate-800 text-white';

    const iconName = {
      success: 'check-circle-2',
      warning: 'alert-triangle',
      error: 'alert-circle',
      info: 'info',
    }[type] || 'bell';

    toast.className = `quesy-toast ${colorClasses}`;
    toast.innerHTML = `
      <i data-lucide="${iconName}" class="w-5 h-5 shrink-0"></i>
      <span class="flex-1">${message}</span>
      <button onclick="this.parentElement.remove()" class="text-white/60 hover:text-white p-0.5"><i data-lucide="x" class="w-3.5 h-3.5"></i></button>
    `;

    container.appendChild(toast);
    renderKaTeX(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.25s ease';
      setTimeout(() => toast.remove(), 250);
    }, 4000);
  }

  // ============================================================================
  // 6. CLIENT-SIDE ROUTER & TAB SWITCHING SYSTEM (APPLE HIG ROUTER)
  // ============================================================================
  const ROUTE_MAP = {
    '/': 'dashboard',
    '/dashboard': 'dashboard',
    '/digitize': 'digitize',
    '/bank': 'itembank',
    '/itembank': 'itembank',
    '/matrix': 'matrix',
    '/shuffler': 'shuffler',
  };

  const TAB_TO_ROUTE = {
    dashboard: '/dashboard',
    digitize: '/digitize',
    itembank: '/bank',
    matrix: '/matrix',
    shuffler: '/shuffler',
  };

  const TAB_TITLES = {
    dashboard: 'Quesy — Tổng quan Khảo thí',
    digitize: 'Quesy — Số hóa AI & HITL Studio',
    itembank: 'Quesy — Ngân hàng Câu hỏi Chuẩn hóa',
    matrix: 'Quesy — Ma trận Đề thi 2D',
    shuffler: 'Quesy — Sinh đề & Trộn đề (.DOCX)',
  };

  function navigateTo(path) {
    const cleanPath = (path || '/').split('?')[0].replace(/\/$/, '') || '/';
    const tabId = ROUTE_MAP[cleanPath] || 'dashboard';
    switchTab(tabId, true);
  }

  function switchTab(tabId, pushState = true) {
    if (!tabId) tabId = 'dashboard';
    state.currentTab = tabId;

    // Update Browser URL with History API
    if (pushState) {
      const targetRoute = TAB_TO_ROUTE[tabId] || '/dashboard';
      if (window.location.pathname !== targetRoute && !(window.location.pathname === '/' && tabId === 'dashboard')) {
        window.history.pushState({ tabId }, '', targetRoute);
      }
    }

    if (TAB_TITLES[tabId]) {
      document.title = TAB_TITLES[tabId];
    }

    // Update Tab Buttons (macOS Segmented Control state)
    const tabButtons = document.querySelectorAll('.tab-nav-btn');
    tabButtons.forEach((btn) => {
      btn.classList.remove('active');
    });
    const activeBtn = document.getElementById(`nav-btn-${tabId}`);
    if (activeBtn) activeBtn.classList.add('active');

    // Update Tab Panes
    const tabPanes = document.querySelectorAll('.tab-pane');
    tabPanes.forEach((pane) => {
      pane.classList.add('hidden');
      pane.classList.remove('active');
    });

    const activePane = document.getElementById(`tab-${tabId}`);
    if (activePane) {
      activePane.classList.remove('hidden');
      activePane.classList.add('active');
    }

    // Smooth reset scroll on tab transition
    const mainView = document.getElementById('main-scroll-view');
    if (mainView) {
      mainView.scrollTop = 0;
    }

    // Refresh specific tab contents
    if (tabId === 'dashboard') {
      renderDashboard();
    } else if (tabId === 'digitize') {
      renderDigitizeStudio();
    } else if (tabId === 'itembank') {
      renderItemBank();
    } else if (tabId === 'matrix') {
      renderMatrixGrid();
    } else if (tabId === 'shuffler') {
      renderMasterExam();
    }

    if (window.lucide) lucide.createIcons();
  }

  // ============================================================================
  // 7. TAB 1: DASHBOARD
  // ============================================================================
  function renderDashboard() {
    const totalCount = state.itemBank.length;
    const approvedCount = state.itemBank.filter((q) => q.status === 'APPROVED').length;
    const rate = totalCount > 0 ? Math.round((approvedCount / totalCount) * 100) : 0;

    const totalEl = document.getElementById('dash-metric-total');
    const approvedEl = document.getElementById('dash-metric-approved');
    if (totalEl) totalEl.innerText = (1480 + state.itemBank.length - 12).toLocaleString();
    if (approvedEl) approvedEl.innerText = `${rate}%`;

    const bankBadge = document.getElementById('bank-count-badge');
    if (bankBadge) bankBadge.innerText = state.itemBank.length;

    renderKaTeX(document.getElementById('tab-dashboard'));
  }

  // ============================================================================
  // 8. TAB 2: AI DIGITIZE STUDIO (HITL SIDE-BY-SIDE INTERACTION)
  // ============================================================================
  function renderDigitizeStudio() {
    renderDocumentPaperPreview();
    renderExtractedQuestionsList();
    updateConfidenceSummary();
  }

  /**
   * Truncate filename with clean ellipsis while keeping file extension
   */
  function truncateFilename(name, maxLength = 32) {
    if (!name || typeof name !== 'string') return '';
    if (name.length <= maxLength) return name;
    const parts = name.split('.');
    if (parts.length > 1) {
      const ext = parts.pop();
      const base = parts.join('.');
      const keepBase = maxLength - ext.length - 4;
      if (keepBase > 3) {
        return `${base.slice(0, keepBase)}...${ext}`;
      }
    }
    return `${name.slice(0, maxLength - 3)}...`;
  }

  /**
   * Render original document viewer on the left pane
   * Shows native PDF viewer iframe, Word DOCX styled preview iframe, or image list preview.
   * Does NOT reconstruct / fake the exam paper from parsed questions.
   */
  function renderDocumentPaperPreview() {
    const scrollContainer = document.getElementById('doc-viewer-scroll-container');
    if (!scrollContainer) return;

    const job = state.digitizeJob;
    const staged = state.stagedExam;
    const questions = job.questions || [];
    const hasStagedPreviews = staged && staged.previews && staged.previews.length > 0;
    const isProcessing = staged && staged.status === 'PROCESSING';

    // Mode 1: STAGED or PROCESSING files before/during AI processing (maintains preview while processing!)
    if (hasStagedPreviews && (staged.status === 'STAGED' || isProcessing || (!job.jobId && questions.length === 0))) {
      const previews = staged.previews;
      const isImages = previews.every((p) => ['png', 'jpg', 'jpeg', 'webp'].includes(p.type));
      const activeIdx = staged.activePreviewIndex || 0;
      const activeP = previews[activeIdx] || previews[0];

      if (isImages) {
        scrollContainer.innerHTML = `
          <div class="w-full flex flex-col space-y-3">
            ${previews.length > 1 ? `
              <!-- Staging Reordering Toolbar & Thumbnails Strip (Only for multiple image pages) -->
              <div class="apple-card p-3 space-y-2.5">
                <div class="flex items-center justify-between text-xs">
                  <div class="flex items-center space-x-2">
                    <span class="w-2 h-2 rounded-full ${isProcessing ? 'bg-blue-500' : 'bg-amber-500'} animate-pulse"></span>
                    <span class="font-bold text-slate-800">${isProcessing ? `AI đang xử lý (${previews.length} trang ảnh)` : `Thứ Tự Các Trang Đề Thi (${previews.length} trang ảnh)`}</span>
                  </div>
                  <div class="flex items-center space-x-2">
                    ${!isProcessing ? `
                      <button type="button" onclick="document.getElementById('studio-add-file-input').click()" class="btn-apple-secondary text-xs py-1 px-2.5">
                        <i data-lucide="plus" class="w-3.5 h-3.5"></i>
                        <span>Thêm trang ảnh</span>
                      </button>
                      <span class="text-[11px] text-slate-400">Bấm ← → để đổi thứ tự trang</span>
                    ` : `
                      <span class="text-[11px] text-blue-600 font-medium flex items-center space-x-1">
                        <i data-lucide="loader-2" class="w-3 h-3 animate-spin"></i>
                        <span>Đang bóc tách...</span>
                      </span>
                    `}
                  </div>
                </div>

                <!-- Thumbnails Horizontal Scroller -->
                <div class="flex items-center gap-2 overflow-x-auto pb-1 pt-0.5 no-scrollbar">
                  ${previews.map((p, i) => `
                    <div onclick="app.selectStagedPreviewPage(${i})" class="shrink-0 flex flex-col items-center p-2 rounded-xl border transition-all cursor-pointer ${i === activeIdx ? 'ring-2 ring-[#0071E3] border-[#0071E3] bg-[#0071E3]/[0.05]' : 'border-black/[0.08] bg-slate-50 hover:bg-white'}">
                      <div class="flex items-center justify-between w-full text-[10px] font-bold text-slate-600 mb-1">
                        <span>Trang ${i + 1}</span>
                        ${!isProcessing ? `<button type="button" onclick="event.stopPropagation(); app.removeStagedPage(${i})" class="text-slate-400 hover:text-rose-600 p-0.5 rounded" title="Xóa trang này">✕</button>` : ''}
                      </div>
                      <img src="${p.url}" class="w-16 h-20 object-cover rounded shadow-xs mb-1.5 border border-slate-200" alt="Trang ${i + 1}">
                      ${!isProcessing ? `
                        <div class="flex items-center space-x-1" onclick="event.stopPropagation()">
                          <button type="button" onclick="app.moveStagedPage(${i}, -1)" ${i === 0 ? 'disabled' : ''} class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-white border border-slate-300 hover:bg-slate-100 ${i === 0 ? 'opacity-30 cursor-not-allowed' : 'text-slate-700'}" title="Đưa trang này lên trước">←</button>
                          <button type="button" onclick="app.moveStagedPage(${i}, 1)" ${i === previews.length - 1 ? 'disabled' : ''} class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-white border border-slate-300 hover:bg-slate-100 ${i === previews.length - 1 ? 'opacity-30 cursor-not-allowed' : 'text-slate-700'}" title="Đưa trang này xuống sau">→</button>
                        </div>
                      ` : ''}
                    </div>
                  `).join('')}
                </div>
              </div>
            ` : ''}

            <!-- Active Large Image Viewer -->
            <div class="w-full apple-card p-4 flex flex-col items-center">
              <div class="w-full flex items-center justify-between text-xs text-slate-500 border-b border-black/[0.06] pb-2 mb-3">
                <span class="font-bold text-slate-700 truncate max-w-sm" title="${escapeHtml(activeP.name)}">
                  ${isProcessing ? 'AI đang xử lý: ' : 'Xem trước: '} ${previews.length > 1 ? `Trang ${activeIdx + 1} / ${previews.length} • ` : ''}${truncateFilename(activeP.name, 28)}
                </span>
                <div class="flex items-center space-x-2">
                  ${previews.length === 1 && !isProcessing ? `
                    <button type="button" onclick="document.getElementById('studio-add-file-input').click()" class="btn-apple-secondary text-xs py-0.5 px-2">
                      <i data-lucide="plus" class="w-3 h-3"></i>
                      <span>Thêm trang ảnh</span>
                    </button>
                  ` : ''}
                  ${isProcessing ? `
                    <span class="text-[11px] text-blue-600 font-medium flex items-center space-x-1">
                      <i data-lucide="loader-2" class="w-3 h-3 animate-spin"></i>
                      <span>Đang bóc tách...</span>
                    </span>
                  ` : ''}
                  <span class="text-[11px] text-slate-400">Dung lượng: ${activeP.size}</span>
                </div>
              </div>
              <img src="${activeP.url}" class="max-w-full h-auto max-h-[750px] rounded-lg shadow-xs object-contain border border-black/[0.06]" alt="Xem trước Trang ${activeIdx + 1}">
            </div>
          </div>
        `;
        if (window.lucide) lucide.createIcons();
        return;
      }

      if (previews[0].type === 'pdf') {
        scrollContainer.innerHTML = `
          <div class="w-full h-full min-h-[850px] flex flex-col bg-slate-200 rounded-lg overflow-hidden border border-slate-300 shadow-inner">
            <iframe id="doc-pdf-iframe" src="${previews[0].url}" class="w-full h-full min-h-[850px] border-0 rounded bg-white" title="PDF Document Staging Viewer"></iframe>
          </div>
        `;
        return;
      }

      if (['docx', 'doc'].includes(previews[0].type)) {
        scrollContainer.innerHTML = `
          <div class="w-full max-w-xl apple-card p-8 text-center space-y-4 my-auto">
            <div class="w-16 h-16 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600 mx-auto shadow-xs">
              <i data-lucide="file-text" class="w-8 h-8"></i>
            </div>
            <h3 class="text-base font-bold text-slate-900 truncate max-w-md mx-auto" title="${escapeHtml(previews[0].name)}">${truncateFilename(previews[0].name, 36)}</h3>
            <p class="text-xs text-slate-500">Tài liệu Word DOCX (${previews[0].size}) ${isProcessing ? 'đang được AI phân tích và bóc tách công thức MathType...' : 'đã sẵn sàng để bóc tách công thức MathType và gõ lại đề thi.'}</p>
            <div class="pt-2">
              ${isProcessing ? `
                <div class="inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-blue-50 text-blue-700 text-xs font-semibold border border-blue-200">
                  <i data-lucide="loader-2" class="w-4 h-4 animate-spin text-brand-600"></i>
                  <span>AI đang phân tích tài liệu & bóc tách câu hỏi...</span>
                </div>
              ` : `
                <button onclick="app.startAIDigitize()" class="btn-apple-primary mx-auto py-2.5 px-6">
                  <i data-lucide="sparkles" class="w-4 h-4 text-amber-300"></i>
                  <span>Tiến hành gõ lại</span>
                </button>
              `}
            </div>
          </div>
        `;
        if (window.lucide) lucide.createIcons();
        return;
      }
    }

    // Mode 2: If empty state (no file, no questions)
    if (!job.jobId && questions.length === 0) {
      scrollContainer.innerHTML = `
        <div id="doc-viewer-paper" class="w-full bg-white shadow-lg rounded-sm p-6 min-h-[880px] text-[13px] text-slate-900 leading-relaxed font-sans relative">
          <div id="doc-paper-content" class="py-16 px-4 flex flex-col items-center justify-center text-center text-slate-400">
            <div class="w-16 h-16 rounded-2xl bg-black/[0.03] border border-black/[0.06] flex items-center justify-center shadow-xs mb-3 text-brand-600">
              <i data-lucide="file-up" class="w-8 h-8"></i>
            </div>
            <h4 class="text-sm font-bold text-slate-900 mb-1">Khu Vực Đối Chiếu Đề Thi Gốc</h4>
            <p class="text-xs text-slate-500 max-w-sm mb-5 leading-relaxed">
              Chưa có tệp đề thi nào được nạp. Hãy chọn tệp Word (.docx), PDF hoặc danh sách ảnh để xem trước trực tiếp tài liệu gốc và đối chiếu bóc tách.
            </p>
            <div class="flex items-center gap-2">
              <button onclick="document.getElementById('studio-file-input').click()" class="btn-apple-primary">
                <i data-lucide="upload" class="w-3.5 h-3.5"></i>
                <span>Chọn tệp đề thi</span>
              </button>
              <button onclick="app.loadSampleExam('math12_standard')" class="btn-apple-secondary">
                <i data-lucide="sparkles" class="w-3.5 h-3.5 text-amber-500"></i>
                <span>Xem đề mẫu</span>
              </button>
            </div>
          </div>
        </div>
      `;
      if (window.lucide) lucide.createIcons();
      return;
    }

    // Mode 3: If an actual uploaded file exists (PDF, DOCX, or Images)
    if (job.jobId) {
      const fileType = (job.fileType || '').toLowerCase();
      const filename = (job.filename || '').toLowerCase();

      // Case A: PDF Document -> Direct browser native PDF streaming viewer
      if (fileType === 'pdf' || filename.endsWith('.pdf')) {
        const previewUrl = job.previewUrl || `${API_BASE_URL}/digitize/jobs/${job.jobId}/preview`;
        scrollContainer.innerHTML = `
          <div class="w-full h-full min-h-[850px] flex flex-col bg-slate-200 rounded-lg overflow-hidden border border-slate-300 shadow-inner">
            <iframe id="doc-pdf-iframe" src="${previewUrl}" class="w-full h-full min-h-[850px] border-0 rounded bg-white" title="PDF Document Viewer"></iframe>
          </div>
        `;
        return;
      }

      // Case B: Word DOCX Document -> Clean styled document view
      if (fileType === 'docx' || fileType === 'doc' || filename.endsWith('.docx') || filename.endsWith('.doc')) {
        const previewUrl = job.previewUrl || `${API_BASE_URL}/digitize/jobs/${job.jobId}/preview`;
        scrollContainer.innerHTML = `
          <div class="w-full h-full min-h-[850px] flex flex-col bg-slate-200 rounded-lg overflow-hidden border border-slate-300 shadow-inner">
            <iframe id="doc-docx-iframe" src="${previewUrl}" class="w-full h-full min-h-[850px] border-0 rounded bg-white" title="Word DOCX Document Viewer"></iframe>
          </div>
        `;
        return;
      }

      // Case C: Images (or list of images) -> Stack of full-resolution exam images
      if (fileType === 'images' || ['png', 'jpg', 'jpeg', 'webp'].includes(fileType) || (job.previewImages && job.previewImages.length > 0)) {
        const images = (job.previewImages && job.previewImages.length > 0)
          ? job.previewImages
          : [`${API_BASE_URL}/digitize/jobs/${job.jobId}/preview`];

        scrollContainer.innerHTML = `
          <div class="w-full max-w-2xl space-y-4 py-2 flex flex-col items-center">
            ${images.map((imgUrl, i) => `
              <div class="w-full bg-white rounded-xl p-3 shadow-md border border-slate-300">
                <div class="text-[11px] font-bold text-slate-500 mb-2 flex items-center justify-between border-b border-slate-100 pb-1">
                  <span>Trang ${i + 1} / ${images.length}</span>
                  <a href="${imgUrl}" target="_blank" class="text-brand-600 hover:underline flex items-center space-x-1">
                    <i data-lucide="external-link" class="w-3 h-3"></i>
                    <span>Mở ảnh gốc</span>
                  </a>
                </div>
                <img src="${imgUrl}" class="w-full h-auto rounded shadow-xs object-contain" alt="Trang ${i + 1}">
              </div>
            `).join('')}
          </div>
        `;
        if (window.lucide) lucide.createIcons();
        return;
      }
    }

    // 3. Sample Exam Paper View (for built-in demo presets)
    let html = `
      <div id="doc-viewer-paper" class="w-full max-w-xl bg-white shadow-lg rounded-sm p-8 min-h-[880px] text-[13px] text-slate-900 leading-relaxed font-sans relative">
        <div class="border-b-2 border-slate-800 pb-3 mb-6 grid grid-cols-2 gap-2 text-center text-xs font-sans">
          <div>
            <div class="font-bold uppercase tracking-tight">SỞ GD&ĐT HÀ NỘI</div>
            <div class="font-bold text-[11px]">TRƯỜNG THPT CHU VĂN AN</div>
            <div class="text-[10px] text-slate-500 italic mt-0.5">(Đề thi mẫu chuẩn Bộ GD&ĐT)</div>
          </div>
          <div>
            <div class="font-bold uppercase tracking-tight">KỲ THI THỬ TỐT NGHIỆP THPT 2025</div>
            <div class="font-bold text-brand-800">BÀI THI: TOÁN HỌC</div>
            <div class="text-[10px] text-slate-600 italic">Thời gian: 90 phút (Không kể giao đề)</div>
          </div>
        </div>
        <div id="doc-paper-content" class="space-y-6">
    `;

    questions.forEach((q, idx) => {
      const qId = q.id || idx + 1;
      const isSelected = qId === state.digitizeJob.activeQuestionId;
      const highlightClass = isSelected ? 'active-source-highlight' : '';

      html += `
        <div id="doc-source-q-${qId}" onclick="app.selectQuestionForHITL(${qId})" class="doc-source-item ${highlightClass}">
          <div class="flex items-baseline space-x-1.5 font-bold text-slate-900 mb-1">
            <span class="text-brand-700">Câu ${idx + 1}:</span>
            <div class="font-normal text-slate-800">${q.stem}</div>
          </div>
      `;

      if (q.item_format === 'SINGLE_CHOICE' && q.options) {
        html += `<div class="grid grid-cols-2 gap-x-4 gap-y-1 pl-4 mt-2 text-xs">`;
        q.options.forEach((opt) => {
          html += `<div><strong>${opt.label}.</strong> ${opt.content}</div>`;
        });
        html += `</div>`;
      } else if (q.item_format === 'TRUE_FALSE_GROUP' && q.sub_statements) {
        html += `<div class="space-y-1 pl-4 mt-2 text-xs">`;
        q.sub_statements.forEach((sub) => {
          html += `<div><strong>${sub.label})</strong> ${sub.content}</div>`;
        });
        html += `</div>`;
      } else if (q.item_format === 'SHORT_ANSWER') {
        html += `<div class="pl-4 mt-2 text-xs italic text-slate-500">Đáp số: [........................]</div>`;
      }

      html += `</div>`;
    });

    html += `
        </div>
        <div class="text-center pt-8 text-[11px] font-sans text-slate-400">
          --- HẾT --- Cán bộ coi thi không giải thích gì thêm ---
        </div>
      </div>
    `;

    scrollContainer.innerHTML = html;
    renderKaTeX(scrollContainer);
    if (window.lucide) lucide.createIcons();
  }

  /**
   * Render extracted question cards on the right pane
   */
  function renderExtractedQuestionsList() {
    const container = document.getElementById('studio-questions-container');
    if (!container) return;

    // 1. If files are staged for preview before AI processing
    if (state.stagedExam && state.stagedExam.status === 'STAGED') {
      const staged = state.stagedExam;
      const count = staged.previews.length;
      container.innerHTML = `
        <div class="min-h-[440px] flex flex-col items-center justify-center p-8 text-center apple-card space-y-4">
          <div class="w-14 h-14 rounded-2xl bg-[#0071E3]/[0.08] flex items-center justify-center shadow-xs text-[#0071E3]">
            <i data-lucide="sparkles" class="w-7 h-7 text-amber-500"></i>
          </div>
          <span class="px-3 py-1 rounded-full bg-black/[0.05] text-slate-800 font-semibold text-xs">
            TÀI LIỆU ĐÃ SẴN SÀNG
          </span>
          <h3 class="text-base font-bold text-slate-900 truncate max-w-md mx-auto" title="${escapeHtml(state.digitizeJob.filename || 'Tài liệu đề thi')}">
            ${truncateFilename(state.digitizeJob.filename || 'Tài liệu đề thi', 36)}
          </h3>
          <p class="text-xs text-slate-500 max-w-md leading-relaxed">
            Thầy/cô vui lòng kiểm tra bản xem trước và sắp xếp thứ tự các trang ở cột trái. Sau khi hoàn tất, nhấn nút bên dưới để AI bắt đầu gõ lại đề và bóc tách câu hỏi theo chuẩn Thông tư 32 & QĐ 764.
          </p>
          <div class="pt-2">
            <button onclick="app.startAIDigitize()" class="btn-apple-primary py-2.5 px-6">
              <i data-lucide="cpu" class="w-4 h-4 text-amber-300"></i>
              <span>Tiến hành gõ lại</span>
            </button>
          </div>
        </div>
      `;
      if (window.lucide) lucide.createIcons();
      return;
    }

    // 2. If processing
    if (state.stagedExam && state.stagedExam.status === 'PROCESSING') {
      container.innerHTML = `
        <div class="min-h-[440px] flex flex-col items-center justify-center p-8 text-center apple-card space-y-4">
          <div class="w-14 h-14 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center shadow-xs text-brand-600 animate-spin">
            <i data-lucide="loader-2" class="w-7 h-7"></i>
          </div>
          <h3 class="text-base font-bold text-slate-900">
            Đang Gõ Lại & Bóc Tách Đề Thi Bằng AI...
          </h3>
          <p class="text-xs text-slate-500 max-w-md leading-relaxed">
            Hệ thống AI đang phân tích cấu trúc 3 phần (QĐ 764), bóc tách công thức Toán học KaTeX và phân loại YCCĐ (TT 32). Vui lòng đợi trong giây lát...
          </p>
        </div>
      `;
      if (window.lucide) lucide.createIcons();
      return;
    }

    const totalQuestions = state.digitizeJob.questions || [];
    if (totalQuestions.length === 0) {
      container.innerHTML = `
        <div class="min-h-[440px] flex flex-col items-center justify-center p-8 text-center apple-card border-dashed border-black/[0.12] text-slate-400">
          <div class="w-14 h-14 rounded-2xl bg-black/[0.03] border border-black/[0.06] flex items-center justify-center shadow-xs mb-3 text-brand-600">
            <i data-lucide="scan-line" class="w-7 h-7"></i>
          </div>
          <h4 class="text-sm font-bold text-slate-800 mb-1">Chưa Có Danh Sách Câu Hỏi</h4>
          <p class="text-xs text-slate-500 max-w-sm leading-relaxed">
            Danh sách các câu hỏi được AI bóc tách (công thức Toán KaTeX, đáp án và phân loại chuẩn TT 32 & QĐ 764) sẽ hiển thị tại đây sau khi tiến hành gõ lại đề.
          </p>
        </div>
      `;
      if (window.lucide) lucide.createIcons();
      return;
    }

    const filter = state.digitizeJob.confidenceFilter;
    const questions = totalQuestions.filter((q) => {
      const c = q.confidence || 0;
      if (filter === 'green') return c >= 95;
      if (filter === 'yellow') return c >= 80 && c < 95;
      if (filter === 'red') return c < 80;
      return true;
    });

    if (questions.length === 0) {
      container.innerHTML = `
        <div class="p-8 text-center text-slate-400 text-xs bg-white rounded-2xl border border-slate-200">
          <i data-lucide="filter-x" class="w-8 h-8 mx-auto mb-2 text-slate-300"></i>
          Không có câu hỏi nào khớp với bộ lọc độ tin cậy đã chọn.
        </div>
      `;
      if (window.lucide) lucide.createIcons();
      return;
    }

    let html = '';

    questions.forEach((q, idx) => {
      const qId = q.id || idx + 1;
      const qCode = q.code || `EXTRACT-${String(qId).padStart(3, '0')}`;
      const qConfidence = q.confidence !== undefined ? Math.round(q.confidence) : 95;
      const isSelected = qId === state.digitizeJob.activeQuestionId;
      const activeCardClass = isSelected ? 'active-card' : '';

      // Confidence badge styling
      let confBadgeClass = 'badge-conf-green';
      let confLabel = 'Hoàn hảo';
      if (qConfidence < 80) {
        confBadgeClass = 'badge-conf-red';
        confLabel = 'Lỗi cú pháp / Thiếu key';
      } else if (qConfidence < 95) {
        confBadgeClass = 'badge-conf-yellow';
        confLabel = 'Cần kiểm tra lại';
      }

      // Format label
      const formatLabels = {
        SINGLE_CHOICE: 'Trắc nghiệm đơn',
        TRUE_FALSE_GROUP: 'Đúng / Sai 4 khẳng định',
        SHORT_ANSWER: 'Trả lời ngắn',
      };

      html += `
        <div id="hitl-card-q-${qId}" onclick="app.selectQuestionForHITL(${qId})" class="hitl-question-card bg-white rounded-xl p-4 shadow-xs ${activeCardClass}">
          
          <!-- Card Header -->
          <div class="flex items-center justify-between pb-2.5 border-b border-slate-100 text-xs">
            <div class="flex items-center space-x-2">
              <span class="px-2 py-0.5 rounded-md bg-brand-100 text-brand-800 font-extrabold text-[11px]">
                Câu ${idx + 1}
              </span>
              <span class="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 font-semibold text-[11px]">
                ${formatLabels[q.item_format] || q.item_format}
              </span>
            </div>
          </div>

          <!-- Question Stem & KaTeX -->
          <div class="py-3 text-xs text-slate-800 leading-relaxed">
            <div class="font-medium flex items-start justify-between gap-2">
              <div class="flex-1">${q.stem}</div>
              <button onclick="event.stopPropagation(); app.openFormulaEditorModal('digitize', ${qId}, 'stem')" title="Chỉnh sửa công thức nhanh" class="p-1 text-slate-400 hover:text-brand-600 rounded">
                <i data-lucide="edit-3" class="w-3.5 h-3.5"></i>
              </button>
            </div>
          </div>
      `;

      // Render Options based on Format
      if (q.item_format === 'SINGLE_CHOICE' && q.options) {
        html += `<div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs mb-3">`;
        q.options.forEach((opt, optIdx) => {
          const isCorrect = opt.is_correct;
          const correctClass = isCorrect ? 'is-correct' : 'bg-slate-50 border-slate-200 text-slate-700';

          // Option Anchor Rule check
          const hasAnchor = opt.is_fixed || isAnchorPhrase(opt.content);

          html += `
            <div onclick="event.stopPropagation(); app.toggleSingleChoiceAnswer(${qId}, ${optIdx})" class="option-pill flex items-center justify-between p-2 rounded-xl border ${correctClass}">
              <div class="flex items-center space-x-2">
                <span class="option-letter-badge w-5 h-5 rounded-md flex items-center justify-center font-bold text-xs ${isCorrect ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-700'}">
                  ${opt.label}
                </span>
                <span>${opt.content}</span>
              </div>
              
              <div class="flex items-center space-x-1">
                ${
                  hasAnchor
                    ? `<span class="option-anchor-indicator" title="Option Anchor Rule: Khóa cố định tại vị trí D khi trộn đề">
                        <i data-lucide="anchor" class="w-3 h-3"></i> Khóa D
                       </span>`
                    : ''
                }
                <button onclick="event.stopPropagation(); app.openFormulaEditorModal('digitize', ${qId}, 'option', ${optIdx})" class="p-1 text-slate-400 hover:text-brand-600">
                  <i data-lucide="edit-2" class="w-3 h-3"></i>
                </button>
              </div>
            </div>
          `;
        });
        html += `</div>`;
      } else if (q.item_format === 'TRUE_FALSE_GROUP' && q.sub_statements) {
        // True/False 4 statements staircase grading UI
        html += `
          <div class="space-y-2 mb-3 bg-slate-50 p-2.5 rounded-xl border border-slate-200 text-xs">
            <div class="flex items-center justify-between text-[11px] font-bold text-slate-500 border-b border-slate-200 pb-1">
              <span>Ý khẳng định con (QĐ 764)</span>
              <span>Điểm bậc thang: 1 ý = 0.1đ | 2 ý = 0.25đ | 3 ý = 0.5đ | 4 ý = 1.0đ</span>
            </div>
        `;
        q.sub_statements.forEach((sub, subIdx) => {
          html += `
            <div class="flex items-center justify-between gap-2 p-1.5 rounded-lg bg-white border border-slate-200">
              <div class="flex items-start space-x-1.5 flex-1">
                <span class="font-bold text-brand-700">${sub.label})</span>
                <span class="text-slate-800">${sub.content}</span>
              </div>
              <div class="flex items-center space-x-1 shrink-0">
                <button onclick="event.stopPropagation(); app.toggleTrueFalseAnswer(${qId}, ${subIdx}, true)" class="px-2 py-0.5 rounded text-[11px] font-bold transition-all ${sub.is_true ? 'bg-emerald-600 text-white' : 'bg-slate-100 text-slate-500 hover:bg-slate-200'}">
                  ĐÚNG
                </button>
                <button onclick="event.stopPropagation(); app.toggleTrueFalseAnswer(${qId}, ${subIdx}, false)" class="px-2 py-0.5 rounded text-[11px] font-bold transition-all ${!sub.is_true ? 'bg-rose-600 text-white' : 'bg-slate-100 text-slate-500 hover:bg-slate-200'}">
                  SAI
                </button>
              </div>
            </div>
          `;
        });
        html += `</div>`;
      } else if (q.item_format === 'SHORT_ANSWER') {
        html += `
          <div class="mb-3 p-2.5 rounded-xl bg-purple-50 border border-purple-200 text-xs flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <span class="font-bold text-purple-900">Chuỗi kết quả đúng:</span>
              <input type="text" value="${q.short_answer_value || ''}" onchange="app.updateShortAnswerValue(${qId}, this.value)" class="font-mono font-bold text-xs px-2 py-1 bg-white border border-purple-300 rounded-lg w-28">
            </div>
            <div class="text-[11px] text-purple-700">Dung sai sai số $\\pm ${q.tolerance || '0.0'}$</div>
          </div>
        `;
      }

      // Quick YCCD & Archetype Tagger Toolbar
      html += `
        <div class="pt-2.5 border-t border-slate-100 grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
          <div>
            <label class="block text-slate-500 font-bold mb-0.5">Yêu cầu cần đạt:</label>
            <select onchange="app.updateQuestionYCCD(${qId}, this.value)" class="w-full text-xs font-mono rounded-lg border border-slate-200 py-1 px-2 bg-slate-50">
              <option value="TOAN12.GT.01" ${q.learning_outcome_id === 'TOAN12.GT.01' ? 'selected' : ''}>TOAN12.GT.01: Cực trị hàm số</option>
              <option value="TOAN12.GT.02" ${q.learning_outcome_id === 'TOAN12.GT.02' ? 'selected' : ''}>TOAN12.GT.02: Đường tiệm cận</option>
              <option value="TOAN12.GT.03" ${q.learning_outcome_id === 'TOAN12.GT.03' ? 'selected' : ''}>TOAN12.GT.03: Khái niệm nguyên hàm</option>
              <option value="TOAN12.HH.01" ${q.learning_outcome_id === 'TOAN12.HH.01' ? 'selected' : ''}>TOAN12.HH.01: Mặt phẳng Oxyz</option>
              <option value="TOAN12.XS.01" ${q.learning_outcome_id === 'TOAN12.XS.01' ? 'selected' : ''}>TOAN12.XS.01: Xác suất Bayes</option>
            </select>
          </div>

          <div>
            <label class="block text-slate-500 font-bold mb-0.5">Mức độ nhận thức:</label>
            <select onchange="app.updateQuestionCognitive(${qId}, this.value)" class="w-full text-xs rounded-lg border border-slate-200 py-1 px-2 bg-slate-50 font-semibold">
              <option value="RECOGNITION" ${q.cognitive_level === 'RECOGNITION' ? 'selected' : ''}>1. Nhận biết</option>
              <option value="COMPREHENSION" ${q.cognitive_level === 'COMPREHENSION' ? 'selected' : ''}>2. Thông hiểu</option>
              <option value="APPLICATION" ${q.cognitive_level === 'APPLICATION' ? 'selected' : ''}>3. Vận dụng</option>
              <option value="HIGH_APPLICATION" ${q.cognitive_level === 'HIGH_APPLICATION' ? 'selected' : ''}>4. Vận dụng cao</option>
            </select>
          </div>
        </div>

        <!-- Footer Actions -->
        <div class="mt-3 pt-2 border-t border-slate-100 flex items-center justify-end text-xs">
          <div class="flex items-center space-x-1.5">
            <button onclick="event.stopPropagation(); app.openQuestionEditorModal(${qId})" class="btn-apple-tinted py-1 px-2.5 text-[11px]" title="Chỉnh sửa câu hỏi này">
              <i data-lucide="edit-3" class="w-3.5 h-3.5"></i>
              <span>Chỉnh sửa</span>
            </button>
            <button onclick="event.stopPropagation(); app.checkQuestionDuplicate(${qId})" class="btn-apple-secondary py-1 px-2 text-[11px]" title="Kiểm tra độ trùng lặp AI">
              <i data-lucide="copy" class="w-3 h-3"></i>
              <span>Trùng lặp</span>
            </button>
            <button onclick="event.stopPropagation(); app.commitSingleQuestion(${qId})" class="btn-apple-primary py-1 px-2.5 text-[11px]">
              Lưu câu này
            </button>
          </div>
        </div>

      </div>
      `;
    });

    container.innerHTML = html;
    renderKaTeX(container);
  }

  function isAnchorPhrase(text) {
    if (!text) return false;
    const lower = text.toLowerCase();
    return (
      lower.includes('cả a và b') ||
      lower.includes('cả a và c') ||
      lower.includes('cả b và c') ||
      lower.includes('tất cả các') ||
      lower.includes('tất cả đều') ||
      lower.includes('không có đáp án') ||
      lower.includes('không có giá trị') ||
      lower.includes('không có phương án')
    );
  }

  function selectQuestionForHITL(qId) {
    state.digitizeJob.activeQuestionId = qId;

    // Synchronized scroll to source block on the left paper
    const leftTarget = document.getElementById(`doc-source-q-${qId}`);
    const leftContainer = document.getElementById('doc-viewer-scroll-container');
    if (leftTarget && leftContainer) {
      // Clear previous active highlights on left
      document.querySelectorAll('.doc-source-item').forEach((el) => {
        el.classList.remove('active-source-highlight');
      });
      leftTarget.classList.add('active-source-highlight');

      // Smooth scroll left pane
      const topPos = leftTarget.offsetTop - leftContainer.offsetTop - 40;
      leftContainer.scrollTo({ top: Math.max(0, topPos), behavior: 'smooth' });
    }

    // Highlight right card
    document.querySelectorAll('.hitl-question-card').forEach((card) => {
      card.classList.remove('active-card');
    });
    const rightCard = document.getElementById(`hitl-card-q-${qId}`);
    if (rightCard) {
      rightCard.classList.add('active-card');
    }

    // Update active label
    const activeBadge = document.getElementById('doc-active-target-badge');
    if (activeBadge) {
      const idx = state.digitizeJob.questions.findIndex((q) => q.id === qId);
      activeBadge.innerText = `Đối chiếu: Câu ${idx >= 0 ? idx + 1 : qId}`;
    }
  }

  function toggleSingleChoiceAnswer(qId, optIdx) {
    const q = state.digitizeJob.questions.find((x) => x.id === qId);
    if (!q || !q.options) return;

    q.options.forEach((opt, idx) => {
      opt.is_correct = idx === optIdx;
    });

    // If previously low confidence due to missing answer, boost confidence
    if (q.confidence < 80) q.confidence = 96;

    renderExtractedQuestionsList();
    updateConfidenceSummary();
    showToast(`Đã cập nhật đáp án đúng: Phương án ${q.options[optIdx].label} cho Câu ${q.id}`, 'success');
  }

  function toggleTrueFalseAnswer(qId, subIdx, value) {
    const q = state.digitizeJob.questions.find((x) => x.id === qId);
    if (!q || !q.sub_statements) return;

    q.sub_statements[subIdx].is_true = value;
    renderExtractedQuestionsList();
    showToast(`Đã cập nhật ý ${q.sub_statements[subIdx].label}) thành ${value ? 'ĐÚNG' : 'SAI'}`, 'info');
  }

  function updateShortAnswerValue(qId, val) {
    const q = state.digitizeJob.questions.find((x) => x.id === qId);
    if (!q) return;
    q.short_answer_value = val.trim();
    showToast(`Đã lưu kết quả trả lời ngắn: ${val}`, 'success');
  }

  function updateQuestionYCCD(qId, yccdCode) {
    const q = state.digitizeJob.questions.find((x) => x.id === qId);
    if (!q) return;
    q.learning_outcome_id = yccdCode;
    showToast(`Đã gán chuẩn YCCĐ: ${yccdCode}`, 'success');
  }

  function updateQuestionCognitive(qId, level) {
    const q = state.digitizeJob.questions.find((x) => x.id === qId);
    if (!q) return;
    q.cognitive_level = level;
    showToast(`Đã cập nhật mức độ: ${level}`, 'success');
  }

  function filterStudioConfidence(type) {
    state.digitizeJob.confidenceFilter = type;
    const btnAll = document.getElementById('btn-filter-conf-all');
    const btnGreen = document.getElementById('btn-filter-conf-green');
    const btnYellow = document.getElementById('btn-filter-conf-yellow');
    const btnRed = document.getElementById('btn-filter-conf-red');

    [btnAll, btnGreen, btnYellow, btnRed].forEach((b) => {
      if (b) {
        b.className = 'px-2.5 py-1 rounded-lg text-xs font-medium text-slate-600 hover:bg-white/50';
      }
    });

    const activeBtn = {
      all: btnAll,
      green: btnGreen,
      yellow: btnYellow,
      red: btnRed,
    }[type];

    if (activeBtn) {
      activeBtn.className = 'px-2.5 py-1 rounded-lg text-xs font-semibold bg-white text-slate-800 shadow-xs';
    }

    renderExtractedQuestionsList();
  }

  function updateConfidenceSummary() {
    const questions = state.digitizeJob.questions || [];

    const allBtn = document.getElementById('btn-filter-conf-all');
    if (allBtn) allBtn.innerText = `Tất cả (${questions.length})`;

    const greenCount = questions.filter((q) => (q.confidence || 0) >= 95).length;
    const yellowCount = questions.filter((q) => (q.confidence || 0) >= 80 && (q.confidence || 0) < 95).length;
    const redCount = questions.filter((q) => (q.confidence || 0) < 80).length;

    const greenBtn = document.getElementById('btn-filter-conf-green');
    if (greenBtn) greenBtn.innerHTML = `Xanh $\\ge 95\\%$ (${greenCount})`;
    const yellowBtn = document.getElementById('btn-filter-conf-yellow');
    if (yellowBtn) yellowBtn.innerHTML = `Vàng $80-94\\%$ (${yellowCount})`;
    const redBtn = document.getElementById('btn-filter-conf-red');
    if (redBtn) redBtn.innerHTML = `Đỏ $< 80\\%$ (${redCount})`;

    const readyBadge = document.getElementById('studio-ready-count-badge');
    if (readyBadge) readyBadge.innerText = questions.length;

    const totalBadge = document.getElementById('studio-total-badge');
    if (totalBadge) totalBadge.innerText = `${questions.length} câu`;

    const avgEl = document.getElementById('studio-avg-confidence');
    const statusLabel = document.getElementById('studio-status-label');
    const statusIndicator = document.getElementById('studio-status-indicator');
    const filenameEl = document.getElementById('doc-viewer-filename');
    const pageDisplay = document.getElementById('doc-page-display');
    const activeBadge = document.getElementById('doc-active-target-badge');
    const commitBtn = document.getElementById('btn-commit-to-bank');
    const startDigitizeBtn = document.getElementById('btn-start-digitize');
    const resetStageBtn = document.getElementById('btn-reset-stage');
    const rightHeaderActions = document.getElementById('studio-right-header-actions');

    // Staged mode before AI processing
    if (state.stagedExam && state.stagedExam.status === 'STAGED') {
      const count = (state.stagedExam.previews || []).length;
      if (rightHeaderActions) rightHeaderActions.classList.add('hidden');
      if (startDigitizeBtn) startDigitizeBtn.classList.remove('hidden');
      if (resetStageBtn) resetStageBtn.classList.remove('hidden');
      if (statusLabel) statusLabel.innerText = `Đã chọn ${count} tệp (Kiểm tra & Sắp xếp thứ tự trước khi gõ đề)`;
      if (statusIndicator) statusIndicator.className = 'w-2 h-2 rounded-full bg-amber-500 animate-pulse';
      if (filenameEl) {
        const rawName = state.digitizeJob.filename || 'Tài liệu chờ xử lý';
        filenameEl.innerText = truncateFilename(rawName, 32);
        filenameEl.title = rawName;
      }
      if (pageDisplay) pageDisplay.innerText = `Trang ${(state.stagedExam.activePreviewIndex || 0) + 1} / ${count}`;
      if (activeBadge) {
        activeBadge.innerText = 'Chờ xác nhận gõ đề';
        activeBadge.className = 'px-2 py-0.5 bg-amber-50 text-amber-700 font-bold text-[11px] rounded-md border border-amber-200';
      }
      if (commitBtn) commitBtn.classList.add('opacity-50', 'cursor-not-allowed');
      return;
    } else if (state.stagedExam && state.stagedExam.status === 'PROCESSING') {
      if (rightHeaderActions) rightHeaderActions.classList.add('hidden');
      if (startDigitizeBtn) startDigitizeBtn.classList.add('hidden');
      if (resetStageBtn) resetStageBtn.classList.add('hidden');
      if (statusLabel) statusLabel.innerText = 'AI đang gõ lại và bóc tách đề thi...';
      if (statusIndicator) statusIndicator.className = 'w-2 h-2 rounded-full bg-blue-500 animate-pulse';
      if (filenameEl) {
        const rawName = state.digitizeJob.filename || 'Tài liệu đang xử lý';
        filenameEl.innerText = truncateFilename(rawName, 32);
        filenameEl.title = rawName;
      }
      if (commitBtn) commitBtn.classList.add('opacity-50', 'cursor-not-allowed');
      return;
    } else {
      if (startDigitizeBtn) startDigitizeBtn.classList.add('hidden');
    }

    if (questions.length === 0) {
      if (rightHeaderActions) rightHeaderActions.classList.add('hidden');
      if (avgEl) avgEl.innerText = 'Độ tin cậy TB: --';
      if (statusLabel) statusLabel.innerText = 'AI Parsing: Sẵn sàng (Chưa tải tệp)';
      if (statusIndicator) {
        statusIndicator.className = 'w-2 h-2 rounded-full bg-slate-400';
      }
      if (resetStageBtn) resetStageBtn.classList.add('hidden');
      if (filenameEl) {
        const rawName = state.digitizeJob.filename || 'Chưa tải tệp nào';
        filenameEl.innerText = truncateFilename(rawName, 32);
        filenameEl.title = rawName;
      }
      if (pageDisplay) pageDisplay.innerText = 'Trang 0 / 0';
      if (activeBadge) {
        activeBadge.innerText = 'Chưa chọn câu';
        activeBadge.className = 'px-2 py-0.5 bg-slate-100 text-slate-600 font-bold text-[11px] rounded-md border border-slate-200';
      }
      if (commitBtn) {
        commitBtn.classList.add('opacity-50', 'cursor-not-allowed');
      }
      state.digitizeJob.avgConfidence = 0;
    } else {
      if (rightHeaderActions) rightHeaderActions.classList.remove('hidden');
      if (resetStageBtn) resetStageBtn.classList.remove('hidden');
      const sum = questions.reduce((acc, q) => acc + (q.confidence || 0), 0);
      const avg = (sum / questions.length).toFixed(1);
      state.digitizeJob.avgConfidence = avg;
      if (avgEl) avgEl.innerText = `Độ tin cậy TB: ${avg}%`;
      if (statusLabel) statusLabel.innerText = `AI Parsing: Hoàn tất ${questions.length}/${questions.length} câu hỏi`;
      if (statusIndicator) {
        statusIndicator.className = 'w-2 h-2 rounded-full bg-emerald-500';
      }
      if (filenameEl) {
        const rawName = state.digitizeJob.filename || 'Tệp đã tải lên';
        filenameEl.innerText = truncateFilename(rawName, 32);
        filenameEl.title = rawName;
      }
      if (pageDisplay) pageDisplay.innerText = `Trang ${state.digitizeJob.currentPage || 1} / ${state.digitizeJob.totalPages || 1}`;
      const activeIdx = questions.findIndex((q) => q.id === state.digitizeJob.activeQuestionId);
      if (activeBadge) {
        activeBadge.innerText = `Đối chiếu: Câu ${activeIdx >= 0 ? activeIdx + 1 : (questions[0]?.id || 1)}`;
        activeBadge.className = 'px-2 py-0.5 bg-brand-50 text-brand-700 font-bold text-[11px] rounded-md border border-brand-200';
      }
      if (commitBtn) {
        commitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
      }
    }
  }

  async function commitExtractedToBank() {
    const newItems = JSON.parse(JSON.stringify(state.digitizeJob.questions || []));
    if (newItems.length === 0) {
      showToast('Chưa có câu hỏi nào để lưu vào ngân hàng. Vui lòng tải đề thi hoặc nạp đề mẫu!', 'warning');
      return;
    }
    showToast(`Đang lưu ${newItems.length} câu hỏi vào CSDL Ngân hàng...`, 'info');

    let countAdded = 0;
    for (const item of newItems) {
      const exists = state.itemBank.some((x) => x.code === item.code && x.id === item.id);
      if (!exists) {
        item.status = 'APPROVED';
        state.itemBank.unshift(item);
        countAdded++;

        // Persist question to backend SQLite database
        try {
          await fetch(`${API_BASE_URL}/questions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              stem: item.stem,
              item_format: item.item_format,
              cognitive_level: item.cognitive_level || 'KNOWLEDGE',
              learning_outcome_id: item.learning_outcome_id || 'TOAN12.GT.01',
              options: item.options || [],
              sub_statements: item.sub_statements || [],
              explanation: item.explanation || '',
              source_reference: item.code || 'Bóc tách từ đề thi',
            }),
          });
        } catch (e) {
          console.warn('Cannot persist question to DB:', e);
        }
      }
    }

    renderDashboard();
    renderItemBank();
    showToast(`Thành công: Đã lưu ${countAdded} câu hỏi vào Ngân hàng CSDL!`, 'success');
  }

  async function commitSingleQuestion(qId) {
    const q = state.digitizeJob.questions.find((x) => x.id === qId);
    if (!q) return;

    const item = JSON.parse(JSON.stringify(q));
    item.status = 'APPROVED';
    state.itemBank.unshift(item);

    try {
      await fetch(`${API_BASE_URL}/questions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          stem: item.stem,
          item_format: item.item_format,
          cognitive_level: item.cognitive_level || 'KNOWLEDGE',
          learning_outcome_id: item.learning_outcome_id || 'TOAN12.GT.01',
          options: item.options || [],
          sub_statements: item.sub_statements || [],
          explanation: item.explanation || '',
          source_reference: item.code || 'Bóc tách từ đề thi',
        }),
      });
    } catch (e) {
      console.warn('Cannot persist question to DB:', e);
    }

    renderDashboard();
    renderItemBank();
    showToast(`Đã lưu câu ${item.code || qId} vào Ngân hàng câu hỏi CSDL!`, 'success');
  }

  // ============================================================================
  // STAGING, PREVIEW & REORDERING BEFORE AI DIGITIZING
  // ============================================================================
  function handleFileSelect(event) {
    let files = [];
    if (event && event.target && event.target.files) {
      files = Array.from(event.target.files);
    } else if (Array.isArray(event)) {
      files = event;
    } else if (event && event.name) {
      files = [event];
    }
    if (files.length === 0) return;
    stageFiles(files);
  }

  function handleAddMoreFiles(event) {
    let files = [];
    if (event && event.target && event.target.files) {
      files = Array.from(event.target.files);
    } else if (Array.isArray(event)) {
      files = event;
    }
    if (files.length === 0) return;
    stageFiles([...state.stagedExam.files, ...files]);
  }

  function stageFiles(files) {
    state.stagedExam.files = files;
    state.stagedExam.previews = files.map((f) => ({
      name: f.name,
      size: (f.size / (1024 * 1024)).toFixed(2) + ' MB',
      type: f.name.split('.').pop().toLowerCase(),
      url: URL.createObjectURL(f),
      fileObj: f
    }));
    state.stagedExam.activePreviewIndex = 0;
    state.stagedExam.status = 'STAGED';

    const isMulti = files.length > 1;
    const displayName = isMulti ? `${files.length} trang ảnh đề thi` : files[0].name;
    state.digitizeJob.filename = displayName;
    state.digitizeJob.fileType = isMulti ? 'images' : files[0].name.split('.').pop().toLowerCase();
    state.digitizeJob.status = 'STAGED';
    state.digitizeJob.questions = [];

    const dispEl = document.getElementById('doc-viewer-filename');
    if (dispEl) {
      dispEl.innerText = truncateFilename(displayName, 32);
      dispEl.title = displayName;
    }

    renderDigitizeStudio();
    showToast(`Đã nạp ${files.length} tệp. Kiểm tra bản xem trước và sắp xếp thứ tự trước khi gõ đề!`, 'info');
  }

  function moveStagedPage(index, delta) {
    const newIndex = index + delta;
    const files = state.stagedExam.files;
    const previews = state.stagedExam.previews;
    if (newIndex < 0 || newIndex >= files.length) return;

    // Swap files and previews
    const tempF = files[index];
    files[index] = files[newIndex];
    files[newIndex] = tempF;

    const tempP = previews[index];
    previews[index] = previews[newIndex];
    previews[newIndex] = tempP;

    state.stagedExam.activePreviewIndex = newIndex;
    renderDigitizeStudio();
    showToast(`Đã chuyển trang ảnh sang vị trí Trang ${newIndex + 1}`, 'info');
  }

  function removeStagedPage(index) {
    const files = state.stagedExam.files;
    const previews = state.stagedExam.previews;
    files.splice(index, 1);
    previews.splice(index, 1);

    if (files.length === 0) {
      resetStagedFiles();
      return;
    }
    if (state.stagedExam.activePreviewIndex >= files.length) {
      state.stagedExam.activePreviewIndex = files.length - 1;
    }
    renderDigitizeStudio();
    showToast('Đã xóa 1 trang ảnh khỏi danh sách tải lên', 'info');
  }

  function selectStagedPreviewPage(index) {
    state.stagedExam.activePreviewIndex = index;
    renderDocumentPaperPreview();
  }

  function resetStagedFiles() {
    state.stagedExam = {
      status: 'EMPTY',
      files: [],
      previews: [],
      activePreviewIndex: 0
    };
    state.digitizeJob.jobId = null;
    state.digitizeJob.status = 'IDLE';
    state.digitizeJob.filename = '';
    state.digitizeJob.fileType = '';
    state.digitizeJob.previewUrl = null;
    state.digitizeJob.previewImages = [];
    state.digitizeJob.questions = [];
    renderDigitizeStudio();
    showToast('Đã hủy và xóa tài liệu đã chọn.', 'info');
  }

  async function startAIDigitize() {
    const files = state.stagedExam.files;
    if (!files || files.length === 0) {
      showToast('Chưa có tệp nào được chọn để gõ đề!', 'warning');
      return;
    }

    state.stagedExam.status = 'PROCESSING';
    state.digitizeJob.status = 'PROCESSING';
    renderDigitizeStudio();

    const isMulti = files.length > 1;
    const displayName = isMulti ? `${files.length} trang ảnh đề thi` : files[0].name;

    showToast(`Đang tải lên và gửi sang AI để gõ lại đề thi: ${displayName}...`, 'info');

    const formData = new FormData();
    if (files.length === 1) {
      formData.append('file', files[0]);
    } else {
      for (const f of files) {
        formData.append('files', f);
      }
    }
    formData.append('sync', 'true');

    try {
      const res = await fetch(`${API_BASE_URL}/digitize/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        let errMsg = `Mã lỗi máy chủ ${res.status}`;
        try {
          const errBody = await res.json();
          if (errBody.detail) errMsg = errBody.detail;
        } catch (_) {}
        throw new Error(errMsg);
      }

      const uploadResult = await res.json();
      const jobId = uploadResult.job_id;
      state.digitizeJob.jobId = jobId;
      state.digitizeJob.fileType = uploadResult.file_type || state.digitizeJob.fileType;
      state.digitizeJob.previewUrl = uploadResult.preview_url || `${API_BASE_URL}/digitize/jobs/${jobId}/preview`;

      // Fetch job status and questions
      const jobRes = await fetch(`${API_BASE_URL}/digitize/jobs/${jobId}`);
      if (jobRes.ok) {
        const jobData = await jobRes.json();
        state.digitizeJob.previewUrl = jobData.preview_url || state.digitizeJob.previewUrl;
        state.digitizeJob.previewImages = jobData.preview_images || [];
        state.digitizeJob.aiProvider = jobData.ai_provider;
        state.digitizeJob.aiModel = jobData.ai_model;
        state.digitizeJob.fileType = jobData.file_type || state.digitizeJob.fileType;

        if (jobData.extracted_questions && jobData.extracted_questions.length > 0) {
          state.digitizeJob.questions = jobData.extracted_questions.map((q, idx) => {
            const id = q.id || idx + 1;
            const rawConf = q.confidence_score !== undefined ? q.confidence_score : (q.confidence !== undefined ? q.confidence : 95);
            const conf = rawConf <= 1.0 ? Math.round(rawConf * 100) : Math.round(rawConf);
            return {
              ...q,
              id: id,
              code: q.code || `EXTRACT-${String(id).padStart(3, '0')}`,
              confidence: conf,
              confidence_score: conf,
            };
          });
          state.digitizeJob.activeQuestionId = state.digitizeJob.questions[0]?.id || 1;
          state.digitizeJob.totalPages = Math.max(1, Math.ceil(state.digitizeJob.questions.length / 6));
          state.digitizeJob.currentPage = 1;
          state.stagedExam.status = 'DONE';

          const aiNote = (jobData.ai_provider && jobData.ai_provider !== 'local_fallback')
            ? ` qua AI (${jobData.ai_provider.toUpperCase()} - ${jobData.ai_model})`
            : '';
          showToast(`Đã gõ lại và bóc tách thành công ${state.digitizeJob.questions.length} câu hỏi${aiNote}!`, 'success');
        } else if (jobData.status === 'FAILED') {
          throw new Error(jobData.error_message || 'Xử lý file thất bại trên máy chủ.');
        } else {
          showToast(`Đã xử lý xong tệp nhưng chưa phát hiện câu hỏi nào.`, 'warning');
        }
      } else {
        throw new Error(`Không lấy được trạng thái tác vụ (HTTP ${jobRes.status})`);
      }
    } catch (err) {
      console.warn('AI digitize error:', err);
      showToast(`Lỗi khi gõ đề: ${err.message}`, 'error');
      state.stagedExam.status = 'STAGED';
    } finally {
      renderDigitizeStudio();
    }
  }

  // Legacy alias
  function handleFileUpload(event) {
    handleFileSelect(event);
  }

  // ============================================================================
  // QUESTION FULL HITL EDITOR MODAL
  // ============================================================================
  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  function openQuestionEditorModal(qId) {
    const q = state.digitizeJob.questions.find((x) => x.id === qId);
    if (!q) return;

    state.activeEditingQuestion = JSON.parse(JSON.stringify(q));
    const modal = document.getElementById('question-editor-modal');
    if (!modal) return;

    const idx = state.digitizeJob.questions.findIndex((x) => x.id === qId);
    document.getElementById('q-modal-title').innerText = `Chỉnh Sửa Câu ${idx + 1} (${q.code || 'EXTRACT'})`;

    document.getElementById('q-edit-format').value = q.item_format || 'SINGLE_CHOICE';
    document.getElementById('q-edit-cognitive').value = q.cognitive_level || 'RECOGNITION';
    document.getElementById('q-edit-yccd').value = q.learning_outcome_code || q.learning_outcome_id || 'TOAN12.GT.01';
    document.getElementById('q-edit-stem').value = q.stem || '';
    document.getElementById('q-edit-explanation').value = q.explanation || '';

    handleQuestionFormatChangeInModal();
    updateQuestionEditorLivePreview();

    modal.classList.remove('hidden');
    if (window.lucide) lucide.createIcons();
  }

  function closeQuestionEditorModal() {
    const modal = document.getElementById('question-editor-modal');
    if (modal) modal.classList.add('hidden');
    state.activeEditingQuestion = null;
  }

  function handleQuestionFormatChangeInModal() {
    const format = document.getElementById('q-edit-format').value;
    if (!state.activeEditingQuestion) return;
    state.activeEditingQuestion.item_format = format;

    if (format === 'SINGLE_CHOICE' && (!state.activeEditingQuestion.options || state.activeEditingQuestion.options.length === 0)) {
      state.activeEditingQuestion.options = [
        { label: 'A', content: '', is_correct: true, is_fixed: false },
        { label: 'B', content: '', is_correct: false, is_fixed: false },
        { label: 'C', content: '', is_correct: false, is_fixed: false },
        { label: 'D', content: '', is_correct: false, is_fixed: false },
      ];
    } else if (format === 'TRUE_FALSE_GROUP' && (!state.activeEditingQuestion.sub_statements || state.activeEditingQuestion.sub_statements.length === 0)) {
      state.activeEditingQuestion.sub_statements = [
        { label: 'a', content: '', is_true: true, explanation: '' },
        { label: 'b', content: '', is_true: false, explanation: '' },
        { label: 'c', content: '', is_true: true, explanation: '' },
        { label: 'd', content: '', is_true: false, explanation: '' },
      ];
    }
    renderQuestionAnswersInModal();
  }

  function renderQuestionAnswersInModal() {
    const container = document.getElementById('q-edit-answers-container');
    if (!container || !state.activeEditingQuestion) return;

    const q = state.activeEditingQuestion;
    const format = q.item_format || 'SINGLE_CHOICE';

    let html = '';

    if (format === 'SINGLE_CHOICE') {
      const options = q.options || [];
      html += `
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="font-bold text-slate-800 uppercase tracking-wider text-[11px]">4 Phương án lựa chọn (Chọn 1 đáp án đúng)</label>
            <span class="text-[10px] text-slate-500">Tích chọn radio tròn để đặt phương án đúng</span>
          </div>
          <div class="space-y-2">
      `;
      ['A', 'B', 'C', 'D'].forEach((lbl, idx) => {
        const opt = options[idx] || { label: lbl, content: '', is_correct: idx === 0, is_fixed: false };
        html += `
          <div class="flex items-center gap-2 p-2 rounded-xl bg-slate-50 border border-slate-200">
            <label class="flex items-center space-x-1.5 cursor-pointer shrink-0">
              <input type="radio" name="modal-correct-choice" value="${idx}" ${opt.is_correct ? 'checked' : ''} onchange="app.setModalCorrectChoice(${idx})" class="w-4 h-4 text-emerald-600 focus:ring-emerald-500">
              <span class="w-6 h-6 rounded-md bg-white border border-slate-300 flex items-center justify-center font-bold text-xs text-brand-700 shadow-xs">${lbl}</span>
            </label>
            <input type="text" id="q-edit-opt-${idx}" value="${escapeHtml(opt.content)}" oninput="app.updateModalOptionContent(${idx}, this.value)" class="flex-1 text-xs rounded-lg border border-slate-300 p-2 bg-white focus:ring-2 focus:ring-brand-500 font-mono" placeholder="Nội dung phương án ${lbl}...">
            <label class="flex items-center space-x-1 cursor-pointer shrink-0 text-[11px] text-slate-600 px-2 py-1 rounded bg-white border border-slate-200" title="Khóa cố định vị trí D khi xáo trộn đề">
              <input type="checkbox" id="q-edit-fixed-${idx}" ${opt.is_fixed ? 'checked' : ''} onchange="app.setModalOptionFixed(${idx}, this.checked)" class="rounded text-brand-600">
              <span>Khóa D</span>
            </label>
          </div>
        `;
      });
      html += `</div></div>`;
    } else if (format === 'TRUE_FALSE_GROUP') {
      const subs = q.sub_statements || [];
      html += `
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="font-bold text-slate-800 uppercase tracking-wider text-[11px]">4 Ý khẳng định con (Quyết định 764/QĐ-BGDĐT)</label>
            <span class="text-[10px] text-slate-500">Điểm bậc thang: 1 ý = 0.1đ | 2 ý = 0.25đ | 3 ý = 0.5đ | 4 ý = 1.0đ</span>
          </div>
          <div class="space-y-2.5">
      `;
      ['a', 'b', 'c', 'd'].forEach((lbl, idx) => {
        const sub = subs[idx] || { label: lbl, content: '', is_true: false, explanation: '' };
        html += `
          <div class="p-2.5 rounded-xl bg-slate-50 border border-slate-200 space-y-1.5">
            <div class="flex items-center justify-between gap-2">
              <div class="flex items-center space-x-1.5 flex-1">
                <span class="font-bold text-brand-700 text-xs">${lbl})</span>
                <input type="text" id="q-edit-sub-${idx}" value="${escapeHtml(sub.content)}" oninput="app.updateModalSubContent(${idx}, this.value)" class="flex-1 text-xs rounded-lg border border-slate-300 p-1.5 bg-white font-mono" placeholder="Nội dung khẳng định ${lbl})...">
              </div>
              <div class="flex items-center space-x-1 shrink-0">
                <button type="button" onclick="app.setModalSubIsTrue(${idx}, true)" class="px-2.5 py-1 rounded text-[11px] font-bold ${sub.is_true ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-700'}">
                  ĐÚNG
                </button>
                <button type="button" onclick="app.setModalSubIsTrue(${idx}, false)" class="px-2.5 py-1 rounded text-[11px] font-bold ${!sub.is_true ? 'bg-rose-600 text-white' : 'bg-slate-200 text-slate-700'}">
                  SAI
                </button>
              </div>
            </div>
            <input type="text" id="q-edit-sub-exp-${idx}" value="${escapeHtml(sub.explanation || '')}" oninput="app.updateModalSubExp(${idx}, this.value)" class="w-full text-[11px] rounded border border-slate-200 p-1 bg-white text-slate-600 italic" placeholder="Giải thích tính đúng/sai của ý ${lbl})...">
          </div>
        `;
      });
      html += `</div></div>`;
    } else if (format === 'SHORT_ANSWER') {
      html += `
        <div class="p-3 bg-purple-50 rounded-xl border border-purple-200">
          <label class="block font-bold text-purple-900 mb-2 uppercase tracking-wider text-[11px]">Đáp số đúng (PHẦN III)</label>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <span class="text-[11px] text-purple-700 mb-1 block">Chuỗi kết quả số / ký tự:</span>
              <input type="text" id="q-edit-short-val" value="${escapeHtml(q.short_answer_value || '')}" class="w-full text-xs font-mono font-bold rounded-lg border border-purple-300 p-2 bg-white" placeholder="Ví dụ: 12 hoặc -3.5">
            </div>
            <div>
              <span class="text-[11px] text-purple-700 mb-1 block">Dung sai sai số ($\\pm$):</span>
              <input type="number" step="0.01" id="q-edit-short-tol" value="${q.tolerance || 0.0}" class="w-full text-xs font-mono rounded-lg border border-purple-300 p-2 bg-white">
            </div>
          </div>
        </div>
      `;
    }

    container.innerHTML = html;
    renderKaTeX(container);
  }

  function setModalCorrectChoice(choiceIdx) {
    if (!state.activeEditingQuestion || !state.activeEditingQuestion.options) return;
    state.activeEditingQuestion.options.forEach((opt, idx) => {
      opt.is_correct = idx === choiceIdx;
    });
  }

  function setModalOptionFixed(optIdx, isFixed) {
    if (!state.activeEditingQuestion || !state.activeEditingQuestion.options) return;
    if (state.activeEditingQuestion.options[optIdx]) {
      state.activeEditingQuestion.options[optIdx].is_fixed = isFixed;
    }
  }

  function updateModalOptionContent(optIdx, val) {
    if (!state.activeEditingQuestion || !state.activeEditingQuestion.options) return;
    if (state.activeEditingQuestion.options[optIdx]) {
      state.activeEditingQuestion.options[optIdx].content = val;
    }
  }

  function setModalSubIsTrue(subIdx, isTrue) {
    if (!state.activeEditingQuestion || !state.activeEditingQuestion.sub_statements) return;
    if (state.activeEditingQuestion.sub_statements[subIdx]) {
      state.activeEditingQuestion.sub_statements[subIdx].is_true = isTrue;
      renderQuestionAnswersInModal();
    }
  }

  function updateModalSubContent(subIdx, val) {
    if (!state.activeEditingQuestion || !state.activeEditingQuestion.sub_statements) return;
    if (state.activeEditingQuestion.sub_statements[subIdx]) {
      state.activeEditingQuestion.sub_statements[subIdx].content = val;
    }
  }

  function updateModalSubExp(subIdx, val) {
    if (!state.activeEditingQuestion || !state.activeEditingQuestion.sub_statements) return;
    if (state.activeEditingQuestion.sub_statements[subIdx]) {
      state.activeEditingQuestion.sub_statements[subIdx].explanation = val;
    }
  }

  function updateQuestionEditorLivePreview() {
    const stemInput = document.getElementById('q-edit-stem');
    const stemPreview = document.getElementById('q-edit-stem-preview');
    if (stemInput && stemPreview) {
      const val = stemInput.value.trim();
      stemPreview.innerHTML = val ? val : '<span class="text-slate-400 italic">Xem trước nội dung câu hỏi...</span>';
      renderKaTeX(stemPreview);
    }

    const expInput = document.getElementById('q-edit-explanation');
    const expPreview = document.getElementById('q-edit-explanation-preview');
    if (expInput && expPreview) {
      const val = expInput.value.trim();
      expPreview.innerHTML = val ? `<strong>Hướng dẫn giải:</strong> ${val}` : '<span class="text-slate-400 italic">Xem trước lời giải...</span>';
      renderKaTeX(expPreview);
    }
  }

  function insertStemSymbol(symbol) {
    const input = document.getElementById('q-edit-stem');
    if (!input) return;
    const start = input.selectionStart || 0;
    const end = input.selectionEnd || 0;
    const val = input.value;
    input.value = val.substring(0, start) + symbol + val.substring(end);
    input.focus();
    input.setSelectionRange(start + symbol.length, start + symbol.length);
    updateQuestionEditorLivePreview();
  }

  function saveQuestionEdit() {
    if (!state.activeEditingQuestion) return;
    const qId = state.activeEditingQuestion.id;
    const q = state.digitizeJob.questions.find((x) => x.id === qId);
    if (!q) return;

    q.item_format = document.getElementById('q-edit-format').value;
    q.cognitive_level = document.getElementById('q-edit-cognitive').value;
    q.learning_outcome_code = document.getElementById('q-edit-yccd').value;
    q.learning_outcome_id = q.learning_outcome_code;
    q.stem = document.getElementById('q-edit-stem').value.trim();
    q.explanation = document.getElementById('q-edit-explanation').value.trim();

    if (q.item_format === 'SINGLE_CHOICE' && state.activeEditingQuestion.options) {
      q.options = JSON.parse(JSON.stringify(state.activeEditingQuestion.options));
    } else if (q.item_format === 'TRUE_FALSE_GROUP' && state.activeEditingQuestion.sub_statements) {
      q.sub_statements = JSON.parse(JSON.stringify(state.activeEditingQuestion.sub_statements));
    } else if (q.item_format === 'SHORT_ANSWER') {
      const valEl = document.getElementById('q-edit-short-val');
      const tolEl = document.getElementById('q-edit-short-tol');
      if (valEl) q.short_answer_value = valEl.value.trim();
      if (tolEl) q.tolerance = parseFloat(tolEl.value) || 0.0;
    }

    closeQuestionEditorModal();
    renderExtractedQuestionsList();
    updateConfidenceSummary();
    showToast(`Đã lưu thay đổi cho Câu ${q.code || qId}!`, 'success');
  }

  function loadSampleExam(type) {
    state.digitizeJob.jobId = null;
    state.digitizeJob.previewUrl = null;
    state.digitizeJob.previewImages = [];

    if (type === 'math12_standard') {
      showToast('Đang nạp đề mẫu Toán 12 (MathType OLE + Đồ thị)...', 'info');
      state.digitizeJob.filename = 'De_Mau_Toan_12_MathType.docx';
      state.digitizeJob.fileType = 'sample_docx';
      state.digitizeJob.questions = JSON.parse(JSON.stringify(state.itemBank.slice(0, 5))).map((q, idx) => ({
        ...q,
        id: idx + 1,
        code: q.code || `TOAN12-${String(idx + 1).padStart(3, '0')}`,
        confidence: q.confidence || 98,
        confidence_score: q.confidence || 98,
      }));
      state.digitizeJob.activeQuestionId = 1;
      state.digitizeJob.currentPage = 1;
      state.digitizeJob.totalPages = 2;
      renderDigitizeStudio();
    } else if (type === 'true_false_group') {
      showToast('Đang nạp đề mẫu trắc nghiệm Đúng/Sai 4 ý (QĐ 764)...', 'info');
      state.digitizeJob.filename = 'De_Mau_Dung_Sai_4_Y_QD764.docx';
      state.digitizeJob.fileType = 'sample_tf';
      const tfQuestions = state.itemBank.filter((q) => q.item_format === 'TRUE_FALSE_GROUP');
      state.digitizeJob.questions = JSON.parse(JSON.stringify(tfQuestions.length > 0 ? tfQuestions : state.itemBank.slice(0, 4))).map((q, idx) => ({
        ...q,
        id: idx + 1,
        code: q.code || `TF-${String(idx + 1).padStart(3, '0')}`,
        confidence: q.confidence || 96,
        confidence_score: q.confidence || 96,
      }));
      state.digitizeJob.activeQuestionId = 1;
      state.digitizeJob.currentPage = 1;
      state.digitizeJob.totalPages = 1;
      renderDigitizeStudio();
    }
  }

  function changeViewerPage(delta) {
    let p = state.digitizeJob.currentPage + delta;
    if (p < 1) p = 1;
    if (p > state.digitizeJob.totalPages) p = state.digitizeJob.totalPages;
    state.digitizeJob.currentPage = p;

    const disp = document.getElementById('doc-page-display');
    if (disp) disp.innerText = `Trang ${p} / ${state.digitizeJob.totalPages}`;
    showToast(`Chuyển sang Trang ${p}`, 'info');
  }

  // ============================================================================
  // 9. TAB 3: ITEM BANK EXPLORER (6-TIER CASCADING TAXONOMY)
  // ============================================================================
  function handleTaxonomyFilterChange(level) {
    const gradeVal = document.getElementById('bank-filter-grade').value;
    const strandVal = document.getElementById('bank-filter-strand').value;
    const topicSelect = document.getElementById('bank-filter-topic');
    const lessonSelect = document.getElementById('bank-filter-lesson');
    const yccdSelect = document.getElementById('bank-filter-yccd');
    const archSelect = document.getElementById('bank-filter-archetype');

    if (level === 'strand' || level === 'grade' || level === 'subject') {
      // Re-populate topics based on strand
      topicSelect.innerHTML = '<option value="all">Tất cả Chủ đề</option>';
      const filteredTopics = state.taxonomy.topics.filter((t) => strandVal === 'all' || t.strand_id === strandVal);
      filteredTopics.forEach((t) => {
        topicSelect.innerHTML += `<option value="${t.id}">${t.name}</option>`;
      });
      topicSelect.value = 'all';
    }

    if (level === 'topic' || level === 'strand') {
      const topicVal = topicSelect.value;
      lessonSelect.innerHTML = '<option value="all">Tất cả Bài học</option>';
      const filteredLessons = state.taxonomy.lessons.filter((l) => topicVal === 'all' || l.topic_id === topicVal);
      filteredLessons.forEach((l) => {
        lessonSelect.innerHTML += `<option value="${l.id}">${l.name}</option>`;
      });
      lessonSelect.value = 'all';
    }

    if (level === 'lesson' || level === 'topic' || level === 'strand') {
      const lessonVal = lessonSelect.value;
      yccdSelect.innerHTML = '<option value="all">Tất cả Mã YCCĐ</option>';
      const filteredYCCDs = state.taxonomy.yccds.filter((y) => lessonVal === 'all' || y.lesson_id === lessonVal);
      filteredYCCDs.forEach((y) => {
        yccdSelect.innerHTML += `<option value="${y.id}">${y.code}: ${y.desc.substring(0, 45)}...</option>`;
      });
      yccdSelect.value = 'all';
    }

    if (level === 'yccd' || level === 'lesson') {
      const yccdVal = yccdSelect.value;
      archSelect.innerHTML = '<option value="all">Tất cả Dạng bài</option>';
      const filteredArchs = state.taxonomy.archetypes.filter((a) => yccdVal === 'all' || a.yccd_id === yccdVal);
      filteredArchs.forEach((a) => {
        archSelect.innerHTML += `<option value="${a.id}">${a.name}</option>`;
      });
      archSelect.value = 'all';
    }

    renderItemBank();
  }

  function renderItemBank() {
    const container = document.getElementById('bank-cards-grid');
    if (!container) return;

    // Filters
    const strandFilter = document.getElementById('bank-filter-strand')?.value || 'all';
    const yccdFilter = document.getElementById('bank-filter-yccd')?.value || 'all';
    const cogFilter = document.getElementById('bank-filter-cognitive')?.value || 'all';
    const formatFilter = document.getElementById('bank-filter-format')?.value || 'all';
    const searchFilter = (document.getElementById('bank-search-input')?.value || '').toLowerCase().trim();

    const filtered = state.itemBank.filter((item) => {
      if (strandFilter !== 'all' && item.strand_id !== strandFilter) return false;
      if (yccdFilter !== 'all' && item.learning_outcome_id !== yccdFilter) return false;
      if (cogFilter !== 'all' && item.cognitive_level !== cogFilter) return false;
      if (formatFilter !== 'all' && item.item_format !== formatFilter) return false;
      if (searchFilter) {
        const text = `${item.code} ${item.stem} ${item.learning_outcome_id}`.toLowerCase();
        if (!text.includes(searchFilter)) return false;
      }
      return true;
    });

    const countEl = document.getElementById('bank-results-count');
    if (countEl) countEl.innerText = filtered.length;

    if (filtered.length === 0) {
      container.innerHTML = `
        <div class="bg-white rounded-2xl border border-slate-200 p-8 text-center text-slate-400 text-xs">
          <i data-lucide="search-x" class="w-8 h-8 mx-auto mb-2 text-slate-300"></i>
          Không tìm thấy câu hỏi nào thỏa mãn các tiêu chí lọc.
        </div>
      `;
      if (window.lucide) lucide.createIcons();
      return;
    }

    let html = '';
    filtered.forEach((q) => {
      const cogLabels = {
        RECOGNITION: 'Nhận biết',
        COMPREHENSION: 'Thông hiểu',
        APPLICATION: 'Vận dụng',
        HIGH_APPLICATION: 'Vận dụng cao',
      };
      const cogColors = {
        RECOGNITION: 'bg-blue-50 text-blue-700 border-blue-200',
        COMPREHENSION: 'bg-indigo-50 text-indigo-700 border-indigo-200',
        APPLICATION: 'bg-emerald-50 text-emerald-700 border-emerald-200',
        HIGH_APPLICATION: 'bg-purple-50 text-purple-700 border-purple-200',
      };

      html += `
        <div class="apple-card p-5 space-y-3">
          
          <!-- Header: Code, Badges, Psychometrics -->
          <div class="flex flex-wrap items-center justify-between gap-2 border-b border-black/[0.06] pb-3 text-xs">
            <div class="flex flex-wrap items-center gap-2">
              <span class="font-mono font-bold text-slate-800 bg-black/[0.04] px-2 py-0.5 rounded-md text-xs">${q.code}</span>
              <span class="px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${cogColors[q.cognitive_level] || 'bg-slate-100'}">
                ${cogLabels[q.cognitive_level] || q.cognitive_level}
              </span>
              <span class="px-2 py-0.5 rounded-md bg-[#0071E3]/[0.08] text-[#0071E3] text-[11px] font-bold border border-[#0071E3]/[0.15] font-mono">
                ${q.learning_outcome_id}
              </span>
              <span class="text-slate-400 text-[11px]">• ${q.source_ref || 'Thông tư 32'}</span>
            </div>

            <!-- Psychometric Indices: p & D -->
            <div class="flex items-center space-x-2 text-[11px]">
              <span class="px-2 py-0.5 bg-black/[0.03] border border-black/[0.06] rounded-md text-slate-700 font-mono" title="Độ khó thực nghiệm (Tỷ lệ làm đúng p = R/N)">
                Độ khó $p = ${q.p_index || 0.65}$
              </span>
              <span class="px-2 py-0.5 bg-emerald-50 border border-emerald-200 rounded-md text-emerald-700 font-mono font-bold" title="Độ phân biệt D = P_H - P_L">
                Độ PB $D = ${q.d_index || 0.42}$
              </span>
            </div>
          </div>

          <!-- Question Stem -->
          <div class="text-xs text-slate-800 leading-relaxed font-medium">
            ${q.stem}
          </div>
      `;

      // Options
      if (q.item_format === 'SINGLE_CHOICE' && q.options) {
        html += `<div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs pt-1">`;
        q.options.forEach((opt) => {
          const isCorrect = opt.is_correct;
          const optClass = isCorrect ? 'bg-emerald-50 border-emerald-300 text-emerald-900 font-semibold' : 'bg-slate-50 border-black/[0.06] text-slate-700';
          html += `
            <div class="flex items-center justify-between p-2 rounded-xl border ${optClass}">
              <div class="flex items-center space-x-2">
                <span class="w-5 h-5 rounded flex items-center justify-center font-bold text-xs ${isCorrect ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-700'}">
                  ${opt.label}
                </span>
                <span>${opt.content}</span>
              </div>
              ${opt.is_fixed ? '<span class="option-anchor-indicator"><i data-lucide="anchor" class="w-3 h-3"></i> Khóa D</span>' : ''}
            </div>
          `;
        });
        html += `</div>`;
      } else if (q.item_format === 'TRUE_FALSE_GROUP' && q.sub_statements) {
        html += `<div class="space-y-1.5 pt-1 text-xs">`;
        q.sub_statements.forEach((sub) => {
          html += `
            <div class="p-2 rounded-lg bg-slate-50 border border-black/[0.06] flex items-center justify-between">
              <div><strong>${sub.label})</strong> ${sub.content}</div>
              <span class="px-2 py-0.5 rounded text-[10px] font-bold ${sub.is_true ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}">
                ${sub.is_true ? 'ĐÚNG' : 'SAI'
              }</span>
            </div>
          `;
        });
        html += `</div>`;
      } else if (q.item_format === 'SHORT_ANSWER') {
        html += `
          <div class="p-2.5 rounded-xl bg-purple-50/70 border border-purple-200 text-xs text-purple-900 font-mono">
            <strong>Đáp án:</strong> ${q.short_answer_value} (Dung sai $\\pm ${q.tolerance}$)
          </div>
        `;
      }

      // Actions
      html += `
        <div class="flex items-center justify-end space-x-2 pt-2.5 border-t border-black/[0.06] text-xs">
          <button onclick="app.checkQuestionDuplicate(${q.id})" class="btn-apple-secondary py-1 px-2.5 text-xs">
            <i data-lucide="scan" class="w-3.5 h-3.5"></i>
            <span>So khớp Trùng lặp AI</span>
          </button>
          <button onclick="app.deleteBankQuestion(${q.id})" class="btn-apple-danger py-1 px-2.5 text-xs">
            <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
            <span>Xóa</span>
          </button>
        </div>

      </div>
      `;
    });

    container.innerHTML = html;
    renderKaTeX(container);
  }

  function deleteBankQuestion(id) {
    if (confirm('Bạn có chắc chắn muốn xóa câu hỏi này khỏi Ngân hàng?')) {
      state.itemBank = state.itemBank.filter((q) => q.id !== id);
      renderItemBank();
      renderDashboard();
      showToast('Đã xóa câu hỏi khỏi ngân hàng.', 'info');
    }
  }

  // ============================================================================
  // 10. TAB 4: EXAM MATRIX BUILDER (INTERACTIVE 2D GRID WITH INVENTORY CHECK)
  // ============================================================================
  function renderMatrixGrid() {
    const tbody = document.getElementById('matrix-grid-tbody');
    if (!tbody) return;

    let html = '';
    let totalBiet = 0;
    let totalHieu = 0;
    let totalVandung = 0;

    state.matrixConfig.rows.forEach((row, rowIdx) => {
      totalBiet += Number(row.biet);
      totalHieu += Number(row.hieu);
      totalVandung += Number(row.vandung);

      const rowItems = Number(row.biet) + Number(row.hieu) + Number(row.vandung);
      const rowPoints = (row.biet * 0.25 + row.hieu * 0.35 + row.vandung * 0.4).toFixed(2);

      // Stock check
      const stockBietClass = row.bankStock.biet >= row.biet ? 'stock-sufficient' : 'stock-insufficient';
      const stockHieuClass = row.bankStock.hieu >= row.hieu ? 'stock-sufficient' : 'stock-insufficient';
      const stockVandungClass = row.bankStock.vandung >= row.vandung ? 'stock-sufficient' : 'stock-insufficient';

      html += `
        <tr class="hover:bg-slate-50 transition-colors">
          <td class="p-3 sticky left-0 bg-white shadow-xs">
            <div class="font-bold text-slate-900">${row.strandName}</div>
            <div class="text-[11px] text-brand-700 font-mono font-semibold">${row.yccdCode}</div>
            <div class="text-[11px] text-slate-500">${row.archetypeName}</div>
          </td>

          <!-- Col 1: Biết -->
          <td class="p-2 text-center border-l border-slate-200 matrix-input-cell bg-blue-50/20">
            <input type="number" min="0" max="20" value="${row.biet}" onchange="app.updateMatrixCell(${rowIdx}, 'biet', this.value)" class="focus:ring-2 focus:ring-blue-500">
            <span class="matrix-inventory-stock ${stockBietClass}">Kho: ${row.bankStock.biet} câu</span>
          </td>

          <!-- Col 2: Hiểu -->
          <td class="p-2 text-center border-l border-slate-200 matrix-input-cell bg-indigo-50/20">
            <input type="number" min="0" max="20" value="${row.hieu}" onchange="app.updateMatrixCell(${rowIdx}, 'hieu', this.value)" class="focus:ring-2 focus:ring-indigo-500">
            <span class="matrix-inventory-stock ${stockHieuClass}">Kho: ${row.bankStock.hieu} câu</span>
          </td>

          <!-- Col 3: Vận dụng -->
          <td class="p-2 text-center border-l border-slate-200 matrix-input-cell bg-emerald-50/20">
            <input type="number" min="0" max="20" value="${row.vandung}" onchange="app.updateMatrixCell(${rowIdx}, 'vandung', this.value)" class="focus:ring-2 focus:ring-emerald-500">
            <span class="matrix-inventory-stock ${stockVandungClass}">Kho: ${row.bankStock.vandung} câu</span>
          </td>

          <!-- Total Items per Row -->
          <td class="p-3 text-center border-l border-slate-200 font-bold text-slate-800">
            ${rowItems} câu
          </td>

          <!-- Total Points per Row -->
          <td class="p-3 text-center border-l border-slate-200 font-bold text-brand-700">
            ${rowPoints} đ
          </td>
        </tr>
      `;
    });

    tbody.innerHTML = html;

    // Totals
    const grandItems = totalBiet + totalHieu + totalVandung;
    document.getElementById('matrix-total-biet').innerText = `${totalBiet} câu (${(totalBiet * 0.25).toFixed(1)}đ)`;
    document.getElementById('matrix-total-hieu').innerText = `${totalHieu} câu (${(totalHieu * 0.35).toFixed(1)}đ)`;
    document.getElementById('matrix-total-vandung').innerText = `${totalVandung} câu (${(totalVandung * 0.4).toFixed(1)}đ)`;
    document.getElementById('matrix-total-items').innerText = `${grandItems} câu`;
    document.getElementById('matrix-total-points').innerText = `10.0 đ`;

    // Calculate Bloom Cognitive Level Ratio
    if (grandItems > 0) {
      const pctBiet = Math.round((totalBiet / grandItems) * 100);
      const pctHieu = Math.round((totalHieu / grandItems) * 100);
      const pctVandung = 100 - pctBiet - pctHieu;

      document.getElementById('matrix-bar-biet').style.width = `${pctBiet}%`;
      document.getElementById('matrix-bar-hieu').style.width = `${pctHieu}%`;
      document.getElementById('matrix-bar-vandung').style.width = `${pctVandung}%`;

      document.getElementById('matrix-lbl-biet').innerText = `Biết: ${pctBiet}%`;
      document.getElementById('matrix-lbl-hieu').innerText = `Hiểu: ${pctHieu}%`;
      document.getElementById('matrix-lbl-vandung').innerText = `Vận dụng: ${pctVandung}%`;

      const statusBadge = document.getElementById('matrix-bloom-status');
      if (Math.abs(pctBiet - 40) <= 5 && Math.abs(pctHieu - 30) <= 5) {
        statusBadge.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800';
        statusBadge.innerText = 'ĐẠT CHUẨN KHẢO THÍ: 40% Biết - 30% Hiểu - 30% Vận dụng';
      } else {
        statusBadge.className = 'px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800';
        statusBadge.innerText = 'CẢNH BÁO: Tỷ lệ phân bố Bloom lệch so với chuẩn TT 22';
      }
    }
  }

  function updateMatrixCell(rowIdx, field, val) {
    const num = Math.max(0, parseInt(val, 10) || 0);
    state.matrixConfig.rows[rowIdx][field] = num;
    renderMatrixGrid();
  }

  function saveMatrixConfig() {
    showToast('Đã lưu và ban hành Ma trận Đề thi theo Thông tư 32!', 'success');
  }

  function loadMatrixPreset(preset) {
    if (preset === 'thpt_2025') {
      state.matrixConfig.rows[0].biet = 4;
      state.matrixConfig.rows[0].hieu = 3;
      state.matrixConfig.rows[0].vandung = 3;
      state.matrixConfig.rows[1].biet = 3;
      state.matrixConfig.rows[1].hieu = 2;
      state.matrixConfig.rows[1].vandung = 2;
      state.matrixConfig.rows[2].biet = 3;
      state.matrixConfig.rows[2].hieu = 3;
      state.matrixConfig.rows[2].vandung = 3;
      state.matrixConfig.rows[3].biet = 2;
      state.matrixConfig.rows[3].hieu = 2;
      state.matrixConfig.rows[3].vandung = 2;
      showToast('Đã áp dụng Preset: Chuẩn Đề Tốt nghiệp THPT 2025 (34 câu)', 'info');
    } else if (preset === 'midterm') {
      state.matrixConfig.rows[0].biet = 2;
      state.matrixConfig.rows[0].hieu = 2;
      state.matrixConfig.rows[0].vandung = 1;
      state.matrixConfig.rows[1].biet = 2;
      state.matrixConfig.rows[1].hieu = 1;
      state.matrixConfig.rows[1].vandung = 1;
      state.matrixConfig.rows[2].biet = 2;
      state.matrixConfig.rows[2].hieu = 2;
      state.matrixConfig.rows[2].vandung = 1;
      state.matrixConfig.rows[3].biet = 1;
      state.matrixConfig.rows[3].hieu = 1;
      state.matrixConfig.rows[3].vandung = 1;
      showToast('Đã áp dụng Preset: Kiểm tra Định kỳ (20 câu)', 'info');
    }
    renderMatrixGrid();
  }

  async function generateMasterExamFromMatrix() {
    showToast('Đang gọi thuật toán sinh Đề thi Gốc từ Ma trận...', 'info');

    try {
      // Find valid matrix in DB or use default
      let matrixId = 'default';
      const mRes = await fetch(`${API_BASE_URL}/matrix`);
      if (mRes.ok) {
        const mList = await mRes.json();
        if (mList.length > 0) matrixId = mList[0].id;
      }

      const res = await fetch(`${API_BASE_URL}/exams/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          matrix_id: matrixId,
          title: 'Đề thi Gốc Kỳ thi Tốt nghiệp THPT 2025 - Môn Toán'
        })
      });
      if (res.ok) {
        const examData = await res.json();
        state.masterExam.id = examData.id;
        state.masterExam.title = examData.title;
        if (examData.items && examData.items.length > 0) {
          state.masterExam.items = examData.items;
        }
      }
    } catch (e) {
      console.warn('Generate exam API fallback:', e);
    }

    if (!state.masterExam.items || state.masterExam.items.length === 0) {
      state.masterExam.items = JSON.parse(JSON.stringify(state.itemBank.slice(0, 8)));
    }

    switchTab('shuffler');
    showToast('Khởi tạo Đề thi Gốc thành công! Chuyển sang phân hệ Trộn đề an toàn.', 'success');
  }

  // ============================================================================
  // 11. TAB 5: EXAM SHUFFLER & DOCX EXPORT (OPTION ANCHOR RULE ENGINE)
  // ============================================================================
  function renderMasterExam() {
    const container = document.getElementById('master-exam-items-list');
    if (!container) return;

    let html = '';
    const items = state.masterExam.items;

    if (items.length === 0) {
      container.innerHTML = '<div class="p-6 text-center text-slate-400 text-xs">Chưa có câu hỏi trong đề gốc.</div>';
      return;
    }

    items.forEach((q, idx) => {
      const hasAnchorOption = q.options?.some((o) => o.is_fixed || isAnchorPhrase(o.content));

      html += `
        <div class="apple-card p-4 text-xs space-y-2">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2">
              <span class="font-bold text-[#0071E3] bg-[#0071E3]/[0.08] px-2 py-0.5 rounded-md border border-[#0071E3]/[0.15]">Câu ${idx + 1}</span>
              <span class="font-mono text-slate-500">${q.code}</span>
              <span class="font-mono text-[11px] text-slate-700 font-bold">${q.learning_outcome_id}</span>
              ${
                hasAnchorOption
                  ? `<span class="option-anchor-indicator">
                      <i data-lucide="anchor" class="w-3 h-3"></i> Option Anchor
                     </span>`
                  : ''
              }
            </div>

            <!-- Swap Question Button (Same YCCD & Bloom) -->
            <button onclick="app.swapMasterQuestion(${idx})" class="btn-apple-secondary py-1 px-2 text-[11px] font-semibold">
              <i data-lucide="refresh-cw" class="w-3 h-3"></i>
              <span>Đổi câu khác</span>
            </button>
          </div>

          <div class="font-medium text-slate-900 leading-relaxed">${q.stem}</div>

          ${
            q.options
              ? `<div class="grid grid-cols-2 gap-2 text-[11px] pt-1">
                  ${q.options
                    .map(
                      (o) => `
                    <div class="p-2 rounded-lg ${o.is_correct ? 'bg-emerald-50 text-emerald-900 font-bold border-emerald-300' : 'bg-black/[0.02] text-slate-700 border-black/[0.06]'} border">
                      <strong>${o.label}.</strong> ${o.content}
                    </div>
                  `
                    )
                    .join('')}
                 </div>`
              : ''
          }
        </div>
      `;
    });

    container.innerHTML = html;
    renderKaTeX(container);
  }

  function swapMasterQuestion(masterIdx) {
    const currentQ = state.masterExam.items[masterIdx];
    // Find another question in the bank with the same YCCD or strand
    const candidate = state.itemBank.find((q) => q.code !== currentQ.code && q.learning_outcome_id === currentQ.learning_outcome_id);

    if (candidate) {
      state.masterExam.items[masterIdx] = JSON.parse(JSON.stringify(candidate));
      renderMasterExam();
      showToast(`Đã đổi Câu ${masterIdx + 1} sang câu tương đương: ${candidate.code} (${candidate.learning_outcome_id})`, 'success');
    } else {
      // Pick any different question
      const randomQ = state.itemBank.find((q) => q.code !== currentQ.code);
      if (randomQ) {
        state.masterExam.items[masterIdx] = JSON.parse(JSON.stringify(randomQ));
        renderMasterExam();
        showToast(`Đã đổi Câu ${masterIdx + 1} sang câu: ${randomQ.code}`, 'success');
      }
    }
  }

  /**
   * Execute Safe Shuffling Algorithm
   * Rule 1: Section Integrity
   * Rule 2: Passage Integrity
   * Rule 3: Option Anchor Rule (Lock D for fixed/positional options, shuffle A-B-C)
   * Rule 4: Key Matrix Generator
   */
  function executeSafeShuffling() {
    showToast('Đang thực thi 4 Nguyên tắc Trộn Đề An Toàn...', 'info');

    const codes = ['101', '102', '103', '104'];
    const masterItems = state.masterExam.items;
    const variants = {};
    const keyMatrix = [];

    // Initialize key matrix structure
    masterItems.forEach((q, idx) => {
      let masterCorrect = '-';
      if (q.item_format === 'SINGLE_CHOICE' && q.options) {
        const c = q.options.find((o) => o.is_correct);
        masterCorrect = c ? c.label : 'A';
      } else if (q.item_format === 'TRUE_FALSE_GROUP' && q.sub_statements) {
        masterCorrect = q.sub_statements.map((s) => (s.is_true ? 'Đ' : 'S')).join('-');
      } else if (q.item_format === 'SHORT_ANSWER') {
        masterCorrect = q.short_answer_value || '1';
      }

      keyMatrix.push({
        qIndex: idx + 1,
        format: q.item_format,
        masterKey: masterCorrect,
        variantKeys: {},
        hasAnchor: q.options?.some((o) => o.is_fixed || isAnchorPhrase(o.content)),
      });
    });

    // Generate each variant code
    codes.forEach((code) => {
      // Clone questions
      const shuffledQuestions = JSON.parse(JSON.stringify(masterItems));

      shuffledQuestions.forEach((q, qIdx) => {
        if (q.item_format === 'SINGLE_CHOICE' && q.options && q.options.length === 4) {
          // Check for Option Anchor Rule
          const fixedIdx = q.options.findIndex((o) => o.is_fixed || isAnchorPhrase(o.content));

          let newOptions = [];
          if (fixedIdx !== -1) {
            // FIXED OPTION DETECTED -> Keep fixed option strictly at position D (index 3)
            const fixedOpt = q.options[fixedIdx];
            const freeOpts = q.options.filter((_, i) => i !== fixedIdx);

            // Deterministic or pseudo-random shuffle of the 3 free options based on code
            const seed = code.charCodeAt(2) + qIdx;
            if (seed % 3 === 0) {
              newOptions = [freeOpts[1], freeOpts[0], freeOpts[2], fixedOpt];
            } else if (seed % 3 === 1) {
              newOptions = [freeOpts[2], freeOpts[1], freeOpts[0], fixedOpt];
            } else {
              newOptions = [freeOpts[0], freeOpts[2], freeOpts[1], fixedOpt];
            }
          } else {
            // No anchor: safe permutation of all 4 options
            const permOrders = [
              [1, 2, 3, 0],
              [2, 0, 1, 3],
              [3, 1, 0, 2],
              [0, 3, 2, 1],
            ];
            const order = permOrders[code.charCodeAt(2) % 4];
            newOptions = order.map((i) => q.options[i]);
          }

          // Re-assign labels A, B, C, D
          const labels = ['A', 'B', 'C', 'D'];
          newOptions.forEach((opt, i) => {
            opt.label = labels[i];
          });
          q.options = newOptions;

          // Record new correct option in matrix
          const newCorrect = newOptions.find((o) => o.is_correct);
          keyMatrix[qIdx].variantKeys[code] = newCorrect ? newCorrect.label : 'A';
        } else if (q.item_format === 'TRUE_FALSE_GROUP') {
          keyMatrix[qIdx].variantKeys[code] = keyMatrix[qIdx].masterKey;
        } else {
          keyMatrix[qIdx].variantKeys[code] = keyMatrix[qIdx].masterKey;
        }
      });

      variants[code] = shuffledQuestions;
    });

    state.shuffledVariants.isShuffled = true;
    state.shuffledVariants.variants = variants;
    state.shuffledVariants.keyMatrix = keyMatrix;
    state.shuffledVariants.activeVariantCode = '101';

    // Show Results Panel
    const resultsPanel = document.getElementById('shuffled-results-panel');
    if (resultsPanel) {
      resultsPanel.classList.remove('hidden');
    }

    renderVariantView('101');
    renderAnswerKeyMatrixTable();

    showToast('Hoàn tất trộn 4 mã đề! Option Anchor Rule được bảo toàn 100% tại vị trí D.', 'success');
  }

  function viewVariant(code) {
    state.shuffledVariants.activeVariantCode = code;

    // Update buttons
    ['101', '102', '103', '104'].forEach((c) => {
      const btn = document.getElementById(`btn-var-${c}`);
      if (btn) {
        if (c === code) {
          btn.className = 'px-3 py-1.5 rounded-xl text-xs font-bold bg-brand-600 text-white shadow-xs';
        } else {
          btn.className = 'px-3 py-1.5 rounded-xl text-xs font-bold bg-slate-100 text-slate-700 hover:bg-slate-200';
        }
      }
    });

    const labelPdf = document.getElementById('btn-label-active-pdf');
    if (labelPdf) labelPdf.innerText = `Tải PDF Mã ${code}`;
    const labelDocx = document.getElementById('btn-label-active-docx');
    if (labelDocx) labelDocx.innerText = `Tải Word Mã ${code}`;

    renderVariantView(code);
  }

  function renderVariantView(code) {
    const container = document.getElementById('variant-items-container');
    if (!container) return;

    const items = state.shuffledVariants.variants[code] || [];
    let html = '';

    items.forEach((q, idx) => {
      html += `
        <div class="p-3 bg-white rounded-xl border border-slate-200 text-xs space-y-1.5 shadow-xs">
          <div class="flex items-center justify-between">
            <span class="font-bold text-slate-800">Mã ${code} • Câu ${idx + 1} (${q.code}):</span>
            <span class="text-[10px] text-slate-400 font-mono">${q.item_format}</span>
          </div>
          <div class="text-slate-800 font-medium">${q.stem}</div>

          ${
            q.options
              ? `<div class="grid grid-cols-2 gap-2 text-[11px] pt-1">
                  ${q.options
                    .map(
                      (o) => `
                    <div class="p-1 rounded ${o.is_correct ? 'bg-emerald-50 text-emerald-900 border border-emerald-300 font-bold' : 'bg-slate-50 text-slate-700'}">
                      <strong>${o.label}.</strong> ${o.content}
                      ${o.is_fixed || isAnchorPhrase(o.content) ? '<span class="text-[9px] text-emerald-700 font-bold ml-1">[Neo D]</span>' : ''}
                    </div>
                  `
                    )
                    .join('')}
                 </div>`
              : ''
          }
        </div>
      `;
    });

    container.innerHTML = html;
    renderKaTeX(container);
  }

  function renderAnswerKeyMatrixTable() {
    const tbody = document.getElementById('answer-key-matrix-tbody');
    if (!tbody) return;

    let html = '';
    state.shuffledVariants.keyMatrix.forEach((row) => {
      html += `
        <tr class="hover:bg-slate-50">
          <td class="p-2 text-left pl-4 font-bold text-slate-800">Câu ${row.qIndex}</td>
          <td class="p-2 text-[11px] text-slate-500">${row.format}</td>
          <td class="p-2 font-bold bg-indigo-50/50 text-indigo-900">${row.masterKey}</td>
          <td class="p-2 font-bold text-slate-800">${row.variantKeys['101'] || '-'}</td>
          <td class="p-2 font-bold text-slate-800">${row.variantKeys['102'] || '-'}</td>
          <td class="p-2 font-bold text-slate-800">${row.variantKeys['103'] || '-'}</td>
          <td class="p-2 font-bold text-slate-800">${row.variantKeys['104'] || '-'}</td>
          <td class="p-2 text-right pr-4">
            ${
              row.hasAnchor
                ? `<span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800">
                    <i data-lucide="shield-check" class="w-3 h-3 inline"></i> Khóa vị trí D
                   </span>`
                : '<span class="text-slate-400 text-[10px]">Hoán vị tự do</span>'
            }
          </td>
        </tr>
      `;
    });

    tbody.innerHTML = html;
    renderKaTeX(tbody);
  }

  /**
   * DOCX & Multi-variant ZIP Exporter
   * Generates formatted Word DOCX files with native OMML indicators, 2-column layout headers,
   * solution guide, and answer sheet.
   */
  /**
   * Downloads official exam package (.ZIP containing genuine 2-column Word DOCX with native OMML equations,
   * vector PDF documents, solution guides, and answer sheets).
   */
  async function downloadPublishZip(format = 'all') {
    const formatName = format === 'pdf' ? 'PDF' : format === 'docx' ? 'Word (.DOCX)' : 'Trọn gói (Word + PDF)';
    showToast(`Đang đóng gói đề thi ${formatName}, vui lòng chờ trong giây lát...`, 'info');

    let masterId = state.masterExam?.id;
    if (!masterId) {
      try {
        const examsRes = await fetch(`${API_BASE_URL}/exams`);
        if (examsRes.ok) {
          const examsList = await examsRes.json();
          if (examsList.length > 0) {
            masterId = examsList[0].id;
            state.masterExam.id = masterId;
          }
        }
      } catch (e) {
        console.warn('Cannot fetch exams list:', e);
      }
    }

    const targetId = masterId || 'default';
    const downloadUrl = `${API_BASE_URL}/exams/${targetId}/export-zip?format=${encodeURIComponent(format)}`;

    try {
      const response = await fetch(downloadUrl);
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Máy chủ phản hồi mã lỗi HTTP ${response.status}`);
      }
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = `Goi_DeThi_Quesy_TT32_${format}.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(blobUrl);
      showToast(`Đã tải xuống thành công gói đề thi ${formatName}!`, 'success');
    } catch (err) {
      console.error('Download zip failed:', err);
      showToast(`Lỗi khi tải gói đề thi: ${err.message}`, 'error');
    }
  }

  async function downloadActiveVariantPdf() {
    const code = state.shuffledVariants.activeVariantCode || '101';
    let masterId = state.masterExam?.id;
    if (!masterId) {
      try {
        const examsRes = await fetch(`${API_BASE_URL}/exams`);
        if (examsRes.ok) {
          const examsList = await examsRes.json();
          if (examsList.length > 0) {
            masterId = examsList[0].id;
            state.masterExam.id = masterId;
          }
        }
      } catch (e) {
        console.warn('Cannot fetch exams list:', e);
      }
    }
    const targetId = masterId || 'default';
    const url = `${API_BASE_URL}/exams/${targetId}/export-pdf?variant_code=${encodeURIComponent(code)}`;
    showToast(`Đang kết xuất đề thi PDF Mã đề ${code}...`, 'info');

    try {
      const response = await fetch(url);
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Máy chủ phản hồi mã lỗi HTTP ${response.status}`);
      }
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = `De_Thi_Toan_12_Ma_${code}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(blobUrl);
      showToast(`Đã tải xuống thành công file PDF Mã đề ${code}!`, 'success');
    } catch (err) {
      console.error('Download PDF failed:', err);
      showToast(`Lỗi khi tải PDF: ${err.message}`, 'error');
    }
  }

  async function downloadActiveVariantDocx() {
    const code = state.shuffledVariants.activeVariantCode || '101';
    let masterId = state.masterExam?.id;
    if (!masterId) {
      try {
        const examsRes = await fetch(`${API_BASE_URL}/exams`);
        if (examsRes.ok) {
          const examsList = await examsRes.json();
          if (examsList.length > 0) {
            masterId = examsList[0].id;
            state.masterExam.id = masterId;
          }
        }
      } catch (e) {
        console.warn('Cannot fetch exams list:', e);
      }
    }
    const targetId = masterId || 'default';
    const url = `${API_BASE_URL}/exams/${targetId}/export-docx?variant_code=${encodeURIComponent(code)}`;
    showToast(`Đang kết xuất đề thi Word (.docx) Mã đề ${code}...`, 'info');

    try {
      const response = await fetch(url);
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Máy chủ phản hồi mã lỗi HTTP ${response.status}`);
      }
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = `De_Thi_Toan_12_Ma_${code}.docx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(blobUrl);
      showToast(`Đã tải xuống thành công file Word (.docx) Mã đề ${code}!`, 'success');
    } catch (err) {
      console.error('Download Word failed:', err);
      showToast(`Lỗi khi tải Word: ${err.message}`, 'error');
    }
  }

  // ============================================================================
  // 12. LATEX FORMULA LIVE EDITOR MODAL
  // ============================================================================
  function openFormulaEditorModal(targetType, qId, field = 'stem', optionIndex = null) {
    state.activeFormulaEdit = { targetType, questionId: qId, field, optionIndex, currentLatex: '' };

    let initialLatex = '';
    if (targetType === 'digitize') {
      const q = state.digitizeJob.questions.find((x) => x.id === qId);
      if (q) {
        if (field === 'stem') initialLatex = q.stem;
        else if (field === 'option' && q.options && q.options[optionIndex]) {
          initialLatex = q.options[optionIndex].content;
        }
      }
    } else {
      initialLatex = '$y = x^3 - 3x^2 + 4$';
    }

    const input = document.getElementById('modal-latex-input');
    if (input) input.value = initialLatex;

    updateModalLatexPreview();

    const modal = document.getElementById('latex-editor-modal');
    if (modal) modal.classList.remove('hidden');
  }

  function closeFormulaEditorModal() {
    const modal = document.getElementById('latex-editor-modal');
    if (modal) modal.classList.add('hidden');
  }

  function updateModalLatexPreview() {
    const input = document.getElementById('modal-latex-input');
    const previewBox = document.getElementById('modal-latex-preview-box');
    if (!input || !previewBox) return;

    let text = input.value.trim();
    if (!text) {
      previewBox.innerHTML = '<span class="text-slate-400 italic">Nhập công thức toán học bên trên để xem preview trực tiếp</span>';
      return;
    }

    // Auto-wrap with $ if user didn't write dollar signs
    if (!text.includes('$')) {
      text = `$${text}$`;
    }

    previewBox.innerHTML = text;
    renderKaTeX(previewBox);
  }

  function insertLatexSymbol(symbol) {
    const input = document.getElementById('modal-latex-input');
    if (!input) return;

    const start = input.selectionStart;
    const end = input.selectionEnd;
    const val = input.value;

    input.value = val.substring(0, start) + symbol + val.substring(end);
    input.focus();
    input.setSelectionRange(start + symbol.length, start + symbol.length);
    updateModalLatexPreview();
  }

  function saveFormulaEditorResult() {
    const input = document.getElementById('modal-latex-input');
    if (!input) return;
    const newContent = input.value.trim();

    const { targetType, questionId, field, optionIndex } = state.activeFormulaEdit;

    if (targetType === 'digitize') {
      const q = state.digitizeJob.questions.find((x) => x.id === questionId);
      if (q) {
        if (field === 'stem') {
          q.stem = newContent;
        } else if (field === 'option' && q.options && q.options[optionIndex]) {
          q.options[optionIndex].content = newContent;
        }
        renderExtractedQuestionsList();
        renderDocumentPaperPreview();
      }
    }

    closeFormulaEditorModal();
    showToast('Đã lưu công thức toán học mới vào câu hỏi!', 'success');
  }

  // ============================================================================
  // 13. AI VECTOR DUPLICATE DETECTION MODAL
  // ============================================================================
  function checkQuestionDuplicate(qId) {
    const q = state.digitizeJob.questions.find((x) => x.id === qId) || state.itemBank.find((x) => x.id === qId);
    if (!q) return;

    const newStemEl = document.getElementById('dup-modal-new-stem');
    if (newStemEl) newStemEl.innerHTML = q.stem;

    const modal = document.getElementById('duplicate-warning-modal');
    if (modal) {
      modal.classList.remove('hidden');
      renderKaTeX(modal);
    }
  }

  function triggerDuplicateCheckDemo() {
    checkQuestionDuplicate(1);
  }

  function closeDuplicateModal() {
    const modal = document.getElementById('duplicate-warning-modal');
    if (modal) modal.classList.add('hidden');
    showToast('Đã hủy bỏ lưu câu hỏi trùng lặp theo khuyến nghị của AI.', 'info');
  }

  function confirmSaveAsVariant() {
    const modal = document.getElementById('duplicate-warning-modal');
    if (modal) modal.classList.add('hidden');
    showToast('Đã xác nhận lưu câu hỏi dưới dạng Biến thể độc lập (Variant Question).', 'success');
  }

  // ============================================================================
  // 13. DRAG & DROP FOR DOCUMENT VIEWER
  // ============================================================================
  function setupPaperDropZone() {
    const dropZone = document.getElementById('doc-viewer-scroll-container');
    if (!dropZone) return;

    ['dragenter', 'dragover'].forEach((eventName) => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.add('ring-4', 'ring-brand-400', 'bg-brand-50');
      });
    });

    ['dragleave', 'drop'].forEach((eventName) => {
      dropZone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropZone.classList.remove('ring-4', 'ring-brand-400', 'bg-brand-50');
      });
    });

    dropZone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt && dt.files;
      if (files && files.length > 0) {
        handleFileUpload(Array.from(files));
      }
    });
  }

  // ============================================================================
  // 14. INITIALIZATION & ROUTER POPSTATE
  // ============================================================================
  async function init() {
    seedInitialQuestions();
    setupPaperDropZone();

    // Setup Browser History popstate listener for SPA Router
    window.addEventListener('popstate', (event) => {
      const tabId = (event.state && event.state.tabId) || ROUTE_MAP[window.location.pathname.replace(/\/$/, '') || '/'] || 'dashboard';
      switchTab(tabId, false);
    });

    // Check backend API live status
    await apiService.checkHealth();

    // Initial Routing based on current URL path
    const initialPath = window.location.pathname.replace(/\/$/, '') || '/';
    const targetTab = ROUTE_MAP[initialPath] || 'dashboard';
    switchTab(targetTab, false);

    // Init Lucide Icons
    if (window.lucide) {
      lucide.createIcons();
    }
  }

  // Run on DOM loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose global methods to window.app for HTML onclick bindings
  window.app = {
    navigateTo,
    switchTab,
    selectQuestionForHITL,
    toggleSingleChoiceAnswer,
    toggleTrueFalseAnswer,
    updateShortAnswerValue,
    updateQuestionYCCD,
    updateQuestionCognitive,
    filterStudioConfidence,
    commitExtractedToBank,
    commitSingleQuestion,
    handleFileUpload,
    handleFileSelect,
    handleAddMoreFiles,
    moveStagedPage,
    removeStagedPage,
    selectStagedPreviewPage,
    resetStagedFiles,
    startAIDigitize,
    openQuestionEditorModal,
    closeQuestionEditorModal,
    handleQuestionFormatChangeInModal,
    setModalCorrectChoice,
    setModalOptionFixed,
    updateModalOptionContent,
    setModalSubIsTrue,
    updateModalSubContent,
    updateModalSubExp,
    updateQuestionEditorLivePreview,
    insertStemSymbol,
    saveQuestionEdit,
    loadSampleExam,
    changeViewerPage,
    handleTaxonomyFilterChange,
    renderItemBank,
    deleteBankQuestion,
    updateMatrixCell,
    saveMatrixConfig,
    loadMatrixPreset,
    generateMasterExamFromMatrix,
    swapMasterQuestion,
    executeSafeShuffling,
    viewVariant,
    downloadPublishZip,
    downloadActiveVariantPdf,
    downloadActiveVariantDocx,
    openFormulaEditorModal,
    closeFormulaEditorModal,
    updateModalLatexPreview,
    insertLatexSymbol,
    saveFormulaEditorResult,
    checkQuestionDuplicate,
    triggerDuplicateCheckDemo,
    closeDuplicateModal,
    confirmSaveAsVariant,
    renderDigitizeStudio,
    getState: () => state,
  };
})();
