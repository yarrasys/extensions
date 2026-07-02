"""Pure guardrail predicates: recursion, deny-globs, budget."""

from collections.abc import Mapping
from fnmatch import fnmatch

DEPTH_ENV = "DEEPSEEK_DELEGATE_DEPTH"


def is_recursive(environ: Mapping) -> bool:
    return DEPTH_ENV in environ


def _match(path: str, pattern: str) -> bool:
    # fnmatch treats "*" as crossing "/", so "**/" and "/**" behave recursively enough
    # for our globs; normalise "**/" to "*" for a leading recursive match.
    if fnmatch(path, pattern):
        return True
    if pattern.startswith("**/") and fnmatch(path, pattern[3:]):
        return True
    if pattern.endswith("/**") and (path == pattern[:-3] or path.startswith(pattern[:-2])):
        return True
    return False


def denied_paths(changed: list[str], deny_globs: list[str]) -> list[str]:
    return [p for p in changed if any(_match(p, g) for g in deny_globs)]


def within_budget(reported_usd, cap_usd: float) -> bool:
    if reported_usd is None:
        return True
    return reported_usd <= cap_usd
