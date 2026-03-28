# CLAUDE.md

This file provides guidance to AI assistants (Claude and others) working in this repository.

## Project Overview

**Claudecode** is a JavaScript library providing Shopify AJAX cart utilities. The core module (`src/shopify-cart.js`) wraps Shopify's storefront cart endpoints with cookie-based session management via `tough-cookie`.

## Repository State (as of 2026-03-28)

- **Language/Runtime**: JavaScript (ES Modules, no transpilation configured)
- **Dependencies**: `tough-cookie` (cookie jar management)
- **Tests**: None present
- **CI/CD**: None configured
- **Main branch**: `main`

## Codebase Structure

```
Claudecode/
├── src/
│   └── shopify-cart.js   # Core Shopify cart module (ES module)
├── README.md
└── CLAUDE.md
```

### `src/shopify-cart.js`

Exports:
- `ShopifyCartError` — custom Error subclass with `code` and `status` fields
- `createShopifyCart(storeUrl, options?)` — factory returning a cart client with three methods:
  - `addVariant(variantId, quantity?)` — POST `/cart/add.js`
  - `getCart()` — GET `/cart.js`
  - `getCheckoutUrl()` — fetches cart token and returns the checkout URL

All HTTP calls go through `fetchWithCookies` (module-private), which reads/writes a shared `CookieJar` so session cookies persist across requests within a single cart instance.

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

```bash
# Clone the repository
git clone https://github.com/detectivesudo/Claudecode.git
cd Claudecode

# Switch to the correct feature branch
git checkout claude/<branch-name>

# Install dependencies (once a package.json is added)
npm install
```

The project currently has no `package.json`. When adding one, include `tough-cookie` as a dependency and configure `"type": "module"` since the source uses ES module syntax.

## Testing

No test suite exists yet. When one is introduced, document here:
- The testing framework (e.g., Jest with `--experimental-vm-modules` for ESM, Vitest)
- How to run all tests: `<command>`
- How to run a single test file: `<command>`
- Coverage requirements or thresholds

## Build & Deployment

No build or deployment pipeline exists yet. The module is written as a native ES module and requires no compilation step. When a bundler or publish workflow is added, document here:
- Build command
- Deployment targets and commands
- Environment-specific configuration

## Code Style & Linting

No linters or formatters are configured yet. The existing code uses:
- 2-space indentation
- Single quotes for strings
- `async`/`await` throughout (no `.then()` chains)
- Named exports for public API; unexported helper functions for internals

When a linter is added (e.g., ESLint + Prettier), document the run commands here.

## Key Conventions

| Area | Convention |
|---|---|
| Branching | `claude/<description>-<id>` |
| Commit messages | Imperative mood, present tense |
| PR target | `main` |
| Module format | ES Modules (`import`/`export`) |
| Error handling | Throw `ShopifyCartError` with a `code` string constant |
| HTTP | Use `fetchWithCookies` for all requests so the cookie jar stays in sync |

---

*This file should be kept up to date as the project evolves. Update it whenever new tooling, conventions, or workflows are established.*
