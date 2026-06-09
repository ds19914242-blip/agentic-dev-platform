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
