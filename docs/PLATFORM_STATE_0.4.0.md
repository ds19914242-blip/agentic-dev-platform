# Agentic Dev Platform
# Platform State 0.4.0

Date: 2026-06-10

---

## Summary

Platform evolved from a single-run autonomous coding workflow into an epic-driven backlog execution system.

Major focus areas completed:

- Epic decomposition
- Backlog management
- Structured run artifacts
- Product-specific validation
- Improved security classification
- PR lifecycle tracking

---

# Workflow

Current execution flow:

Feature Request
↓
Complexity Classification
↓
Feature OR Epic
↓
Planning
↓
Security Gate
↓
Implementation
↓
Test Generation
↓
Validation
↓
Post Run Review
↓
Confidence Gate
↓
PR Creation

---

# Epic Workflow

Large requests are no longer executed immediately.

Flow:

Feature Request
↓
LLM Complexity Classifier
↓
DECOMPOSE_FIRST
↓
Epic
↓
Task Backlog
↓
Task Execution

Implemented:

- decompose_feature.py
- run_backlog_task.py
- backlog_status.py

---

# Backlog System

Structure:

backlog/
└── epic/
    ├── task-001.md
    ├── task-002.md
    └── task-N.md

Task states:

- todo
- in_progress
- pr_created
- merged
- blocked

Implemented:

- next pending task execution
- task progress reporting
- PR state synchronization

Files:

- run_backlog_task.py
- backlog_status.py
- sync_backlog_prs.py

---

# Validation System

Validation moved from hardcoded TypeScript validation to product-defined validation.

Before:

npx tsc --noEmit

After:

Product Config
↓
Validators
↓
Validation Runner

Example:

validators:
  - typecheck
  - build

Implemented:

- validation_runner.py
- validate_latest_run.py

---

# Structured Artifacts

Platform now separates:

Human-readable output
Machine-readable output

Implemented:

validation.md
validation.json

confidence.md
confidence.json

security-gate.md
security-gate.json

Benefits:

- no markdown parsing
- stable automation contracts
- future API compatibility

---

# Confidence Gate

Confidence gate now reads structured JSON artifacts.

No longer depends on markdown formatting.

Statuses:

- passed
- needs_review
- failed

Artifact:

confidence.json

---

# Security Gate

Security classification improved.

UI pages:

app/*/page.tsx

are now treated as low risk.

Protected areas:

- auth
- permissions
- roles
- schema
- migrations
- billing
- secrets
- deployment

Statuses:

- passed
- passed_with_warning
- needs_approval
- blocked

Artifacts:

security-gate.md
security-gate.json

---

# Test Generation

New stage added:

Implementation
↓
Test Generation
↓
Validation

Implemented:

test_generator.py

Current behavior:

- generates task-specific tests when possible
- skips safely when repository has no test framework

---

# Product Configuration

Products now own their validation strategy.

Example:

products/<product>/config.yaml

Contains:

- repo_path
- validators

Current RSS validators:

- typecheck
- build

---

# Current Product Support

Verified:

- Next.js
- TypeScript

Partial:

- Jest
- Playwright

Not yet implemented:

- Python projects
- Go projects
- Rust projects

Validation architecture supports future expansion.

---

# Known Gaps

1. Security Gate still uses heuristics instead of repository-aware reasoning.

2. Test Generator creates tests only when frameworks already exist.

3. Post Run Review still partially relies on markdown outputs.

4. Backlog merge tracking requires manual sync:

python3 sync_backlog_prs.py

5. Product capability model not implemented.

---

# Next Major Milestone

Version 0.5.0

Planned:

Product Capability Profile

Example:

capabilities:
  build: true
  lint: true
  unit_tests: true
  e2e_tests: false
  i18n: false

This will allow:

- smarter planning
- smarter validation
- smarter test generation

---

# Current Version

0.4.0

Codename:

Epic & Backlog Workflow
