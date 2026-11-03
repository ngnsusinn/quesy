# Quesy — AI Exam Management & Mathematical Publishing Platform

> **An enterprise-grade assessment platform, 2-Pass AI digitization pipeline, and high-fidelity mathematical publishing engine for modern examination standards.**

[![CI Test Suite](https://github.com/ngnsusinn/quesy/actions/workflows/ci.yml/badge.svg)](https://github.com/ngnsusinn/quesy/actions)
![Python](https://img.shields.io/badge/Python-3.10%20--%203.14-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI%20%2B%20SQLAlchemy-009688?logo=fastapi&logoColor=white)
![Frontend](https://img.shields.io/badge/Frontend-Vanilla%20SPA%20%2B%20Apple%20HIG-000000?logo=apple&logoColor=white)
![Pytest](https://img.shields.io/badge/Tests-289%2F289%20Passing-brightgreen?logo=pytest&logoColor=white)
![Formal Invariants](https://img.shields.io/badge/Invariants-8028%20Verified%20(Z3%20SMT)-blueviolet)

---

## What is Quesy?

**Quesy** streamlines the entire examination lifecycle for educators: from digitizing paper tests and organizing question banks to designing test blueprints, shuffling variants safely, and publishing print-ready vector PDFs.

- **No Retyping:** Ingest scanned PDFs or smartphone photos; AI converts formulas to KaTeX/LaTeX and diagrams into native TikZ code.
- **Preamble-Free LaTeX Authoring:** Edit questions using standard `ex_test.sty` syntax (`\begin{ex}`, `\choice`, `\choiceTF[1]`, `\shortans`). Canonical preambles, fonts, and packages are injected automatically.
- **Mathematical Invariant Shuffling:** Guaranteed option anchoring (meta-choices stay at D), passage contiguity, and progressive tiered scoring (0.1, 0.25, 0.5, 1.0 pt).
- **Pure Vector PDF Output:** 100% full-size `\dfrac` typography via Computer Modern Unicode (CMU Serif) and zero raster PNG degradation.

---

## Core Capabilities

| Subsystem | Key Capabilities |
|---|---|
| **LaTeX Exam Composer** | Preamble-free editor, Apple HIG split-view with live PDF preview, multimodal AI Copilot (clipboard image paste `Ctrl+V`, natural language search & replace, 1-click syntax repair, and diff review). |
| **2-Pass AI Digitizer** | Pass 1: Layout segmentation, OpenCV CLAHE contrast enhancement, and WebP asset cropping.<br>Pass 2: Semantic extraction, KaTeX math normalization, native TikZ/`tkz-tab` compilation, and duplicate detection ($\ge 90\%$ cosine similarity blocked). |
| **Assessment Matrix** | 3-tier taxonomy tree (Topic $\rightarrow$ Lesson $\rightarrow$ Archetype) $\times$ 3 exam parts $\times$ 4 Bloom cognitive tiers. Real-time question stock validation (`Kho: {stock}`). |
| **Safe Shuffling Engine** | 4 mathematically verified rules: progressive scoring, Option Anchoring (locks dependent choices to D), passage contiguity, and automated cross-variant key matrix generation. |
| **Vector PDF & ZIP Publishing** | Produces bundled `.ZIP` publications containing variant PDFs, step-by-step solution keys, master answer sheets (PDF & CSV UTF-8 BOM), and standard 2025 OMR bubble sheets. |
| **Question Item Bank** | 6-tier cascading taxonomy filters, 100% persistent SQLite/PostgreSQL storage, Apple HIG pagination, on-demand KaTeX rendering (<10ms), and 1-click save from Composer. |
| **Auth & Security** | PBKDF2-HMAC-SHA256 (600,000 iterations), JWT HS256 lifecycle, role-based access control (`ADMIN`, `TEACHER`, `STUDENT`), and Google/GitHub OAuth2. |

---

## Architecture at a Glance

```
[Browser SPA (Apple HIG)]
        │  HTTP / JSON REST API
        ▼
[FastAPI Gateway (Port 8000)]
  ├── /composer  ──► Tectonic XeTeX Service (armbian:8090) ──► Vector PDF
  ├── /digitize  ──► OpenCV Preprocessing + Multimodal LLM  ──► KaTeX / TikZ
  ├── /matrix    ──► Matrix Constraint Solver (Real-time stock validation)
  ├── /exams     ──► Safe Shuffler (Option Anchor + Passage Contiguity)
  └── /questions ──► SQLAlchemy ORM ──► SQLite / PostgreSQL (storage/quesy.db)
```

---

## Quick Start

### 1. Prerequisites
- **Python:** 3.10 – 3.14
- **Node.js:** 18+ or 20+ (for MathJax vector rendering worker)
- **Google Chrome / Chromium** (headless vector fallback)

### 2. Setup
```bash
# Clone repository
git clone https://github.com/ngnsusinn/quesy.git
cd quesy

# Setup Python environment
python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1 | Linux/macOS: source venv/bin/activate
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Initialize environment configuration
cp .env.example .env
```

### 3. Run Application
```bash
# Recommended: Smart launcher with automatic DB init, seed data, and port auto-recovery
python start_server.py

# Or directly with Uvicorn
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Or with Docker Compose
docker-compose up --build -d
```

- **Web Studio UI:** [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Swagger API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check:** [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## Testing & Formal Verification

Quesy enforces strict 100% test pass rates across all modules:

```bash
# 1. Run full automated test suite (289/289 passing)
pytest -v

# 2. Run formal mathematical verification of exam invariants (Z3 SMT solver)
python scripts/formal_verification_exam_invariants.py

# 3. Run full end-to-end pipeline verification (creates genuine PDF & ZIP bundles)
python scripts/verify_pipeline.py
```

---

## Tóm Tắt Dự Án (Vietnamese Summary)

**Quesy** là hệ thống quản lý khảo thí, soạn thảo $\LaTeX$ thông minh và số hóa đề thi chuyên sâu dành cho giáo viên và tổ chuyên môn:

1. **Soạn đề không Preamble:** Giáo viên chỉ cần viết nội dung câu hỏi chuẩn `ex_test.sty` (`\begin{ex}`, `\choice`, `\choiceTF[1]`, `\shortans`). Hệ thống tự động nhúng gói lệnh chuẩn, font CMU Serif và xuất PDF tức thì.
2. **Trợ lý AI Copilot:** Dán ảnh đề bài trực tiếp (`Ctrl+V`), AI tự dựng hình TikZ/bảng biến thiên vector; tìm & thay thế bằng tiếng Việt tự nhiên; tự động phân tích và sửa lỗi biên dịch $\LaTeX$.
3. **Số hóa AI 2-Pass:** Bóc tách đề thi từ file scan/ảnh/PDF, lọc nhiễu ảnh OpenCV CLAHE, trích xuất công thức KaTeX và kiểm tra chống trùng câu hỏi.
4. **Ma trận & Trộn đề an toàn:** Thiết lập ma trận đề 3 phần $\times$ 4 mức độ nhận thức kèm kiểm tra số dư kho câu hỏi thực tế; khóa cứng đáp án phụ thuộc vào phương án D và giữ nguyên vẹn bài đọc chùm.
5. **Xuất bản thuần Vector PDF:** Đóng gói trọn bộ tệp `.ZIP` gồm các mã đề thi hoán vị, hướng dẫn giải chi tiết, bảng ma trận đáp án (PDF & CSV UTF-8 BOM) và phiếu trả lời trắc nghiệm OMR.

---

## License

Distributed under the MIT License. Developed and maintained by [@ngnsusinn](https://github.com/ngnsusinn).
