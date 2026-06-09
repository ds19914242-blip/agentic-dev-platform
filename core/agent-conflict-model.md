# Agent Conflict Model

## Definition

Agent Conflict occurs when agents produce different conclusions, recommendations or risk assessments.

## Principle

Agents recommend.

Orchestrator decides.

Governance constrains.

Critical agents may block.

## Agent Outputs

Agents may return:

- finding
- recommendation
- warning
- risk_assessment
- hard_block

## Conflict Examples

- Product Agent approves scope, Architect Agent says scope is too large.
- Engineer Agent proposes implementation, Security Agent flags vulnerability.
- Release Agent recommends deployment, QA Agent reports failing tests.

## Decision Authority

The Orchestrator resolves normal conflicts.

Governance rules constrain Orchestrator decisions.

Human approval is required for high-risk overrides.

## Hard Blocks

Some agents may issue hard blocks.

Examples:

- Security Agent
- Compliance Agent
- Production Safety Agent

A hard block stops execution until:

- issue is resolved
- graph is modified
- human override is approved and recorded

## Rules

1. Agents cannot make final platform decisions.

2. The Orchestrator must record conflicting opinions.

3. Hard blocks must include reasons and evidence.

4. Human overrides must be auditable.

5. Conflicts must be stored as Artifacts or execution history.
