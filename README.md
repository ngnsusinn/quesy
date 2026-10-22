# Quesy: AI-Powered National Assessment & Mathematical Publishing Platform

> **An enterprise-grade assessment platform, AI digitization pipeline, and high-fidelity mathematical publishing engine built strictly for Vietnam's Ministry of Education and Training (MoET) Circular 32/2018/TT-BGDĐT and Decision 764/QĐ-BGDĐT examination standards.**

[![CI Test Suite](https://github.com/ngnsusinn/quesy/actions/workflows/ci.yml/badge.svg)](https://github.com/ngnsusinn/quesy/actions)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%2B%20SQLAlchemy-009688?logo=fastapi&logoColor=white)
![Node.js](https://img.shields.io/badge/Engine-Node.js%2020%20%2B%20MathJax%203-339933?logo=node.js&logoColor=white)
![Frontend](https://img.shields.io/badge/Frontend-Apple%20HIG%20%2B%20TailwindCSS%20%2B%20KaTeX-000000?logo=apple&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-70%2F70%20Passing-brightgreen?logo=pytest&logoColor=white)
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

**Quesy** is a high-performance assessment management, AI digitization, and mathematical publishing platform. It eliminates hours of manual exam retyping, automates question item classification, compiles mathematical diagrams into native vector graphics, and produces publication-ready examination papers in both **pure LaTeX vector PDF** and **bidirectionally editable MathType 7.0 OLE Word `.docx`** formats.

The platform is strictly tailored to national assessment standards:
- **Circular 32/2018/TT-BGDĐT:** 6-tier competency-based knowledge taxonomy mapped to Learning Outcomes (Yêu cầu cần đạt - YCCĐ) and Problem Archetypes, strictly independent of commercial textbook series.
- **Decision 764/QĐ-BGDĐT (Format 2025):** Automated progressive tiered scoring for multi-statement True/False items (0.1 pt for 1 correct, 0.25 pt for 2, 0.5 pt for 3, and 1.0 pt for all 4).

---

## Why Quesy? Problem & Solution Matrix

| # | Real-World Examination Pain Point | Quesy Architectural Solution |
|:---:|:---|:---|
| **1** | **Exhausting Manual Retyping:** Teachers spend 1.5–2 hours retyping an exam from scanned PDFs, photos, or legacy Word files; formulas lose formatting and special symbols corrupt during copy-pasting. | **Multimodal AI OCR & MTEF Decoder:** Ingests scanned PDFs, smartphone photos, and Word files in seconds, directly converting binary MathType MTEF streams into standardized KaTeX/LaTeX. |
| **2** | **Corrupted or Downscaled Formulas:** Exporting exams often shrinks in-text fractions to illegible script sizes, drops brackets, or renders fuzzy raster PNG images that cannot be edited. | **Dual Publishing Engines:** Generates print-ready PDFs with 100% full-size `\dfrac` typography via **CMU Serif**, or Word `.docx` documents containing **genuine MathType 7.0 OLE Vector WMFs** editable via double-click. |
| **3** | **Rasterized & Blurred Geometry/Plots:** Standard OCR tools either skip coordinate plots entirely or insert low-res raster images with distorted asymptotes and blown-out aspect ratios. | **Vector TikZ/PGFPlots Engine:** Compiles geometry and function plots directly from LaTeX source code into vector SVGs with automatic bounding-box clipping (**zero raster PNGs** in PDF output). |
| **4** | **Broken Question Logic during Shuffling:** Traditional exam shufflers blindly randomize choices, causing options like *"Both A and B are correct"* to appear at position A, or splitting reading passages from sub-questions. | **Safe Shuffling Engine:** Enforces **Option Anchoring** (keeps meta-choices fixed at choice D), **Passage Integrity**, **Section Integrity**, and generates cross-variant answer keys automatically. |
| **5** | **Error-Prone Tiered Grading:** Hand-grading 4-statement True/False questions with progressive weights (0.1, 0.25, 0.5, 1.0) leads to frequent human error and grading disputes. | **Automated Grading & Classroom Roster:** Instantly scores submissions according to official decision logic, provides score distribution analytics, and supports UTF-8 BOM Excel/CSV rosters. |
| **6** | **Black-Box Errors on PDF Tables:** Data tables exported from LaTeX arrays frequently turn into opaque black blocks when converted to Word or printed to PDF. | **Native Word Table Converter:** Automatically detects `\begin{array}` and `\begin{tabular}` blocks and builds native OpenXML `<w:tbl>` elements with clean borders and centered cell alignment. |

---

## Core Capabilities

### 1. AI-Powered LaTeX Exam Composer & Live PDF Preview (Open-Prism Clone)

Located in `backend/services/composer_service.py` & `backend/routers/composer.py`:
- **Open-Prism Architecture Clone & ex_test v3.3 Integration:** A full-featured 3-pane AI LaTeX authoring workspace (`/composer`) with live PDF compilation and preview, bundled with Vietnam's standard `ex_test.sty` (v3.3) package (`\begin{ex}`, `\choice`, `\choiceTF`, `\shortans`, `\immini`).
- **AI-Assisted Writing Workspace:** Integrated chat copilot specifically trained on Vietnam MoET Circular 32/2018 and Decision 764/2025 formats, generating multiple-choice questions, True/False sets, `tkz-tab` variation tables, and TikZ graphs with 1-click "Insert at cursor", "Replace document", and "Copy code" actions.
- **CodeMirror-Grade LaTeX Editor:** Code editor with real-time gutter line numbers, tab indentation, bracket auto-closing, and quick-insert math toolbars (`\dfrac`, `\sqrt`, `\vec`, `\in \mathbb{R}`, `+ ex (4 PA)`, `+ ex (Đ/S)`, `+ ex (Điền số)`, `+ immini`, `tkz-tab`, 3D Pyramids).
- **Live PDF Preview & Tectonic Docker Microservice:** Debounced instant compilation via remote Tectonic XeTeX engine (or local fallback), displaying vector-crisp 100% CMU Serif PDFs inline with zoom controls, fullscreen preview, and compilation error drawer.
- **Local Persistence & 1-Click Question Bank Export:** Automatically saves drafts to `localStorage` across page reloads (F5) and enables 1-click question extraction directly into the central Question Bank.

### 2. Pure LaTeX Vector PDF Publishing

Located in `backend/services/latex_pdf_exporter.py`:
- **Authentic LaTeX Typography:** Adopts **Computer Modern Unicode (CMU Serif)** across the entire document, completely replacing office-style Times New Roman.
- **100% Full-Size `\dfrac` Display Fractions:** Automatically promotes all fractions to `\dfrac` (`\displaystyle`), guaranteeing 100% font sizing (11pt) for numerators and denominators without in-line downscaling.
- **Micro-Typography Spacing:** Employs persistent MathJax SVG rendering with tight horizontal padding (`padX = 15`) and auto-strips leading spaces before trailing punctuation (`.`, `,`, `;`, `:`, `!`, `?`), ensuring periods rest flush on the text baseline.
- **Official Exam Header & Student Block:** Formats a clean 3-column student metadata table (`Name`, `Candidate ID`, `Exam Room`) on a single line, paired with standard Ministry exam banners and footers (`Page X - Exam Code Y`).

### 3. MathType 7.0 OLE Vector Word Export

Located in `backend/services/docx_exporter.py`:
- **Genuine OLE Binary Storage:** Synthesizes Compound File Binary (CFB) streams housing `\x01CompObj` (`MathType 7.0 Equation`, root CLSID `{0002CE03-0000-0000-C000-000000000046}`), `\x01Ole`, `\x03ObjInfo` (`0x0004`), and `Equation Native` (MTEF v5 generated from MathJax MathML).
- **Aldus Placeable Metafile (APM) Header:** Uses pure vector WMF graphics (`magic: 0x9AC6CDD7`, scale 20 twips/pt, 1440 DPI) as the OLE inline preview image. Never uses fuzzy raster PNGs.
- **Bidirectional Editing:** Double-clicking any equation in Microsoft Word directly opens the MathType 7 desktop equation editor.

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
│       ├── docx_exporter.py       # MathType 7.0 OLE Vector WMF Word exporter
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
│   └── exports/                   # Published Word, PDF, and ZIP exam packages
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
- **Trộn đề thông minh & an toàn:** Khóa cố định các đáp án phụ thuộc (*"Cả A và B đều đúng"*) tại vị trí D, giữ nguyên bài đọc chung và sinh ma trận hoán vị đáp án tự động.
- **Giao diện Apple HIG:** Trải nghiệm đối chiếu song song mượt mà, phản hồi xúc giác tinh tế, chạy mượt trên cả Web và thiết bị di động (PWA Offline).
