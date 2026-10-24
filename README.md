# Quesy: AI-Powered National Assessment & Mathematical Publishing Platform

> **An enterprise-grade assessment platform, AI digitization pipeline, and high-fidelity mathematical publishing engine built strictly for Vietnam's Ministry of Education and Training (MoET) Circular 32/2018/TT-BGDĐT and Decision 764/QĐ-BGDĐT examination standards.**

[![CI Test Suite](https://github.com/ngnsusinn/quesy/actions/workflows/ci.yml/badge.svg)](https://github.com/ngnsusinn/quesy/actions)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%2B%20SQLAlchemy-009688?logo=fastapi&logoColor=white)
![Node.js](https://img.shields.io/badge/Engine-Node.js%2020%20%2B%20MathJax%203-339933?logo=node.js&logoColor=white)
![Frontend](https://img.shields.io/badge/Frontend-Apple%20HIG%20%2B%20TailwindCSS%20%2B%20KaTeX-000000?logo=apple&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-125%2F125%20Passing-brightgreen?logo=pytest&logoColor=white)
![Standard](https://img.shields.io/badge/Standard-Circular%2032%20%26%20Decision%20764-orange)

---

> [!NOTE]
> **Bilingual Documentation / Tài liệu Song ngữ:**  
> This documentation is written primarily in **English** with comprehensive **Vietnamese summaries** for educators, assessment boards, and software engineers in Vietnam.  
> *Tài liệu này được biên soạn với ngôn ngữ chính là Tiếng Anh, kèm theo các phần tóm tắt và chỉ dẫn Tiếng Việt phục vụ công tác giảng dạy, khảo thí và tích hợp hệ thống tại Việt Nam.*

---

## Table of Contents

- [Overview](#overview)
- [Why Quesy? Problem & Solution Matrix](#why-quesy-problem--solution-matrix)
- [Core Capabilities](#core-capabilities)
- [System Architecture](#system-architecture)
- [Getting Started](#getting-started)
- [Automated Verification & CI/CD Pipeline](#automated-verification--cicd-pipeline)
- [Vietnamese Executive Summary (Tóm Tắt Dự Án)](#vietnamese-executive-summary-tóm-tắt-dự-án)

---

## Overview

**Quesy** is a high-performance assessment management, AI digitization, and mathematical publishing platform. It eliminates hours of manual exam retyping, automates question item classification, compiles mathematical diagrams into native vector graphics, and produces publication-ready examination papers in **pure LaTeX vector PDF** (via **Tectonic XeTeX Engine** and **ReportLab**).

The platform is strictly tailored to national assessment standards:
- **Circular 32/2018/TT-BGDĐT:** 6-tier competency-based knowledge taxonomy mapped to Learning Outcomes (Yêu cầu cần đạt - YCCĐ) and Problem Archetypes, strictly independent of commercial textbook series.
- **Decision 764/QĐ-BGDĐT (Format 2025):** Automated progressive tiered scoring for multi-statement True/False items (0.1 pt for 1 correct, 0.25 pt for 2, 0.5 pt for 3, and 1.0 pt for all 4).

---

## Why Quesy? Problem & Solution Matrix

| # | Real-World Examination Pain Point | Quesy Architectural Solution |
|:---:|:---|:---|
| **1** | **Exhausting Manual Retyping:** Teachers spend 1.5–2 hours retyping an exam from scanned PDFs, photos, or legacy files; formulas lose formatting and special symbols corrupt during copy-pasting. | **Multimodal AI OCR & LaTeX Decoder:** Ingests scanned PDFs, smartphone photos, and files in seconds, directly converting mathematical equations into standardized KaTeX/LaTeX. |
| **2** | **Corrupted or Downscaled Formulas:** Exporting exams often shrinks in-text fractions to illegible script sizes, drops brackets, or renders fuzzy raster PNG images that cannot be printed sharply. | **Pure Vector PDF Publishing Engine:** Generates print-ready vector PDFs with 100% full-size `\dfrac` typography via **Computer Modern Unicode (CMU Serif)** and high-fidelity XeTeX font metrics. |
| **3** | **Rasterized & Blurred Geometry/Plots:** Standard OCR tools either skip coordinate plots entirely or insert low-res raster images with distorted asymptotes and blown-out aspect ratios. | **Vector TikZ/PGFPlots Engine:** Compiles geometry and function plots directly from LaTeX source code into vector SVGs with automatic bounding-box clipping (**zero raster PNGs** in PDF output). |
| **4** | **Broken Question Logic during Shuffling:** Traditional exam shufflers blindly randomize choices, causing options like *"Both A and B are correct"* to appear at position A, or splitting reading passages from sub-questions. | **Safe Shuffling Engine:** Enforces **Option Anchoring** (keeps meta-choices fixed at choice D), **Passage Integrity**, **Section Integrity**, and generates cross-variant answer keys automatically. |
| **5** | **Error-Prone Tiered Grading:** Hand-grading 4-statement True/False questions with progressive weights (0.1, 0.25, 0.5, 1.0) leads to frequent human error and grading disputes. | **Automated Grading & Classroom Roster:** Instantly scores submissions according to official decision logic, provides score distribution analytics, and supports UTF-8 BOM Excel/CSV rosters. |
| **6** | **Black-Box Errors & Formatting Inconsistencies:** Complex tables and multi-column exams frequently suffer from overlapping lines and black blocks when printed. | **Native LaTeX 2-Column Typesetting:** Built-in two-column typesetting with `ex_test.sty` v3.3, automatic table borders, and zero-defect PDF vector rendering. |

---

## Core Capabilities

### 1. AI-Powered LaTeX Exam Composer & Live PDF Preview (Noctorium & Open-Prism Layout)

Located in `backend/services/composer_service.py` & `backend/routers/composer.py`:
- **Apple HIG Split Resizer & Resizable 2-Column Architecture:** A full-featured 2-column LaTeX authoring workspace (`/composer`) with live PDF compilation and preview, bundled with Vietnam's standard `ex_test.sty` (v3.3) package (`\begin{ex}`, `\choice`, `\choiceTF`, `\shortans`, `\immini`). Equipped with an Apple HIG horizontal splitter (`#composer-split-resizer`) with ergonomic gutter spacing (`w-3.5`/`w-4` with `mx-1`/`mx-1.5`) keeping a 6-8px breathing room from the editor and preview card borders (eliminating tight border collisions). Features an Apple capsule grabber pill (`w-1 h-9 rounded-full bg-slate-300 dark:bg-[#34415e]`) with Apple Blue `#0071e3` hover glow, smooth 60 FPS dragging between 25% and 75% width ratio, double-click 60:40 reset, and persistent storage in `localStorage`.
- **Unified Single Pill Handle & Vertical Drag Resizer:** The AI Assistant popup (`#composer-ai-popup`) features a single unified grabber pill (`#composer-ai-resize-handle`) seamlessly integrated into the header center (completely eliminating redundant duplicate pill strips), enabling smooth vertical drag resizing from 180px up to 92% of the editor height, with instant transition suppression during drag and single/double-click height toggling.
- **Clean Session Lifecycle & Archived History Drawer:** Each new session opens with a clean workspace containing only the default Quesy Copilot greeting, without cluttering the chat with old conversation logs. Previous sessions are safely archived in `localStorage` (`quesy_composer_chat_sessions`) and viewable via the "Lịch sử" drawer button.
- **Multi-Diff Review & Apply All Engine (Zero Bubble Chat Clutter):** When the AI proposes code changes, visual diff decorations (red `- old_line`, green `+ new_line`, and action buttons) are rendered exclusively on the LaTeX code editor (Inline Diff Overlay and Top Diff Banner), keeping chat bubbles clean. Fully supports multi-diff proposals (`diffs: List[DiffSuggestion]`) with a dynamic counter capsule (`1/N`), sequential stepper navigation (`[< Trước]` / `[Sau >]`), individual Keep/Undo, and a prominent **[Áp dụng tất cả] (Apply All)** button for 1-click batch application of all suggested changes.
- **Compact Floating AI Prompt Bar with Optimistic Input Reset:** A sleek glassmorphism pill bar anchored at the bottom of the editor (`#composer-ai-compact-bar`). Equipped with high-contrast text tokens (`#f8fafc` white text and `#38bdf8` Apple blue caret) complying with WCAG 2.1 AA standards, eliminating dark-on-dark text invisibility. Clicking on the bar focuses the input for undisturbed typing without premature modal popups. Pressing `Enter` or clicking the round Send button triggers an instant, zero-lag optimistic dispatch with **synchronous input wipe ($\le 0\text{ms}$)** across both compact and popup input fields, completely preventing stale text retention after sending.
- **AI Copilot with Compile Error Forwarding & Diagnostics:** Automatically captures the latest XeTeX/Tectonic compiler error log (`compile_error_log`) whenever a compilation fails and forwards it into the AI Copilot context. The AI analyzes the raw TeX diagnostic stream (`! Undefined control sequence`, unclosed environments, missing packages), pinpoints the erroneous line in source code, and formulates an instant syntax repair diff.
- **6-Tier Resilient Fuzzy Replacement Engine:** Driven by a robust 6-tier fuzzy matching algorithm (normalizing whitespace/CRLF, indentation-agnostic comparison, and sliding-window sequence matching), clicking **[Đồng ý] (Accept)** achieves a 100% replacement success rate without ever raising "old line not found" errors.
- **CodeMirror-Grade Dark LaTeX Editor:** Code editor with real-time gutter line numbers, tab indentation, bracket auto-closing, persistent dark background `#141824` on cursor focus, and quick-insert `ex_test` template menus (`MỚI`, `THÊM ▾`).
- **Live PDF Preview, Auto Fit-to-Width & Smart Zoom-to-Point Engine:** Debounced instant compilation via remote Tectonic XeTeX engine (or local fallback), displaying vector-crisp 100% CMU Serif PDFs. Features dynamic auto fit-to-width (`fitToWidth`) on column resize/splitter drag, safe horizontal scrolling (`overflow-x-auto`) preventing right-margin truncation, and adaptive zoom-to-point (Cursor Anchor under mouse pointer and Viewport Center Anchor on button clicks), eliminating jarring jumps to (0, 0).
- **Local Persistence & 1-Click Question Bank Export:** Automatically saves drafts, column split ratio, and assistant height to `localStorage` across page reloads (F5) and enables 1-click question extraction directly into the central Question Bank.

### 2. Pure LaTeX Vector PDF Publishing

Located in `backend/services/latex_pdf_exporter.py`:
- **Authentic LaTeX Typography:** Adopts **Computer Modern Unicode (CMU Serif)** across the entire document, completely replacing office-style Times New Roman.
- **100% Full-Size `\dfrac` Display Fractions:** Automatically promotes all fractions to `\dfrac` (`\displaystyle`), guaranteeing 100% font sizing (11pt) for numerators and denominators without in-line downscaling.
- **Micro-Typography Spacing:** Employs persistent MathJax SVG rendering with tight horizontal padding (`padX = 15`) and auto-strips leading spaces before trailing punctuation (`.`, `,`, `;`, `:`, `!`, `?`), ensuring periods rest flush on the text baseline.
- **Official Exam Header & Student Block:** Formats a clean 3-column student metadata table (`Name`, `Candidate ID`, `Exam Room`) on a single line, paired with standard Ministry exam banners and footers (`Page X - Exam Code Y`).

### 3. Bundled Publication Package (.ZIP)

Located in `backend/services/docx_exporter.py` & `backend/routers/exams.py`:
- **Complete PDF Exam Bundle:** Packages all shuffled exam variants (`De_101.pdf`, `De_102.pdf`, etc.) with official Ministry 2-column styling, full headers, and crisp vector typography.
- **Detailed Solution Keys:** Generates separate step-by-step solution documents (`LoiGiai_101.pdf`) including progressive Decision 764 grading criteria for True/False sections.
- **Master Cross-Variant Answer Key:** Produces cross-variant permutation tables in both print-ready PDF and machine-readable CSV (`BangDapAn_TongHop.csv`).
- **Standardized OMR Answer Sheet:** Automatically includes standard Vietnam MoET 2025 optical mark recognition bubble sheets (`Phieu_Tra_Loi_Trac_Nghiem_2025.pdf`).

### 4. Native TikZ/PGFPlots Vector Diagram Compilation

Located in `backend/services/tikz_renderer.py`:
- **Direct TeX-to-Vector Compilation:** Uses a dedicated `dvisvgm` pipeline to compile raw `\begin{tikzpicture}` source code into standalone vector SVGs.
- **Zero Raster PNGs:** Diagrams are embedded as pure vector elements inside the PDF DOM, ensuring lines, asymptotes, coordinates, and labels remain crisp at 2000% zoom.
- **Auto-Clipping for Rational Functions:** Detects extreme coordinate ranges in rational curves and injects bounding `\clip` rectangles to preserve balanced aspect ratios.

### 5. Safe Shuffling Engine

Located in `backend/services/shuffling_engine.py`:
- **Option Anchoring (Rule 02):** Automatically identifies options with semantic dependencies (e.g., *"Both A and B are correct"*, *"All of the above"*, or `is_fixed = true`) and locks them strictly to Choice D across all generated variants.
- **Passage Integrity (Rule 03):** Keeps multi-question reading stems and stimulus passages glued to their corresponding child questions.
- **Section Integrity:** Shuffles items only within their respective format groups (Single Choice, Multi-Statement True/False, Short Answer).
- **Master Mapping Key:** Produces an instant answer permutation matrix mapping every shuffled variant code (101, 102, 103, 104...) back to the Master Exam.

### 6. National Curriculum Taxonomy & Progressive Grading

- **Circular 32 Taxonomy:** 6-tier hierarchical classification:
  $$\text{Grade} \longrightarrow \text{Subject} \longrightarrow \text{Strand} \longrightarrow \text{Topic} \longrightarrow \text{Lesson} \longrightarrow \text{YCCĐ Code} \longrightarrow \text{Problem Archetype}$$
- **Decision 764 Progressive Scoring Logic:**
  - 1 correct affirmation: **0.10 point**
  - 2 correct affirmations: **0.25 point**
  - 3 correct affirmations: **0.50 point**
  - 4 correct affirmations: **1.00 point**

### 7. Apple HIG Human-in-the-Loop Studio

Located in `frontend/`:
- **Single Page Application:** Fast client-side navigation with clean `/path` routing (`/digitize`, `/bank`, `/matrix`, `/shuffler`) registered on FastAPI to prevent 404s on browser reloads.
- **Dual-Pane Side-by-Side Review:** Compares raw scanned exam pages (left pane) against parsed electronic questions (right pane) in real time.
- **Tactile Micro-Interactions:** 0.97 active press scale feedback, clean typography, and zero clutter adhering to Apple Human Interface Guidelines.

---

## System Architecture

```
quesy/
├── backend/
│   ├── config.py                  # Environment config (.env), AI tokens, paths
│   ├── database.py                # SQLAlchemy engine & session factory
│   ├── models.py                  # ORM Models (Taxonomy, Question, Exam, Matrix)
│   ├── schemas.py                 # Strict Pydantic v2 validation contracts
│   ├── seed_data.py               # Pre-populated Circular 32 Mathematics 12 bank
│   ├── main.py                    # FastAPI application, CORS, SPA routes
│   ├── routers/
│   │   ├── taxonomy.py            # Circular 32 6-level taxonomy tree endpoints
│   │   ├── questions.py           # Question CRUD, AI Vector deduplication
│   │   ├── digitize.py            # AI Ingestion, OCR parsing & PDF export
│   │   ├── matrix.py              # 2D Assessment blueprint specification
│   │   └── exams.py               # MasterExam generation, shuffling & scoring
│   └── services/
│       ├── ai_provider_service.py # Multimodal AI connector (Gemini, OpenAI, Claude)
│       ├── ai_parser.py           # Document ingestion & OCR parsing pipeline
│       ├── mathjax_service.py     # Persistent MathJax client, caching & baseline metrics
│       ├── mathjax_worker.js      # Persistent Node.js worker (MathJax 3 + Resvg)
│       ├── tikz_renderer.py       # TikZ/PGFPlots-to-SVG vector compiler
│       ├── latex_converter.py     # MathType MTEF-to-LaTeX converter
│       ├── latex_pdf_exporter.py  # Pure LaTeX PDF compiler (CMU Serif + MathJax SVG)
│       ├── docx_exporter.py       # High-fidelity PDF & ZIP exam publishing engine
│       ├── shuffling_engine.py    # Safe shuffling engine (Option Anchor & Integrity)
│       └── excel_exporter.py      # UTF-8 BOM Excel/CSV score roster exporter
├── frontend/
│   ├── index.html                 # Apple HIG SPA UI (TailwindCSS, KaTeX, Lucide)
│   ├── manifest.json              # Progressive Web App (PWA) manifest
│   ├── sw.js                      # Network-first Service Worker
│   └── static/
│       ├── app.js                 # Frontend state machine & API client
│       ├── style.css              # Apple HIG micro-interactions & responsive styles
│       └── fonts/cmu-serif/       # Local Computer Modern Unicode TrueType fonts
├── .github/
│   └── workflows/
│       └── ci.yml                 # Automated CI test pipeline (Python 3.13 + Node.js 20)
├── storage/                       # Local filesystem storage
│   ├── uploads/                   # Staged source documents & images
│   ├── assets/                    # Cropped diagram assets (WebP)
│   ├── tikz_cache/                # Compiled TikZ SVG cache
│   └── exports/                   # Published PDF and ZIP exam packages
├── tests/                         # Comprehensive Pytest test suite (56 cases)
├── requirements.txt               # Locked Python dependencies
├── package.json                   # Node.js dependencies for MathJax & Fonts
└── start_server.py                # Smart server launcher with port auto-discovery
```

---

## Getting Started

### Prerequisites

Ensure you have the following installed on your machine:
- **Python:** Version 3.10 to 3.13
- **Node.js:** Version 18.x or 20.x
- **Google Chrome** or **Chromium Browser** (for headless PDF generation)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ngnsusinn/quesy.git
   cd quesy
   ```

2. **Install Python dependencies:**
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

### Environment Configuration

Create a `.env` file in the project root (optional if running in offline mode):

```env
# AI Multimodal Provider (gemini, openai, anthropic, openrouter)
AI_PROVIDER=gemini
AI_MODEL=gemini-1.5-flash
AI_API_KEY=your_api_key_here

# Server host & port (default: 127.0.0.1:8000)
HOST=127.0.0.1
PORT=8000
```

> [!TIP]
> If `AI_API_KEY` is not provided, Quesy automatically operates in **Offline Mode**, utilizing its built-in rule-based document parser and pre-seeded Circular 32 math bank.

### Running the Application

Launch the application using the smart process runner:

```bash
python start_server.py
```

The launcher automatically validates database tables, seeds Circular 32 taxonomy items, frees busy ports, and starts the API:
- **Web Studio (Apple HIG UI):** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check Endpoint:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

### Docker Deployment

Deploy in production using Docker Compose:

```bash
docker-compose up --build -d
```

---

## Automated Verification & CI/CD Pipeline

Quesy maintains a strict test suite verifying business logic, API contracts, mathematical typography, and performance budgets:

```bash
python -m pytest -v --durations=10
```

### Test Coverage Highlights (64/64 Tests Passing)

- `test_digitize_2pass.py`: Verifies uniform page rasterization (PyMuPDF), OpenCV CLAHE contrast enhancement, precision layout diagram/table segmentation, option text sentence case normalization, parallel 2-pass AI figure stitching & safety fallback, and TikZ `tkz-tab` variation table vector compilation.
- `test_rules_shuffling.py`: Verifies all 16 True/False permutations under progressive grading, ensures Choice D anchoring across 100 shuffling runs, and validates passage integrity.
- `test_mathjax_service.py` & `test_math_format_export.py`: Validates MTEF binary decoding, vector WMF APM generation, full-size `\dfrac` sizing, and baseline alignment.
- `test_digitize_docx_export.py`: Tests print-quality PDF export and genuine MathType 7.0 Word generation.
- `test_performance_budgets.py`: Enforces execution latency budgets (< 200 ms for matrix solving and shuffle generation).

### CI/CD Workflow (`.github/workflows/ci.yml`)

Every pull request and commit to `main` executes a multi-runtime GitHub Actions workflow on `ubuntu-latest`:
1. Sets up Python 3.13 and Node.js 20.
2. Installs system graphics dependencies and headless Chromium with `--no-sandbox` flags.
3. Installs `npm` math packages and `pip` requirements.
4. Executes the full 64-case test suite with mock AI adapters.

---

## Vietnamese Executive Summary (Tóm Tắt Dự Án)

### Quesy là gì?
**Quesy** là hệ sinh thái phần mềm khảo thí chuyên sâu, số hóa đề thi và quản lý ngân hàng câu hỏi chuẩn quốc gia:
- **Chuẩn hóa Thông tư 32/2018/TT-BGDĐT:** Cây kiến thức 6 tầng theo Yêu cầu cần đạt (YCCĐ) và Dạng câu hỏi, tuyệt đối không phân chia theo các bộ sách giáo khoa thương mại.
- **Chuẩn hóa Quyết định 764/QĐ-BGDĐT (Form 2025):** Chấm điểm tự động bậc thang cho câu trắc nghiệm Đúng/Sai 4 khẳng định (0.1đ - 0.25đ - 0.5đ - 1.0đ).
- **Xuất bản PDF chuẩn $\LaTeX$ thuần túy:** Toàn bộ đề thi in ấn sử dụng font chữ **Computer Modern Unicode (CMU Serif)**, 100% phân số hiển thị dạng **`\dfrac`** to rõ (11pt chuẩn đề thi), công thức toán vector sắc nét tuyệt đối, ôm sát chân dòng chữ.
- **Biên dịch Đồ thị & Hình học TikZ Vector:** 100% hình vẽ hình học và đồ thị hàm số được biên dịch trực tiếp từ mã nguồn $\LaTeX$ sang Vector SVG nguyên bản (`dvisvgm`), tuyệt đối **không biến thành ảnh raster PNG** (0% ảnh mờ vỡ hạt khi in ấn hay phóng to).
- **Xuất bản Word MathType 7.0 OLE Vector WMF:** Xuất file `.docx` nhúng OLE Equation Native binary, giáo viên nhấp đúp chuột trong Microsoft Word sẽ mở thẳng MathType 7 để chỉnh sửa 2 chiều bình thường.
- **Trợ lý Soạn thảo AI Copilot, Tối ưu Ô nhập Lạc quan & Duyệt Đa Diff (Multi-Diff 1/N, Apply All):** Thanh nhập Prompt dạng viên thuốc thu gọn (Compact Pill Bar) ở chân editor: chữ màu trắng sáng `#f8fafc` và con trỏ `#38bdf8` tương phản hoàn hảo trên Dark mode; click chuột chỉ để gõ text bình thường, chỉ bung mở popup trợ lý khi nhấn Enter hoặc bấm nút gửi. Cơ chế xóa sạch lạc quan (Optimistic Dual-Input Reset) triệt tiêu hoàn toàn lỗi text cũ còn kẹt trong ô nhập sau khi gửi. Khởi tạo phiên mới luôn sạch sẽ với lời chào mặc định và lưu trữ lịch sử phiên cũ qua ngăn kéo "Lịch sử". Tự động chuyển tiếp nhật ký lỗi biên dịch XeTeX/Tectonic (`compile_error_log`) để AI phân tích cú pháp và gợi ý sửa lỗi. Đề xuất sửa đổi hiển thị trực quan và độc quyền trực tiếp trên ô soạn thảo (Inline Editor Diff Overlay: dòng đỏ `-`, dòng xanh `+`, **loại bỏ hoàn toàn widget diff trong bubble chat**) kết hợp Động cơ Thay thế Dòng mờ 6 Tầng. Hỗ trợ đầy đủ đa khối diff với bộ đếm động 1/N, nút điều hướng tuần tự (`[< Trước]` / `[Sau >]`), duyệt chấp nhận/từ chối từng khối, và nút **`[Áp dụng tất cả] (Apply All)`** để hợp nhất toàn bộ các thay đổi vào mã nguồn chỉ với 1 cú click. Tái thiết kế thanh Split Resizer ngang `#composer-split-resizer` giữa 2 cột Editor / Preview chuẩn Apple HIG với khoảng cách đệm công thái học thông thoáng, trục viên thuốc thanh lịch, quầng sáng xanh Apple `#0071e3`, không bị đè sát viền box soạn thảo.
- **Trộn đề thông minh & an toàn:** Khóa cố định các đáp án phụ thuộc (*"Cả A và B đều đúng"*) tại vị trí D, giữ nguyên bài đọc chung và sinh ma trận hoán vị đáp án tự động.
- **Giao diện Apple HIG:** Trải nghiệm đối chiếu song song mượt mà, phản hồi xúc giác tinh tế, chạy mượt trên cả Web và thiết bị di động (PWA Offline).
