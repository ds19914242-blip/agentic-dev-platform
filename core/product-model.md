# Product Model

## Definition

A Product is a software product managed, created or improved by the system.

The system may manage existing products or create new products.

## Purpose

Products provide business and technical context for Work Items, Repositories, Environments, Memory and Releases.

## Product Fields

Each Product must define:

- id
- name
- description
- vision
- target_users
- business_model
- current_status
- repositories
- environments
- roadmap
- architecture_summary
- key_features
- business_rules
- constraints
- risks
- owner
- created_at
- updated_at

## Product Status

- idea
- planning
- development
- local
- staging
- production
- maintenance
- archived

## Product Relationships

A Product may have:

- many Work Items
- many Repositories
- many Environments
- many Releases
- many Incidents
- many Memory records
- many Artifacts

## Rules

Every product-related Work Item must be linked to a Product.

Every Repository should be linked to a Product.

Every Environment should be linked to a Product.

Product Memory must be stored separately from Global Memory.

## New Product Creation

When creating a new product, the system must produce:

- product specification
- architecture proposal
- repository plan
- environment plan
- implementation roadmap
- initial release plan
