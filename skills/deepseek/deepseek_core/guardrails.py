"""Pure guardrail predicates: recursion, deny-globs, budget."""

from collections.abc import Mapping
from fnmatch import fnmatch

DEPTH_ENV = "DEEPSEEK_DELEGATE_DEPTH"


def is_recursive(environ: Mapping[str, str]) -> bool:
    return DEPTH_ENV in environ


def denied_paths(changed: list[str], deny_globs: list[str]) -> list[str]:
    # fnmatch's `*` already crosses `/`, so `.github/**` matches nested paths directly.
    return [p for p in changed if any(fnmatch(p, g) for g in deny_globs)]


def within_budget(reported_usd: float | None, cap_usd: float) -> bool:
    if reported_usd is None:
        return True
    return reported_usd <= cap_usd
