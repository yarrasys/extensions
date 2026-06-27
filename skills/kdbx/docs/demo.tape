# kdbx demo — regenerate with:  vhs skills/kdbx/docs/demo.tape   (run from repo root)
# Produces skills/kdbx/docs/demo.gif. Requires: vhs, uv. Self-contained & sandboxed
# (see demo-setup.sh) — it never touches your real ~/.config/keepassxc.
#
# VHS renders via a headless browser (go-rod). If it errors with
# "could not open ttyd: ... ERR_CONNECTION_REFUSED", point rod at a local Chrome:
#   ROD_BROWSER_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" vhs ...

Output skills/kdbx/docs/demo.gif

Require uv
Set Shell "bash"
Set FontSize 19
Set Width 1180
Set Height 760
Set Padding 28
Set Theme "Catppuccin Mocha"
Set TypingSpeed 30ms

# --- hidden sandbox setup -------------------------------------------------
Hide
Type "source skills/kdbx/docs/demo-setup.sh" Enter
Sleep 2s
Show

# --- visible demo ---------------------------------------------------------
# A blank `Enter` between blocks emits an empty prompt line, spacing the
# command/output groups apart so they're easier to read back in the GIF.
Type "# kdbx: per-project, per-env secrets in a key-file-only KeePassXC vault" Sleep 400ms Enter
Sleep 700ms

Type "kdbx init                       # create the dev vault + key file (0600)" Sleep 300ms Enter
Sleep 1.8s
Enter Sleep 500ms

Type "# store a secret from a file — never typed, never on argv, never echoed" Sleep 400ms Enter
Type "kdbx set api/openai < secret.txt" Sleep 300ms Enter
Sleep 1.3s
Enter Sleep 500ms

Type "kdbx get api/openai             # masked by default" Sleep 300ms Enter
Sleep 1.4s
Enter Sleep 500ms

Type "# inject into a child process — the value is never printed" Sleep 400ms Enter
Type "kdbx run -- sh -c 'echo OPENAI_API_KEY is ${#OPENAI_API_KEY} chars'" Sleep 300ms Enter
Sleep 1.8s
Enter Sleep 500ms

Type "kdbx check                      # every mapped var resolves" Sleep 300ms Enter
Sleep 1.8s

Sleep 1.5s
