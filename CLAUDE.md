# CLAUDE.md

This file provides guidance to AI assistants (Claude and others) working in this repository.

## Project Overview

**Claudecode** is a project in its initial state. The repository currently contains only a README and this documentation file. As the project grows, this file should be updated to reflect the actual codebase structure, tooling, and conventions.

## Repository State (as of 2026-03-20)

- **Language/Framework**: Not yet established
- **Dependencies**: None present
- **Tests**: None present
- **CI/CD**: None configured
- **Main branch**: `main` (remote), `master` (local default)

## Git Workflow

### Branch Naming

Feature and task branches follow the pattern:
```
claude/<short-description>-<session-id>
```

Examples:
- `claude/add-claude-documentation-0nXNm`

### Commit Style

Write clear, descriptive commit messages in the imperative mood:
```
Add initial project structure
Fix authentication token refresh logic
Update CLAUDE.md with build instructions
```

Avoid vague messages like "fix stuff" or "WIP".

### Push Commands

Always push with upstream tracking:
```bash
git push -u origin <branch-name>
```

If a push fails due to network errors, retry up to 4 times with exponential backoff (2s, 4s, 8s, 16s).

### Pull Requests

When creating PRs:
- Target the `main` branch unless otherwise specified
- Include a summary of changes and a test plan in the PR body

## Development Guidelines for AI Assistants

### General Principles

1. **Read before modifying** — Always read a file fully before editing it.
2. **Minimal changes** — Only make changes that are directly requested or clearly necessary. Do not refactor surrounding code, add docstrings to untouched functions, or introduce extra abstractions.
3. **No speculation** — Do not add features, error handling, or configuration for hypothetical future requirements.
4. **Security-first** — Never introduce command injection, XSS, SQL injection, or other OWASP Top 10 vulnerabilities. Fix any such issues immediately if discovered.
5. **No backwards-compatibility hacks** — Remove dead code fully rather than commenting it out or aliasing it.

### File Management

- Prefer editing existing files over creating new ones.
- Do not create documentation files (README, CLAUDE.md, etc.) unless explicitly requested.
- Do not create helper utilities for one-off operations.

### Reversibility & Blast Radius

Before taking any action, consider:
- **Local, reversible actions** (editing files, running tests) — proceed freely.
- **Destructive or hard-to-reverse actions** (deleting files, force-pushing, dropping data) — confirm with the user first.
- **Actions visible to others** (pushing code, opening PRs, posting comments) — confirm unless explicitly pre-authorized.

## Setting Up the Project

Since the project is in its early stages, the setup steps will evolve. At minimum:

```bash
# Clone the repository
git clone <repo-url>
cd Claudecode

# Switch to the correct feature branch (if working on a task)
git checkout claude/<branch-name>
```

When a language/framework is chosen, update this section with:
- Dependency installation commands
- Environment variable setup (`.env.example`)
- Database/service setup steps
- How to start the development server

## Testing

No test suite exists yet. When one is introduced, document here:
- The testing framework (e.g., Jest, pytest, Go test)
- How to run all tests: `<command>`
- How to run a single test file: `<command>`
- Coverage requirements or thresholds

## Build & Deployment

No build or deployment pipeline exists yet. When configured, document here:
- Build command
- Deployment targets and commands
- Environment-specific configuration

## Code Style & Linting

No linters or formatters are configured yet. When added, document here:
- Linter (ESLint, Ruff, Clippy, etc.) and run command
- Formatter (Prettier, Black, rustfmt, etc.) and run command
- Whether formatting is enforced in CI

## Key Conventions (to be filled as the project grows)

| Area | Convention |
|---|---|
| Branching | `claude/<description>-<id>` |
| Commit messages | Imperative mood, present tense |
| PR target | `main` |

---

*This file should be kept up to date as the project evolves. Update it whenever new tooling, conventions, or workflows are established.*
