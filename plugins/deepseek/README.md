# deepseek — Claude Code plugin

A thin **plugin wrapper** around the [`deepseek` skill](../../skills/deepseek) that
adds capabilities a skill alone cannot provide. The skill stays the portable source
of truth; this plugin shares it by symlink (no duplication) and layers on:

- 🔒 **An enforced autonomy-guard hook** (`PreToolUse`) — the skill's `.deepseek.json`
  `mode` contract is advisory; this hook turns it into a hard gate on agent-issued
  delegate calls.
- ⌨️ **`/deepseek:*` slash commands** — ergonomic entry points for the five operations.

The standalone skill remains available and portable (Agent SDK / claude.ai);
the plugin is **additive and Claude Code-only**. Use the skill if you just want
the model-invoked capability; add the plugin when you want enforcement
and slash commands.

## Install

This repository doubles as a plugin marketplace.

```text
/plugin marketplace add yarrasys/extensions
/plugin install deepseek@yarrasys-extensions
```

(`uv` is required at runtime, as for the skill.)

## What it adds

### Guard hook (`hooks/guard.py`)

A `PreToolUse` hook on **`Bash` commands matching `deepseek delegate`** that
enforces the **autonomy mode** declared in `.deepseek.json`. The skill recommends
modes — this hook gates them:

| Mode | What the hook enforces | Rationale |
|------|------------------------|-----------|
| `auto` | Refuses any `deepseek delegate` call carrying `--in-place`. | Auto-mode forces worktree isolation; `--in-place` bypasses it. A human must re-run with worktree. |
| `explicit` | Refuses agent-initiated delegate unless the command line contains `DEEPSEEK_DELEGATE_APPROVED` (the sentinel supplied by `/deepseek:delegate`). Also refuses when `DEEPSEEK_DELEGATE_DEPTH` is set (no recursive delegation). | The agent must have been explicitly invited via the slash command. |
| `suggest` (default) | No gate — all delegate calls pass through. | Maximum flexibility; safety is by convention. |

All other `deepseek` subcommands (`apply`, `check`, `config`, `init`) pass
through unmodified — the hook is scoped strictly to `delegate`.

Design notes:

- **Fails open.** Any parse error, missing `python3`, or unreadable `.deepseek.json`
  allows the command — a guard must never brick your shell.
- **Scoped to delegation.** The guard only intercepts the one operation where autonomy
  boundaries matter. All other skill operations are unrestricted.
- **Disable it** by removing `hooks/hooks.json` (or uninstall the plugin) and keep
  using the standalone skill — which then states the mode as a contract rather than
  enforcing it.

⚠️ **Honest-guarantee note.** The `explicit` gate stops an over-eager cooperative
agent, not an unforgeable sandbox — an agent could set the sentinel itself. It
raises the bar and makes any bypass a deliberate, visible act, but it cannot
prevent an adversary already past the agent's restraint boundary. This is the same
threat model as the kdbx plugin's role-guard.

### Slash commands (`commands/`)

`/deepseek:delegate` · `/deepseek:apply` · `/deepseek:check` · `/deepseek:config` ·
`/deepseek:init` — thin wrappers over the skill CLI, each supplying the
`DEEPSEEK_DELEGATE_APPROVED` sentinel that satisfies the explicit-mode guard.

| Command | Wraps | Purpose |
|---------|-------|---------|
| `delegate` | `deepseek delegate` | Delegate a bounded dev task to a headless DeepSeek agent (human-invoked → supplies approved sentinel). |
| `apply` | `deepseek apply` | Land a withheld patch (`.deepseek/edit-*.patch`) from a prior `patch_ready` receipt. |
| `check` | `deepseek check` | Offline preflight — `claude`/`git` on PATH and `DEEPSEEK_API_KEY` resolvable (no live endpoint ping). |
| `config` | `deepseek config` | Print the effective merged config (read-only; defaults + `.deepseek.json`). |
| `init` | `deepseek init` | Scaffold `.deepseek.json` for a project (refuses to overwrite). |

### No MCP server

Unlike the kdbx plugin, this plugin ships **no MCP server**. All operations are
triggered through slash commands or via the agent's Bash calls — a proven pattern
for this workflow. An MCP server is deferred as YAGNI; if concrete needs emerge
(typed tool schemas for non-Claude-Code hosts), it can be added later without
breaking changes.

## Layout

```text
plugins/deepseek/
├── .claude-plugin/plugin.json
├── skills/deepseek -> ../../../skills/deepseek   # symlink: shared skill (dereferenced + copied on install)
├── hooks/{hooks.json, guard.py}                  # PreToolUse autonomy-guard (stdlib-only, fails open)
├── commands/*.md                                 # /deepseek:* slash commands
└── tests/test_plugin_guard.py                    # guard unit tests (run in CI via pytest.ini)
```

This README's first draft was itself produced by delegating to DeepSeek through
the skill (`deepseek delegate`), then reviewed and corrected — dogfooding in
practice.
