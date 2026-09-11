# [Project Name]

> One-sentence tagline: what the system does and for whom.

|                  |                                   |
| ---------------- | --------------------------------- |
| **Repository**   | [name / URL]                      |
| **Stack**        | [language · framework · database] |
| **Version**      | [last tag or inferred]            |
| **Architecture** | [pattern name]                    |

---

## Overview

Two to four paragraphs covering what problem this system solves and in what domain, what kind of application it is and its main capabilities beyond basic CRUD, and who consumes it and how.

---

## Architecture

### Layer Map

| Layer        | Responsibility | Depends on      | Depended on by  |
| ------------ | -------------- | --------------- | --------------- |
| [Layer name] | What it does   | [layer/service] | [layer/service] |
| [Layer name] | What it does   | [layer/service] | [layer/service] |

### Request Flow

| Step | Component                  | Action                    |
| ---- | -------------------------- | ------------------------- |
| 1    | `[component]` — `file.ext` | What happens at this step |
| 2    | `[component]` — `file.ext` | What happens at this step |
| 3    | `[component]` — `file.ext` | What happens at this step |

### Directory Structure

| Path        | Contents                  |
| ----------- | ------------------------- |
| `[folder]/` | What lives here and why   |
| `[folder]/` | What lives here and why   |
| `[file]`    | What this file configures |

---

## Modules

### Module Inventory

List every module or layer identified in the codebase, even ones only briefly covered below. Every row here must have a corresponding block in the detail section that follows.

| Module | Role |
| ------ | ---- |
| [Module Name] | One-line responsibility |

### Module Detail

For each module listed above, fill in the summary table and the component table below.

### [Module Name]

**Role:** One sentence on the responsibility of this module within the system.

| Attribute               | Detail                                |
| ----------------------- | ------------------------------------- |
| **What it does**        | Concrete actions this module performs |
| **What it must not do** | Boundary definition                   |
| **Depends on**          | Modules or services it calls          |
| **Used by**             | Modules or services that call it      |

#### Components

| File           | Component | What it does                    | Why it exists                                      | Key methods                    |
| -------------- | --------- | ------------------------------- | -------------------------------------------------- | ------------------------------ |
| `filename.ext` | ClassName | Concrete description of actions | Design rationale — what responsibility it isolates | `method(params)` — description |

---

## Data Model

### Entity Summary

| Entity       | File               | Key fields             | Relationships                |
| ------------ | ------------------ | ---------------------- | ---------------------------- |
| [EntityName] | `path/to/file.ext` | field1, field2, field3 | belongs to [X], has many [Y] |

### Entity Detail

Every entity listed in Entity Summary above must have a corresponding block here — do not omit any, even if some fields must be abbreviated for space. For each entity, list its fields and include a JSON example.

#### [Entity Name] — `path/to/model/file.ext`

| Field   | Type   | Description                            |
| ------- | ------ | -------------------------------------- |
| [field] | [type] | What it represents and any constraints |

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

| Attribute             | Detail                                                        |
| --------------------- | ------------------------------------------------------------- |
| **Mechanism**         | How authentication works (JWT, session, OAuth, API key, etc.) |
| **Token acquisition** | How to obtain credentials step by step                        |
| **Roles**             | What roles exist and what each one can access                 |

```json
// Example: Authorization header
{
    "Authorization": "Bearer <token>"
}
```

### Endpoint Inventory

List every endpoint found in the router/controller files, even ones not detailed in the OpenAPI spec below. Build the full path by combining the class-level route prefix (e.g. a Spring controller's `@RequestMapping`) with each method's own mapping, and check whether security is applied at the controller/group level (e.g. `@PreAuthorize`, a security config class) rather than assuming it per-method.

| Method | Path | Controller | Auth |
| ------ | ---- | ---------- | ---- |
| [METHOD] | `/path/to/endpoint` | `ControllerName` | Yes/No — role |

### OpenAPI Specification

Complete OpenAPI 3.0 specification inferred from the codebase — it must include every endpoint listed in the Endpoint Inventory above, not just a representative sample. Do not invent endpoints — only document routes found in the router and controller files.

```yaml
openapi: 3.0.3
info:
    title: "[Project Name] API"
    version: "[inferred version]"
    description: "One-sentence description of the API."

servers:
    - url: "[base URL or placeholder]"

components:
    securitySchemes:
        bearerAuth:
            type: http
            scheme: bearer
            bearerFormat: JWT

    schemas:
        # For each entity in the data model, add a schema here
        EntityName:
            type: object
            properties:
                field:
                    type: string
                    description: What it represents

security:
    - bearerAuth: []

paths:
    /path/to/endpoint:
        post:
            summary: What this endpoint does
            tags: [ResourceGroup]
            security:
                - bearerAuth: [] # remove if no auth required
            requestBody:
                required: true
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                field:
                                    type: string
                                    description: description
            responses:
                "200":
                    description: Success description
                    content:
                        application/json:
                            schema:
                                $ref: "#/components/schemas/EntityName"
                "400":
                    description: When this error occurs
                "401":
                    description: When this error occurs
```

---

## External Integrations

| Integration | File               | Type                          | Purpose                     | Communication           |
| ----------- | ------------------ | ----------------------------- | --------------------------- | ----------------------- |
| [Name]      | `path/to/file.ext` | Database / API / Cloud / etc. | What the system uses it for | SDK / HTTP / ORM / etc. |

---

## Error Handling & Validations

| Concern              | Approach                                   | File               |
| -------------------- | ------------------------------------------ | ------------------ |
| **Error catching**   | Where errors are caught and how            | `path/to/file.ext` |
| **Error format**     | How errors are structured in responses     | `path/to/file.ext` |
| **Input validation** | Strategy used for validating incoming data | `path/to/file.ext` |

---

## Glossary

| Term   | Definition                                  |
| ------ | ------------------------------------------- |
| [Term] | What it means in the context of this system |
