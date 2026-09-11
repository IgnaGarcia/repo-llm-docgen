# [Project Name]

> One-sentence tagline: what the system does and for whom.

**Repository:** [repository name and/or URL]
**Stack:** [main language, framework, database — inferred from code]
**Version:** [last tag or inferred from repository]

---

## Overview

Two to four paragraphs covering:

- What problem this system solves and in what domain.
- What kind of application it is (REST API, background worker, etc.) and its main capabilities beyond basic CRUD.
- Who consumes it and how (frontend clients, third-party integrations, internal services).

---

## Architecture

### Architectural Pattern

Name and describe the architectural pattern used (MVC, Clean Architecture, Hexagonal, layered, etc.). Explain how it shapes the codebase structure and why it is appropriate for this system. Use the terminology of the identified pattern consistently throughout the document (e.g. handler, middleware, repository, use case, controller, service).

### Layer Overview

For each layer or major structural group, one sentence describing its responsibility and its position in the dependency chain.

- **[Layer name]:** Responsibility and what it depends on.
- **[Layer name]:** Responsibility and what it depends on.

### Request Flow

Describe how a typical request travels through the system from entry point to response. Walk through each layer it touches in order, naming the concrete components involved. This should give the reader a end-to-end picture of how the layers interact and what each one contributes to processing the request.

> Example: A `POST /orders` request enters through the router, is validated by the `OrderMiddleware`, delegated to `OrderController`, which calls `OrderService` to apply business rules, which in turn calls `OrderRepository` to persist the result, and returns a structured response through a shared response formatter.

### Directory Structure

Annotated overview of the top-level directory structure. For each significant folder, explain what it contains and why. Reference actual folder names from the repository.

```
[project-root]/
├── [folder]/       # What lives here and why
├── [folder]/       # What lives here and why
└── [file]          # What this file configures
```

---

## Modules

### Module Inventory

List every module or layer identified in the codebase, even ones only briefly covered below. Every row here must have a corresponding block in the detail section that follows.

| Module | Role (one line) |
| ------ | ---------------- |
| [Module Name] | One-line responsibility |

### Module Detail

For each module or layer listed above, repeat the block below. Use the terminology of the architectural pattern identified above.

### [Module Name]

**Role:** One sentence on the responsibility of this module within the system.

**Responsibilities:**

- What it does (concrete actions, not vague descriptions).
- What decisions it makes or delegates.
- What it must not do (boundary definition).

**Dependencies:**

- Modules or services it depends on.
- Modules or services that depend on it.

**Key components:**

#### [`filename.ext`] [Component / Class name]

- **What it does:** Concrete description of the actions this component performs.
- **Why it exists:** The design rationale — what problem it solves or what responsibility it isolates.
- **Input:** What it receives (type, structure).
- **Output:** What it returns or produces.
- **Key functions / methods:** List the main functions or methods with a one-line description each.
    - `functionName(params)` — what it does.
- **Notes:** Any relevant behavior, edge cases, or design decisions worth highlighting.

---

## Data Model

### Entity Summary

List every entity/model found in the codebase, even ones not expanded in detail below. Every row here must have a corresponding block in Entities below.

| Entity | File | Key fields |
| ------ | ---- | ---------- |
| [EntityName] | `path/to/file.ext` | field1, field2, field3 |

### Entities

For each entity listed above, list its key fields and their purpose. Focus on fields that carry business meaning, not boilerplate (id, timestamps). Reference the source file where the entity is defined.

#### [Entity Name] — [`path/to/model/file.ext`]

| Field   | Type   | Description                            |
| ------- | ------ | -------------------------------------- |
| [field] | [type] | What it represents and any constraints |

**Relationships:**

- Describe how this entity relates to others (one-to-many, belongs-to, etc.).

**Example:**

```json
{
    "field": "example value matching the real model"
}
```

### Entity Relationship Summary

Narrative description of how the main entities relate to each other and what the data model represents as a whole.

---

## API Reference

### Authentication & Authorization

- **Mechanism:** How authentication works (JWT, session, OAuth, API key, etc.).
- **How to authenticate:** Step-by-step for obtaining and using credentials.
- **Roles and permissions:** What roles exist and what each one can access.

```json
// Example: Authorization header
{
    "Authorization": "Bearer <token>"
}
```

### Endpoint Inventory

List every endpoint found in the router/controller files, even ones not detailed below. Build the full path by combining the route-group prefix (if routes are mounted under a common path) with each route's own sub-path, and mark whether authorization is enforced at the route-group level rather than assuming it is per-route.

| Method | Path | Group / File | Auth |
| ------ | ---- | ------------- | ---- |
| [METHOD] | `/path/to/endpoint` | `path/to/router/file.ext` | Yes/No — role |

### Endpoints

For each logical group of endpoints listed above, repeat the block below. Reference the router or controller file where these routes are defined.

#### [Resource or Feature Group] — [`path/to/router/file.ext`]

Brief description of what this group of endpoints manages.

---

**[METHOD] `/path/to/endpoint`**
Description of what this endpoint does and what it returns.

- **Auth required:** Yes / No — [role required if applicable]
- **Path params:** `[param]` — description
- **Query params:** `[param]` — description, default value
- **Request body:**

```json
{
    "field": "type — description"
}
```

- **Success response** `[status code]`:

```json
{
    "field": "example value"
}
```

- **Error responses:** `[status]` — when this happens.

---

## External Integrations

For each external dependency, describe what it is, why the system uses it, and how it interacts with it. Reference the file or module that implements the integration.

### [Integration Name] — [`path/to/integration/file.ext`]

- **Type:** Database / Third-party API / Cloud service / Message broker / etc.
- **Purpose:** What the system uses it for.
- **Interaction:** How the system communicates with it (SDK, HTTP, ORM, etc.).

---

## Error Handling & Validations

Describe the general approach to error handling: where errors are caught, how they are formatted in responses, and what validation strategy is used for incoming data. Reference the middleware or utility file responsible if one exists.

---

## Glossary

Define domain-specific or project-specific terms that appear in the codebase or this document. Especially useful for onboarding new developers.

| Term   | Definition                                  |
| ------ | ------------------------------------------- |
| [Term] | What it means in the context of this system |
