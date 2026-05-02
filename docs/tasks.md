# Tasks: A2Z DSA Learning System - Production Completion

**Input**: Design documents from `docs/plans/01-07/` and `docs/plan.md`
**Prerequisites**: plan.md (required), existing plans (data-quality, security-robustness, frontend-ux, testing-quality, api-backend, documentation, deployment)

**Tests**: This task list INCLUDES test tasks - comprehensive testing is a key requirement for production readiness.

**Organization**: Tasks are grouped by work area (Security, Data Quality, API/Backend, Testing, Frontend, Documentation, Deployment) to enable independent implementation of each area.

## Format: `[ID] [P?] [Area] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Area]**: Which work area this task belongs to (SEC, DATA, API, TEST, FE, DOC, DEP)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `api/` at repository root
- **Frontend**: `frontend/` at repository root
- **Scripts**: `scripts/` at repository root
- **Tests**: `tests/` at repository root
- **Data**: `data/` at repository root
- **Docs**: `docs/` at repository root
- **Deploy**: `deploy/` at repository root

---

## Phase 1: Setup & Configuration (Shared Infrastructure)

**Purpose**: Project initialization for testing, linting, and production configuration

- [ ] T001 Verify .gitignore includes .env and sensitive files in .gitignore
- [ ] T002 [P] Setup pytest configuration in pyproject.toml
- [ ] T003 [P] Setup ruff configuration for Python linting in pyproject.toml
- [ ] T004 [P] Create .env.example template with all required environment variables
- [ ] T005 [P] Create production .env template in .env.production
- [ ] T006 [P] Setup ESLint configuration for frontend in frontend/.eslintrc.js

---

## Phase 2: Foundational Security (Blocking Prerequisites)

**Purpose**: Critical security infrastructure that MUST be complete before other features

**CRITICAL**: No user-facing work can proceed safely until this phase is complete

- [ ] T007 Create api/config.py for environment configuration and validation
- [ ] T008 [P] Create code validation function validate_code_for_execution in api/services.py
- [ ] T009 [P] Add Docker sandboxing for code execution in api/services.py
- [ ] T010 Add rate limiting middleware to api/main.py using slowapi
- [ ] T011 Create global exception handler with sanitized error responses in api/main.py
- [ ] T012 Setup structured logging in api/logging_config.py
- [ ] T013 Add request logging middleware in api/main.py

**Checkpoint**: Security foundation ready - safe to proceed with API and data work

---

## Phase 3: User Story 1 - Secure Code Execution (Priority: P1) 🎯 MVP

**Goal**: Users can execute Python code safely in an isolated sandbox environment

**Independent Test**: Run code with dangerous patterns (imports, file access) and verify they are blocked; run valid code and verify it executes correctly

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T014 [P] [SEC] Test dangerous imports are blocked in tests/test_security.py
- [ ] T015 [P] [SEC] Test path traversal is blocked in tests/test_security.py
- [ ] T016 [P] [SEC] Test rate limiting works in tests/test_security.py
- [ ] T017 [P] [SEC] Test code execution timeout in tests/test_code_execution.py
- [ ] T018 [SEC] Test syntax error handling in tests/test_code_execution.py
- [ ] T019 [SEC] Test runtime error handling in tests/test_code_execution.py

### Implementation for User Story 1

- [ ] T020 [SEC] Implement Docker container isolation in api/services.py
- [ ] T021 [SEC] Add resource limits (memory, CPU) to code execution in api/services.py
- [ ] T022 [SEC] Implement input validation for dangerous patterns in api/services.py
- [ ] T023 [SEC] Add timeout handling with cleanup in api/services.py
- [ ] T024 [SEC] Integrate sandboxed execution with /api/questions/{id}/run endpoint in api/routers/questions.py
- [ ] T025 [SEC] Add execution error mapping to user-friendly messages in api/services.py

**Checkpoint**: Code execution is secure and ready for production use

---

## Phase 4: User Story 2 - Data Quality & Enrichment (Priority: P1)

**Goal**: All questions have valid test cases and complete metadata

**Independent Test**: Run dataset validation script - all 361 questions have 3+ valid tests, no placeholders remain

### Tests for User Story 2

- [ ] T026 [P] [DATA] Test all questions have required fields in tests/test_dataset.py
- [ ] T027 [P] [DATA] Test minimum test cases requirement in tests/test_dataset.py
- [ ] T028 [DATA] Test no placeholder tests remain in tests/test_dataset.py

### Implementation for User Story 2

- [ ] T029 [P] [DATA] Create placeholder test identifier script in scripts/identify_placeholder_tests.py
- [ ] T030 [P] [DATA] Create test case generator script in scripts/generate_test_cases.py
- [ ] T031 [DATA] Create test case validator script in scripts/validate_test_cases.py
- [ ] T032 [DATA] Enhance enricher with resume/control flags in scripts/enrich_questions_with_gemini.py
- [ ] T033 [DATA] Add retry logic with exponential backoff to enricher in scripts/enrich_questions_with_gemini.py
- [ ] T034 [DATA] Store generated Python solutions to data/solutions/{id}.py in scripts/enrich_questions_with_gemini.py
- [ ] T035 [DATA] Create dataset validation script in scripts/validate_dataset.py
- [ ] T036 [DATA] Create path normalization script in scripts/normalize_paths.py
- [ ] T037 [DATA] Run enrichment on 100 highest-priority questions using enriched enricher
- [ ] T038 [DATA] Generate and validate test cases for all 361 questions
- [ ] T039 [DATA] Run full dataset validation and fix any failures

**Checkpoint**: Dataset is complete and validated, ready for AI enrichment at scale

---

## Phase 5: User Story 3 - Study Plan API (Priority: P2)

**Goal**: Users can generate and retrieve personalized study plans

**Independent Test**: Call /api/study-plan/generate, verify plan is created; call /api/study-plan/today, verify today's tasks are returned

### Tests for User Story 3

- [ ] T040 [P] [API] Test study plan generation in tests/test_api_planning.py
- [ ] T041 [P] [API] Test today's plan retrieval in tests/test_api_planning.py

### Implementation for User Story 3

- [ ] T042 [API] Create StudyPlanService class in api/services.py
- [ ] T043 [API] Implement get_study_plan method in api/services.py
- [ ] T044 [API] Implement get_today_plan method in api/services.py
- [ ] T045 [API] Implement generate_plan method in api/services.py
- [ ] T046 [API] Add POST /api/study-plan/generate endpoint in api/main.py
- [ ] T047 [API] Update GET /api/study-plan endpoint in api/main.py
- [ ] T048 [API] Update GET /api/study-plan/today endpoint in api/main.py
- [ ] T049 [API] Enhance rebuild endpoint to trigger plan generation in api/main.py

**Checkpoint**: Study plans work end-to-end

---

## Phase 6: User Story 4 - Frontend UX & Mobile (Priority: P2)

**Goal**: Application works on mobile devices with accessible, polished UX

**Independent Test**: Open application on mobile device (375px width); all pages render correctly; keyboard navigation works

### Tests for User Story 4

- [ ] T050 [P] [FE] Test utility functions in frontend/assets/js/utils.test.js
- [ ] T051 [FE] Setup Vitest configuration in frontend/vitest.config.js

### Implementation for User Story 4

- [ ] T052 [P] [FE] Create responsive.css with mobile breakpoints in frontend/assets/css/responsive.css
- [ ] T053 [P] [FE] Enhance loading overlay with timeout behavior in frontend/assets/js/ui/loading.js
- [ ] T054 [P] [FE] Create centralized config.js in frontend/assets/js/config.js
- [ ] T055 [P] [FE] Add favicon files to frontend/
- [ ] T056 [FE] Fix favicon route in api/main.py
- [ ] T057 [FE] Improve error toast messages in frontend/assets/js/ui/toast.js
- [ ] T058 [FE] Add keyboard navigation to question cards in frontend/assets/js/questions.js
- [ ] T059 [FE] Fix Chart.js global App reference in frontend/assets/js/charts.js
- [ ] T060 [FE] Add ARIA attributes to components in frontend/components/*.html
- [ ] T061 [FE] Add reduced motion support in frontend/assets/css/responsive.css
- [ ] T062 [FE] Test and fix mobile layouts across all pages

**Checkpoint**: Application is mobile-responsive and accessible

---

## Phase 7: User Story 5 - API Backend Completion (Priority: P1)

**Goal**: All API endpoints return proper responses with error handling

**Independent Test**: Test all API endpoints from docs/plans/05-api-backend-plan.md; all return valid JSON or proper error codes

### Tests for User Story 5

- [ ] T063 [P] [API] Test questions list endpoint in tests/test_api_questions.py
- [ ] T064 [P] [API] Test single question endpoint in tests/test_api_questions.py
- [ ] T065 [P] [API] Test question filtering in tests/test_api_questions.py
- [ ] T066 [P] [API] Test questions search in tests/test_api_questions.py
- [ ] T067 [API] Test 404 for non-existent question in tests/test_api_questions.py

### Implementation for User Story 5

- [ ] T068 [API] Verify all static mounts work in api/main.py
- [ ] T069 [API] Create ErrorResponse and ValidationErrorResponse models in api/models.py
- [ ] T070 [API] Add validation exception handler in api/main.py
- [ ] T071 [API] Add value error handler in api/main.py
- [ ] T072 [API] Add not found error handler in api/main.py
- [ ] T073 [API] Complete Pydantic models for all endpoints in api/models.py
- [ ] T074 [API] Add path normalization to responses in api/services.py
- [ ] T075 [API] Tighten CORS configuration for production in api/main.py
- [ ] T076 [API] Sanitize AI chat inputs in api/routers/ai.py
- [ ] T077 [API] Add endpoint-specific error handling in api/routers/questions.py

**Checkpoint**: API is production-ready with comprehensive error handling

---

## Phase 8: User Story 6 - Testing Infrastructure (Priority: P1)

**Goal**: Comprehensive test coverage with CI/CD automation

**Independent Test**: Run pytest - all tests pass with 80%+ coverage; run ruff check - zero errors

### Tests for User Story 6

- [ ] T078 [P] [TEST] Write AI chat tests in tests/test_ai_chat.py
- [ ] T079 [TEST] Create dataset regression tests in tests/test_dataset.py

### Implementation for User Story 6

- [ ] T080 [P] [TEST] Run ruff check on api/ and scripts/
- [ ] T081 [P] [TEST] Run ruff format on api/ and scripts/
- [ ] T082 [P] [TEST] Run ESLint on frontend/assets/js/
- [ ] T083 [TEST] Setup ESLint package.json scripts in frontend/package.json
- [ ] T084 [TEST] Create GitHub Actions test workflow in .github/workflows/test.yml
- [ ] T085 [TEST] Verify test coverage meets 80% threshold for api/ and scripts/

**Checkpoint**: CI/CD pipeline runs tests on every commit

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements across multiple work areas

- [ ] T086 [P] [DOC] Create getting-started.md in docs/
- [ ] T087 [P] [DOC] Create developer-setup.md in docs/
- [ ] T088 [P] [DOC] Create data-pipeline.md in docs/
- [ ] T089 [P] [DOC] Create data-schema.md in docs/
- [ ] T090 [P] [DOC] Update api-reference.md in docs/
- [ ] T091 [P] [DOC] Create troubleshooting.md in docs/
- [ ] T092 [P] [DOC] Create CONTRIBUTING.md in repository root
- [ ] T093 [DOC] Update main README.md with complete documentation
- [ ] T094 [DOC] Verify all documentation links work
- [ ] T095 [P] [DEP] Create Dockerfile in repository root
- [ ] T096 [P] [DEP] Create docker-compose.yml in repository root
- [ ] T097 [DEP] Create render.yaml for Render.com deployment
- [ ] T098 [DEP] Create systemd service file in deploy/a2z-dsa.service
- [ ] T099 [DEP] Create nginx configuration in deploy/a2z-dsa.nginx
- [ ] T100 [DEP] Create server setup script in deploy/setup-server.sh
- [ ] T101 [DEP] Create GitHub Actions deploy workflow in .github/workflows/deploy.yml
- [ ] T102 [DEP] Run post-deployment verification checklist
- [ ] T103 [DATA] Create cleanup script in scripts/cleanup_dataset.py
- [ ] T104 [API] Add health check endpoint /health in api/main.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Security Foundation (Phase 2)**: Depends on Setup completion - BLOCKS all API/data work
- **User Stories (Phase 3-8)**: Can proceed in parallel after Security Foundation
  - User Story 1 (Secure Code Execution): Must complete before any code execution features
  - User Story 2 (Data Quality): Independent of other stories
  - User Story 3 (Study Plan API): Depends on foundational API work
  - User Story 4 (Frontend UX): Independent - can work in parallel with backend
  - User Story 5 (API Backend): Depends on Security Foundation
  - User Story 6 (Testing): Can run alongside implementation, tests written first (TDD)
- **Polish (Phase 9)**: Depends on core features being complete

### User Story Dependencies

- **US1 (Secure Code Execution)**: BLOCKING - must complete before any code execution is safe
- **US2 (Data Quality)**: Independent - can proceed in parallel
- **US3 (Study Plan API)**: Requires foundational API infrastructure
- **US4 (Frontend UX)**: Independent - frontend can be polished while backend work continues
- **US5 (API Backend)**: Requires Security Foundation (Phase 2)
- **US6 (Testing)**: Tests should be written FIRST (TDD), then implementation

### Parallel Opportunities

- Phase 1: All setup tasks marked [P] can run in parallel
- Phase 2: T007, T008, T009 can be done in parallel
- Phase 3: All tests (T014-T019) can be written in parallel
- Phase 4: T029, T030 can be done in parallel; dataset tests independent of enrichment
- Phase 5: Tests can be written while implementing service
- Phase 6: Frontend CSS/JS tasks (T052-T055) are independent
- Phase 7: All API tests (T063-T067) can be written in parallel
- Phase 9: Documentation tasks (T086-T094) can be done in parallel; deployment files (T095-T098) can be created in parallel

---

## Parallel Example: Security Foundation (Phase 2)

```bash
# Launch security foundation tasks in parallel:
Task: "Create code validation function validate_code_for_execution in api/services.py"
Task: "Add Docker sandboxing for code execution in api/services.py"
Task: "Add rate limiting middleware to api/main.py using slowapi"
```

---

## Parallel Example: API Tests (Phase 7)

```bash
# Launch all API tests together:
Task: "Test questions list endpoint in tests/test_api_questions.py"
Task: "Test single question endpoint in tests/test_api_questions.py"
Task: "Test question filtering in tests/test_api_questions.py"
Task: "Test questions search in tests/test_api_questions.py"
```

---

## Parallel Example: Documentation (Phase 9)

```bash
# Launch all documentation tasks together:
Task: "Create getting-started.md in docs/"
Task: "Create developer-setup.md in docs/"
Task: "Create data-pipeline.md in docs/"
Task: "Create troubleshooting.md in docs/"
```

---

## Implementation Strategy

### MVP First (Critical Path Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Security Foundation (CRITICAL)
3. Complete Phase 3: Secure Code Execution (US1) - MVP core feature
4. **STOP and VALIDATE**: Code execution is safe and works
5. Deploy to production if ready

### Incremental Delivery (Recommended)

1. Setup + Security Foundation → Foundation ready
2. Add Secure Code Execution → Test → Deploy (Security MVP!)
3. Add Data Quality improvements → Test → Deploy
4. Add Study Plan API → Test → Deploy
5. Add Frontend UX improvements → Test → Deploy
6. Complete API Backend → Test → Deploy
7. Full Testing + CI/CD → Test → Deploy
8. Documentation + Deployment → Deploy to production

Each phase adds value without breaking previous work.

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Security Foundation together
2. Once Security Foundation is done:
   - Developer A: Data Quality (US2)
   - Developer B: Study Plan API (US3)
   - Developer C: Frontend UX (US4)
3. After core features:
   - Developer A: API Backend completion (US5)
   - Developer B: Testing infrastructure (US6)
4. Everyone: Documentation and deployment

---

## Task Summary by Area

| Area | Task Count | Task IDs |
|------|------------|----------|
| Setup | 6 | T001-T006 |
| Security (SEC) | 19 | T007, T008-T025, T076 |
| Data Quality (DATA) | 14 | T026-T039, T103 |
| API Backend (API) | 22 | T040-T049, T063-T077, T056, T068-T075 |
| Testing (TEST) | 8 | T014-T019, T078-T085 |
| Frontend (FE) | 11 | T050-T062 |
| Documentation (DOC) | 9 | T086-T094 |
| Deployment (DEP) | 7 | T095-T102, T104 |
| **Total** | **104** | |

---

## MVP Scope (First Production Release)

**Minimum Viable Product = Phases 1, 2, 3 + Deployment basics**

- Setup (6 tasks)
- Security Foundation (7 tasks: T007-T013)
- Secure Code Execution (12 tasks: T014-T025)
- Basic Deployment (3 tasks: T004, T095, T102)
- Health Check (1 task: T104)

**Total MVP: 29 tasks**

This gets you a secure code execution platform that can be deployed to production.

---

## Success Criteria by Phase

### Phase 1: Setup
- [ ] .gitignore properly excludes sensitive files
- [ ] pytest runs without errors
- [ ] ruff check configuration exists
- [ ] .env.example documents all required variables

### Phase 2: Security Foundation
- [ ] Config class validates environment on startup
- [ ] Dangerous code patterns are rejected
- [ ] Rate limiting is configured on sensitive endpoints
- [ ] Error responses don't expose stack traces
- [ ] Logging captures all API activity

### Phase 3: Secure Code Execution
- [ ] Code runs in isolated Docker container
- [ ] Memory and CPU limits are enforced
- [ ] Network access is blocked
- [ ] File system access is blocked
- [ ] Timeout is enforced with cleanup
- [ ] All security tests pass

### Phase 4: Data Quality
- [ ] All 361 questions have 3+ valid tests
- [ ] No placeholder strings remain
- [ ] Dataset validation passes
- [ ] AI enrichment can resume after failure

### Phase 5: Study Plan API
- [ ] Study plan generation works
- [ ] Today's tasks endpoint returns valid data
- [ ] Plans persist to file

### Phase 6: Frontend UX
- [ ] Works on mobile (375px+)
- [ ] Loading overlays have timeout behavior
- [ ] All errors show user-friendly messages
- [ ] Keyboard navigation works
- [ ] Reduced motion preference is respected

### Phase 7: API Backend
- [ ] All endpoints return valid JSON
- [ ] Error responses are structured
- [ ] Static files serve without 404s
- [ ] CORS is properly configured
- [ ] All API tests pass

### Phase 8: Testing
- [ ] pytest runs with 80%+ coverage
- [ ] ruff check passes with 0 errors
- [ ] ESLint passes for frontend
- [ ] CI/CD pipeline runs on commits

### Phase 9: Polish & Deployment
- [ ] Documentation is complete
- [ ] Docker container builds successfully
- [ ] Application deploys to production
- [ ] Health check responds
- [ ] SSL certificate is valid

---

## Notes

- Tests are written FIRST (TDD) - ensure they FAIL before implementation
- Security tasks are highest priority - complete Phase 2 before any user-facing features
- [P] tasks can run in parallel (different files, no dependencies)
- [Area] labels map tasks to specific work areas for traceability
- Each area should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
- Run tests and linting before committing
- Focus on MVP (Phases 1-3) for first production release
- Avoid: vague tasks, same file conflicts, cross-area dependencies that break independence
