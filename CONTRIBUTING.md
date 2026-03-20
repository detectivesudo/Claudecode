# Contributing to Claudecode

## Branches

Follow the naming pattern:

```
claude/<short-description>-<session-id>
```

Branch off `main` and target PRs back to `main`.

## Commits

Use the imperative mood, present tense:

```
Add user authentication
Fix token refresh edge case
Update README with setup steps
```

One logical change per commit. Avoid "WIP" or "fix stuff".

## Pull Requests

- Keep PRs small and focused.
- Include a brief summary of what changed and why.
- Add a test plan describing how to verify the change.
- Request review before merging.

## Code Standards

- Read a file fully before editing it.
- Make only the changes required — do not refactor surrounding code opportunistically.
- Do not introduce dead code; remove unused code entirely.
- Never introduce security vulnerabilities (injection, XSS, etc.).

## Reporting Issues

Open an issue on GitHub with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
