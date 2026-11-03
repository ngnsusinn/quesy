# AGENTS.md

## System Overview

Quesy is a comprehensive platform for Question Bank Management, Hierarchical Exam Specification Matrix Design, Smart Exam Shuffling, and 2-Pass AI Digitization, fully compliant with the assessment standards of Vietnam's 2018 General Education Curriculum.

### Key Functional Subsystems
1. **Question bank and Taxonomy Structure:** Manages questions within a hierarchical framework (Subject -> Grade -> Chapter -> Lesson -> Question Format -> Cognitive level) and supporting four questions formats:
   - Multiple-Choice Questions (MCQ)
   - True/False Questions
   - Short-Answer Questions
   - Essay/Constructed-Response Questions.
2. **AI Exam Digization:** Extract questions from PDFs, images, Word files (.doc, .docx) or LaTeX (.tex) files; automatically handles pages segmentation, figure cropping, image enhancement, math fomula conversation to LaTeX, deduplication and automated cognitive level tagging.
3. **Exam Composer and Copilot:** Visual authoring, smart toolbar, and a split-view mode for question replacement and quality assurance.
4. **Hierarchical Specification Matrix & Shuffling Engine:** Designs multi-dimensional matrix grids, automatically samples questions satisfying defined constraints, and generates permuted exam variants while strictly preserving mathematical invariants.
5. **Format Publishing:** Exports and compiles standard PDFs using the ex_test.sty package and TikZ.

### Source Map & Feature Map
Before making any changes, the Agent must cross-reference `docs/SOURCE_MAP.md` to understand the project architecture and the purpose of each file, and run `tree /f /a` to verify the repository structure. To look up features, UI controls, modals, or API endpoints, the Agent must first check `docs/FEATURE_MAP.md` for rapid discovery; only read the source code directly if not found in `docs/FEATURE_MAP.md`.

### Environment Setup & Operations
1. Development Environment Setup
```
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Node.js dependencies (for MathJax worker)
npm install

# 3. Initialize the environment configuration file (if not already created)
cp .env.example .env
```
2. Running the Application
```
# Option 1: Run via management script (Automatically initializes DB & seeds data)
python start_server.py

# Option 2: Run directly with Uvicorn in hot-reload mode
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Option 3: Run using Docker Compose
docker-compose up --build -d
```
3. Scoped Test Suite Execution
After modifying any source code, the Agent must only run the test suites directly mapped to the modified modules or features (unmodified components should be skipped). All executed tests must achieve a $100\%$ pass rate:
   - When modifying APIs, Routers, Models, or General Schemas:
   ```
   pytest tests/test_api_endpoints.py tests/test_api_contracts_and_negatives.py
   ```
   - When modifying AI Digitization Pipeline, OCR, Parsers, or Cloud Vision Adapter:
   ```
   pytest tests/test_digitize_2pass.py tests/test_ai_pipeline.py tests/test_cloud_vision_adapter.py
   ```
   - When modifying Specification Matrix, Shuffling Engine, or Grading:
   ```
   pytest tests/test_matrix_and_shuffler.py tests/test_rules_shuffling.py
   python scripts/formal_verification_exam_invariants.py
   ```
   - When modifying File Exporting:
   ```
   test_math_format_export.py tests/test_mathjax_service.py tests/test_excel_roster_import_export.py
   ```
   - When modifying Exam Composer & AI Copilot/Assistant:
   ```
   pytest tests/test_composer.py tests/test_composer_ai_assistant.py tests/test_composer_toolbar.py
   ```
   - When modifying Frontend UI or End-to-End Workflows (E2E):
   ```
   pytest tests/test_e2e_workflow.py tests/test_e2e_composer_blind_audit.py tests/test_e2e_composer_toolbar.py tests/test_e2e_dashboard_launchpad.py tests/test_e2e_friendly_item_bank.py tests/test_e2e_matrix_and_shuffler_headers.py
   ```
   - When optimizing performance, modifying system configs, or prior to final submission:
   ```
   pytest tests/test_performance_budgets.py
   python scripts/verify_pipeline.py
   # Run full automated regression only when explicitly requested: pytest
   ```
### Core Technical Invariants
The Agent must strictly adhere to the following 7 core technical invariants across all bug fixes, refactoring tasks, and new feature implementations:
1. Strict Compliance with the LaTeX `ex_test.sty` Package Specification
   - Reference Document: `docs/GUIDELINE_EX_TEST.md`.
   - All transformation workflows within `backend/services/latex_converter.py` and `backend/services/latex_pdf_exporter.py` must maintain complete compatibility with the structural conventions of the `ex_test.sty` package:
     - Standard Question Environment: `\begin{ex} ... \end{ex}`.
     - 4-Choice Multiple-Choice Questions (MCQs): `\choice{\True Correct answer}{Distractor 2}{Distractor 3}{Distractor 4}` (supporting presentation layout macros `\motcot`, `\haicot`, and `\boncot)`.
     - True/False Questions: `\choiceTF{\True Statement a}{Statement b}{\True Statement c}{Statement d}`.
     - Short-Answer Questions: `\shortans{Numeric answer}`.
     - Solution Environment: `\loigiai{Detailed solution content}`.
     - For graphic elements declared via `\begin{tikzpicture} ... \end{tikzpicture}`.
2. AI Digitization Pipeline Architecture
The digitization pipeline in `backend/routers/digitize.py` and `backend/services/ai_parser.py` must maintain strict separation of concerns across two discrete phases:
- Pass 1 — Layout Segmentation & Image Preprocessing (`layout_segmenter.py`, `crop_service.py`, `image_enhancer.py`): Analyzes the document page structure, determines bounding boxes for individual questions and embedded diagrams, executes automated image cropping, performs image sharpening, and persists assets into `storage/assets/`.

- Pass 2 — Semantic Extraction & Mathematical Normalization (`ai_parser.py`, `deduplication.py`, `tagging_service.py`): Parses content into structured data, normalizes all mathematical expressions into standard LaTeX syntax (`$...$` or `$$...$$`), extracts answer choices, identified keys, and step-by-step explanations, detects duplicated questions, and assigns hierarchical taxonomy tags automatically.
3. Exam Permutation Invariants during Shuffling
Every algorithm within `shuffling_engine.py` must demonstrably pass the formal mathematical verification suite in `scripts/formal_verification_exam_invariants.py`:
- Question Set Conservation: The total count and original content of all questions in every generated variant must form an exact $100\%$ bijection with the master exam.
- Exam Partition Conservation: Questions must never be shuffled across distinct sections (Part I, Part II, Part III, and Part IV must preserve their strict sectional grouping order).
- Anchored Choices Preservation: Position-dependent options (such as "All of the above", "Both A and B are correct", or "None of the above") must either remain fixed in place or have their relative choice references dynamically updated.
- Answer Key Integrity: The answer keys for every question (including individual sub-statements a, b, c, and d in True/False items) after permutation must map bijectively and with absolute precision to the generated answer sheet for that specific exam variant.
4. Standardized Grading Invariants
The scoring engine in `backend/services/grading.py` must enforce the evaluation rubric:
- 4-Choice MCQs: Each correct choice awards a fixed point value per exam configuration (defaulting to $0.25$ points per question).
- True/False Questions: Points per question follow a progressive scale based on the number of correct sub-statements out of 4 (a, b, c, d):
  - 1 correct sub-statement: awards $0.1$ points.
  - 2 correct sub-statements: awards $0.25$ points.
  - 3 correct sub-statements: awards $0.5$ points.
  - All 4 correct sub-statements: awards $1.0$ point.
- Short-Answer Questions: Matches numeric values after normalizing decimal separators (accepting both standard periods . and Vietnamese convention commas ,).
5. Hierarchical Matrix Specification Grid
Reference Document: `docs/SPEC_HIERARCHICAL_MATRIX_GRID_DESIGN.md`.
If the item bank lacks sufficient questions to satisfy a particular cell, the system must return detailed telemetry pinpointing the exact missing cell coordinates and deficit count, rather than raising an unhandled exception or crashing the pipeline.
6. Exam Composer, AI Copilot & Split-View QA
Reference Document: `docs/SPEC_AI_COPILOT_SPLIT_VIEW_REPLACE_AND_QA.md`.
The Composer UI and backend APIs must support:
- Split-View Replace Mode: Side-by-side comparative inspection between the currently selected exam question and candidate replacements (retrieved from the Question Bank or generated on demand by AI matching the identical matrix specification).

- Blind Audit & QA Mode: Automated validation auditing cross-checking question integrity (complete choices, valid answer key, balanced LaTeX delimiter/bracket matching, and complete solution walk-through).
### 5. Coding & Security Standards

#### 5.1. Backend (Python / FastAPI / SQLAlchemy)

* **Type Hints & Validation**: Every function across `services/` and `routers/` must include explicit type annotations. All request bodies and response payloads must be validated through Pydantic schemas defined in `backend/schemas.py`.
* **Database Session Lifecycle Management**: Always inject database sessions via `Depends(get_db)` in API routers; ensure proper session closure or safe rollback whenever an unhandled exception occurs.
* **Error Handling**: Use `HTTPException` with precise standard HTTP status codes (`400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity`) and descriptive error payloads compliant with the contract validations in `tests/test_api_contracts_and_negatives.py`.

#### 5.2. Frontend (Vanilla JavaScript SPA & CSS)

* **Zero External Framework Dependency**: The user interface in `frontend/` is architected using pure Vanilla JavaScript (`app.js`), HTML5 (`index.html`), and CSS3 (`style.css`). Do not introduce React, Vue, Tailwind build steps, or Webpack bundling pipelines that alter the project's static asset serving architecture.
* **DOM Selector Synchronization for E2E Tests**: When modifying `frontend/index.html` or `frontend/static/app.js`, preserve all existing `id`, `class`, and `data-*` attributes asserted by test cases in `tests/test_e2e_*.py`.
* **XSS Prevention**: Always sanitize or escape raw text input before injecting it into `innerHTML`, especially for untrusted content extracted and digitized from external files.

### 6. Mandatory Agent Workflow Protocol

Upon receiving any user request (bug fixing, feature implementation, performance optimization), the Agent must sequentially execute the following four steps:

1. **Step 1 — Analyze & Plan**:
* Inspect `tasks/plan.md`, `tasks/todo.md`, `docs/SOURCE_MAP.md`, and `docs/FEATURE_MAP.md`.
* For any feature, UI element, or API endpoint lookup, always consult `docs/FEATURE_MAP.md` first; inspect source code only if not found in `docs/FEATURE_MAP.md`.
* Review all specification documents directly related to the request within the `docs/` directory (e.g., `SRS_System_Requirements_Specification.md`, `FRD_Functional_Requirements_Document.md`, `NFR_Non_Functional_Requirements.md`, `UC_Use_Case_Specifications.md`).


2. **Step 2 — Incremental & Safe Implementation**:
* Apply modifications to the correct architectural tier in order: Model $\rightarrow$ Schema $\rightarrow$ Service $\rightarrow$ Router $\rightarrow$ Frontend.
* Guarantee zero regression on existing functionality.


3. **Step 3 — Targeted Test & Verify**:
* Execute tests strictly for the features/modules affected by Step 2 or directly dependent on them (consult Section 3.3 for corresponding commands); avoid running the entire test suite indiscriminately unless necessary.
* Write new test cases or update existing ones in `tests/` to properly cover the modified functionality, API endpoint, or resolved edge case.
* If the modification impacts exam shuffling or matrix solving algorithms (`matrix_solver.py`, `shuffling.py`, `shuffling_engine.py`), executing `python scripts/formal_verification_exam_invariants.py` is mandatory.


4. **Step 4 — Documentation Synchronization**:
* Whenever a new API is added or updated, data schemas are modified, business logic workflows are adjusted, or the project structure changes, the Agent must immediately review and synchronize those updates across all documentation in `docs/` and `tasks/`:
* `docs/SOURCE_MAP.md`: Update immediately when adding, removing, or renaming files, modules, routers, services, or restructuring directories.
* `docs/SRS_System_Requirements_Specification.md` & `docs/FRD_Functional_Requirements_Document.md`: Update when introducing new APIs, changing endpoints, request/response payloads, or business rules.
* `docs/UC_Use_Case_Specifications.md` & `docs/BAO_CAO_YEU_CAU_VA_CHUC_NANG_PHAN_MEM_QUESY.md`: Update when adding new features or altering user interaction scenarios.
* `docs/SPEC_AI_COPILOT_SPLIT_VIEW_REPLACE_AND_QA.md` & `docs/SPEC_HIERARCHICAL_MATRIX_GRID_DESIGN.md`: Update when refining deep architectural designs of the AI Copilot/Composer or Exam Matrix subsystems.
* `docs/TEST_Test_Cases_Specification.md` & `docs/TEST_LOOP_COMPREHENSIVE_REPORT.md`: Update when adding new test scenarios or revising acceptance criteria.
* `tasks/plan.md` & `tasks/todo.md`: Update task completion statuses and document technical changes just performed.

### Some-rules
1. You are allowed to create sub-agents to complete requests. There is no limit on the number of sub-agents.
2. Commit your changes once the request is completed. If a pull request does not already exist, create one.
3. Read and use the skills: `karpathy-guidelines`, `doc-coauthoring` and `poteto-mode` for every request.
4. Tra cứu tính năng và mã nguồn: Khi cần tìm kiếm hoặc định vị bất kỳ chức năng nào trong hệ thống, Agent luôn phải truy cập vào `docs/FEATURE_MAP.md` trước để tra cứu nhanh (giao diện, nút bấm, modal, API endpoint, luồng xử lý). Chỉ khi đã tra cứu trong `docs/FEATURE_MAP.md` mà không tìm thấy thông tin cần thiết thì mới tiến hành đọc mã nguồn (source code).