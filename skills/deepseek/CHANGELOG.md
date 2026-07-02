# Changelog — deepseek

All notable changes to the **deepseek** skill. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and [SemVer](https://semver.org/spec/v2.0.0.html).
Releases are tagged `deepseek/v<version>`.

## [Unreleased]

### Added

- Initial `deepseek` skill: `delegate` a bounded dev task to a nested headless `claude`
  running on DeepSeek's Anthropic-compatible endpoint; `init`, `check`, `config`, `apply`.
- Worktree+patch isolation by default; `--in-place` opt-in. Per-project `.deepseek.json`
  with autonomy modes (explicit/suggest/auto) and guardrails (deny-globs, per-run cost cap,
  recursion guard).
