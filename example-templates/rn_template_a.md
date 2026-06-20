# Release [INFER VERSION: MAJOR.MINOR.PATCH]

| Field             | Value                                                                         |
| ----------------- | ----------------------------------------------------------------------------- |
| **Version**       | MAJOR.MINOR.PATCH                                                             |
| **Version Type**  | MAJOR / MINOR / PATCH                                                         |
| **Justification** | Why this version type was chosen based on the nature and scope of the changes |
| **Contributors**  | List of contributors, inferred from commit authors                            |

---

## Summary

Eye-catching headline and a high-level summary of the most impactful changes. Written for a developer who hasn't seen the diff — explain what changed and why it matters, not just what files were touched.

---

## Breaking Changes

List any change that breaks backward compatibility, modifies a public API contract, or requires action from consumers of this system. Include migration guidance for each.
If none, write: _No breaking changes in this release._

---

## Changes

For each change, describe the impact on the system or its consumers — not just what lines or files changed. Mention the affected module or file when it adds clarity. Group by type.

### Features

New functionality that did not exist before.

- **[INFER NAME]** (`affected-module/file`): What was added, what it enables, and what impact it has on the system or its users.

### Enhancements

Improvements to existing functionality without breaking changes.

- **[INFER NAME]** (`affected-module/file`): What was improved, what the previous behavior was, and what changed.

### Bug Fixes

Corrections to defects or unexpected behaviors.

- **[INFER NAME]** (`affected-module/file`): What was broken, what the fix does, and what scenarios it corrects.

### Tests

New or updated tests.

- **[INFER NAME]** (`affected-module/file`): What is now covered, what confidence it adds, or what regression it prevents.

### Other

Refactors, dependency updates, configuration or documentation changes. Group minor changes (variable renames, formatting, comments) into a single entry rather than listing each one individually.

- **[INFER NAME]** (`affected-module/file`): What changed and why, even if there is no functional impact.

---

## Affected Components

Bullet list of the modules, services or files with the most significant changes in this release, with a one-line description of what changed in each.

- [`path/to/file.ext`] — summary of what changed.
