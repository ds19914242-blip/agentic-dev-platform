# Scenario: New Product

## Example Request

Create a new SaaS product from an idea.

## Questions

- Who creates the initial specification?
- Who creates the architecture?
- How are repositories created?
- How are environments provisioned?
- How are tasks generated?
- How is progress tracked?
- How is deployment handled?
- How is memory initialized?

## Expected Outcome

A deployable product is created with repositories, environments and documentation.

---

## Architecture Check

New Product request should use:

- Product Model
- Work Item Model
- Workflow Template Model
- Execution Graph Model
- Agent Registry Model
- Context Model
- Artifact Flow Model
- Tool Model
- Repository Model
- Environment Model
- Approval Model
- Risk Model
- Governance Model
- Memory Model

---

## Main Open Questions

- Who creates the initial Product record?
- Who selects the Workflow Template?
- Who validates the generated Execution Graph?
- How are repositories created?
- How are environments created?
- When does human approval happen?
- What artifacts are required before implementation starts?

---

## Decision: Product Creation

Initial Product record is not created directly by the Human.

Flow:

Human Request
→ Orchestrator
→ Product Agent
→ Draft Product
→ Orchestrator Validation
→ Human Approval
→ Product Created

## Rule

Product Agent creates a Draft Product.

Orchestrator validates the Draft Product.

Human approves before the Product becomes active.

---

## Decision: Workflow Template Selection

The Orchestrator selects the initial Workflow Template.

Flow:

Human Request
→ Orchestrator
→ Select Workflow Template
→ Planner Agent validates template choice
→ Orchestrator adapts template
→ Execution Graph Draft

## Rule

The Orchestrator selects the Workflow Template.

Planner Agent validates whether the selected template fits the request.

Human approval is required only when:

- template risk is high
- request is ambiguous
- production systems may be affected
- new infrastructure or paid services are required

---

## Decision: Execution Graph Validation

The generated Execution Graph must be reviewed before execution.

Flow:

Orchestrator
→ Execution Graph Draft
→ Planner Agent Review
→ Architect Agent Review
→ Risk Evaluation
→ Approved Execution Graph

## Review Goals

Planner Agent validates:

- completeness
- missing stages
- missing dependencies

Architect Agent validates:

- architecture impact
- technical feasibility
- implementation sequencing

Risk Evaluation validates:

- approval gates
- production impact
- security impact
- cost impact

## Rule

Execution Graphs must be reviewed before execution.

High-risk graphs require human approval.

## Decision: Repository Creation

Repositories are not created directly by the Human.

Flow:

Approved Product
→ Repository Planner Agent
→ Repository Plan
→ Orchestrator Validation
→ Repository Provisioning
→ Repository Created

## Repository Plan

The Repository Plan defines:

- repository structure
- repository names
- ownership
- branching strategy
- technology stack
- CI/CD requirements

## Rule

Repository creation must be based on an approved Product.

Repository plans must be stored as Artifacts.

Repository creation must be recorded in execution history.

## Decision: Environment Creation

Environments are created from an approved Environment Plan.

Flow:

Approved Product
→ Environment Planner Agent
→ Environment Plan
→ Orchestrator Validation
→ Environment Provisioning
→ Environment Created

## Environment Plan

The Environment Plan defines:

- local environment
- development environment
- staging environment
- production environment

It also defines:

- deployment platform
- secrets strategy
- monitoring requirements
- backup strategy
- rollback strategy

## Rule

Environment creation must be based on an approved Product.

Environment plans must be stored as Artifacts.

Production environments require approval before provisioning.

## Decision: Implementation Readiness

Implementation may not begin until required artifacts exist.

## Required Artifacts Before Implementation

- Product Specification
- Architecture Proposal
- Repository Plan
- Environment Plan
- Approved Execution Graph
- Risk Assessment

## Optional Artifacts

- Market Research
- Competitive Analysis
- Cost Estimate
- Security Review

## Readiness Validation

Before implementation starts:

Orchestrator
→ Readiness Check
→ Validation Result

## Rule

Implementation Agents may not start until readiness validation passes.

Missing required artifacts block execution.

## Decision: Task Generation

Tasks are generated from approved planning artifacts.

Flow:

Product Specification
→ Architecture Proposal
→ Planner Agent
→ Task Breakdown
→ Orchestrator Validation
→ Execution Graph Update

## Task Breakdown

Task Breakdown defines:

- implementation tasks
- dependencies
- required agents
- required tools
- expected artifacts
- validation steps
- risk level per task

## Rule

Planner Agent creates the Task Breakdown.

Orchestrator validates it.

Task Breakdown must be stored as an Artifact.

Execution Graph is updated based on the approved Task Breakdown.

## Remaining Open Questions

- Who creates repositories and environments in the real world?
- How are secrets managed?
- How are costs tracked?
- How are model providers selected?
- How are long-running executions resumed?
- How are failed executions recovered?
- How are multiple products coordinated?
- How are execution graphs versioned?
- How are workflow templates versioned?
- How are agent versions managed?
