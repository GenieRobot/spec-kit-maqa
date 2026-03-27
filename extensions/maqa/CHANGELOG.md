# MAQA Changelog

## 0.1.5 — 2026-03-27

- Feature agent: add CRITICAL cwd warning — Bash resets working directory to main repo between invocations; every git/test command must be prefixed with `cd <worktree> &&` to prevent index corruption
- Setup command: propagate cwd warning into deployed `.claude/agents/feature.md` key rules

## 0.1.2 — 2026-03-26

- Coordinator: auto-populate prompt triggers whenever any local spec is missing from the board (not only when board is empty)

## 0.1.1 — 2026-03-26

- Coordinator: auto-populate prompt when Trello board is empty but local specs exist

## 0.1.0 — 2026-03-26

Initial release.

- Coordinator command: assess ready features, create git worktrees, return SPAWN plan
- Feature command: implement one feature per worktree, optional TDD cycle, optional tests
- QA command: static analysis quality gate with configurable checks
- Setup command: deploy native Claude Code subagents to .claude/agents/
- Optional Trello integration via companion extension maqa-trello
- Language-agnostic: works with any stack; configure test runner in maqa-config.yml
