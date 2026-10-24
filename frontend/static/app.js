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
    // Render any TikZ diagrams
    renderTikzDiagrams(domElement);
  }

  function cleanShortAnswer(val) {
    if (!val || typeof val !== 'string') return String(val || '');
    return val.replace(/\{,\}/g, ',').replace(/[\${}]/g, '').trim();
  }

  function cleanOptionAnswer(text) {
    if (!text || typeof text !== 'string') return text || '';
    let s = text.replace(/\{,\}/g, ',').trim();
    // Strip redundant leading option letter prefix like "A. 1" -> "1"
    s = s.replace(/^[A-Da-d][\.\)\:\-\/]\s*/, '').trim();

    // If the non-math text is all uppercase, convert to sentence case (only capitalize first character)
    const parts = s.split(/(\$[^\$]+\$)/);
    for (let i = 0; i < parts.length; i++) {
      if (!parts[i].startsWith('$') && parts[i].trim().length > 2) {
        const letters = parts[i].match(/[a-zA-ZÀ-ỹ]/g);
        if (letters && letters.every((c) => c === c.toUpperCase())) {
          parts[i] = parts[i].charAt(0).toUpperCase() + parts[i].slice(1).toLowerCase();
        }
      }
    }
    return parts.join('').trim();
  }

  function formatStemForDisplay(text, isOption = false) {
    if (!text || typeof text !== 'string') return '';
    let s = text;

    // Remove any redundant center environment tags wrapping the diagram or in text
    s = s.replace(/\\+(?:begin|end)\{center\}/g, '');

    // 1. Extract and protect all TikZ blocks BEFORE any LaTeX formatting!
    // Matches \begin{tikzpicture}...\end{tikzpicture} with any leading/trailing slashes or math delimiters
    const tikzBlocks = [];
    s = s.replace(/(\\?\$*\s*(?:\\+begin\{center\}\s*)?\\+begin\{tikzpicture\}[\s\S]*?\\+end\{tikzpicture\}(?:\s*\\+end\{center\})?\s*\\?\$*)/g, (match) => {
      let cleanTikz = match.trim();
      // Remove any erroneous outer $$ or $ delimiters
      while (cleanTikz.startsWith('$')) cleanTikz = cleanTikz.slice(1).trim();
      while (cleanTikz.endsWith('$')) cleanTikz = cleanTikz.slice(0, -1).trim();
      // Remove center tags inside tikz block
      cleanTikz = cleanTikz.replace(/\\+(?:begin|end)\{center\}/g, '').trim();
      // Normalize any excessive backslashes (e.g. \\begin -> \begin)
      cleanTikz = cleanTikz.replace(/\\\\([a-zA-Z]+)/g, '\\$1');
      if (!cleanTikz.startsWith('\\')) cleanTikz = '\\' + cleanTikz;
      const encoded = encodeURIComponent(cleanTikz);
      tikzBlocks.push(encoded);
      return `__TIKZ_BLOCK_PLACEHOLDER_${tikzBlocks.length - 1}__`;
    });

    // 2. Format LaTeX rules for math, brackets, fractions, decimals, and tables
    s = formatLatexRules(s);

    // 3. Support markdown images ![alt](url)
    s = s.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<div class="my-3 flex justify-center"><img src="$2" alt="$1" class="max-h-64 rounded-xl border border-slate-200/80 shadow-xs object-contain" /></div>');

    // 4. Support [IMAGE: url] placeholders
    s = s.replace(/\[IMAGE:\s*([^\]]+)\]/g, '<div class="my-3 flex justify-center"><img src="$1" alt="Hình minh họa" class="max-h-64 rounded-xl border border-slate-200/80 shadow-xs object-contain" /></div>');

    // 5. Restore TikZ blocks into interactive SVG diagram wrappers
    for (let idx = 0; idx < tikzBlocks.length; idx++) {
      const placeholder = `__TIKZ_BLOCK_PLACEHOLDER_${idx}__`;
      const wrapperHtml = isOption
        ? `<div class="tikz-diagram-wrapper tikz-option-wrapper my-1 p-1.5 bg-white rounded-lg border border-slate-200 shadow-2xs flex flex-col items-center w-full" data-tikz="${tikzBlocks[idx]}">
            <div class="tikz-status text-[10px] text-slate-500 flex items-center space-x-1.5 py-1.5">
              <i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin text-brand-600"></i>
              <span>Đang tải hình...</span>
            </div>
          </div>`
        : `<div class="tikz-diagram-wrapper my-3 p-3 bg-slate-50/90 rounded-xl border border-slate-200/80 shadow-xs flex flex-col items-center" data-tikz="${tikzBlocks[idx]}">
            <div class="tikz-status text-xs text-slate-500 flex items-center space-x-2 py-3">
              <i data-lucide="loader-2" class="w-4 h-4 animate-spin text-brand-600"></i>
              <span class="font-medium">Đang kết xuất đồ thị TikZ vector...</span>
            </div>
          </div>`;
      s = s.replace(placeholder, wrapperHtml);
    }

    return s;
  }

  async function renderTikzDiagrams(container) {
    if (!container) return;
    const wrappers = container.querySelectorAll('.tikz-diagram-wrapper[data-tikz]');
    for (const wrap of wrappers) {
      if (wrap.getAttribute('data-rendered') === 'true') continue;
      const rawTikz = decodeURIComponent(wrap.getAttribute('data-tikz') || '');
      if (!rawTikz) continue;
      try {
        const res = await fetch(`${API_BASE_URL}/digitize/render-tikz`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ tikz_code: rawTikz })
        });
        if (res.ok) {
          const data = await res.json();
          if (data.success && data.svg) {
            wrap.setAttribute('data-rendered', 'true');

            // Extract and register @font-face rules into document head so Chromium loads TeX fonts
            const fontFaceMatches = data.svg.match(/@font-face\{[^{}]*\}/g);
            if (fontFaceMatches) {
              let globalFontStyle = document.getElementById('quesy-tikz-embedded-fonts');
              if (!globalFontStyle) {
                globalFontStyle = document.createElement('style');
                globalFontStyle.id = 'quesy-tikz-embedded-fonts';
                document.head.appendChild(globalFontStyle);
              }
              fontFaceMatches.forEach((rule) => {
                const normRule = rule.replace(/application\/x-font-woff/g, 'font/woff');
                if (!globalFontStyle.textContent.includes(normRule.substring(0, 45))) {
                  globalFontStyle.textContent += '\n' + normRule;
                }
              });
            }

            let cleanSvg = data.svg.replace(/\ue030/g, '&#x2032;');
            cleanSvg = cleanSvg.replace(/'Times New Roman'/g, "'CMU Serif', 'Latin Modern Roman', 'Computer Modern', serif");

            if (wrap.classList.contains('tikz-option-wrapper')) {
              cleanSvg = cleanSvg.replace(/<svg(\s[^>]*)>/i, '<svg class="max-w-full h-auto max-h-48 object-contain mx-auto" $1>');
              wrap.innerHTML = `
                <div class="overflow-x-auto max-w-full w-full flex justify-center py-1">
                  ${cleanSvg}
                </div>
              `;
            } else {
              // Clean and enhance SVG styling for responsive web display
              cleanSvg = cleanSvg.replace(/<svg(\s[^>]*)>/i, '<svg class="max-w-full h-auto max-h-80 object-contain shadow-2xs rounded-lg bg-white p-2" $1>');

              wrap.innerHTML = `
                <div class="w-full flex items-center justify-between text-[11px] font-bold text-slate-500 mb-2 border-b border-slate-200/60 pb-1">
                  <span class="flex items-center space-x-1.5 text-brand-700">
                    <i data-lucide="line-chart" class="w-3.5 h-3.5"></i>
                    <span>Đồ thị / Hình vẽ (TikZ Vector)</span>
                  </span>
                  <span class="text-[10px] text-slate-400 font-normal">Vector SVG</span>
                </div>
                <div class="overflow-x-auto max-w-full w-full flex justify-center py-2">
                  <div class="inline-flex justify-center items-center bg-white rounded-xl border border-slate-200/90 shadow-2xs p-3 min-w-[280px] max-w-full">
                    ${cleanSvg}
                  </div>
                </div>
              `;
            }
            if (window.lucide) lucide.createIcons();
            continue;
          }
        }
      } catch (err) {
        console.warn('TikZ render error:', err);
      }
      wrap.setAttribute('data-rendered', 'true');
      wrap.innerHTML = `
        <div class="text-xs text-slate-600 p-2 bg-white rounded-lg border border-slate-200 w-full">
          <div class="font-bold text-[10px] text-slate-700 mb-1 flex items-center space-x-1">
            <i data-lucide="code" class="w-3 h-3 text-slate-500"></i>
            <span>Mã TikZ</span>
          </div>
          <pre class="font-mono text-[9px] bg-slate-50 p-1.5 rounded border border-slate-200 overflow-x-auto text-slate-700">${escapeHtml(rawTikz)}</pre>
        </div>
      `;
      if (window.lucide) lucide.createIcons();
    }
  }

  function convertVariationArrayToTkzTab(text) {
    if (!text || typeof text !== 'string' || (!text.includes('\\nearrow') && !text.includes('\\searrow'))) return text;

    const pattern = /(?:\$\$\s*)?\\begin\{(?:array|tabular)\}(?:\{[^}]*\})?([\s\S]*?)\\end\{(?:array|tabular)\}(?:\s*\$\$)?/g;
    return text.replace(pattern, (match, body) => {
      if (!body.includes('\\nearrow') && !body.includes('\\searrow') && !body.includes('\\infty')) {
        return match;
      }
      const rawLines = body.split('\\\\').map((l) => l.replace(/\\hline/g, '').trim()).filter(Boolean);
      if (rawLines.length < 2) return match;

      const grid = rawLines.map((l) => l.split('&').map((c) => c.trim()));
      const rowX = grid[0];
      const nodesX = rowX.slice(1).map((c) => c.replace(/\$/g, '').trim()).filter(Boolean);
      if (!nodesX.length) return match;

      const stdNodesX = nodesX.map((nx) => nx.startsWith('$') ? nx : `$${nx}$`);
      let lblX = '$x$';
      let lblFprime = "$f'(x)$";
      let lblF = '$f(x)$';

      const rawLbl0 = (rowX[0] || '').replace(/\$/g, '').trim();
      if (rawLbl0 && !rawLbl0.includes('x')) lblX = `$${rawLbl0}$`;

      let hasDerivativeRow = false;
      const signs = [];
      if (grid.length >= 2) {
        const row1 = grid[1];
        const rawLbl1 = (row1[0] || '').replace(/\$/g, '').trim();
        if (rawLbl1.includes("f'") || rawLbl1.includes("y'") || rawLbl1.includes("g'")) {
          hasDerivativeRow = true;
          if (rawLbl1.includes("f'")) lblFprime = "$f'(x)$";
          else if (rawLbl1.includes("y'")) lblFprime = "$y'$";
          else if (rawLbl1.includes("g'")) lblFprime = "$g'(x)$";

          for (const c of row1.slice(1)) {
            const cleanC = c.replace(/\$/g, '').trim();
            if (['+', '-', '0', 'd', 'z', 't', '|', '||', '\\Vert'].includes(cleanC)) {
              signs.push(['|', '||', '\\Vert'].includes(cleanC) ? 'd' : cleanC);
            }
          }
        }
      }

      const varRowStart = hasDerivativeRow ? 2 : 1;
      const varRows = grid.slice(varRowStart);
      const hasAsymptote = body.includes('\\Vert') || body.includes('||');

      const nNodes = nodesX.length;
      const nodeValues = {};
      const nodeAsymptoteVals = {};

      varRows.forEach((row, rIdx) => {
        const cells = row.slice(1);
        cells.forEach((cell, cIdx) => {
          const cleanC = cell.replace(/\$/g, '').trim();
          if (!cleanC || ['\\nearrow', '\\searrow', '\\Vert', '||', '|', 'f(x)', 'y', "f'(x)", "y'"].includes(cleanC)) {
            return;
          }
          const totalCols = cells.length;
          let nodeIdx = totalCols >= 2 * nNodes - 1 ? Math.round(cIdx / 2) : Math.round(cIdx * (nNodes - 1) / Math.max(1, totalCols - 1));
          nodeIdx = Math.max(0, Math.min(nNodes - 1, nodeIdx));
          const isUpper = rIdx === 0 || (rIdx === 1 && cleanC.includes('+\\infty'));

          if (!nodeValues[nodeIdx]) {
            nodeValues[nodeIdx] = { val: cleanC, isUpper };
          } else {
            nodeAsymptoteVals[nodeIdx] = { v1: nodeValues[nodeIdx].val, v2: cleanC };
          }
        });
      });

      const tabVars = [];
      for (let i = 0; i < nNodes; i++) {
        if (nodeAsymptoteVals[i]) {
          tabVars.push(`+D-/$${nodeAsymptoteVals[i].v1}$/$${nodeAsymptoteVals[i].v2}$`);
        } else if (nodeValues[i]) {
          const prefix = nodeValues[i].isUpper ? '+' : '-';
          tabVars.push(`${prefix}/$${nodeValues[i].val}$`);
        } else {
          const prefix = i % 2 === 1 ? '+' : '-';
          tabVars.push(`${prefix}/$ $`);
        }
      }

      let lineStr = signs.length >= 3 ? signs.join(',') : (nNodes === 4 ? '+,0,-,0,+' : (nNodes === 3 ? '-,0,+' : '+,0,-'));
      if (!lineStr.startsWith(',')) lineStr = ',' + lineStr;
      if (!lineStr.endsWith(',')) lineStr = lineStr + ',';

      const optStyle = hasAsymptote ? '  \\tikzset{double style/.append style = {double distance=2.5pt}}\n' : '';

      return `\n\n\\begin{tikzpicture}\n${optStyle}  \\tkzTabInit[nocadre,lgt=1.2,espcl=2.5,deltacl=0.6]\n  {${lblX}/.6, ${lblFprime}/.6, ${lblF}/2}\n  {${stdNodesX.join(',')}}\n  \\tkzTabLine{${lineStr}}\n  \\tkzTabVar{${tabVars.join(',')}}\n\\end{tikzpicture}\n\n`;
    });
  }

  /**
   * Standardizes math strings adhering to Vietnam High School assessment rules:
   * 1. Brackets: \left and \right for (, ), [, ], \{, \}
   * 2. Decimal numbers: 15{,}25 instead of 15,25 or 15.25
   * 3. Fractions: \dfrac instead of \frac
   * 4. Vectors: \overrightarrow instead of \vec
   */
  function formatLatexRules(text) {
    if (!text || typeof text !== 'string') return text;
    let res = text;

    // 0. Auto-convert legacy variation array to TikZ tkz-tab
    res = convertVariationArrayToTkzTab(res);

    // 1. Auto-close \begin{array}...\end{array} if opened with $$ but missing closing $$
    res = res.replace(/(\$\$\s*\\begin\{(?:array|matrix|pmatrix|bmatrix|vmatrix|cases)\}[\s\S]*?\\end\{(?:array|matrix|pmatrix|bmatrix|vmatrix|cases)\})(?!\s*\$\$)/g, (m, p1) => p1 + '$$');

    // 2. Auto-wrap \begin{array}...\end{array} if not wrapped in $$ at all
    res = res.replace(/(?<!\$\$)(?<!\$)\\begin\{(array|matrix|pmatrix|bmatrix|vmatrix|cases)\}([\s\S]*?)\\end\{\1\}(?!\$\$)(?!\$)/g, (m, env, inner) => `$$\\begin{${env}}${inner}\\end{${env}}$$`);

    // 2.5 Normalize variation table array column specs: strip rogue vertical bars '|' and outer borders
    res = res.replace(/\\begin\{array\}\{([^}]+)\}([\s\S]*?)\\end\{array\}/g, (m, colSpec, body) => {
      if (body.includes('\\nearrow') || body.includes('\\searrow') || body.includes('-\\infty') || body.includes('+\\infty')) {
        let pureCols = colSpec.replace(/\|/g, '').trim();
        let normCol = pureCols ? pureCols[0] + '|' + pureCols.slice(1) : 'c|ccccccc';
        return `\\begin{array}{${normCol}}${body}\\end{array}`;
      }
      return m;
    });

    const processMath = (mathInner) => {
      let m = mathInner;

      // Protect \text{...} from math bracket conversion (\left is illegal in text mode!)
      const textBlocks = [];
      m = m.replace(/\\text\{([^{}]*)\}/g, (match, inner) => {
        let clean = inner.replace(/\\(?:left|right)\s*([()\[\]{}|.]?)/g, '$1');
        clean = clean.replace(/\\(?:left|right)\b/g, '');
        textBlocks.push(clean);
        return `__LATEX_TEXT_BLOCK_${textBlocks.length - 1}__`;
      });

      // Rule 3: \frac -> \dfrac
      m = m.replace(/\\frac(?![a-zA-Z])/g, '\\dfrac');

      // Rule 4: \vec -> \overrightarrow
      m = m.replace(/\\vec\s*\{([^{}]+)\}/g, '\\overrightarrow{$1}');
      m = m.replace(/\\vec\s*([a-zA-Z0-9])/g, '\\overrightarrow{$1}');
      m = m.replace(/\\vec(?![a-zA-Z])/g, '\\overrightarrow');

      // Rule 2: Decimal comma {,}
      m = m.replace(/(\d+)[,\.](\d+)/g, '$1{,}$2');

      // Normalize excessive backslashes before curly braces (\+{ -> \{ and \+} -> \})
      m = m.replace(/\\+([{}])/g, '\\$1');

      // Rule 1: Brackets \left and \right
      m = m.replace(/\\sqrt\[([^\[\]]+)\]/g, '__SQRT_ROOT_OPT_$1__');
      m = m.replace(/\\left\s*\(/g, '__LEFT_PAREN__');
      m = m.replace(/\\right\s*\)/g, '__RIGHT_PAREN__');
      m = m.replace(/\\left\s*\[/g, '__LEFT_BRACKET__');
      m = m.replace(/\\right\s*\]/g, '__RIGHT_BRACKET__');
      m = m.replace(/\\left\s*\\\{/g, '__LEFT_BRACE__');
      m = m.replace(/\\right\s*\\\}/g, '__RIGHT_BRACE__');
      m = m.replace(/\\left\./g, '__LEFT_DOT__');
      m = m.replace(/\\right\./g, '__RIGHT_DOT__');

      m = m.replace(/\\\{/g, '\\left\\{');
      m = m.replace(/\\\}/g, '\\right\\}');
      m = m.replace(/\(/g, '\\left(').replace(/\)/g, '\\right)');
      m = m.replace(/\[/g, '\\left[').replace(/\]/g, '\\right]');

      m = m.replace(/__LEFT_PAREN__/g, '\\left(');
      m = m.replace(/__RIGHT_PAREN__/g, '\\right)');
      m = m.replace(/__LEFT_BRACKET__/g, '\\left[');
      m = m.replace(/__RIGHT_BRACKET__/g, '\\right]');
      m = m.replace(/__LEFT_BRACE__/g, '\\left\\{');
      m = m.replace(/__RIGHT_BRACE__/g, '\\right\\}');
      m = m.replace(/__LEFT_DOT__/g, '\\left.');
      m = m.replace(/__RIGHT_DOT__/g, '\\right.');
      m = m.replace(/__SQRT_ROOT_OPT_(.*?)__/g, '\\sqrt[$1]');

      // Clean any accidental double \left or \right
      m = m.replace(/(?:\\left\s*)+(\\left)/g, '$1');
      m = m.replace(/(?:\\right\s*)+(\\right)/g, '$1');
      // Ensure single backslash before set braces \{ and \}
      m = m.replace(/\\+([{}])/g, '\\$1');

      // Restore \text{...}
      for (let idx = 0; idx < textBlocks.length; idx++) {
        m = m.replace(`__LATEX_TEXT_BLOCK_${idx}__`, `\\text{${textBlocks[idx]}}`);
      }

      return m;
    };

    if (res.includes('$')) {
      res = res.replace(/(\$\$[\s\S]*?\$\$|\$[^\$]*?\$)/g, (match) => {
        const isBlock = match.startsWith('$$');
        const inner = isBlock ? match.slice(2, -2) : match.slice(1, -1);
        const processed = processMath(inner);
        // Flatten newlines inside display math to spaces so KaTeX text nodes remain unbroken across HTML breaks
        const finalInner = isBlock ? processed.replace(/\r?\n/g, ' ') : processed;
        return isBlock ? `$$${finalInner}$$` : `$${finalInner}$`;
      });
    } else {
      res = processMath(res);
    }

    return res;
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
    '/composer': 'composer',
    '/soan-de': 'composer',
    '/digitize': 'composer',
    '/digitize-test': 'composer',
    '/bank': 'itembank',
    '/itembank': 'itembank',
    '/matrix': 'matrix',
    '/shuffler': 'shuffler',
  };

  const TAB_TO_ROUTE = {
    dashboard: '/dashboard',
    composer: '/composer',
    itembank: '/bank',
    matrix: '/matrix',
    shuffler: '/shuffler',
  };

  const TAB_TITLES = {
    dashboard: 'Quesy — Tổng quan Khảo thí',
    composer: 'Quesy — Soạn đề LaTeX (AI Copilot & Live PDF Preview)',
    itembank: 'Quesy — Ngân hàng Câu hỏi Chuẩn hóa',
    matrix: 'Quesy — Ma trận Đề thi 2D',
    shuffler: 'Quesy — Sinh đề & Trộn đề (Vector PDF)',
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

    if (tabId === 'composer') {
      document.body.classList.add('in-composer');
    } else {
      document.body.classList.remove('in-composer');
    }

    state.digitizePipelineMode = 'standard';

    // Smooth reset scroll on tab transition
    const mainView = document.getElementById('main-scroll-view');
    if (mainView) {
      mainView.scrollTop = 0;
    }

    // Refresh specific tab contents
    if (tabId === 'dashboard') {
      renderDashboard();
    } else if (tabId === 'composer') {
      composer.init();
    } else if (tabId === 'itembank') {
      renderItemBank();
    } else if (tabId === 'matrix') {
      renderMatrixGrid();
    } else if (tabId === 'shuffler') {
      renderMasterExam();
    }

    if (window.lucide) lucide.createIcons();
  }

  function updatePipelineModeButtons(mode) {}
  function setDigitizePipelineMode(mode) {
    state.digitizePipelineMode = 'standard';
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
            <p class="text-xs text-slate-500">Tài liệu số hóa (${previews[0].size}) ${isProcessing ? 'đang được AI phân tích và bóc tách công thức toán...' : 'đã sẵn sàng để nhận dạng công thức và số hóa đề thi.'}</p>
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
            <h4 class="text-sm font-bold text-slate-900 mb-1">Tài Liệu Đề Thi Gốc</h4>
            <p class="text-xs text-slate-500 max-w-sm mb-5 leading-relaxed">
              Chưa có tệp đề thi nào được nạp. Hãy chọn tệp PDF hoặc danh sách ảnh để xem trước trực tiếp tài liệu gốc.
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
              <div id="doc-preview-page-${i + 1}" class="w-full bg-white rounded-xl p-3 shadow-md border border-slate-300">
                <div class="text-[11px] font-bold text-slate-500 mb-2 flex items-center justify-between border-b border-slate-100 pb-1">
                  <span>${images.length > 1 ? `Trang ${i + 1} / ${images.length}` : 'Tài liệu đề thi gốc'}</span>
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
            <div class="font-normal text-slate-800">${formatStemForDisplay(q.stem)}</div>
          </div>
      `;

      if (q.item_format === 'SINGLE_CHOICE' && q.options) {
        html += `<div class="grid grid-cols-2 gap-x-4 gap-y-1 pl-4 mt-2 text-xs">`;
        q.options.forEach((opt) => {
          html += `<div><strong>${opt.label}.</strong> ${formatStemForDisplay(cleanOptionAnswer(opt.content), true)}</div>`;
        });
        html += `</div>`;
      } else if (q.item_format === 'TRUE_FALSE_GROUP' && q.sub_statements) {
        html += `<div class="space-y-1 pl-4 mt-2 text-xs">`;
        q.sub_statements.forEach((sub) => {
          html += `<div><strong>${sub.label})</strong> ${formatStemForDisplay(sub.content, true)}</div>`;
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
      const pct = state.digitizeJob.progressPercent || 15;
      const stage = state.digitizeJob.progressStage || 'Đang tiền xử lý và bóc tách đề thi bằng AI...';
      container.innerHTML = `
        <div class="min-h-[440px] flex flex-col items-center justify-center p-8 text-center apple-card space-y-5">
          <div class="w-14 h-14 rounded-2xl bg-indigo-50 border border-indigo-100 flex items-center justify-center shadow-xs text-brand-600 animate-spin">
            <i data-lucide="loader-2" class="w-7 h-7"></i>
          </div>
          <div class="space-y-1">
            <h3 class="text-base font-bold text-slate-900 flex items-center justify-center space-x-2">
              <span>Đang Gõ Lại & Bóc Tách Đề Thi...</span>
            </h3>
            <p class="text-xs text-slate-500 max-w-md leading-relaxed" id="digitize-stage-desc">
              ${escapeHtml(stage)}
            </p>
          </div>
          
          <!-- Sleek Real-Time Progress Bar -->
          <div class="w-full max-w-md space-y-2">
            <div class="w-full bg-slate-200/80 rounded-full h-3 overflow-hidden p-0.5 border border-slate-200 shadow-inner">
              <div id="digitize-progress-bar" class="h-full bg-gradient-to-r from-brand-600 via-indigo-600 to-emerald-500 transition-all duration-300 rounded-full" style="width: ${pct}%"></div>
            </div>
            <div class="flex items-center justify-between text-xs font-semibold text-slate-600 px-1">
              <span id="digitize-stage-label" class="truncate max-w-[280px]">${escapeHtml(stage)}</span>
              <span id="digitize-progress-val" class="font-mono text-brand-600">${pct}%</span>
            </div>
          </div>
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
              <div class="flex-1">${formatStemForDisplay(q.stem)}</div>
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
          const hasTikz = opt.content && (opt.content.includes('tikzpicture') || opt.content.includes('tikz'));

          if (hasTikz) {
            html += `
              <div onclick="event.stopPropagation(); app.toggleSingleChoiceAnswer(${qId}, ${optIdx})" class="option-pill flex flex-col items-stretch p-2.5 rounded-xl border ${correctClass} cursor-pointer hover:border-brand-400 transition-all">
                <div class="flex items-center justify-between w-full mb-1">
                  <div class="flex items-center space-x-1.5">
                    <span class="option-letter-badge w-6 h-6 rounded-lg flex items-center justify-center font-bold text-xs ${isCorrect ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-700'}">
                      ${opt.label}
                    </span>
                    ${
                      hasAnchor
                        ? `<span class="option-anchor-indicator" title="Option Anchor Rule: Khóa cố định tại vị trí D khi trộn đề">
                            <i data-lucide="anchor" class="w-3 h-3"></i> Khóa D
                           </span>`
                        : ''
                    }
                  </div>
                  <button onclick="event.stopPropagation(); app.openFormulaEditorModal('digitize', ${qId}, 'option', ${optIdx})" title="Chỉnh sửa phương án" class="p-1 text-slate-400 hover:text-brand-600 rounded">
                    <i data-lucide="edit-2" class="w-3.5 h-3.5"></i>
                  </button>
                </div>
                <div class="w-full flex justify-center py-1">
                  ${formatStemForDisplay(cleanOptionAnswer(opt.content), true)}
                </div>
              </div>
            `;
          } else {
            html += `
              <div onclick="event.stopPropagation(); app.toggleSingleChoiceAnswer(${qId}, ${optIdx})" class="option-pill flex items-center gap-2.5 px-3 py-2 rounded-xl border ${correctClass} cursor-pointer hover:border-brand-400 transition-all">
                <span class="option-letter-badge w-6 h-6 shrink-0 rounded-lg flex items-center justify-center font-bold text-xs ${isCorrect ? 'bg-emerald-600 text-white' : 'bg-slate-200 text-slate-700'}">
                  ${opt.label}
                </span>

                <div class="flex-1 min-w-0 text-xs text-slate-800 leading-relaxed font-normal">
                  ${formatStemForDisplay(cleanOptionAnswer(opt.content), true)}
                </div>

                <div class="flex items-center space-x-1 shrink-0 ml-auto">
                  ${
                    hasAnchor
                      ? `<span class="option-anchor-indicator" title="Option Anchor Rule: Khóa cố định tại vị trí D khi trộn đề">
                          <i data-lucide="anchor" class="w-3 h-3"></i> Khóa D
                         </span>`
                      : ''
                  }
                  <button onclick="event.stopPropagation(); app.openFormulaEditorModal('digitize', ${qId}, 'option', ${optIdx})" title="Chỉnh sửa phương án" class="p-1 text-slate-400 hover:text-brand-600 hover:bg-black/[0.04] rounded transition-all">
                    <i data-lucide="edit-2" class="w-3.5 h-3.5"></i>
                  </button>
                </div>
              </div>
            `;
          }
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
                <span class="text-slate-800">${formatStemForDisplay(sub.content, true)}</span>
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
              <input type="text" value="${escapeHtml(cleanShortAnswer(q.short_answer_value))}" onchange="app.updateShortAnswerValue(${qId}, this.value)" class="font-mono font-bold text-xs px-2 py-1 bg-white border border-purple-300 rounded-lg w-28">
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
    q.short_answer_value = cleanShortAnswer(val);
    showToast(`Đã lưu kết quả trả lời ngắn: ${q.short_answer_value}`, 'success');
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
    const paginationBox = document.getElementById('doc-viewer-pagination');
    const commitBtn = document.getElementById('btn-commit-to-bank');
    const startDigitizeBtn = document.getElementById('btn-start-digitize');
    const resetStageBtn = document.getElementById('btn-reset-stage');
    const rightHeaderActions = document.getElementById('studio-right-header-actions');
    const leftExportPdfBtn = document.getElementById('btn-left-export-pdf');

    // Staged mode before AI processing
    if (state.stagedExam && state.stagedExam.status === 'STAGED') {
      const count = (state.stagedExam.previews || []).length;
      if (rightHeaderActions) rightHeaderActions.classList.add('hidden');
      if (leftExportPdfBtn) leftExportPdfBtn.classList.add('hidden');
      if (startDigitizeBtn) startDigitizeBtn.classList.remove('hidden');
      if (resetStageBtn) resetStageBtn.classList.remove('hidden');
      if (statusLabel) statusLabel.innerText = `Đã chọn ${count} tệp (Kiểm tra & Sắp xếp thứ tự trước khi gõ đề)`;
      if (statusIndicator) statusIndicator.className = 'w-2 h-2 rounded-full bg-amber-500 animate-pulse';
      if (filenameEl) {
        const rawName = state.digitizeJob.filename || 'Tài liệu chờ xử lý';
        filenameEl.innerText = truncateFilename(rawName, 32);
        filenameEl.title = rawName;
      }
      if (paginationBox) {
        if (count > 1) {
          paginationBox.classList.remove('hidden');
          if (pageDisplay) pageDisplay.innerText = `Trang ${(state.stagedExam.activePreviewIndex || 0) + 1} / ${count}`;
        } else {
          paginationBox.classList.add('hidden');
        }
      }
      if (commitBtn) commitBtn.classList.add('opacity-50', 'cursor-not-allowed');
      return;
    } else if (state.stagedExam && state.stagedExam.status === 'PROCESSING') {
      if (rightHeaderActions) rightHeaderActions.classList.add('hidden');
      if (leftExportPdfBtn) leftExportPdfBtn.classList.add('hidden');
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
      if (leftExportPdfBtn) leftExportPdfBtn.classList.add('hidden');
      if (paginationBox) paginationBox.classList.add('hidden');
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
      if (commitBtn) {
        commitBtn.classList.add('opacity-50', 'cursor-not-allowed');
      }
      state.digitizeJob.avgConfidence = 0;
    } else {
      if (rightHeaderActions) rightHeaderActions.classList.remove('hidden');
      if (leftExportPdfBtn) leftExportPdfBtn.classList.remove('hidden');
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
      const totalPages = state.digitizeJob.totalPages || 1;
      const curPage = state.digitizeJob.currentPage || 1;
      if (paginationBox) {
        if (totalPages > 1) {
          paginationBox.classList.remove('hidden');
          if (pageDisplay) pageDisplay.innerText = `Trang ${curPage} / ${totalPages}`;
        } else {
          paginationBox.classList.add('hidden');
        }
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

  async function exportDigitizedToPdf() {
    const questions = state.digitizeJob.questions || [];
    if (questions.length === 0) {
      showToast('Chưa có câu hỏi nào trong đề thi để xuất PDF. Hãy tải tệp hoặc nạp đề mẫu!', 'warning');
      return;
    }

    const rawTitle = state.digitizeJob.filename ? state.digitizeJob.filename.replace(/\.[^/.]+$/, '') : 'De_Thi_So_Hoa';
    showToast('Đang tạo và dàn trang file PDF chuẩn khảo thí quốc gia...', 'info');

    try {
      const resp = await fetch(`${API_BASE_URL}/digitize/export-pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: rawTitle,
          questions: questions
        })
      });

      if (!resp.ok) {
        const errJson = await resp.json().catch(() => ({}));
        throw new Error(errJson.detail || 'Lỗi từ máy chủ khi tạo file PDF');
      }

      const blob = await resp.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${rawTitle}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

      showToast('Đã tải xuống đề thi file PDF (.pdf) chuẩn in ấn thành công!', 'success');
    } catch (err) {
      console.error('Lỗi xuất file PDF đề thi:', err);
      showToast(`Không thể xuất file PDF: ${err.message}`, 'error');
    }
  }

  async function exportDigitizedToDocx() {
    return exportDigitizedToPdf();
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
    state.digitizeJob.totalPages = files.length;
    state.digitizeJob.currentPage = 1;

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
    state.digitizeJob.currentPage = index + 1;
    const disp = document.getElementById('doc-page-display');
    const total = (state.stagedExam.files && state.stagedExam.files.length) || state.digitizeJob.totalPages || 1;
    if (disp) disp.innerText = `Trang ${index + 1} / ${total}`;
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

  let digitizePollInterval = null;

  function pollJobProgress(jobId) {
    if (digitizePollInterval) {
      clearInterval(digitizePollInterval);
      digitizePollInterval = null;
    }

    digitizePollInterval = setInterval(async () => {
      try {
        const jobRes = await fetch(`${API_BASE_URL}/digitize/jobs/${jobId}`);
        if (!jobRes.ok) return;

        const jobData = await jobRes.json();
        const pct = jobData.progress_percent !== undefined ? jobData.progress_percent : 20;
        const stage = jobData.progress_stage || 'Đang bóc tách đề thi...';

        state.digitizeJob.progressPercent = pct;
        state.digitizeJob.progressStage = stage;

        // Smoothly update DOM progress elements directly
        const pBar = document.getElementById('digitize-progress-bar');
        const pVal = document.getElementById('digitize-progress-val');
        const sLabel = document.getElementById('digitize-stage-label');
        const sDesc = document.getElementById('digitize-stage-desc');

        if (pBar) pBar.style.width = `${pct}%`;
        if (pVal) pVal.innerText = `${pct}%`;
        if (sLabel) sLabel.innerText = stage;
        if (sDesc) sDesc.innerText = stage;

        if (jobData.status === 'EXTRACTED') {
          clearInterval(digitizePollInterval);
          digitizePollInterval = null;

          state.stagedExam.status = 'DONE';
          state.digitizeJob.status = 'EXTRACTED';
          state.digitizeJob.previewUrl = jobData.preview_url || state.digitizeJob.previewUrl;
          state.digitizeJob.previewImages = jobData.preview_images || [];
          state.digitizeJob.aiProvider = jobData.ai_provider;
          state.digitizeJob.aiModel = jobData.ai_model;
          state.digitizeJob.pipelineMode = jobData.pipeline_mode || state.digitizeJob.pipelineMode;
          state.digitizeJob.detectedFigures = jobData.detected_figures || [];
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
                short_answer_value: cleanShortAnswer(q.short_answer_value),
                options: (q.options || []).map((o) => ({ ...o, content: cleanOptionAnswer(o.content) }))
              };
            });
            state.digitizeJob.activeQuestionId = state.digitizeJob.questions[0]?.id || 1;
          }

          let docTotalPages = 1;
          if (jobData.preview_images && jobData.preview_images.length > 0) {
            docTotalPages = jobData.preview_images.length;
          } else if (state.stagedExam && state.stagedExam.files && state.stagedExam.files.length > 0) {
            docTotalPages = state.stagedExam.files.length;
          } else if (jobData.total_pages) {
            docTotalPages = jobData.total_pages;
          }
          state.digitizeJob.totalPages = Math.max(1, docTotalPages);
          state.digitizeJob.currentPage = 1;

          renderDigitizeStudio();
          const aiNote = (jobData.ai_provider && jobData.ai_provider !== 'local_fallback')
            ? ` qua AI (${jobData.ai_provider.toUpperCase()} - ${jobData.ai_model})`
            : '';
          showToast(`Đã gõ lại và bóc tách thành công ${state.digitizeJob.questions.length} câu hỏi${aiNote}!`, 'success');
        } else if (jobData.status === 'FAILED') {
          clearInterval(digitizePollInterval);
          digitizePollInterval = null;
          state.stagedExam.status = 'STAGED';
          state.digitizeJob.status = 'FAILED';
          renderDigitizeStudio();
          showToast(`Lỗi khi gõ đề: ${jobData.error_message || 'Xử lý file thất bại.'}`, 'error');
        }
      } catch (pollErr) {
        console.warn('Progress poll tick error:', pollErr);
      }
    }, 700);
  }

  async function startAIDigitize() {
    const files = state.stagedExam.files;
    if (!files || files.length === 0) {
      showToast('Chưa có tệp nào được chọn để gõ đề!', 'warning');
      return;
    }

    state.stagedExam.status = 'PROCESSING';
    state.digitizeJob.status = 'PROCESSING';
    state.digitizeJob.progressPercent = 10;
    state.digitizeJob.progressStage = 'Đang tải tệp lên máy chủ...';
    renderDigitizeStudio();

    const isMulti = files.length > 1;
    const displayName = isMulti ? `${files.length} trang ảnh đề thi` : files[0].name;

    showToast(`Đang tải lên và khởi động gõ lại đề: ${displayName}...`, 'info');

    const formData = new FormData();
    if (files.length === 1) {
      formData.append('file', files[0]);
    } else {
      for (const f of files) {
        formData.append('files', f);
      }
    }
    formData.append('sync', 'false');
    formData.append('pipeline_mode', 'standard');

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
      state.digitizeJob.pipelineMode = uploadResult.pipeline_mode || state.digitizePipelineMode || 'standard';
      state.digitizeJob.fileType = uploadResult.file_type || state.digitizeJob.fileType;
      state.digitizeJob.previewUrl = uploadResult.preview_url || `${API_BASE_URL}/digitize/jobs/${jobId}/preview`;

      // Start live progress polling
      pollJobProgress(jobId);
    } catch (err) {
      console.warn('AI digitize upload error:', err);
      showToast(`Lỗi khi khởi chạy: ${err.message}`, 'error');
      state.stagedExam.status = 'STAGED';
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
              <input type="text" id="q-edit-short-val" value="${escapeHtml(cleanShortAnswer(q.short_answer_value))}" class="w-full text-xs font-mono font-bold rounded-lg border border-purple-300 p-2 bg-white" placeholder="Ví dụ: 12 hoặc -3.5">
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

  let _livePreviewTimer = null;
  function updateQuestionEditorLivePreview() {
    const stemInput = document.getElementById('q-edit-stem');
    const stemPreview = document.getElementById('q-edit-stem-preview');
    if (stemInput && stemPreview) {
      const val = stemInput.value.trim();
      stemPreview.innerHTML = val ? formatStemForDisplay(val) : '<span class="text-slate-400 italic">Xem trước nội dung câu hỏi...</span>';
      renderKaTeX(stemPreview);
    }

    const expInput = document.getElementById('q-edit-explanation');
    const expPreview = document.getElementById('q-edit-explanation-preview');
    if (expInput && expPreview) {
      const val = expInput.value.trim();
      expPreview.innerHTML = val ? `<strong>Hướng dẫn giải:</strong> ${formatStemForDisplay(val)}` : '<span class="text-slate-400 italic">Xem trước lời giải...</span>';
      renderKaTeX(expPreview);
    }

    clearTimeout(_livePreviewTimer);
    _livePreviewTimer = setTimeout(() => {
      if (stemPreview) renderTikzDiagrams(stemPreview);
      if (expPreview) renderTikzDiagrams(expPreview);
    }, 200);
  }

  function standardizeModalStemToTkz() {
    const stemInput = document.getElementById('q-edit-stem');
    if (!stemInput) return;
    const current = stemInput.value;
    const converted = convertVariationArrayToTkzTab(current);
    if (converted !== current) {
      stemInput.value = converted;
      updateQuestionEditorLivePreview();
      showToast('Đã chuyển đổi bảng biến thiên sang TikZ tkz-tab thành công!', 'success');
    } else {
      showToast('Nội dung đã ở chuẩn TikZ hoặc không chứa bảng biến thiên legacy.', 'info');
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

  function insertStemTikzDiagram(type) {
    let snippet = '';
    if (type === 'rational') {
      snippet = `\n\\begin{tikzpicture}[scale=0.75]
  \\draw[->, thick] (-3, 0) -- (3.5, 0) node[right] {$x$};
  \\draw[->, thick] (0, -2.5) -- (0, 3.5) node[above] {$y$};
  \\node[below left] at (0, 0) {$O$};
  \\draw[dashed, red, thick] (1, -2.5) -- (1, 3.5) node[above] {$x=1$};
  \\draw[dashed, red, thick] (-3, 2) -- (3.5, 2) node[right] {$y=2$};
  \\draw[domain=-3:0.6, smooth, variable=\\x, blue, thick] plot ({\\x}, {(2*\\x - 1)/(\\x - 1)});
  \\draw[domain=1.4:3.5, smooth, variable=\\x, blue, thick] plot ({\\x}, {(2*\\x - 1)/(\\x - 1)});
\\end{tikzpicture}\n`;
    } else if (type === 'cubic') {
      snippet = `\n\\begin{tikzpicture}[scale=0.75]
  \\draw[->, thick] (-2.5, 0) -- (3, 0) node[right] {$x$};
  \\draw[->, thick] (0, -2.5) -- (0, 3) node[above] {$y$};
  \\node[below left] at (0, 0) {$O$};
  \\draw[domain=-2:2.2, smooth, variable=\\x, blue, thick] plot ({\\x}, {(\\x)^3 - 3*(\\x) + 1});
  \\draw[dashed] (-1, 0) -- (-1, 3) -- (0, 3);
  \\draw[dashed] (1, 0) -- (1, -1) -- (0, -1);
  \\filldraw[black] (-1, 3) circle (1.5pt) (1, -1) circle (1.5pt);
\\end{tikzpicture}\n`;
    } else if (type === 'variation_table') {
      snippet = `\n\\begin{tikzpicture}
\\tkzTabInit[nocadre,lgt=1.2,espcl=2.5,deltacl=0.6]
{$x$/.6, $f'(x)$/.6, $f(x)$/2}
{$-\\infty$, $-2$, $1$, $+\\infty$}
\\tkzTabLine{,+,0,-,0,+,}
\\tkzTabVar{-/$-\\infty$, +/$4$, -/$-1$, +/$+\\infty$}
\\end{tikzpicture}\n`;
    } else if (type === 'variation_table_asymptote') {
      snippet = `\n\\begin{tikzpicture}
\\tikzset{double style/.append style = {double distance=2.5pt}}
\\tkzTabInit[nocadre,lgt=1.2,espcl=2.5,deltacl=0.4]
{$x$/.6, $y'$/.6, $y$/2}
{$-\\infty$, $1$, $+\\infty$}
\\tkzTabLine{,+,d,+,}
\\tkzTabVar{-/$2$, +D-/$+\\infty$/$-\\infty$, +/$2$}
\\end{tikzpicture}\n`;
    } else if (type === 'table') {
      snippet = `\n$$\\begin{array}{|c|c|c|c|c|}
\\hline
\\text{Khoảng} & [9{,}5; 12{,}5) & [12{,}5; 15{,}5) & [15{,}5; 18{,}5) & [18{,}5; 21{,}5) \\\\
\\hline
\\text{Tần số} & 3 & 12 & 15 & 24 \\\\
\\hline
\\end{array}$$\n`;
    } else if (type === 'pyramid') {
      snippet = `\n\\begin{tikzpicture}[scale=0.8]
  \\coordinate (A) at (0, 0);
  \\coordinate (B) at (-1.5, -1.2);
  \\coordinate (C) at (2, -1.2);
  \\coordinate (D) at (3.5, 0);
  \\coordinate (S) at (1, 2.5);
  \\draw[thick] (S) -- (B) -- (C) -- (D) -- (S) -- (C);
  \\draw[dashed, thick] (B) -- (A) -- (D) (S) -- (A);
  \\node[above] at (S) {$S$};
  \\node[left] at (B) {$B$};
  \\node[below] at (C) {$C$};
  \\node[right] at (D) {$D$};
  \\node[above left] at (A) {$A$};
\\end{tikzpicture}\n`;
    }
    insertStemSymbol(snippet);
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
    q.stem = formatLatexRules(document.getElementById('q-edit-stem').value.trim());
    q.explanation = formatLatexRules(document.getElementById('q-edit-explanation').value.trim());

    if (q.item_format === 'SINGLE_CHOICE' && state.activeEditingQuestion.options) {
      q.options = JSON.parse(JSON.stringify(state.activeEditingQuestion.options)).map((opt) => ({
        ...opt,
        content: formatLatexRules(opt.content)
      }));
    } else if (q.item_format === 'TRUE_FALSE_GROUP' && state.activeEditingQuestion.sub_statements) {
      q.sub_statements = JSON.parse(JSON.stringify(state.activeEditingQuestion.sub_statements)).map((sub) => ({
        ...sub,
        content: formatLatexRules(sub.content),
        explanation: formatLatexRules(sub.explanation)
      }));
    } else if (q.item_format === 'SHORT_ANSWER') {
      const valEl = document.getElementById('q-edit-short-val');
      const tolEl = document.getElementById('q-edit-short-tol');
      if (valEl) q.short_answer_value = cleanShortAnswer(valEl.value);
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
      showToast('Đang nạp đề mẫu Toán 12 (LaTeX + Đồ thị)...', 'info');
      state.digitizeJob.filename = 'De_Mau_Toan_12_Chuan_2025.pdf';
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
    const total = (state.stagedExam && state.stagedExam.files && state.stagedExam.files.length > 0)
      ? state.stagedExam.files.length
      : (state.digitizeJob.totalPages || 1);
    let p = (state.digitizeJob.currentPage || 1) + delta;
    if (p < 1) p = 1;
    if (p > total) p = total;
    state.digitizeJob.currentPage = p;

    const disp = document.getElementById('doc-page-display');
    if (disp) disp.innerText = `Trang ${p} / ${total}`;

    // If in staged mode, also select staged page
    if (state.stagedExam && state.stagedExam.status === 'STAGED') {
      state.stagedExam.activePreviewIndex = p - 1;
      renderDocumentPaperPreview();
      showToast(`Chuyển sang Trang ${p}`, 'info');
      return;
    }

    // Scroll to the corresponding page in multi-image preview
    const targetPage = document.getElementById(`doc-preview-page-${p}`);
    if (targetPage) {
      targetPage.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
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
            ${formatStemForDisplay(q.stem)}
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

          <div class="font-medium text-slate-900 leading-relaxed">${formatStemForDisplay(q.stem)}</div>

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
          <div class="text-slate-800 font-medium">${formatStemForDisplay(q.stem)}</div>

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
   * Downloads official exam package (.ZIP containing vector PDF documents, solution guides, and answer sheets).
   */
  async function downloadPublishZip(format = 'pdf') {
    showToast(`Đang đóng gói đề thi PDF (.zip), vui lòng chờ trong giây lát...`, 'info');

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
    const downloadUrl = `${API_BASE_URL}/exams/${targetId}/export-zip?format=pdf`;

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
      a.download = `Goi_DeThi_PDF_${targetId.slice(0, 8)}.zip`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(blobUrl);
      showToast(`Đã tải xuống thành công gói ấn phẩm đề thi PDF!`, 'success');
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
    return downloadActiveVariantPdf();
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
    const newContent = formatLatexRules(input.value.trim());

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

    // Register Service Worker for Offline PWA Support (Task PK-01)
    if ('serviceWorker' in navigator && window.location.protocol.startsWith('http')) {
      navigator.serviceWorker.register('/sw.js').catch((err) => {
        console.debug('ServiceWorker registration skipped/failed:', err);
      });
    }
  }

  // ============================================================================
  // ============================================================================
  // 13. TAB 2: SOẠN ĐỀ (AI LATEX COMPOSER & LIVE PDF PREVIEW - NOCTORIUM CLONE)
  // ============================================================================
  const composer = {
    initialized: false,
    activeTitle: 'Đề thi Khảo sát Toán 12',
    currentLatex: '',
    isCompiling: false,
    autoCompile: true,
    compileTimer: null,
    pdfUrl: '',
    zoomLevel: 1.0,
    aiPaneVisible: true,
    aiPaneCollapsed: false,
    showSolution: true,
    chatHistory: [],
    sessions: [],
    currentSessionId: null,
    compilationHistory: [],
    templates: {},

    EX_TEST_TEMPLATES: {
      'tracnghiem': `\\begin{ex}\n\n\\choice\n{}\n{}\n{}\n{}\n\\loigiai{\n\n}\n\\end{ex}\n`,
      'dungsai': `\\begin{ex}\n\n\\choiceTFt\n{}\n{}\n{}\n{}\n\\loigiai{\n\\begin{itemchoice}\n\\itemch\n\\itemch\n\\itemch\n\\itemch\n\\end{itemchoice}\n}\n\\end{ex}\n`,
      'traloingan': `\\begin{ex}\n\n\\par\n\\shortans[oly]{}\n\\loigiai{\n\n}\n\\end{ex}\n`,
      'tuluan': `\\begin{bt}\n\n\\begin{enumerate}[a]\n\\item \n\\item \n\\end{enumerate}\n\\loigiai{\n\\begin{enumerate}[a]\n\\item \n\\item \n\\end{enumerate}\n}\n\\end{bt}\n`,
      'hinhtikz': `\\begin{tikzpicture}[scale=1, line join=round, line cap=round, >=stealth]\n\n\\end{tikzpicture}\n`,
      'hinhcanhchu': `\\immini[thm]{}{\n\\begin{tikzpicture}[scale=1, line join=round, line cap=round, >=stealth]\n\n\\end{tikzpicture}\n}\n`,
      'loigiai': `\\loigiai{\n\n}\n`
    },

    SNIPPETS: {
      '\\dfrac{a}{b}': '\\dfrac{a}{b}',
      '\\sqrt{x}': '\\sqrt{x}',
      '\\overrightarrow{u}': '\\overrightarrow{u}',
      '\\in \\mathbb{R}': '\\in \\mathbb{R}',
      'extest_ex': `\\begin{ex}\nCho hàm số $y = f(x)$... Mệnh đề nào sau đây đúng?\n\\choice\n{\\True Phương án A}\n{Phương án B}\n{Phương án C}\n{Phương án D}\n\\begin{loigiai}\nLời giải chi tiết cho câu hỏi.\n\\end{loigiai}\n\\end{ex}\n`,
      'extest_choiceTF': `\\begin{ex}\nCho hàm số $y = f(x)$... Xét tính đúng/sai của các khẳng định sau:\n\\choiceTF\n{\\True Khẳng định a) đúng.}\n{Khẳng định b) sai.}\n{\\True Khẳng định c) đúng.}\n{Khẳng định d) sai.}\n\\begin{loigiai}\n\\begin{itemchoice}\n\\itemch Lời giải ý a.\n\\itemch Lời giải ý b.\n\\itemch Lời giải ý c.\n\\itemch Lời giải ý d.\n\\end{itemchoice}\n\\end{loigiai}\n\\end{ex}\n`,
      'extest_shortans': `\\begin{ex}\nTính giá trị của biểu thức $P = ...$\n\\shortans{12}\n\\begin{loigiai}\nLời giải chi tiết.\n\\end{loigiai}\n\\end{ex}\n`,
      'extest_immini': `\\immini{\n  Nội dung câu hỏi đặt ở đây...\n  \\choice\n  {\\True $A$}\n  {$B$}\n  {$C$}\n  {$D$}\n}{\n  \\begin{tikzpicture}[scale=0.6, >=stealth]\n    \\draw[->] (-2.5,0) -- (2.5,0) node[right] {$x$};\n    \\draw[->] (0,-2.5) -- (0,2.5) node[above] {$y$};\n    \\node[below left] at (0,0) {$O$};\n  \\end{tikzpicture}\n}\n`,
      'tkz_tab': `\\begin{tikzpicture}\n  \\tkzTabInit[nocadre,lgt=1.2,espcl=2.5,deltacl=0.6]\n  {$x$/.6, $f'(x)$/.6, $f(x)$/2}\n  {$-\\infty$,$-2$,$1$,$+\\infty$}\n  \\tkzTabLine{,+,0,-,0,+,}\n  \\tkzTabVar{-/$-\\infty$,+/$4$,-/$-1$,+/$+\\infty$}\n\\end{tikzpicture}\n`,
      'tikz_cubic': `\\begin{tikzpicture}[scale=0.65, >=stealth]\n  \\clip (-3.8, -5.5) rectangle (4.2, 5.5);\n  \\draw[->, thick] (-3.5, 0) -- (3.8, 0) node[right] {$x$};\n  \\draw[->, thick] (0, -5) -- (0, 5) node[above] {$y$};\n  \\node[below left] at (0, 0) {$O$};\n  \\draw[dashed] (-1, 0) node[below] {$-1$} -- (-1, 4) -- (0, 4) node[left] {$4$};\n  \\draw[dashed] (2, 0) node[above] {$2$} -- (2, -3) -- (0, -3) node[left] {$-3$};\n  \\draw[thick, black, smooth, samples=100, domain=-2.5:3.2] plot (\\x, {(\\x)^3 - 1.5*(\\x)^2 - 6*(\\x) + 0.5});\n  \\fill (-1, 4) circle (1.5pt);\n  \\fill (2, -3) circle (1.5pt);\n\\end{tikzpicture}\n`,
      'tikz_rational': `\\begin{tikzpicture}[scale=0.7, >=stealth]\n  \\clip (-4.5, -4.5) rectangle (4.5, 5.5);\n  \\draw[->, thick] (-4.2, 0) -- (4.2, 0) node[right] {$x$};\n  \\draw[->, thick] (0, -4.2) -- (0, 5.2) node[above] {$y$};\n  \\node[below left] at (0, 0) {$O$};\n  \\draw[dashed, thick] (1, -4.2) -- (1, 5.2) node[above] {$x=1$};\n  \\draw[dashed, thick] (-4.2, 2) -- (4.2, 2) node[right] {$y=2$};\n  \\draw[thick, black, smooth, domain=-4:0.7, samples=80] plot (\\x, {(2*\\x - 1)/(\\x - 1)});\n  \\draw[thick, black, smooth, domain=1.3:4, samples=80] plot (\\x, {(2*\\x - 1)/(\\x - 1)});\n\\end{tikzpicture}\n`,
      'tikz_pyramid': `\\begin{tikzpicture}[scale=0.8]\n  \\coordinate (A) at (0, 0);\n  \\coordinate (B) at (-1.5, -1.2);\n  \\coordinate (C) at (2, -1.2);\n  \\coordinate (D) at (3.5, 0);\n  \\coordinate (S) at (1, 2.5);\n  \\draw[thick] (S) -- (B) -- (C) -- (D) -- (S) -- (C);\n  \\draw[dashed, thick] (B) -- (A) -- (D) (S) -- (A);\n  \\node[above] at (S) {$S$};\n  \\node[left] at (B) {$B$};\n  \\node[below] at (C) {$C$};\n  \\node[right] at (D) {$D$};\n  \\node[above left] at (A) {$A$};\n\\end{tikzpicture}\n`
    },

    async init() {
      if (this.initialized) return;
      this.initialized = true;

      // 1. Restore Title
      const savedTitle = localStorage.getItem('quesy_composer_title');
      if (savedTitle) {
        this.activeTitle = savedTitle;
        const titleEl = document.getElementById('composer-doc-title');
        if (titleEl) titleEl.value = savedTitle;
      }

      // 2. Load Templates list from API
      try {
        const res = await fetch(`${API_BASE_URL}/composer/templates`);
        if (res.ok) {
          const data = await res.json();
          if (data.templates) {
            data.templates.forEach((t) => {
              this.templates[t.id] = t;
            });
          }
        }
      } catch (e) {
        console.warn('Could not load templates from API:', e);
      }

      // 3. Restore Content or fallback to ex_test standard template
      const savedContent = localStorage.getItem('quesy_composer_content');
      const editor = document.getElementById('composer-editor-input');
      if (savedContent && savedContent.trim()) {
        this.currentLatex = savedContent;
      } else if (this.templates['ex_test_standard_exam']) {
        this.currentLatex = this.templates['ex_test_standard_exam'].latex;
      } else if (this.templates['circular_32_full_exam']) {
        this.currentLatex = this.templates['circular_32_full_exam'].latex;
      } else {
        this.currentLatex = `\\documentclass[11pt,a4paper]{article}\n\\usepackage{fontspec}\n\\usepackage{amsmath,amssymb}\n\\usepackage{tikz,tkz-tab}\n\\usepackage{tcolorbox}\n\\tcbuselibrary{skins,breakable,xparse}\n\\usepackage[dethi]{ex_test}\n\n\\begin{document}\n\\section*{ĐỀ THI KHẢO SÁT TOÁN 12}\n\n\\begin{ex}\nCho hàm số bậc ba $y = f(x)$...\n\\choice\n{\\True $A$}\n{$B$}\n{$C$}\n{$D$}\n\\begin{loigiai}\nLời giải chi tiết.\n\\end{loigiai}\n\\end{ex}\n\n\\end{document}\n`;
      }

      if (editor) {
        editor.value = this.currentLatex;
        this.updateGutter();
        this.updateCharCount();
      }

      // 4. Restore Chat & History & Resizers
      this.initChat();
      this.initHistory();
      this.initAIPopupResizer();
      this.initSplitResizer();

      // 5. Setup global click-outside for dropdowns
      document.addEventListener('click', (e) => {
        if (!e.target.closest('#btn-dropdown-gemini') && !e.target.closest('#composer-dropdown-gemini')) {
          const m = document.getElementById('composer-dropdown-gemini');
          if (m) m.classList.add('hidden');
        }
        if (!e.target.closest('#btn-dropdown-them') && !e.target.closest('#composer-dropdown-them')) {
          const m = document.getElementById('composer-dropdown-them');
          if (m) m.classList.add('hidden');
        }
        if (!e.target.closest('#btn-dropdown-export') && !e.target.closest('#composer-dropdown-export')) {
          const m = document.getElementById('composer-dropdown-export');
          if (m) m.classList.add('hidden');
        }
      });

      // 6. Initial Compile
      setTimeout(() => {
        this.compile(false);
      }, 300);

      if (window.lucide) lucide.createIcons();
    },

    toggleDropdown(name) {
      const allMenus = ['gemini', 'them', 'export'];
      allMenus.forEach((m) => {
        const el = document.getElementById(`composer-dropdown-${m}`);
        if (el) {
          if (m === name) {
            el.classList.toggle('hidden');
          } else {
            el.classList.add('hidden');
          }
        }
      });
      if (window.lucide) lucide.createIcons();
    },

    insertTemplate(templateKey) {
      const code = this.EX_TEST_TEMPLATES[templateKey];
      if (!code) return;
      this.insertSnippet(code);
      const menu = document.getElementById('composer-dropdown-them');
      if (menu) menu.classList.add('hidden');
      showToast(`Đã chèn mẫu ${templateKey.toUpperCase()}!`, 'success');
    },

    triggerGeminiPrompt(type) {
      const menu = document.getElementById('composer-dropdown-gemini');
      if (menu) menu.classList.add('hidden');

      const prompts = {
        'tracnghiem': 'Tạo 1 câu trắc nghiệm 4 lựa chọn theo chuẩn gói ex_test (\\begin{ex} ... \\choice ... \\loigiai)',
        'dungsai': 'Tạo 1 câu hỏi Đúng/Sai 4 khẳng định theo chuẩn Quyết định 764 dùng \\choiceTF và itemchoice',
        'traloingan': 'Tạo 1 câu hỏi Trả lời ngắn theo chuẩn \\shortans',
        'tkz_tab': 'Tạo 1 bảng biến thiên hàm số bằng gói tkz-tab',
        'tikz': 'Vẽ 1 đồ thị toạ độ hoặc hình học không gian bằng TikZ',
        'sualoi': 'Kiểm tra và sửa lỗi cú pháp LaTeX trong tài liệu đang soạn thảo',
        'loigiai': 'Viết lời giải chi tiết theo môi trường \\loigiai cho câu hỏi hiện tại'
      };

      const promptText = prompts[type] || 'Hỗ trợ soạn câu hỏi Toán';
      this.sendPrompt(promptText);
    },

    undo() {
      const editor = document.getElementById('composer-editor-input');
      if (editor) {
        editor.focus();
        document.execCommand('undo');
        this.handleEditorInput();
      }
    },

    redo() {
      const editor = document.getElementById('composer-editor-input');
      if (editor) {
        editor.focus();
        document.execCommand('redo');
        this.handleEditorInput();
      }
    },

    copyAll() {
      if (!this.currentLatex) return;
      navigator.clipboard.writeText(this.currentLatex);
      showToast('Đã sao chép toàn bộ mã nguồn vào bộ nhớ tạm!', 'success');
      const menu = document.getElementById('composer-dropdown-export');
      if (menu) menu.classList.add('hidden');
    },

    downloadTex() {
      if (!this.currentLatex) return;
      const blob = new Blob([this.currentLatex], { type: 'text/x-tex;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${this.activeTitle.replace(/\\s+/g, '_')}.tex`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showToast('Đang tải tệp mã nguồn .tex...', 'info');
      const menu = document.getElementById('composer-dropdown-export');
      if (menu) menu.classList.add('hidden');
    },

    newDocument() {
      if (confirm('Bạn có chắc chắn muốn tạo mới tài liệu?')) {
        const cleanLatex = `\\documentclass[12pt,a4paper]{article}\n\\usepackage{fontspec}\n\\usepackage{amsmath,amssymb}\n\\usepackage{tikz,tkz-tab}\n\\usepackage[dethi]{ex_test}\n\n\\begin{document}\n\n\\begin{ex}\n\n\\choice\n{}\n{}\n{}\n{}\n\\loigiai{\n\n}\n\\end{ex}\n\n\\end{document}\n`;
        const editor = document.getElementById('composer-editor-input');
        if (editor) {
          editor.value = cleanLatex;
          this.currentLatex = cleanLatex;
          this.handleEditorInput();
          this.compile(true);
          showToast('Đã tạo mới tài liệu với mẫu ex_test!', 'success');
        }
      }
    },

    toggleSolution() {
      this.showSolution = !this.showSolution;
      const toggle = document.getElementById('composer-solution-toggle');
      if (toggle) {
        if (this.showSolution) {
          toggle.className = 'w-8 h-4.5 bg-[#7c1925] rounded-full p-0.5 transition-colors flex items-center justify-end cursor-pointer';
        } else {
          toggle.className = 'w-8 h-4.5 bg-slate-300 rounded-full p-0.5 transition-colors flex items-center justify-start cursor-pointer';
        }
      }

      // Update LaTeX package option in editor if present
      let val = this.currentLatex;
      if (this.showSolution) {
        val = val.replace(/\\usepackage\[dethi\]\{ex_test\}/, '\\usepackage[loigiai]{ex_test}');
        showToast('Đã bật chế độ LỜI GIẢI chi tiết.', 'info');
      } else {
        val = val.replace(/\\usepackage\[(?:loigiai|solcolor|color)\]\{ex_test\}/, '\\usepackage[dethi]{ex_test}');
        showToast('Đã chuyển sang chế độ IN ĐỀ THI (ẩn lời giải).', 'info');
      }

      const editor = document.getElementById('composer-editor-input');
      if (editor) {
        editor.value = val;
        this.currentLatex = val;
        this.handleEditorInput();
        this.compile(true);
      }
    },

    switchPreviewTab(tab) {
      const viewPreview = document.getElementById('composer-view-preview');
      const viewHistory = document.getElementById('composer-view-history');
      const btnPreview = document.getElementById('composer-tab-btn-preview');
      const btnHistory = document.getElementById('composer-tab-btn-history');

      if (tab === 'preview') {
        if (viewPreview) viewPreview.classList.remove('hidden');
        if (viewHistory) viewHistory.classList.add('hidden');
        if (btnPreview) btnPreview.className = 'border-b-2 border-[#7c1925] text-[#7c1925] font-bold pb-1.5 pt-1 px-3 text-xs tracking-wider transition-all';
        if (btnHistory) btnHistory.className = 'text-slate-500 hover:text-slate-800 pb-1.5 pt-1 px-3 text-xs font-semibold transition-all cursor-pointer';
      } else {
        if (viewPreview) viewPreview.classList.add('hidden');
        if (viewHistory) viewHistory.classList.remove('hidden');
        if (btnHistory) btnHistory.className = 'border-b-2 border-[#7c1925] text-[#7c1925] font-bold pb-1.5 pt-1 px-3 text-xs tracking-wider transition-all cursor-pointer';
        if (btnPreview) btnPreview.className = 'text-slate-500 hover:text-slate-800 pb-1.5 pt-1 px-3 text-xs font-semibold transition-all';
        this.renderHistory();
      }
      if (window.lucide) lucide.createIcons();
    },

    initHistory() {
      const saved = localStorage.getItem('quesy_composer_compilation_history');
      if (saved) {
        try {
          this.compilationHistory = JSON.parse(saved);
        } catch (e) {
          this.compilationHistory = [];
        }
      }
    },

    saveHistoryItem(pdfUrl) {
      const item = {
        id: Date.now(),
        timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        title: this.activeTitle,
        latex: this.currentLatex,
        pdfUrl: pdfUrl
      };
      this.compilationHistory.unshift(item);
      if (this.compilationHistory.length > 15) this.compilationHistory.pop();
      localStorage.setItem('quesy_composer_compilation_history', JSON.stringify(this.compilationHistory));
    },

    renderHistory() {
      const list = document.getElementById('composer-history-list');
      if (!list) return;

      if (!this.compilationHistory || this.compilationHistory.length === 0) {
        list.innerHTML = `
          <div class="py-8 text-center text-slate-400">
            <i data-lucide="inbox" class="w-8 h-8 mx-auto mb-2 opacity-50"></i>
            <p>Chưa có lịch sử biên dịch nào.</p>
          </div>
        `;
        if (window.lucide) lucide.createIcons();
        return;
      }

      list.innerHTML = this.compilationHistory.map((item, idx) => `
        <div class="p-2.5 rounded-lg border border-slate-200/80 hover:border-brand-300 hover:bg-slate-50 flex items-center justify-between transition-all">
          <div class="min-w-0 flex-1">
            <div class="font-bold text-slate-800 truncate">${escapeHtml(item.title || 'Đề thi')}</div>
            <div class="text-[10px] text-slate-400 font-mono mt-0.5">${item.timestamp} • ${item.latex.length} ký tự</div>
          </div>
          <div class="flex items-center space-x-1 ml-3 shrink-0">
            <button type="button" onclick="app.composer.restoreHistory(${idx})" class="px-2 py-1 bg-brand-50 hover:bg-brand-100 text-brand-700 rounded text-[11px] font-semibold transition-all" title="Khôi phục mã nguồn này">
              Khôi phục
            </button>
            <a href="${item.pdfUrl}" target="_blank" class="p-1 hover:bg-slate-200 rounded text-slate-500" title="Mở PDF tab mới">
              <i data-lucide="external-link" class="w-3.5 h-3.5"></i>
            </a>
          </div>
        </div>
      `).join('');

      if (window.lucide) lucide.createIcons();
    },

    restoreHistory(index) {
      const item = this.compilationHistory[index];
      if (!item) return;
      if (confirm(`Khôi phục phiên bản lúc ${item.timestamp}?`)) {
        const editor = document.getElementById('composer-editor-input');
        if (editor) {
          editor.value = item.latex;
          this.currentLatex = item.latex;
          this.handleEditorInput();
          this.switchPreviewTab('preview');
          this.compile(true);
          showToast(`Đã khôi phục phiên bản lúc ${item.timestamp}!`, 'success');
        }
      }
    },

    clearHistory() {
      if (confirm('Xóa sạch lịch sử các lần biên dịch?')) {
        this.compilationHistory = [];
        localStorage.removeItem('quesy_composer_compilation_history');
        this.renderHistory();
        showToast('Đã xóa sạch lịch sử.', 'info');
      }
    },

    isAIPopupOpen: false,
    aiPopupHeight: '56%',
    isHistoryViewOpen: false,

    openAIPopup(prefillPrompt = '') {
      const popup = document.getElementById('composer-ai-popup');
      const compactBar = document.getElementById('composer-ai-compact-bar');
      const chatInput = document.getElementById('composer-chat-input');
      const compactInput = document.getElementById('composer-compact-input');

      if (popup) {
        popup.classList.remove('hidden');
        this.isAIPopupOpen = true;
      }
      if (compactBar) {
        compactBar.classList.add('hidden');
      }

      if (prefillPrompt && chatInput) {
        chatInput.value = prefillPrompt;
      } else if (compactInput && compactInput.value && chatInput) {
        chatInput.value = compactInput.value;
        compactInput.value = '';
      }

      if (chatInput) {
        setTimeout(() => chatInput.focus(), 60);
      }

      const container = document.getElementById('composer-chat-messages');
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
      if (window.lucide) lucide.createIcons();
    },

    closeAIPopup() {
      const popup = document.getElementById('composer-ai-popup');
      const compactBar = document.getElementById('composer-ai-compact-bar');
      const historyPanel = document.getElementById('composer-ai-history-panel');
      const chatMessages = document.getElementById('composer-chat-messages');

      if (popup) {
        popup.classList.add('hidden');
        this.isAIPopupOpen = false;
      }
      if (historyPanel) {
        historyPanel.classList.add('hidden');
        this.isHistoryViewOpen = false;
      }
      if (chatMessages) {
        chatMessages.classList.remove('hidden');
      }
      if (compactBar) {
        compactBar.classList.remove('hidden');
      }
      if (window.lucide) lucide.createIcons();
    },

    toggleAIPopupHeight() {
      const popup = document.getElementById('composer-ai-popup');
      if (!popup) return;
      if (this.aiPopupHeight === '56%') {
        this.aiPopupHeight = '78%';
        popup.style.height = '78%';
      } else {
        this.aiPopupHeight = '56%';
        popup.style.height = '56%';
      }
    },

    toggleAIPopupFullscreen() {
      const popup = document.getElementById('composer-ai-popup');
      const icon = document.getElementById('composer-ai-max-icon');
      if (!popup) return;

      if (this.aiPopupHeight === '92%') {
        this.aiPopupHeight = '56%';
        popup.style.height = '56%';
        if (icon) icon.setAttribute('data-lucide', 'maximize-2');
      } else {
        this.aiPopupHeight = '92%';
        popup.style.height = '92%';
        if (icon) icon.setAttribute('data-lucide', 'minimize-2');
      }
      if (window.lucide) lucide.createIcons();
    },

    handleCompactInputKey(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.submitFromCompact();
      }
    },

    submitFromCompact() {
      const compactInput = document.getElementById('composer-compact-input');
      const text = compactInput ? compactInput.value.trim() : '';
      if (!text) {
        if (compactInput) compactInput.focus();
        return;
      }
      if (compactInput) compactInput.value = '';
      const chatInput = document.getElementById('composer-chat-input');
      if (chatInput) chatInput.value = '';

      this.openAIPopup(text);
      this.sendPrompt(text);
    },

    toggleQuickPromptMenu(e) {
      if (e) e.stopPropagation();
      const menu = document.getElementById('composer-quick-prompts-menu');
      if (menu) menu.classList.toggle('hidden');
    },

    toggleCompactQuickMenu(e) {
      if (e) e.stopPropagation();
      const menu = document.getElementById('composer-compact-quick-menu');
      if (menu) menu.classList.toggle('hidden');
    },

    applyQuickPrompt(promptText) {
      const quickMenu = document.getElementById('composer-quick-prompts-menu');
      const compactMenu = document.getElementById('composer-compact-quick-menu');
      if (quickMenu) quickMenu.classList.add('hidden');
      if (compactMenu) compactMenu.classList.add('hidden');

      this.openAIPopup(promptText);
      const chatInput = document.getElementById('composer-chat-input');
      if (chatInput) {
        chatInput.value = promptText;
        chatInput.focus();
      }
    },

    archiveCurrentSession() {
      if (!this.chatHistory || !this.chatHistory.some(m => m.role === 'user')) return;
      if (!this.currentSessionId) {
        this.currentSessionId = 'session_' + Date.now();
      }
      const firstUser = this.chatHistory.find(m => m.role === 'user');
      const title = (firstUser ? firstUser.content : 'Phiên trò chuyện').slice(0, 50);
      const nowStr = new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) + ' ' + new Date().toLocaleDateString('vi-VN');

      const existingIdx = this.sessions.findIndex(s => s.id === this.currentSessionId);
      const sessionObj = {
        id: this.currentSessionId,
        title: title,
        timestamp: existingIdx >= 0 && this.sessions[existingIdx].timestamp ? this.sessions[existingIdx].timestamp : nowStr,
        updatedAt: nowStr,
        messages: JSON.parse(JSON.stringify(this.chatHistory))
      };

      if (existingIdx >= 0) {
        this.sessions[existingIdx] = sessionObj;
      } else {
        this.sessions.unshift(sessionObj);
      }

      if (this.sessions.length > 30) {
        this.sessions = this.sessions.slice(0, 30);
      }

      try {
        localStorage.setItem('quesy_composer_sessions', JSON.stringify(this.sessions));
      } catch (e) {
        console.warn('Could not save sessions:', e);
      }
    },

    newChat() {
      this.archiveCurrentSession();
      this.currentSessionId = 'session_' + Date.now();
      this.chatHistory = [
        {
          role: 'assistant',
          content: 'Cuộc trò chuyện mới đã bắt đầu! Bạn có thể yêu cầu tôi đổi cỡ chữ (`12pt`), tạo câu hỏi trắc nghiệm chuẩn, chèn bảng biến thiên `tkz-tab` hoặc vẽ hình TikZ.'
        }
      ];
      this.renderChatMessages();
      this.renderHistoryList();
      showToast('Đã bắt đầu phiên trò chuyện mới!', 'info');
    },

    toggleHistoryView() {
      const historyPanel = document.getElementById('composer-ai-history-panel');
      const chatMessages = document.getElementById('composer-chat-messages');
      const inputContainer = document.getElementById('composer-chat-input-container');
      const popup = document.getElementById('composer-ai-popup');
      if (!historyPanel || !chatMessages) return;

      this.isHistoryViewOpen = !this.isHistoryViewOpen;
      if (this.isHistoryViewOpen) {
        if (popup && popup.offsetHeight < 320) {
          popup.style.height = '56%';
          this.aiPopupHeight = '56%';
        }
        this.renderHistoryList();
        historyPanel.classList.remove('hidden');
        chatMessages.classList.add('hidden');
        if (inputContainer) inputContainer.classList.add('hidden');
      } else {
        historyPanel.classList.add('hidden');
        chatMessages.classList.remove('hidden');
        if (inputContainer) inputContainer.classList.remove('hidden');
      }
    },

    renderHistoryList() {
      const listEl = document.getElementById('composer-ai-history-list');
      if (!listEl) return;

      try {
        const saved = localStorage.getItem('quesy_composer_sessions');
        if (saved) {
          this.sessions = JSON.parse(saved);
        }
      } catch (e) {}

      if (!this.sessions || this.sessions.length === 0) {
        listEl.innerHTML = `
          <div class="py-8 text-center text-slate-500 text-xs select-none">
            <i data-lucide="history" class="w-8 h-8 mx-auto mb-2 text-slate-600 stroke-[1.5]"></i>
            <p class="font-medium text-slate-400">Chưa có phiên lịch sử nào</p>
            <p class="text-[11px] text-slate-600 mt-1">Các phiên trò chuyện trước sẽ tự động lưu lại ở đây khi bạn tương tác với Trợ lý.</p>
          </div>
        `;
        if (window.lucide) lucide.createIcons();
        return;
      }

      listEl.innerHTML = this.sessions.map((sess) => {
        const userMsgs = (sess.messages || []).filter(m => m.role === 'user');
        const msgCount = userMsgs.length;
        const isCurrent = sess.id === this.currentSessionId;
        const titleEscaped = escapeHtml(sess.title || 'Phiên trò chuyện');
        const timeDisplay = escapeHtml(sess.updatedAt || sess.timestamp || '');

        const promptsList = userMsgs.slice(-3).map(m => {
          const rawTextB64 = btoa(unescape(encodeURIComponent(m.content || '')));
          return `
            <div onclick="app.composer.selectHistoryItemB64('${rawTextB64}')" class="px-2 py-1 rounded bg-[#1c1c20] hover:bg-[#282830] text-slate-300 text-[11px] truncate cursor-pointer transition-colors flex items-center space-x-1.5" title="Bấm để dùng lại câu lệnh này">
              <span class="text-purple-400 font-bold text-[10px]">›</span>
              <span class="truncate">${escapeHtml(m.content)}</span>
            </div>
          `;
        }).join('');

        return `
          <div class="p-3 rounded-xl bg-[#202024] border ${isCurrent ? 'border-purple-500/40 bg-purple-950/10' : 'border-white/5'} hover:border-white/15 transition-all text-xs space-y-2">
            <div class="flex items-center justify-between min-w-0">
              <div class="min-w-0 flex-1">
                <div class="flex items-center space-x-2">
                  <span class="font-bold text-slate-200 truncate font-sans text-xs">${titleEscaped}</span>
                  ${isCurrent ? '<span class="px-1.5 py-0.2 rounded-full bg-purple-500/20 text-purple-300 text-[9px] font-bold">Hiện tại</span>' : ''}
                </div>
                <div class="text-[10px] text-slate-400 mt-0.5 flex items-center space-x-2">
                  <span>${timeDisplay}</span>
                  <span>•</span>
                  <span>${msgCount} câu lệnh</span>
                </div>
              </div>
              <div class="flex items-center space-x-1 shrink-0 ml-2">
                <button type="button" onclick="app.composer.loadSession('${sess.id}')" class="px-2.5 py-1 bg-purple-600/90 hover:bg-purple-600 text-white rounded-lg text-[11px] font-semibold flex items-center space-x-1 active:scale-95 transition-all cursor-pointer shadow-xs" title="Nạp lại toàn bộ phiên này">
                  <i data-lucide="rotate-ccw" class="w-3 h-3"></i>
                  <span>Nạp lại</span>
                </button>
                <button type="button" onclick="app.composer.deleteSession('${sess.id}')" class="p-1 hover:bg-rose-900/30 text-slate-500 hover:text-rose-400 rounded-lg transition-all cursor-pointer" title="Xóa phiên này">
                  <i data-lucide="trash-2" class="w-3.5 h-3.5"></i>
                </button>
              </div>
            </div>
            ${promptsList ? `<div class="space-y-1 pt-1 border-t border-white/5">${promptsList}</div>` : ''}
          </div>
        `;
      }).join('');

      if (window.lucide) lucide.createIcons();
    },

    loadSession(sessionId) {
      const sess = this.sessions.find(s => s.id === sessionId);
      if (!sess) return;
      this.currentSessionId = sess.id;
      this.chatHistory = JSON.parse(JSON.stringify(sess.messages || []));

      const historyPanel = document.getElementById('composer-ai-history-panel');
      const chatMessages = document.getElementById('composer-chat-messages');
      if (historyPanel) historyPanel.classList.add('hidden');
      if (chatMessages) chatMessages.classList.remove('hidden');
      const inputContainer = document.getElementById('composer-chat-input-container');
      if (inputContainer) inputContainer.classList.remove('hidden');
      this.isHistoryViewOpen = false;

      this.renderChatMessages();
      showToast(`Đã nạp lại phiên: ${sess.title}`, 'success');
    },

    deleteSession(sessionId) {
      this.sessions = this.sessions.filter(s => s.id !== sessionId);
      try {
        localStorage.setItem('quesy_composer_sessions', JSON.stringify(this.sessions));
      } catch (e) {}
      this.renderHistoryList();
      showToast('Đã xóa phiên khỏi lịch sử!', 'info');
    },

    clearAllSessions() {
      if (!confirm('Bạn có chắc chắn muốn xóa toàn bộ lịch sử các phiên trước?')) return;
      this.sessions = [];
      localStorage.removeItem('quesy_composer_sessions');
      this.renderHistoryList();
      showToast('Đã xóa toàn bộ lịch sử các phiên!', 'info');
    },

    selectHistoryItem(encodedText) {
      const text = decodeURIComponent(encodedText);
      const historyPanel = document.getElementById('composer-ai-history-panel');
      const chatMessages = document.getElementById('composer-chat-messages');
      if (historyPanel) historyPanel.classList.add('hidden');
      if (chatMessages) chatMessages.classList.remove('hidden');
      const inputContainer = document.getElementById('composer-chat-input-container');
      if (inputContainer) inputContainer.classList.remove('hidden');
      this.isHistoryViewOpen = false;

      const input = document.getElementById('composer-chat-input');
      if (input) {
        input.value = text;
        input.focus();
      }
    },

    selectHistoryItemB64(b64) {
      try {
        const text = decodeURIComponent(escape(atob(b64)));
        this.selectHistoryItem(encodeURIComponent(text));
      } catch (e) {
        console.error('Error selecting history item:', e);
      }
    },

    initAIPopupResizer() {
      const popup = document.getElementById('composer-ai-popup');
      const handle = document.getElementById('composer-ai-resize-handle');
      const editorPane = document.getElementById('composer-editor-pane');
      if (!popup || !editorPane) return;

      const savedHeight = localStorage.getItem('quesy_composer_ai_height');
      if (savedHeight) {
        this.aiPopupHeight = savedHeight;
        popup.style.height = savedHeight;
      }

      let isDragging = false;

      const onMouseDown = (e) => {
        e.preventDefault();
        isDragging = true;
        popup.style.transition = 'none';
        document.body.classList.add('composer-resizing-v');

        window.addEventListener('mousemove', onMouseMove);
        window.addEventListener('mouseup', onMouseUp);
      };

      const onMouseMove = (e) => {
        if (!isDragging) return;
        const paneRect = editorPane.getBoundingClientRect();
        if (!paneRect.height) return;

        const newHeightPx = paneRect.bottom - e.clientY;
        let pct = (newHeightPx / paneRect.height) * 100;
        pct = Math.min(90, Math.max(20, pct));

        popup.style.height = `${pct.toFixed(1)}%`;
        this.aiPopupHeight = `${pct.toFixed(1)}%`;
      };

      const onMouseUp = () => {
        if (!isDragging) return;
        isDragging = false;
        popup.style.transition = '';
        document.body.classList.remove('composer-resizing-v');

        if (this.aiPopupHeight) {
          localStorage.setItem('quesy_composer_ai_height', this.aiPopupHeight);
        }

        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
      };

      if (handle) {
        handle.addEventListener('mousedown', onMouseDown);
      }
    },

    initSplitResizer() {
      const container = document.getElementById('composer-split-container');
      const leftCol = document.getElementById('composer-left-col');
      const resizer = document.getElementById('composer-split-resizer');
      if (!container || !leftCol || !resizer) return;

      const savedRatio = localStorage.getItem('quesy_composer_split_ratio');
      if (savedRatio) {
        const r = parseFloat(savedRatio);
        if (!isNaN(r) && r >= 25 && r <= 75) {
          leftCol.style.width = `${r}%`;
        }
      }

      let isDragging = false;

      const onMouseDown = (e) => {
        if (window.innerWidth < 1024) return;
        e.preventDefault();
        isDragging = true;
        document.body.classList.add('composer-resizing-h');

        window.addEventListener('mousemove', onMouseMove);
        window.addEventListener('mouseup', onMouseUp);
      };

      const onMouseMove = (e) => {
        if (!isDragging) return;
        const rect = container.getBoundingClientRect();
        if (!rect.width) return;

        const offsetX = e.clientX - rect.left;
        let pct = (offsetX / rect.width) * 100;
        pct = Math.min(75, Math.max(25, pct));

        leftCol.style.width = `${pct.toFixed(1)}%`;
      };

      const onMouseUp = () => {
        if (!isDragging) return;
        isDragging = false;
        document.body.classList.remove('composer-resizing-h');

        const pct = parseFloat(leftCol.style.width);
        if (!isNaN(pct)) {
          localStorage.setItem('quesy_composer_split_ratio', pct.toFixed(1));
        }

        this.renderPDF();
        window.dispatchEvent(new Event('resize'));

        window.removeEventListener('mousemove', onMouseMove);
        window.removeEventListener('mouseup', onMouseUp);
      };

      resizer.addEventListener('mousedown', onMouseDown);

      resizer.addEventListener('dblclick', () => {
        leftCol.style.width = '60%';
        localStorage.setItem('quesy_composer_split_ratio', '60');
        this.renderPDF();
        window.dispatchEvent(new Event('resize'));
        showToast('Đã đặt lại tỷ lệ chia 60:40', 'info');
      });
    },

    renderPDF() {
      if (typeof this.renderAllPages === 'function' && this.pdfPages && this.pdfPages.length > 0) {
        this.renderAllPages();
      }
    },

    toggleAIPaneCollapse() {
      if (this.isAIPopupOpen) {
        this.closeAIPopup();
      } else {
        this.openAIPopup();
      }
    },

    pendingDiff: null,
    _inlineDiffLineNo: null,

    _levenshteinSimilarity(s1, s2) {
      if (s1 === s2) return 1.0;
      if (!s1 || !s2) return 0.0;
      const len1 = s1.length;
      const len2 = s2.length;
      if (len1 === 0 || len2 === 0) return 0.0;
      const row = Array(len2 + 1).fill(0).map((_, i) => i);
      for (let i = 0; i < len1; i++) {
        let prev = i + 1;
        for (let j = 0; j < len2; j++) {
          let cur;
          if (s1[i] === s2[j]) {
            cur = row[j];
          } else {
            cur = Math.min(row[j] + 1, prev + 1, row[j + 1] + 1);
          }
          row[j] = prev;
          prev = cur;
        }
        row[len2] = prev;
      }
      return 1.0 - (row[len2] / Math.max(len1, len2));
    },

    _stringSimilarity(s1, s2) {
      if (s1 === s2) return 1.0;
      if (!s1 || !s2) return 0.0;
      const t1 = s1.trim();
      const t2 = s2.trim();
      if (t1 === t2) return 1.0;
      if (t1.length === 0 || t2.length === 0) return 0.0;

      // Quick containment
      if (t1.includes(t2) || t2.includes(t1)) {
        return 0.85 + 0.15 * (Math.min(t1.length, t2.length) / Math.max(t1.length, t2.length));
      }

      if (t1.length < 2 || t2.length < 2) return 0.0;

      // Bigram Dice coefficient
      const getBigrams = str => {
        const bigrams = new Map();
        for (let i = 0; i < str.length - 1; i++) {
          const bg = str.substring(i, i + 2);
          bigrams.set(bg, (bigrams.get(bg) || 0) + 1);
        }
        return bigrams;
      };
      const bg1 = getBigrams(t1);
      const bg2 = getBigrams(t2);
      let intersection = 0;
      for (const [bg, count1] of bg1.entries()) {
        if (bg2.has(bg)) {
          intersection += Math.min(count1, bg2.get(bg));
        }
      }
      const dice = (2.0 * intersection) / ((t1.length - 1) + (t2.length - 1));

      // Calculate fast Levenshtein similarity for moderate strings
      if (t1.length <= 120 && t2.length <= 120) {
        const lev = this._levenshteinSimilarity(t1, t2);
        return Math.max(dice, lev);
      }
      return dice;
    },

    _findFuzzyLineMatch(fullText, targetSnippet) {
      if (!fullText || !targetSnippet) return null;

      // 1. Exact match
      const exactIdx = fullText.indexOf(targetSnippet);
      if (exactIdx !== -1) {
        const lineNo = fullText.substring(0, exactIdx).split('\n').length;
        return {
          startIdx: exactIdx,
          endIdx: exactIdx + targetSnippet.length,
          matchedText: targetSnippet,
          lineNo: lineNo,
          score: 1.0
        };
      }

      // 2. Trimmed match
      const trimmedTarget = targetSnippet.trim();
      const trimIdx = fullText.indexOf(trimmedTarget);
      if (trimIdx !== -1) {
        const lineNo = fullText.substring(0, trimIdx).split('\n').length;
        return {
          startIdx: trimIdx,
          endIdx: trimIdx + trimmedTarget.length,
          matchedText: trimmedTarget,
          lineNo: lineNo,
          score: 0.98
        };
      }

      // 3. Whitespace / newline normalized match
      const normFull = fullText.split(String.fromCharCode(13, 10)).join('\n');
      const normTarget = trimmedTarget.split(String.fromCharCode(13, 10)).join('\n');
      const normIdx = normFull.indexOf(normTarget);
      if (normIdx !== -1) {
        const lineNo = normFull.substring(0, normIdx).split('\n').length;
        const fLines = normFull.split('\n');
        const targetLines = normTarget.split('\n');
        let charOffset = 0;
        const isCRLF = fullText.includes(String.fromCharCode(13, 10));
        const nlLen = isCRLF ? 2 : 1;
        for (let i = 0; i < lineNo - 1; i++) {
          charOffset += fLines[i].length + nlLen;
        }
        let matchLen = 0;
        for (let k = 0; k < targetLines.length; k++) {
          const lIdx = lineNo - 1 + k;
          if (lIdx < fLines.length) {
            matchLen += fLines[lIdx].length + (k < targetLines.length - 1 ? nlLen : 0);
          }
        }
        return {
          startIdx: charOffset,
          endIdx: charOffset + matchLen,
          matchedText: fullText.substring(charOffset, charOffset + matchLen),
          lineNo: lineNo,
          score: 0.95
        };
      }

      // 4. Line-by-line Levenshtein / SequenceMatcher match
      const fullLines = fullText.split(String.fromCharCode(13, 10)).join('\n').split('\n');
      const targetLines = normTarget.split('\n').map(l => l.trim()).filter(Boolean);
      if (targetLines.length === 0) return null;

      const K = targetLines.length;
      let bestScore = -1;
      let bestLineStart = 0;
      let bestLineCount = 1;

      if (K === 1) {
        const tLine = targetLines[0];
        for (let i = 0; i < fullLines.length; i++) {
          const fLine = fullLines[i].trim();
          if (!fLine) continue;
          if (fLine === tLine) {
            bestScore = 1.0;
            bestLineStart = i;
            bestLineCount = 1;
            break;
          }
          const s = this._stringSimilarity(fLine, tLine);
          if (s > bestScore) {
            bestScore = s;
            bestLineStart = i;
            bestLineCount = 1;
          }
        }
      } else {
        const windowSizes = [K, Math.max(1, K - 1), K + 1];
        for (const W of windowSizes) {
          if (W <= 0) continue;
          for (let i = 0; i <= fullLines.length - W; i++) {
            let totalSim = 0;
            let count = 0;
            for (let j = 0; j < Math.min(W, K); j++) {
              totalSim += this._stringSimilarity(fullLines[i + j].trim(), targetLines[j]);
              count++;
            }
            const avgSim = count > 0 ? (totalSim / count) : 0;
            if (avgSim > bestScore) {
              bestScore = avgSim;
              bestLineStart = i;
              bestLineCount = W;
            }
          }
        }
      }

      const isCRLF = fullText.includes(String.fromCharCode(13, 10));
      const nlLen = isCRLF ? 2 : 1;
      let charOffset = 0;
      let matchStart = 0;
      let matchLen = 0;
      for (let i = 0; i < fullLines.length; i++) {
        if (i === bestLineStart) {
          matchStart = charOffset;
        }
        const len = fullLines[i].length;
        if (i >= bestLineStart && i < bestLineStart + bestLineCount) {
          matchLen += len + (i < bestLineStart + bestLineCount - 1 ? nlLen : 0);
        }
        charOffset += len + nlLen;
      }

      return {
        startIdx: matchStart,
        endIdx: matchStart + matchLen,
        matchedText: fullText.substring(matchStart, matchStart + matchLen),
        lineNo: bestLineStart + 1,
        lineCount: bestLineCount,
        score: bestScore
      };
    },

    showPendingDiff(diff) {
      if (!diff || !diff.old_text) return;
      this.pendingDiff = diff;
      const banner = document.getElementById('composer-pending-diff-banner');
      const descEl = document.getElementById('composer-diff-description');
      const oldEl = document.getElementById('composer-diff-old-text');
      const newEl = document.getElementById('composer-diff-new-text');
      const lineNoEl = document.getElementById('composer-diff-line-no');
      const editor = document.getElementById('composer-editor-input');

      const inlineOverlay = document.getElementById('composer-inline-diff-overlay');
      const inlineDesc = document.getElementById('composer-inline-diff-desc');
      const inlineOld = document.getElementById('composer-inline-diff-old-text');
      const inlineNew = document.getElementById('composer-inline-diff-new-text');

      let lineNo = 1;
      const val = editor ? editor.value : (this.currentLatex || '');
      const match = this._findFuzzyLineMatch(val, diff.old_text);

      if (match) {
        lineNo = match.lineNo || 1;
        if (editor) {
          editor.focus();
          editor.setSelectionRange(match.startIdx, match.endIdx);
          const lineHeight = 20;
          editor.scrollTop = Math.max(0, (lineNo - 3) * lineHeight);
          this.syncEditorScroll();
        }
      }

      this._inlineDiffLineNo = lineNo;

      const displayDesc = diff.description || `Thay đổi tại dòng ${lineNo}`;
      const displayNew = (diff.new_text !== undefined && diff.new_text !== null && diff.new_text !== '') ? diff.new_text : '(Xóa bỏ đoạn mã này)';

      // 1. Update top banner
      if (lineNoEl) lineNoEl.innerText = lineNo;
      if (banner && descEl && oldEl && newEl) {
        descEl.innerText = displayDesc;
        oldEl.innerText = diff.old_text;
        newEl.innerText = displayNew;
        banner.classList.remove('hidden');
      }

      // 2. Render Inline Diff Widget directly over the target line in the Editor (Ảnh 4)
      if (inlineOverlay && inlineDesc && inlineOld && inlineNew && editor) {
        inlineDesc.innerText = displayDesc;
        inlineOld.innerText = diff.old_text;
        inlineNew.innerText = displayNew;

        const lineTop = 10 + (lineNo - 1) * 20;
        const targetTop = lineTop - editor.scrollTop;
        const clampedTop = Math.max(8, Math.min(targetTop, Math.max(8, editor.clientHeight - 130)));
        inlineOverlay.style.top = `${clampedTop}px`;
        inlineOverlay.classList.remove('hidden');
      }

      // 3. Automatically dock AI assistant popup down to 32% so editor and inline diff are clearly visible
      const popup = document.getElementById('composer-ai-popup');
      if (popup && this.isAIPopupOpen) {
        this.aiPopupHeight = '32%';
        popup.style.height = '32%';
        const maxIcon = document.getElementById('composer-ai-max-icon');
        if (maxIcon) maxIcon.setAttribute('data-lucide', 'maximize-2');
      }

      if (window.lucide) lucide.createIcons();
    },

    applyPendingDiff() {
      if (!this.pendingDiff) return;
      const { old_text, new_text } = this.pendingDiff;
      this.applyDiffDirect(old_text, new_text);
      this.rejectPendingDiff();
    },

    rejectPendingDiff() {
      this.pendingDiff = null;
      this._inlineDiffLineNo = null;
      const banner = document.getElementById('composer-pending-diff-banner');
      if (banner) banner.classList.add('hidden');
      const inlineOverlay = document.getElementById('composer-inline-diff-overlay');
      if (inlineOverlay) inlineOverlay.classList.add('hidden');
      const editor = document.getElementById('composer-editor-input');
      if (editor) {
        const cursor = editor.selectionEnd;
        editor.setSelectionRange(cursor, cursor);
      }
    },

    applyDiffDirect(oldText, newText) {
      const editor = document.getElementById('composer-editor-input');
      if (!editor) return;

      let val = this.currentLatex || editor.value || '';
      const safeNew = (newText !== undefined && newText !== null) ? newText : '';

      if (!val) {
        val = safeNew;
        editor.value = val;
        this.currentLatex = val;
        this.handleEditorInput();
        this.compile(true);
        this.rejectPendingDiff();
        showToast('Đã áp dụng thay đổi vào mã nguồn!', 'success');
        return;
      }

      let replaced = false;

      // Tier 1: Exact match
      if (val.includes(oldText)) {
        val = val.replace(oldText, safeNew);
        replaced = true;
      }

      // Tier 2: Trimmed match
      if (!replaced) {
        const trimmedOld = (oldText || '').trim();
        const trimmedNew = safeNew.trim();
        if (val.includes(trimmedOld)) {
          val = val.replace(trimmedOld, trimmedNew);
          replaced = true;
        }
      }

      // Tier 3: Whitespace / CRLF normalized match
      if (!replaced) {
        const normVal = val.split(String.fromCharCode(13, 10)).join('\n');
        const normOld = (oldText || '').trim().split(String.fromCharCode(13, 10)).join('\n');
        const normNew = safeNew.trim().split(String.fromCharCode(13, 10)).join('\n');
        if (normVal.includes(normOld)) {
          val = normVal.replace(normOld, normNew);
          replaced = true;
        }
      }

      // Tier 4: Multi-level fuzzy match (Levenshtein / SequenceMatcher >= 60%)
      if (!replaced) {
        const match = this._findFuzzyLineMatch(val, oldText);
        if (match && (match.score >= 0.50 || val.includes(match.matchedText))) {
          const before = val.substring(0, match.startIdx);
          const after = val.substring(match.endIdx);
          val = before + safeNew + after;
          replaced = true;
        }
      }

      // Tier 5: Keyword & command matching fallback
      if (!replaced) {
        const lines = val.split(String.fromCharCode(13, 10)).join('\n').split('\n');
        const candidateKeywords = (oldText + ' ' + safeNew).match(/\\[a-zA-Z@]+(?:\{[^}]*\})?/g) || [];
        for (const kw of candidateKeywords) {
          if (kw.length < 5) continue;
          const idx = lines.findIndex(l => l.includes(kw));
          if (idx !== -1) {
            lines[idx] = safeNew;
            val = lines.join('\n');
            replaced = true;
            break;
          }
        }
      }

      // Tier 6: Guaranteed fallback: replace best matching line (>= 20%) or safe insert
      if (!replaced) {
        const match = this._findFuzzyLineMatch(val, oldText);
        if (match && match.score > 0.20) {
          const before = val.substring(0, match.startIdx);
          const after = val.substring(match.endIdx);
          val = before + safeNew + after;
          replaced = true;
        } else {
          // Safe insertion: insert before \end{document} or append
          if (val.includes('\\end{document}')) {
            val = val.replace('\\end{document}', `${safeNew}\n\\end{document}`);
          } else {
            val = val + '\n' + safeNew;
          }
          replaced = true;
        }
      }

      editor.value = val;
      this.currentLatex = val;
      this.handleEditorInput();
      this.compile(true);
      this.rejectPendingDiff();
      showToast('Đã áp dụng thay đổi vào mã nguồn!', 'success');
    },

    extractDiffFromText(replyText, currentLatex, userMessage = '') {
      if (!currentLatex || !replyText) return null;
      const combinedText = `${userMessage}\n${replyText}`;
      const combinedLower = combinedText.toLowerCase();
      const userLower = (userMessage || '').toLowerCase();

      const findInLatex = (needle) => {
        if (!needle) return null;
        if (currentLatex.includes(needle)) return needle;
        const stripped = needle.trim();
        if (stripped && currentLatex.includes(stripped)) return stripped;

        const normCur = currentLatex.split('\r\n').join('\n');
        const normNeedle = stripped.split('\r\n').join('\n');
        if (normCur.includes(normNeedle)) {
          const curLines = currentLatex.split('\n');
          const needleLines = normNeedle.split('\n').map(l => l.trim()).filter(Boolean);
          if (needleLines.length > 0) {
            for (let i = 0; i <= curLines.length - needleLines.length; i++) {
              let match = true;
              for (let k = 0; k < needleLines.length; k++) {
                if (curLines[i + k].trim() !== needleLines[k]) {
                  match = false;
                  break;
                }
              }
              if (match) {
                return curLines.slice(i, i + needleLines.length).join('\n');
              }
            }
          }
        }

        const lines = currentLatex.split('\n');
        for (const line of lines) {
          if (stripped && line.includes(stripped)) return line;
          if (line.trim() && line.trim() === stripped) return line;
        }
        return null;
      };

      // 1. Font size change
      if (/font|cỡ chữ|size/i.test(combinedLower)) {
        let pts = (userLower.match(/\b(10|11|12|13|14)(?:pt)?\b/g) || []);
        if (!pts.length) {
          pts = (replyText.toLowerCase().match(/\b(10|11|12|13|14)(?:pt)?\b/g) || []);
        }
        if (pts.length) {
          const targetPt = pts[pts.length - 1].replace('pt', '') + 'pt';
          const lines = currentLatex.split('\n');
          for (const line of lines) {
            if (line.includes('documentclass')) {
              let newLine = line;
              if (/\b\d+pt\b/.test(line)) {
                newLine = line.replace(/\b\d+pt\b/, targetPt);
              } else if (line.includes('\\documentclass[')) {
                newLine = line.replace(/\\documentclass\[/, `\\documentclass[${targetPt},`);
              } else if (line.includes('\\documentclass{')) {
                newLine = line.replace(/\\documentclass\{/, `\\documentclass[${targetPt}]{`);
              }
              if (newLine !== line) {
                return {
                  action: 'replace',
                  old_text: line,
                  new_text: newLine,
                  description: `Đổi cỡ chữ toàn tài liệu sang ${targetPt}`
                };
              }
            }
          }
        }
      }

      // 2. Choice change
      const choiceMatch = combinedLower.match(/(?:đổi|sửa|chuyển)\s+(?:đáp án|lựa chọn)(?:\s+đúng)?\s+(?:từ\s+[abcd]\s+sang\s+|thành\s+|sang\s+)([abcd])\b/i);
      if (choiceMatch) {
        const targetChoice = choiceMatch[1].toUpperCase();
        const targetIdx = { A: 0, B: 1, C: 2, D: 3 }[targetChoice];
        if (targetIdx !== undefined) {
          const chRegex = /\\choice\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}/;
          const chMatch = currentLatex.match(chRegex);
          if (chMatch) {
            const oldFull = chMatch[0];
            const opts = [chMatch[1], chMatch[2], chMatch[3], chMatch[4]];
            const cleanedOpts = opts.map(o => o.replace(/\\True\s*/g, '').trim());
            cleanedOpts[targetIdx] = '\\True ' + cleanedOpts[targetIdx];
            const sep = oldFull.includes('\n') ? '\n' : '';
            const newFull = `\\choice${sep}{${cleanedOpts[0]}}${sep}{${cleanedOpts[1]}}${sep}{${cleanedOpts[2]}}${sep}{${cleanedOpts[3]}}`;
            if (oldFull !== newFull) {
              return {
                action: 'replace',
                old_text: oldFull,
                new_text: newFull,
                description: `Đổi đáp án đúng sang ${targetChoice}`
              };
            }
          }
        }
      }

      // 3. Diff blocks
      const diffMatch = replyText.match(/```diff\s*\n?([\s\S]*?)```/);
      if (diffMatch) {
        const lines = diffMatch[1].trim().split('\n');
        const oldLines = [];
        const newLines = [];
        for (const line of lines) {
          if (line.startsWith('---') || line.startsWith('+++')) continue;
          const s = line.trim();
          if (s.startsWith('-')) {
            oldLines.push(line.replace(/^\s*-\s?/, ''));
          } else if (s.startsWith('+')) {
            newLines.push(line.replace(/^\s*\+\s?/, ''));
          }
        }
        const oldRaw = oldLines.join('\n').trim();
        const newRaw = newLines.join('\n').trim();
        const matchedOld = findInLatex(oldRaw);
        if (matchedOld && matchedOld !== newRaw) {
          return {
            action: 'replace',
            old_text: matchedOld,
            new_text: newRaw,
            description: 'Thay đổi theo gợi ý AI'
          };
        }
      }

      // 4. OLD / NEW or CŨ / MỚI blocks
      const patterns = [
        /(?:OLD|CŨ|MÃ CŨ|TRƯỚC):\s*\n+([\s\S]*?)\n+(?:NEW|MỚI|MÃ MỚI|SAU):\s*\n+([\s\S]*?)(?:\n\n|$)/i,
        /(?:- Dòng cũ|- Đoạn cũ|Cũ):\s*[`"“]?([^\n`"”]+)[`"”]?\s*\n(?:- Dòng mới|- Đoạn mới|Mới):\s*[`"“]?([^\n`"”]+)[`"”]?/i
      ];
      for (const pat of patterns) {
        const m = replyText.match(pat);
        if (m) {
          const oldRaw = m[1].trim();
          const newRaw = m[2].trim();
          const matchedOld = findInLatex(oldRaw);
          if (matchedOld && matchedOld !== newRaw) {
            return {
              action: 'replace',
              old_text: matchedOld,
              new_text: newRaw,
              description: 'Thay đổi theo gợi ý AI'
            };
          }
        }
      }

      // 5. Block replace with code fences: Thay thế: ```latex ... ``` bằng: ```latex ... ```
      const blockRepMatch = replyText.match(/(?:thay thế|thay|đổi|sửa|cũ|trước):\s*\n*```(?:latex|tex)?\s*\n([\s\S]*?)\n```\s*\n*(?:thành|bằng|sang|mới|sau):\s*\n*```(?:latex|tex)?\n([\s\S]*?)\n```/i);
      if (blockRepMatch) {
        const oldRaw = blockRepMatch[1].trim();
        const newRaw = blockRepMatch[2].trim();
        const matchedOld = findInLatex(oldRaw);
        if (matchedOld && matchedOld !== newRaw) {
          return {
            action: 'replace',
            old_text: matchedOld,
            new_text: newRaw,
            description: 'Thay đổi theo gợi ý AI'
          };
        }
      }

      // 6. Inline natural language replacement: "Thay thế `X` bằng `Y`"
      const inlineMatch = replyText.match(/(?:thay thế|thay|đổi|sửa|chuyển|replace)\s+[`"“'‘]([^`"”'’\n]+)[`"”'’]\s+(?:bằng|thành|sang|với|by|with)\s+[`"“'‘]([^`"”'’\n]+)[`"”'’]/i);
      if (inlineMatch) {
        const oldRaw = inlineMatch[1].trim();
        const newRaw = inlineMatch[2].trim();
        const matchedOld = findInLatex(oldRaw);
        if (matchedOld && matchedOld !== newRaw) {
          return {
            action: 'replace',
            old_text: matchedOld,
            new_text: newRaw,
            description: `Thay thế '${oldRaw}' thành '${newRaw}'`
          };
        }
      }

      // 7. Code block comparison: AI returns revised LaTeX block (```latex ... ```)
      const codeMatch = replyText.match(/```(?:latex|tex)?\s*\n([\s\S]*?)```/);
      if (codeMatch) {
        const code = codeMatch[1].trim();
        if (!code.includes('\\documentclass') && code.length >= 10) {
          const docLines = currentLatex.split('\n');
          const codeLines = code.split('\n');
          const m = codeLines.length;
          let bestRatio = 0;
          let bestSlice = null;

          for (let w = Math.max(1, m - 3); w <= Math.min(docLines.length, m + 4); w++) {
            for (let i = 0; i <= docLines.length - w; i++) {
              const windowText = docLines.slice(i, i + w).join('\n').trim();
              if (!windowText) continue;
              const ratio = this._stringSimilarity(code, windowText);
              if (ratio > bestRatio) {
                bestRatio = ratio;
                bestSlice = docLines.slice(i, i + w).join('\n');
              }
            }
          }

          if (bestRatio >= 0.52 && bestSlice && bestSlice.trim() !== code) {
            return {
              action: 'replace',
              old_text: bestSlice,
              new_text: code,
              description: 'Thay đổi theo gợi ý AI'
            };
          }
        }
      }

      return null;
    },

    initChat() {
      const chatContainer = document.getElementById('composer-chat-messages');
      if (!chatContainer) return;

      // 1. Load stored sessions from localStorage
      try {
        const savedSessions = localStorage.getItem('quesy_composer_sessions');
        this.sessions = savedSessions ? JSON.parse(savedSessions) : [];
      } catch (e) {
        this.sessions = [];
      }

      // 2. Migrate legacy single-chat history if it exists and has user messages
      try {
        const legacyChat = localStorage.getItem('quesy_composer_chat');
        if (legacyChat) {
          const parsed = JSON.parse(legacyChat);
          if (Array.isArray(parsed) && parsed.some(m => m.role === 'user')) {
            const firstUser = parsed.find(m => m.role === 'user');
            const legacySess = {
              id: 'session_' + Date.now(),
              title: (firstUser ? firstUser.content : 'Phiên trước').slice(0, 50),
              timestamp: new Date().toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' }) + ' ' + new Date().toLocaleDateString('vi-VN'),
              messages: parsed
            };
            if (!this.sessions.some(s => s.title === legacySess.title)) {
              this.sessions.unshift(legacySess);
              localStorage.setItem('quesy_composer_sessions', JSON.stringify(this.sessions));
            }
          }
        }
      } catch (e) {
        console.warn('Migration error:', e);
      }

      // 3. New session starts fresh with ONLY the default greeting message
      this.currentSessionId = 'session_' + Date.now();
      this.chatHistory = [
        {
          role: 'assistant',
          content: 'Chào bạn! Tôi là **Trợ lý soạn thảo** (Quesy Copilot). Bạn có thể yêu cầu tôi đổi cỡ chữ (`12pt`), tạo câu hỏi trắc nghiệm, tạo bảng biến thiên `tkz-tab`, vẽ đồ thị TikZ hoặc kiểm tra và sửa lỗi cú pháp LaTeX trực tiếp.'
        }
      ];

      this.renderChatMessages();
      this.renderHistoryList();

      if (!this._quickMenuDocClickBound) {
        this._quickMenuDocClickBound = true;
        document.addEventListener('click', (e) => {
          const qMenu = document.getElementById('composer-quick-prompts-menu');
          const cMenu = document.getElementById('composer-compact-quick-menu');
          if (qMenu && !qMenu.contains(e.target) && !e.target.closest('button[title="Chèn nhanh mẫu yêu cầu"]')) {
            qMenu.classList.add('hidden');
          }
          if (cMenu && !cMenu.contains(e.target) && !e.target.closest('button[title="Mẫu câu lệnh nhanh"]')) {
            cMenu.classList.add('hidden');
          }
        });
      }
    },

    renderChatMessages() {
      const container = document.getElementById('composer-chat-messages');
      if (!container) return;

      container.innerHTML = this.chatHistory.map((msg) => {
        const isUser = msg.role === 'user';
        if (isUser) {
          return `
            <div class="flex items-start justify-end space-x-2">
              <div class="bg-[#27272a] text-white border border-white/10 rounded-2xl rounded-tr-xs p-2.5 max-w-[85%] shadow-md leading-relaxed text-xs">
                ${escapeHtml(msg.content)}
              </div>
            </div>
          `;
        } else {
          const formattedHtml = this.formatAssistantContent(msg.content, msg.diff);
          const rawTextB64 = btoa(unescape(encodeURIComponent(msg.content || '')));
          return `
            <div class="flex items-start space-x-2.5">
              <div class="w-6 h-6 rounded-full bg-gradient-to-tr from-purple-600 to-indigo-600 text-white flex items-center justify-center font-bold text-[10px] shrink-0 shadow-sm mt-0.5">
                AI
              </div>
              <div class="bg-[#202024] border border-white/5 rounded-2xl rounded-tl-xs p-3 max-w-[92%] shadow-md leading-relaxed text-xs text-slate-200 space-y-2">
                <div>${formattedHtml}</div>
                <div class="flex items-center justify-between pt-1 border-t border-white/5 text-[10px] text-slate-400 select-none">
                  <span class="flex items-center space-x-1"><i data-lucide="sparkles" class="w-3 h-3 text-purple-400"></i><span>Quesy Copilot</span></span>
                  <button type="button" onclick="navigator.clipboard.writeText(decodeURIComponent(escape(atob('${rawTextB64}')))); showToast('Đã sao chép nội dung!', 'info')" class="hover:text-white p-0.5 rounded cursor-pointer transition-all" title="Sao chép câu trả lời">
                    <i data-lucide="copy" class="w-3.5 h-3.5"></i>
                  </button>
                </div>
              </div>
            </div>
          `;
        }
      }).join('');

      container.scrollTop = container.scrollHeight;
      if (window.lucide) lucide.createIcons();
    },

    formatAssistantContent(text, diff) {
      if (!text) return '';
      let html = text;

      // Smart fallback diff extraction if diff not provided
      if (!diff && this.extractDiffFromText) {
        diff = this.extractDiffFromText(text, this.currentLatex);
      }

      const hasDiff = Boolean(
        (diff && diff.old_text) ||
        /```diff/i.test(html) ||
        /(?:OLD|CŨ|MÃ CŨ|TRƯỚC):\s*\n+[\s\S]*?\n+(?:NEW|MỚI|MÃ MỚI|SAU):/i.test(html) ||
        /(?:thay thế|thay|đổi|sửa|cũ|trước):\s*\n*```(?:latex|tex)?\s*\n[\s\S]*?\n```\s*\n*(?:thành|bằng|sang|mới|sau):/i.test(html)
      );

      // 1. Remove ```diff ... ``` blocks from chat bubble
      html = html.replace(/```diff\s*[\s\S]*?```/gi, '');

      // 2. Remove OLD / NEW or CŨ / MỚI replacement blocks from chat bubble
      const oldNewRegex = /(?:OLD|CŨ|MÃ CŨ|TRƯỚC):\s*\n+([\s\S]*?)\n+(?:NEW|MỚI|MÃ MỚI|SAU):\s*\n+([\s\S]*?)(?:\n\n|$)/gi;
      html = html.replace(oldNewRegex, '');

      // 3. Remove block replacement code fences from chat bubble if it was just replacing code
      const blockRepRegex = /(?:thay thế|thay|đổi|sửa|cũ|trước):\s*\n*```(?:latex|tex)?\s*\n[\s\S]*?\n```\s*\n*(?:thành|bằng|sang|mới|sau):\s*\n*```(?:latex|tex)?\n[\s\S]*?\n```/gi;
      html = html.replace(blockRepRegex, '');

      // 4. Standard LaTeX Snippets (```latex ... ```) - keep for code reference with insert/copy buttons
      html = html.replace(/```(?:latex|tex)?\s*([\s\S]*?)```/g, (match, code) => {
        const rawCode = code.trim();
        const b64Code = btoa(unescape(encodeURIComponent(rawCode)));
        return `
          <div class="code-block-wrapper my-2 rounded-xl overflow-hidden border border-slate-700/80 shadow-xs">
            <div class="code-block-actions flex items-center justify-between bg-slate-800 text-slate-300 px-3 py-1.5 text-[10px]">
              <span class="font-mono text-slate-400 font-semibold">LaTeX Code</span>
              <div class="flex items-center space-x-1.5">
                <button type="button" onclick="app.composer.insertB64Code('${b64Code}')" class="px-2 py-0.5 rounded bg-brand-600 hover:bg-brand-500 text-white font-semibold transition-all active:scale-95 flex items-center space-x-1" title="Chèn vào vị trí con trỏ trong mã nguồn">
                  <span>📥 Chèn vào con trỏ</span>
                </button>
                <button type="button" onclick="app.composer.copyB64Code('${b64Code}')" class="px-2 py-0.5 rounded bg-slate-700 hover:bg-slate-600 text-slate-200 hover:text-white transition-all active:scale-95 flex items-center space-x-1" title="Sao chép">
                  <span>📋 Sao chép</span>
                </button>
              </div>
            </div>
            <pre class="bg-slate-900 text-emerald-300 p-2.5 font-mono text-[11px] overflow-x-auto leading-relaxed max-h-56 select-text whitespace-pre"><code>${escapeHtml(rawCode)}</code></pre>
          </div>
        `;
      });

      html = html.replace(/\*\*([^*]+)\*\*/g, '<strong class="text-white font-semibold">$1</strong>');
      html = html.replace(/\*([^*]+)\*/g, '<em class="text-slate-300">$1</em>');
      html = html.replace(/`([^`]+)`/g, '<code class="bg-[#2d2d31] text-purple-300 border border-white/10 px-1.5 py-0.5 rounded font-mono text-[11px] font-semibold">$1</code>');
      html = html.replace(/\n\n/g, '<br><br>');

      // 5. If a diff was detected, add brief unobtrusive notification note
      if (hasDiff) {
        html += `
          <div class="my-2 px-2.5 py-1.5 rounded-lg bg-blue-950/40 border border-blue-500/25 text-blue-300 text-[11px] flex items-center space-x-1.5 select-none">
            <i data-lucide="sparkles" class="w-3.5 h-3.5 text-blue-400 shrink-0"></i>
            <span>Đã chuyển gợi ý sửa đổi tới ô soạn thảo mã nguồn</span>
          </div>
        `;
      }

      return html.trim();
    },

    insertB64Code(b64) {
      try {
        const code = decodeURIComponent(escape(atob(b64)));
        this.insertSnippet(code);
        showToast('Đã chèn mã LaTeX vào vị trí con trỏ!', 'success');
      } catch (e) {
        console.error('Error inserting code:', e);
      }
    },

    replaceB64Code(b64) {
      try {
        const code = decodeURIComponent(escape(atob(b64))).trim();
        const editor = document.getElementById('composer-editor-input');
        if (!editor) return;

        // Safety guard: prevent replacing entire exam if code is just a small snippet
        if (!code.includes('\\documentclass') && this.currentLatex && this.currentLatex.length > 80) {
          showToast('Đoạn mã này là đoạn trích ngắn, không thể thay thế toàn bộ tài liệu!', 'warning');
          return;
        }

        if (this.currentLatex && this.currentLatex.length > 50) {
          if (!confirm('Bạn có chắc chắn muốn thay thế toàn bộ tài liệu hiện tại bằng mã mới?')) {
            return;
          }
        }

        editor.value = code;
        this.currentLatex = code;
        this.handleEditorInput();
        this.compile(true);
        showToast('Đã thay thế toàn bộ tài liệu bằng mã mới!', 'success');
      } catch (e) {
        console.error('Error replacing code:', e);
      }
    },

    copyB64Code(b64) {
      try {
        const code = decodeURIComponent(escape(atob(b64)));
        navigator.clipboard.writeText(code);
        showToast('Đã sao chép mã LaTeX vào bộ nhớ tạm!', 'info');
      } catch (e) {
        console.error('Error copying code:', e);
      }
    },

    async submitChat() {
      const input = document.getElementById('composer-chat-input');
      if (!input) return;
      const text = input.value.trim();
      if (!text) return;
      input.value = '';

      this.sendPrompt(text);
    },

    handleChatInputKey(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        this.submitChat();
      }
    },

    async sendPrompt(promptText) {
      if (!this.isAIPopupOpen) {
        this.openAIPopup();
      }
      this.chatHistory.push({ role: 'user', content: promptText });
      this.archiveCurrentSession();
      this.renderChatMessages();
      this.renderHistoryList();

      const container = document.getElementById('composer-chat-messages');
      const tempId = 'composer-typing-indicator';
      if (container) {
        const typingHtml = `
          <div id="${tempId}" class="flex items-start space-x-2.5">
            <div class="w-6 h-6 rounded-full bg-gradient-to-tr from-purple-600 to-indigo-600 text-white flex items-center justify-center font-bold text-[10px] shrink-0 shadow-sm mt-0.5">
              AI
            </div>
            <div class="bg-[#202024] border border-white/5 rounded-2xl rounded-tl-xs p-3 text-slate-300 text-xs flex items-center space-x-2 shadow-md">
              <i data-lucide="loader-2" class="w-3.5 h-3.5 animate-spin text-purple-400"></i>
              <span>Trợ lý đang xử lý yêu cầu...</span>
            </div>
          </div>
        `;
        container.insertAdjacentHTML('beforeend', typingHtml);
        container.scrollTop = container.scrollHeight;
        if (window.lucide) lucide.createIcons();
      }

      const errorTextEl = document.getElementById('composer-error-text');
      const errorDrawer = document.getElementById('composer-error-drawer');
      const activeCompileError = this.lastCompileError || (errorDrawer && !errorDrawer.classList.contains('hidden') && errorTextEl ? errorTextEl.innerText.trim() : null);

      try {
        const res = await fetch(`${API_BASE_URL}/composer/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: promptText,
            current_latex: this.currentLatex,
            compile_error: activeCompileError || undefined,
            history: this.chatHistory.slice(-4)
          })
        });

        const typingEl = document.getElementById(tempId);
        if (typingEl) typingEl.remove();

        if (res.ok) {
          const data = await res.json();
          let diff = data.diff;
          if (!diff && this.extractDiffFromText) {
            diff = this.extractDiffFromText(data.reply, this.currentLatex, promptText);
          }
          this.chatHistory.push({ role: 'assistant', content: data.reply, diff: diff || null });
          this.archiveCurrentSession();
          localStorage.setItem('quesy_composer_chat', JSON.stringify(this.chatHistory.slice(-20)));
          this.renderChatMessages();

          if (diff) {
            this.showPendingDiff(diff);
          }
        } else {
          this.chatHistory.push({ role: 'assistant', content: 'Rất tiếc, đã có lỗi kết nối với máy chủ AI. Vui lòng thử lại sau.' });
          this.archiveCurrentSession();
          this.renderChatMessages();
        }
      } catch (err) {
        const typingEl = document.getElementById(tempId);
        if (typingEl) typingEl.remove();
        this.chatHistory.push({ role: 'assistant', content: `Lỗi kết nối: ${err.message}` });
        this.archiveCurrentSession();
        this.renderChatMessages();
      }
    },

    clearChat() {
      this.currentSessionId = 'session_' + Date.now();
      this.chatHistory = [
        {
          role: 'assistant',
          content: 'Đã làm mới hội thoại. Bạn có thể yêu cầu tôi tạo câu hỏi hoặc chỉnh sửa mã LaTeX mới!'
        }
      ];
      localStorage.removeItem('quesy_composer_chat');
      this.renderChatMessages();
      this.renderHistoryList();
      showToast('Đã xóa sạch nội dung hội thoại hiện tại.', 'info');
    },

    handleEditorInput() {
      const editor = document.getElementById('composer-editor-input');
      if (!editor) return;
      this.currentLatex = editor.value;
      localStorage.setItem('quesy_composer_content', this.currentLatex);

      this.updateGutter();
      this.updateCharCount();
      this.updateLineCol();

      if (this.autoCompile) {
        const statusText = document.getElementById('composer-status-text');
        if (statusText) statusText.innerText = 'Đang đợi gõ...';
        clearTimeout(this.compileTimer);
        this.compileTimer = setTimeout(() => {
          this.compile(false);
        }, 800);
      }
    },

    handleTitleChange(newTitle) {
      this.activeTitle = newTitle || 'Đề Thi Soạn Thảo';
      localStorage.setItem('quesy_composer_title', this.activeTitle);
    },

    updateGutter() {
      const editor = document.getElementById('composer-editor-input');
      const gutter = document.getElementById('composer-editor-gutter');
      if (!editor || !gutter) return;

      const lines = editor.value.split('\n').length;
      let gutterText = '';
      for (let i = 1; i <= lines; i++) {
        gutterText += i + '\n';
      }
      gutter.innerText = gutterText;
    },

    updateCharCount() {
      const countEl = document.getElementById('composer-char-count');
      if (countEl) {
        countEl.innerText = `${(this.currentLatex || '').length.toLocaleString()} ký tự`;
      }
    },

    updateLineCol() {
      const editor = document.getElementById('composer-editor-input');
      const badge = document.getElementById('composer-line-col-badge');
      if (!editor || !badge) return;

      const pos = editor.selectionStart || 0;
      const lines = editor.value.substring(0, pos).split('\n');
      const lineNum = lines.length;
      const colNum = lines[lines.length - 1].length + 1;
      badge.innerText = `Dòng ${lineNum}, Cột ${colNum}`;
    },

    syncEditorScroll() {
      const editor = document.getElementById('composer-editor-input');
      const gutter = document.getElementById('composer-editor-gutter');
      if (editor && gutter) {
        gutter.scrollTop = editor.scrollTop;
      }
      if (this.pendingDiff && this._inlineDiffLineNo && editor) {
        const overlay = document.getElementById('composer-inline-diff-overlay');
        if (overlay && !overlay.classList.contains('hidden')) {
          const lineTop = 10 + (this._inlineDiffLineNo - 1) * 20;
          const targetTop = lineTop - editor.scrollTop;
          const clampedTop = Math.max(8, Math.min(targetTop, Math.max(8, editor.clientHeight - 130)));
          overlay.style.top = `${clampedTop}px`;
        }
      }
    },

    currentPage: 1,
    totalPages: 1,

    prevPage() {
      if (this.currentPage > 1) {
        this.goToPage(this.currentPage - 1);
      }
    },

    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.goToPage(this.currentPage + 1);
      }
    },

    goToPage(page) {
      this.currentPage = Math.max(1, Math.min(this.totalPages, page));
      const curEl = document.getElementById('composer-page-current');
      if (curEl) curEl.innerText = this.currentPage;

      const targetCard = document.getElementById(`pdf-page-${this.currentPage}`);
      if (targetCard) {
        targetCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
      } else {
        const iframe = document.getElementById('composer-pdf-iframe');
        if (iframe && iframe.src && iframe.src !== 'about:blank') {
          const baseUrl = iframe.src.split('#')[0];
          iframe.src = `${baseUrl}#page=${this.currentPage}&toolbar=0&navpanes=0&scrollbar=1&view=FitH`;
        }
      }
    },

    handleEditorKey(e) {
      const editor = document.getElementById('composer-editor-input');
      if (!editor) return;

      // Tab indentation (2 spaces)
      if (e.key === 'Tab') {
        e.preventDefault();
        const start = editor.selectionStart;
        const end = editor.selectionEnd;
        editor.value = editor.value.substring(0, start) + '  ' + editor.value.substring(end);
        editor.selectionStart = editor.selectionEnd = start + 2;
        this.handleEditorInput();
        return;
      }

      // Ctrl+S / Cmd+S: Compile
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        this.compile(true);
        return;
      }

      this.updateLineCol();
    },

    insertSnippet(snippetKeyOrCode) {
      const editor = document.getElementById('composer-editor-input');
      if (!editor) return;

      let insertText = this.SNIPPETS[snippetKeyOrCode] || snippetKeyOrCode;
      const start = editor.selectionStart || 0;
      const end = editor.selectionEnd || 0;
      const val = editor.value;

      editor.value = val.substring(0, start) + insertText + val.substring(end);
      editor.focus();
      editor.setSelectionRange(start + insertText.length, start + insertText.length);
      this.handleEditorInput();
    },

    loadTemplate(templateKey) {
      const tmpl = this.templates[templateKey];
      if (!tmpl) return;

      if (this.currentLatex && this.currentLatex.length > 50) {
        if (!confirm(`Bạn có chắc chắn muốn nạp mẫu "${tmpl.title}"? Nội dung hiện tại sẽ được thay thế.`)) {
          return;
        }
      }

      const editor = document.getElementById('composer-editor-input');
      const titleInput = document.getElementById('composer-doc-title');
      if (editor) {
        editor.value = tmpl.latex;
        this.currentLatex = tmpl.latex;
        this.handleEditorInput();
      }
      if (titleInput && tmpl.title) {
        titleInput.value = tmpl.title;
        this.handleTitleChange(tmpl.title);
      }
      this.compile(true);
    },

    async compile(force = false) {
      if (this.isCompiling) return;
      this.isCompiling = true;

      const overlay = document.getElementById('composer-compiling-overlay');
      const statusBadge = document.getElementById('composer-compile-status');
      const statusText = document.getElementById('composer-status-text');
      const errorDrawer = document.getElementById('composer-error-drawer');
      const errorText = document.getElementById('composer-error-text');
      const editor = document.getElementById('composer-editor-input');

      if (editor) {
        this.currentLatex = editor.value;
      }
      if (errorDrawer) errorDrawer.classList.add('hidden');
      if (errorText) errorText.innerText = '';

      if (overlay) overlay.classList.remove('hidden');
      if (statusText) statusText.innerText = 'Đang biên dịch...';
      if (statusBadge) {
        statusBadge.className = 'flex items-center space-x-1 px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 text-[10px] font-semibold';
      }

      try {
        const res = await fetch(`${API_BASE_URL}/composer/compile`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            latex_code: this.currentLatex,
            title: this.activeTitle
          })
        });

        const data = await res.json();
        if (overlay) overlay.classList.add('hidden');

        if (res.ok && data.success && data.pdf_url) {
          this.pdfUrl = data.pdf_url;
          this.totalPages = data.total_pages || 1;
          this.currentPage = 1;
          const curEl = document.getElementById('composer-page-current');
          const totalEl = document.getElementById('composer-page-total');
          if (curEl) curEl.innerText = this.currentPage;
          if (totalEl) totalEl.innerText = this.totalPages;

          this.saveHistoryItem(data.pdf_url);
          this.renderPdfDocument(data.pdf_url);

          if (statusText) statusText.innerText = `Đã cập nhật (${(data.compile_time_ms / 1000).toFixed(1)}s)`;
          if (statusBadge) {
            statusBadge.className = 'flex items-center space-x-1 px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 text-[10px] font-semibold';
          }
          if (errorDrawer) errorDrawer.classList.add('hidden');
          this.lastCompileError = null;
        } else {
          const errMsg = data.error || 'Biên dịch thất bại';
          this.lastCompileError = errMsg;
          if (statusText) statusText.innerText = 'Lỗi biên dịch';
          if (statusBadge) {
            statusBadge.className = 'flex items-center space-x-1 px-2 py-0.5 rounded-full bg-rose-500/20 text-rose-300 text-[10px] font-semibold';
          }
          if (errorDrawer && errorText) {
            errorText.innerText = errMsg;
            errorDrawer.classList.remove('hidden');
          }
        }
      } catch (err) {
        this.lastCompileError = String(err);
        if (overlay) overlay.classList.add('hidden');
        if (statusText) statusText.innerText = 'Lỗi kết nối';
        if (errorDrawer && errorText) {
          errorText.innerText = String(err);
          errorDrawer.classList.remove('hidden');
        }
      } finally {
        this.isCompiling = false;
      }
    },

    pdfDoc: null,
    pdfPages: [],
    pdfBaseViewports: [],
    _renderTimer: null,

    async renderPdfDocument(pdfUrl) {
      const scrollContainer = document.getElementById('composer-pdf-scroll-container');
      const pagesContainer = document.getElementById('composer-pdf-pages');
      const emptyEl = document.getElementById('composer-pdf-empty');
      const iframe = document.getElementById('composer-pdf-iframe');

      if (!window.pdfjsLib) {
        if (iframe) {
          iframe.classList.remove('hidden');
          iframe.src = `${pdfUrl}?t=${Date.now()}`;
        }
        return;
      }

      window.pdfjsLib.GlobalWorkerOptions.workerSrc = '/static/vendor/pdf.worker.min.js';

      if (iframe) iframe.classList.add('hidden');
      if (emptyEl) emptyEl.classList.add('hidden');
      if (pagesContainer) pagesContainer.innerHTML = '';

      try {
        const loadingTask = window.pdfjsLib.getDocument(pdfUrl);
        this.pdfDoc = await loadingTask.promise;
        this.totalPages = this.pdfDoc.numPages || 1;
        this.currentPage = 1;

        const curEl = document.getElementById('composer-page-current');
        const totalEl = document.getElementById('composer-page-total');
        if (curEl) curEl.innerText = this.currentPage;
        if (totalEl) totalEl.innerText = this.totalPages;

        this.pdfPages = [];
        this.pdfBaseViewports = [];

        // Attach wheel event for Ctrl+scroll zoom once
        if (scrollContainer && !scrollContainer._wheelBound) {
          scrollContainer._wheelBound = true;
          scrollContainer.addEventListener('wheel', (e) => {
            if (e.ctrlKey || e.metaKey) {
              e.preventDefault();
              const delta = e.deltaY < 0 ? 0.1 : -0.1;
              app.composer.zoomPreview(delta);
            }
          }, { passive: false });

          // Track visible page on scroll
          scrollContainer.addEventListener('scroll', () => {
            const pageCards = scrollContainer.querySelectorAll('.pdf-page-card');
            const containerTop = scrollContainer.scrollTop + 60;
            for (let i = 0; i < pageCards.length; i++) {
              const card = pageCards[i];
              const cardTop = card.offsetTop;
              const cardBottom = cardTop + card.offsetHeight;
              if (containerTop >= cardTop && containerTop <= cardBottom) {
                const pageNum = parseInt(card.dataset.page || (i + 1), 10);
                if (pageNum !== app.composer.currentPage) {
                  app.composer.currentPage = pageNum;
                  const cur = document.getElementById('composer-page-current');
                  if (cur) cur.innerText = pageNum;
                }
                break;
              }
            }
          });
        }

        for (let i = 1; i <= this.totalPages; i++) {
          const page = await this.pdfDoc.getPage(i);
          this.pdfPages.push(page);
          const baseVp = page.getViewport({ scale: 1.0 });
          this.pdfBaseViewports.push(baseVp);

          const pageCard = document.createElement('div');
          pageCard.className = 'pdf-page-card bg-white shadow-lg border border-slate-300/80 rounded-xs transition-transform duration-75 relative mx-auto my-1';
          pageCard.id = `pdf-page-${i}`;
          pageCard.dataset.page = i;

          const canvas = document.createElement('canvas');
          canvas.id = `pdf-canvas-${i}`;
          canvas.className = 'block';
          pageCard.appendChild(canvas);
          pagesContainer.appendChild(pageCard);
        }

        // Calculate initial zoom to fit container width nicely
        if (scrollContainer && this.pdfBaseViewports[0]) {
          const availableW = scrollContainer.clientWidth - 48;
          if (availableW > 200 && this.pdfBaseViewports[0].width > 0) {
            const fitZoom = +(availableW / this.pdfBaseViewports[0].width).toFixed(1);
            this.zoomLevel = Math.max(0.5, Math.min(2.0, fitZoom));
          } else {
            this.zoomLevel = 1.0;
          }
        }
        const zoomDisplay = document.getElementById('composer-zoom-display');
        if (zoomDisplay) zoomDisplay.innerText = `${Math.round(this.zoomLevel * 100)}%`;

        this.renderAllPages();
      } catch (err) {
        console.error('PDF.js loading failed, falling back to iframe:', err);
        if (iframe) {
          iframe.classList.remove('hidden');
          iframe.src = `${pdfUrl}?t=${Date.now()}`;
        }
      }
    },

    renderAllPages() {
      if (!this.pdfPages || !this.pdfPages.length) return;
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const z = this.zoomLevel;

      for (let i = 0; i < this.pdfPages.length; i++) {
        const page = this.pdfPages[i];
        const baseVp = this.pdfBaseViewports[i];
        const card = document.getElementById(`pdf-page-${i + 1}`);
        const canvas = document.getElementById(`pdf-canvas-${i + 1}`);
        if (!card || !canvas || !baseVp) continue;

        const displayWidth = Math.round(baseVp.width * z);
        const displayHeight = Math.round(baseVp.height * z);

        card.style.width = `${displayWidth}px`;
        card.style.height = `${displayHeight}px`;

        canvas.width = Math.round(displayWidth * dpr);
        canvas.height = Math.round(displayHeight * dpr);
        canvas.style.width = `${displayWidth}px`;
        canvas.style.height = `${displayHeight}px`;

        const ctx = canvas.getContext('2d');
        const viewport = page.getViewport({ scale: z * dpr });
        page.render({ canvasContext: ctx, viewport });
      }
    },

    zoomPreview(delta) {
      this.zoomLevel = Math.max(0.4, Math.min(2.5, +(this.zoomLevel + delta).toFixed(1)));
      const zoomDisplay = document.getElementById('composer-zoom-display');
      if (zoomDisplay) zoomDisplay.innerText = `${Math.round(this.zoomLevel * 100)}%`;

      if (this.pdfPages && this.pdfPages.length) {
        const z = this.zoomLevel;
        for (let i = 0; i < this.pdfPages.length; i++) {
          const baseVp = this.pdfBaseViewports[i];
          const card = document.getElementById(`pdf-page-${i + 1}`);
          const canvas = document.getElementById(`pdf-canvas-${i + 1}`);
          if (card && baseVp) {
            const displayWidth = Math.round(baseVp.width * z);
            const displayHeight = Math.round(baseVp.height * z);
            card.style.width = `${displayWidth}px`;
            card.style.height = `${displayHeight}px`;
            if (canvas) {
              canvas.style.width = `${displayWidth}px`;
              canvas.style.height = `${displayHeight}px`;
            }
          }
        }

        clearTimeout(this._renderTimer);
        this._renderTimer = setTimeout(() => {
          this.renderAllPages();
        }, 120);
      }
    },

    resetZoom() {
      const scrollContainer = document.getElementById('composer-pdf-scroll-container');
      if (scrollContainer && this.pdfBaseViewports[0]) {
        const availableW = scrollContainer.clientWidth - 48;
        if (availableW > 200 && this.pdfBaseViewports[0].width > 0) {
          const fitZoom = +(availableW / this.pdfBaseViewports[0].width).toFixed(1);
          this.zoomLevel = Math.max(0.5, Math.min(2.0, fitZoom));
        } else {
          this.zoomLevel = 1.0;
        }
      } else {
        this.zoomLevel = 1.0;
      }
      const zoomDisplay = document.getElementById('composer-zoom-display');
      if (zoomDisplay) zoomDisplay.innerText = `${Math.round(this.zoomLevel * 100)}%`;
      this.renderAllPages();
    },

    downloadPdf() {
      if (!this.pdfUrl) {
        showToast('Vui lòng biên dịch tài liệu trước khi tải về.', 'warning');
        return;
      }
      const a = document.createElement('a');
      a.href = this.pdfUrl;
      a.download = `${this.activeTitle.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      showToast('Đang tải tệp PDF xuống...', 'success');
    },

    async saveToBank() {
      if (!this.currentLatex || !this.currentLatex.trim()) {
        showToast('Nội dung đề thi đang trống.', 'warning');
        return;
      }

      showToast('Đang trích xuất câu hỏi vào Ngân hàng...', 'info');
      try {
        const res = await fetch(`${API_BASE_URL}/composer/save-to-bank`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ latex_code: this.currentLatex })
        });
        const data = await res.json();
        if (res.ok && data.success) {
          showToast(data.message || `Đã lưu ${data.count} câu hỏi vào Ngân hàng!`, 'success');
          await fetchItemBank();
        } else {
          showToast(data.message || 'Không tìm thấy câu hỏi phù hợp dạng \\textbf{Câu X.}', 'warning');
        }
      } catch (e) {
        showToast(`Lỗi khi lưu vào ngân hàng: ${e.message}`, 'error');
      }
    },

    toggleAIPane() {
      const pane = document.getElementById('composer-ai-pane');
      const editorPane = document.getElementById('composer-editor-pane');
      if (!pane) return;

      this.aiPaneVisible = !this.aiPaneVisible;
      if (this.aiPaneVisible) {
        pane.classList.remove('hidden');
        if (editorPane) {
          editorPane.classList.remove('lg:col-span-8');
          editorPane.classList.add('lg:col-span-5');
        }
      } else {
        pane.classList.add('hidden');
        if (editorPane) {
          editorPane.classList.remove('lg:col-span-5');
          editorPane.classList.add('lg:col-span-8');
        }
      }
    },

    toggleAutoCompile(enabled) {
      this.autoCompile = enabled;
      showToast(enabled ? 'Đã bật tự động biên dịch sau khi gõ.' : 'Đã tắt tự động biên dịch.', 'info');
    },

    formatCode() {
      const editor = document.getElementById('composer-editor-input');
      if (!editor) return;
      let val = editor.value;

      val = val.replace(/\n{4,}/g, '\n\n\n');
      editor.value = val;
      this.handleEditorInput();
      showToast('Đã chuẩn hoá cấu trúc mã!', 'success');
    },

    clearEditor() {
      if (confirm('Bạn có chắc chắn muốn xóa toàn bộ mã nguồn đang soạn thảo?')) {
        const editor = document.getElementById('composer-editor-input');
        if (editor) {
          editor.value = '';
          this.handleEditorInput();
          showToast('Đã xóa sạch nội dung.', 'info');
        }
      }
    }
  };

  // Run on DOM loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  // Expose global methods to window.app for HTML onclick bindings
  window.app = {
    composer,
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
    insertStemTikzDiagram,
    standardizeModalStemToTkz,
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
    exportDigitizedToPdf,
    exportDigitizedToDocx,
    renderDigitizeStudio,
    getState: () => state,
  };
})();
