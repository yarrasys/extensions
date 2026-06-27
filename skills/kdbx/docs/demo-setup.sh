# Sandbox setup for the kdbx demo recording (skills/kdbx/docs/demo.tape).
# Sourced inside a VHS `Hide` block so the GIF shows clean `kdbx …` commands
# instead of this plumbing. Creates a throwaway project + vault under /tmp and
# defines a `kdbx` shell function. Nothing here touches your real ~/.config.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KDBX_PY="$(cd "$SCRIPT_DIR/.." && pwd)/kdbx.py"
SB=/tmp/kdbx-demo

rm -rf "$SB"; mkdir -p "$SB/vaults" "$SB/proj"
export KEEPASSXC_DIR="$SB/vaults"          # sandbox the vault dir away from the real one

# A committed pointer maps env-var names to vault entries (contains no secrets).
cat > "$SB/proj/.keepassxc.json" <<'JSON'
{ "project": "demo", "defaultEnv": "dev",
  "envs": { "dev": { "vars": { "OPENAI_API_KEY": "api/openai:password" } } } }
JSON

# A dummy, throwaway secret in a file — never typed, never on argv.
printf 'sk-DEMO-not-a-real-key-1234' > "$SB/proj/secret.txt"

cd "$SB/proj"
kdbx() { uv run --locked "$KDBX_PY" "$@"; }

kdbx envs >/dev/null 2>&1 || true           # warm uv cache so the GIF omits "Installed N packages"
clear
