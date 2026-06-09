# Artifact Flow Model

## Definition

Artifact Flow defines how outputs from one node become inputs for other nodes.

## Purpose

Agents must not rely on hidden knowledge.

All important outputs must be passed through Artifacts.

## Flow

Agent
→ Artifact
→ Orchestrator
→ Execution Graph
→ Next Agent

## Examples

Architect Agent
→ Architecture Proposal

Backend Engineer Agent
receives
→ Architecture Proposal

QA Agent
receives
→ Test Plan
→ Implementation Summary

Release Agent
receives
→ Validation Reports
→ Deployment Results

## Rules

Agents communicate through Artifacts.

Agents do not communicate directly.

Important decisions must be stored as Artifacts.

Artifacts may be reused across multiple nodes.

Artifact history must be preserved.
