# Risk Model

## Definition

Risk is the potential impact of an action on code, data, users, infrastructure or cost.

The system must classify risk before executing important actions.

## Risk Levels

### Low Risk

Safe or reversible actions.

Examples:

- read files
- analyze repository
- generate plan
- write documentation
- run local tests

### Medium Risk

Actions that modify code or configuration but are usually reversible.

Examples:

- edit source files
- create branch
- update dependencies
- change non-production config
- run local migrations

### High Risk

Actions that may affect users, data, security or production systems.

Examples:

- deploy to production
- change database schema
- modify authentication
- modify billing logic
- access secrets
- delete files
- merge pull request
- change infrastructure

## Risk Evaluation

The Orchestrator must evaluate risk before tool execution.

Risk evaluation should consider:

- environment
- repository
- affected files
- action type
- data impact
- user impact
- reversibility
- security impact
- cost impact

## Risk Rules

1. Low-risk actions may proceed automatically.

2. Medium-risk actions may proceed if allowed by policy.

3. High-risk actions require human approval.

4. Unknown risk must be treated as high risk.

5. Risk level must be recorded in execution history.

## Escalation

The Orchestrator must escalate when:

- risk is high
- risk is unknown
- agents disagree
- production is affected
- sensitive data may be involved
