# System Interactions

## Core Principle

The Orchestrator is the central control system.

Agents do not control the platform.

Agents execute work on behalf of the Orchestrator.

---

## Main Flow

Human
→ Orchestrator
→ Work Item
→ Execution Graph
→ Agent Execution
→ Results
→ Orchestrator
→ Human

---

## Entity Interactions

### Human ↔ Orchestrator

Humans communicate only with the Orchestrator.

Humans do not communicate directly with agents.

### Orchestrator ↔ Work Item

The Orchestrator creates, updates and closes Work Items.

### Orchestrator ↔ Execution Graph

The Orchestrator creates and manages Execution Graphs.

### Orchestrator ↔ Agents

The Orchestrator selects, starts, stops and coordinates agents.

### Orchestrator ↔ Memory

The Orchestrator reads and writes memory.

### Orchestrator ↔ Repository

The Orchestrator provides repository access to agents.

### Orchestrator ↔ Environment

The Orchestrator controls environment access.

### Orchestrator ↔ Tools

The Orchestrator manages tool access.

### Orchestrator ↔ Approval

The Orchestrator requests human approvals when required.

---

## Control Rules

1. Agents cannot create Work Items.

2. Agents cannot launch other agents.

3. Agents cannot bypass approval requirements.

4. Agents cannot directly modify production environments.

5. Agents cannot access secrets unless explicitly authorized.

6. All actions must be traceable through the Orchestrator.

7. All execution history must be stored.

8. Memory updates must be recorded.

9. Tool usage must be tracked.

10. Human approval overrides agent decisions.
