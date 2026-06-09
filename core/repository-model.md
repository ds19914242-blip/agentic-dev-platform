# Repository Model

## Definition

A Repository is a source code location managed by the system.

Repositories contain code that agents can analyze, modify, test and release.

## Repository Types

- local repository
- GitHub repository
- GitLab repository

## Repository Fields

Each repository must define:

- id
- name
- url
- local_path
- default_branch
- product_owner
- stack
- environments
- access_level

## Repository Access

Repository access is controlled by the Orchestrator.

Agents cannot access repositories directly.

## Allowed Actions

- read code
- analyze structure
- create branch
- modify files
- run tests
- create pull request

## Restricted Actions

Require approval:

- merge pull request
- delete branch
- delete files
- change auth logic
- modify production config
- change database schema

## Rules

All repository changes must be traceable.

Every code modification must be connected to a Work Item.
